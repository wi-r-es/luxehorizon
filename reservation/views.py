from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse
from .models import Reservation, RoomReservation, Guest, Season
from hotel_management.models import Room
from .forms import SeasonForm

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

            # Chamar o procedimento no banco de dados
            with connection.cursor() as cursor:
                cursor.execute("""
                    CALL create_reservation(%s, %s, %s, %s, %s);
                """, [user_id, room_id, checkin, checkout, guests])

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

    # Sorting
    sort = request.GET.get('sort', 'descriptive')
    order = request.GET.get('order', 'asc')
    
    if order == 'desc':
        sort = '-' + sort

    # Sort seasons based on the sort parameter
    seasons = seasons.order_by(sort)

    # Passing context to the template
    context = {
        'seasons': seasons,
        'query': query,
        'sort': sort.lstrip('-'),  
        'order': order,

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