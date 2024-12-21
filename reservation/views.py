from django.shortcuts import render

# Create your views here.
def my_reservations(request):
    reservations = [
        {
            'title': 'Lakeside Motel Warefront',
            'rating': '4.5',
            'reviews': '1,200 Reviews',
            'non_refundable': True,
            'check_in': 'Sunday, March 18, 2022',
            'check_out': 'Tuesday, March 20, 2022',
            'nights': 2,
            'room_details': '1 room, 2 days',
            'price': '€1,200',
            'tax_inclusive': True,
        }
    ]
    
    return render(request, 'reservations/my_reservations.html', {'reservations': reservations})