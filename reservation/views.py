from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse
from .models import Reservation, RoomReservation, Guest, Season
from hotel_management.models import Room
from .forms import SeasonForm
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.db.models import Q  

def my_reservations(request):
    # Fetch reservations for the logged-in user
    reservations = Reservation.objects.filter(client=request.user).prefetch_related('room_reservations__room__hotel')
    reservation_list = []

    for reservation in reservations:
        refundable = False  # Substituir por `reservation.is_refundable()` se a lógica for implementada

        # Verificar se existem associações com quartos
        if reservation.room_reservations.exists():
            # Obter detalhes do(s) quarto(s)
            room_details = ", ".join(
                [f"Room {rr.room.room_number} at {rr.room.hotel.h_name}" for rr in reservation.room_reservations.all()]
            )

            # Buscar o hotel associado ao primeiro quarto
            hotel = reservation.room_reservations.first().room.hotel
            hotel_rating = hotel.stars
        else:
            # Configuração padrão para reservas sem quartos
            room_details = "No rooms associated"
            hotel_rating = 0

        # Calcular o número de noites
        nights = (reservation.end_date - reservation.begin_date).days

        print(reservation.begin_date)
        print(reservation.end_date)
        
        reservation_list.append({
            'id': reservation.id,
            'title': room_details,
            'check_in': reservation.begin_date,
            'check_out': reservation.end_date,
            'nights': nights,
            'price': reservation.total_value,
            'tax_inclusive': True,  # Assuming tax inclusion for all reservations
            'non_refundable': not refundable,
            'hotel_rating': hotel_rating,
            'status': reservation.status,
        })

    return render(request, 'reservations/my_reservations.html', {'reservations': reservation_list})

