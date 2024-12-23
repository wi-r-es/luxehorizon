from django.db import connection
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import render

class AdminEmployeeDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def call_stored_procedure(self, proc_name, *params):
        with connection.cursor() as cursor:
            cursor.callproc(proc_name, params)
            results = cursor.fetchall()
            colnames = [desc[0] for desc in cursor.description]
            return [dict(zip(colnames, row)) for row in results]

    def get(self, request, *args, **kwargs):
    # Call the stored procedures
        overview = self.call_stored_procedure('get_overview')[0]
        top_placements = self.call_stored_procedure('get_top_placements')
        sales_data = self.call_stored_procedure('get_sales_over_time')

        # Handle None values
        total_revenue = overview.get('total_revenue') or 0
        expected_guests = overview.get('expected_guests') or 0

        context = {
            "total_revenue": f"{total_revenue:,.2f} €",
            "expected_guests": f"{expected_guests:,}",
            "top_placements": top_placements,
            "sales_over_time": sales_data,
        }

        return render(request, self.template_name, context)


# overview = {
#     "total_revenue": 1234567.89,
#     "expected_guests": 5000,
# }

# top_placements = [
#     {"city": "New York", "revenue": 100000.50},
#     {"city": "London", "revenue": 90000.25},
#     {"city": "Tokyo", "revenue": 85000.00},
#     {"city": "Sydney", "revenue": 75000.75},
#     {"city": "Berlin", "revenue": 70000.10},
# ]

# sales_data = [
#     {"day": 1, "revenue": 1200.50},
#     {"day": 2, "revenue": 1350.75},
#     {"day": 3, "revenue": 1400.30},
#     {"day": 4, "revenue": 1500.60},
#     {"day": 5, "revenue": 1600.00},
#     {"day": 6, "revenue": 1700.40},
#     {"day": 7, "revenue": 1800.20},
#     {"day": 8, "revenue": 1900.50},
#     {"day": 9, "revenue": 2000.00},
#     {"day": 10, "revenue": 2100.75},
#     {"day": 11, "revenue": 2200.30},
#     {"day": 12, "revenue": 2300.60},
#     {"day": 13, "revenue": 2400.90},
#     {"day": 14, "revenue": 2500.50},
#     {"day": 15, "revenue": 2600.20},
#     {"day": 16, "revenue": 2700.40},
#     {"day": 17, "revenue": 2800.10},
#     {"day": 18, "revenue": 2900.80},
#     {"day": 19, "revenue": 3000.00},
#     {"day": 20, "revenue": 3100.20},
#     {"day": 21, "revenue": 3200.50},
#     {"day": 22, "revenue": 3300.75},
#     {"day": 23, "revenue": 3400.10},
#     {"day": 24, "revenue": 3500.40},
#     {"day": 25, "revenue": 3600.60},
#     {"day": 26, "revenue": 3700.90},
#     {"day": 27, "revenue": 3800.75},
#     {"day": 28, "revenue": 3900.20},
#     {"day": 29, "revenue": 4000.50},
#     {"day": 30, "revenue": 4100.30},
# ]

# context = {
#     "total_revenue": f"{overview['total_revenue']:,.2f} €",
#     "expected_guests": f"{overview['expected_guests']:,}",
#     "top_placements": top_placements,
#     "sales_over_time": sales_data,
# }

# return render(request, self.template_name, context)
