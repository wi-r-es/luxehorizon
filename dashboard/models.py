from django.db import models

class PerformanceOverview(models.Model):
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    expected_guests = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Performance Overview"
        verbose_name_plural = "Performance Overviews"

    def __str__(self):
        return f"Revenue: {self.total_revenue} | Guests: {self.expected_guests}"


class TopPlacement(models.Model):
    city = models.CharField(max_length=100)
    revenue = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Top Placement"
        verbose_name_plural = "Top Placements"

    def __str__(self):
        return f"{self.city}: {self.revenue} €"


class SalesOverTime(models.Model):
    day = models.PositiveIntegerField()
    revenue = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Sales Over Time"
        verbose_name_plural = "Sales Over Time"

    def __str__(self):
        return f"Day {self.day}: {self.revenue} €"