def all_reservations(request):
    # Fetch all reservations
    reservations = Reservation.objects.prefetch_related('room_reservations__room__hotel')

    # Filtrar por pesquisa (se fornecido na requisição)
    search_query = request.GET.get('q', '')
    if search_query:
        reservations = reservations.filter(
            Q(status__icontains=search_query) |
            Q(begin_date__icontains=search_query) |
            Q(end_date__icontains=search_query) |
            Q(room_reservations__room__hotel__h_name__icontains=search_query) |
            Q(room_reservations__room__room_number__icontains=search_query) |
            Q(client__first_name__icontains=search_query) |
            Q(client__last_name__icontains=search_query) |
            Q(client__nif__icontains=search_query)
        ).distinct()

    # Filtrar por mês (se fornecido na requisição)
    selected_month = request.GET.get('month')
    if selected_month:
        reservations = reservations.filter(begin_date__month=selected_month)

    # Obter lista de meses disponíveis
    months = (
        reservations.annotate(month=TruncMonth('begin_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    # Preparar lista de meses para a combobox
    month_choices = [{'value': m['month'].month, 'name': m['month'].strftime('%B'), 'count': m['count']} for m in months]

    reservation_list = []

    for reservation in reservations:
        # Verificar associações com quartos
        if reservation.room_reservations.exists():
            room_details = ", ".join(
                [f"Room {rr.room.room_number} at {rr.room.hotel.h_name}" for rr in reservation.room_reservations.all()]
            )
            first_room_reservation = reservation.room_reservations.first()
            hotel_rating = first_room_reservation.room.hotel.stars if first_room_reservation else 0
        else:
            room_details = "No rooms associated"
            hotel_rating = 0

        try:
            nights = (reservation.end_date - reservation.begin_date).days
        except (TypeError, AttributeError):
            nights = 0

        reservation_list.append({
            'id': reservation.id,
            'client': reservation.client.first_name + ' ' + reservation.client.last_name,
            'nif': reservation.client.nif,
            'title': room_details,
            'check_in': reservation.begin_date,
            'check_out': reservation.end_date,
            'nights': nights,
            'price': reservation.total_value,
            'tax_inclusive': True,
            'hotel_rating': hotel_rating,
            'status': reservation.status,
        })

    has_actions = any(reservation['status'] not in ['CC', 'CO'] for reservation in reservation_list)

    return render(
        request,
        'reservations/list_resertions_employee.html',
        {
            'reservations': reservation_list,
            'has_actions': has_actions,
            'months': month_choices,
            'selected_month': selected_month,
        }
    )

def reservation_details(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    nights = (reservation.end_date - reservation.begin_date).days
    return render(request, 'reservations/check_in.html', {'reservation': reservation, 'nights': nights})

def check_in(request, reservation_id):
    print(reservation_id)
            
    # Chamar o procedimento armazenado no banco de dados
    with connection.cursor() as cursor:
        cursor.execute("""CALL sp_check_in(%s);""", [reservation_id])

    # Redirecionar para a página de reservas com uma mensagem de sucesso
    return redirect('list_reservations_employee')

def check_out(request, reservation_id):
    print(reservation_id)
            
    # Chamar o procedimento armazenado no banco de dados
    with connection.cursor() as cursor:
        cursor.execute("""CALL sp_check_out(%s);""", [reservation_id])

    # Redirecionar para a página de reservas com uma mensagem de sucesso
    return redirect('list_reservations_employee')

def payment(request):
    if request.method == "POST":
        try:
            # Extrair o ID da reserva do formulário
            reservation_id = int(request.POST.get("reservation_id"))
            
            # Atualizar o campo invoice_status para acionar o trigger
            #with connection.cursor() as cursor:
            #    cursor.execute("""
            #       UPDATE "finance.invoice"
            #        SET invoice_status = TRUE
            #        WHERE reservation_id = %s;
            #    """, [reservation_id])

            with connection.cursor() as cursor:
                cursor.execute('SELECT id FROM "finance.invoice" WHERE reservation_id = %s;', [reservation_id])
                _invoice_id = cursor.fetchone()[0]
                print('_invoice_id', _invoice_id)

            with connection.cursor() as cursor:
                cursor.execute('SELECT total_value FROM "reserves.reservation" WHERE id = %s;', [reservation_id])
                _payment_amount = cursor.fetchone()[0]
                print('_payment_amount', _payment_amount)

            with connection.cursor() as cursor:
                cursor.execute('SELECT payment_method_id FROM "finance.invoice" WHERE id = %s;', [_invoice_id])
                _payment_method_id = cursor.fetchone()[0]
                print('_payment_method_id', _payment_method_id)

            with connection.cursor() as cursor:
                cursor.execute("""CALL sp_add_payment(%s, %s, %s);""", [_invoice_id, _payment_amount, _payment_method_id])
            
            # Redirecionar para a página de reservas com uma mensagem de sucesso
            return redirect('list_reservations_employee')
        except Exception as e:
            # Caso ocorra um erro, renderizar a página com uma mensagem de erro
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Método não suportado. Use POST."}, status=405)

def reservation_page(request, room_id):

    hotel_id = request.GET.get('hotel_id')
    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')
    guests = request.GET.get('guests')
    
    # Busca os dados do quarto pelo room_id
    room = get_object_or_404(Room, id=room_id)
    
    # Adicionar user_id no contexto
    user_id = request.user.id
    user_name = request.user.first_name
    user_last_name = request.user.last_name
    user_email = request.user.email
    user_nif = request.user.nif
    user_phone = request.user.phone
    user_address = request.user.full_address
    user_postal_code = request.user.postal_code
    user_city = request.user.city

    context = {
        'room': room,
        'hotel_id': hotel_id,
        'hotel_name': room.hotel,
        'checkin': checkin,
        'checkout': checkout,
        'guests': guests,
        'user_id': user_id,  
        'user_name': user_name,
        'user_last_name': user_last_name,
        'user_email': user_email,
        'user_nif': user_nif,
        'user_phone': user_phone,
        'user_address': user_address,
        'user_postal_code': user_postal_code,
        'user_city': user_city
    }
    return render(request, 'reservations/reservation_page.html', context)

def confirm_reservation(request):
    if request.method == "POST":
        try:
            # Receber os parâmetros do corpo da requisição
            user_id = int(request.POST.get("user_id"))
            room_id = int(request.POST.get("room_id"))
            checkin = request.POST.get("checkin")  # Formato: YYYY-MM-DD
            checkout = request.POST.get("checkout")  # Formato: YYYY-MM-DD
            guests = int(request.POST.get("guests"))

            # verificacao se quer pagar agora ou depois
            payment_method_id = 1 # Método de pagamento padrão (credit card)

            # Chamar o procedimento no banco de dados
            with connection.cursor() as cursor:
                cursor.execute("""
                    CALL sp_create_reservation(%s, %s, %s, %s, %s);
                """, [user_id, room_id, checkin, checkout, guests])

                cursor.execute('SELECT MAX(id) FROM "reserves.reservation"')
                reservation_id = cursor.fetchone()[0]

                cursor.execute("""
                    CALL sp_generate_invoice(%s, %s, %s);
                """, [reservation_id, payment_method_id, None])

            return redirect('my_reservations')
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Método não suportado. Use POST."}, status=405)

def cancel_reservation(request):
    if request.method == "POST":
        try:
            # Extrair o ID da reserva do formulário
            reservation_id = int(request.POST.get("reservation_id"))

            # Chamar o procedimento armazenado no banco de dados
            with connection.cursor() as cursor:
                cursor.execute("""
                    CALL sp_cancel_reservation(%s);
                """, [reservation_id])

            # Redirecionar para a página de reservas com uma mensagem de sucesso
            return redirect('my_reservations')
        except Exception as e:
            # Caso ocorra um erro, renderizar a página com uma mensagem de erro
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Método não suportado. Use POST."}, status=405)

def season_list(request):
    # Get the query parameter for searching
    query = request.GET.get('q', '')

    # Filter seasons based on the query
    seasons = Season.objects.all()
    if query:
        seasons = seasons.filter(descriptive__icontains=query)

    # Sorting parameters
    sort = request.GET.get('sort', 'descriptive')  # Default sorting field
    order = request.GET.get('order', 'asc')  # Default order is ascending

    # Validate sorting fields
    valid_sort_fields = ['descriptive', 'begin_month', 'begin_day', 'end_month', 'end_day', 'rate']
    if sort not in valid_sort_fields:
        sort = 'descriptive'  # Fallback to default sorting

    # Adjust for descending order if specified
    if order == 'desc':
        sort = f"-{sort}"

    # Apply sorting to the queryset
    seasons = seasons.order_by(sort)

    # Format context data
    context = {
        'seasons': [
            {
                'id': season.id,
                'descriptive': season.get_descriptive_display(),  # Use display name for choices
                'begin_date': f"{season.begin_day}/{season.begin_month}",
                'end_date': f"{season.end_day}/{season.end_month}",
                'rate': season.rate,
            }
            for season in seasons
        ],
        'query': query,
        'sort': sort.lstrip('-'),  # Pass the current sorting field without the '-' for templates
        'order': order,  # Pass the current order for templates
    }
    return render(request, 'seasons/seasons_list.html', context)


def season_form(request, season_id=None):
    if season_id:
        season = get_object_or_404(Season, id=season_id)
        operation = "editar"
    else:
        season = None
        operation = "adicionar"

    if request.method == 'POST':
        form = SeasonForm(request.POST, instance=season)
        if form.is_valid():
            new_season = form.save(commit=False)
            new_season.save()
            messages.success(request, f"{'Temporada adicionada' if season is None else 'Temporada atualizada'} com sucesso!")
            return redirect('seasons_list')
        else:
            messages.error(request, "Erro ao processar o formulário.")
    else:
        form = SeasonForm(instance=season)

    return render(request, 'seasons/seasons_form.html', {
        'form': form,
        'operation': operation,
        'season': season or {},
    })
