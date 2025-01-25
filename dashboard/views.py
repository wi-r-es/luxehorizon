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
        raw_sales_data = self.call_stored_procedure('get_sales_over_time')

        # Handle None values
        total_revenue = overview.get('total_revenue') or 0
        expected_guests = overview.get('expected_guests') or 0

        # Transform the data into the required format
        sales_data = [
            {"day": item["day"], "revenue": float(item["revenue"])}
            for item in raw_sales_data
            if "day" in item and "revenue" in item
        ]

        if not sales_data:
            sales_data = []

        context = {
            "total_revenue": f"{total_revenue:,.2f} €",
            "expected_guests": f"{expected_guests:,}",
            "top_placements": top_placements,
            "sales_over_time": sales_data,
        }

        return render(request, self.template_name, context)

def employee_dashboard(request):
    return render(request, 'dashboard/employee_dash.html')
