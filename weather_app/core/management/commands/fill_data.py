from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Series, Measurement
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = "Generuje 14 dni danych pogodowych od 22.11.2025"

    def handle(self, *args, **options):
        Series.objects.all().delete()
        Measurement.objects.all().delete()

        start_date = datetime(2025, 11, 22)
        colors = [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
            "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
            "#aec7e8", "#ffbb78", "#98df8a", "#ff9896", "#c5b0d5"
        ]

        for day_offset in range(14):
            current_date = start_date + timedelta(days=day_offset)
            color = colors[day_offset % len(colors)]
            base_temp = random.uniform(-8, 8)      # średnia dzienna
            amplitude = random.uniform(4, 12)      # amplituda dobowa

            hourly_temps = []
            for hour in range(24):
                temp_shift = -amplitude * 0.8 * ((hour - 14) ** 2) / 196 + amplitude
                noise = random.uniform(-1.5, 1.5)
                temp = base_temp + temp_shift + noise
                hourly_temps.append(round(temp, 1))

            daily_min = min(hourly_temps)
            daily_max = max(hourly_temps)

            series = Series.objects.create(
                date=current_date.date(),
                color=color
            )

            base_dt = datetime.combine(current_date.date(), datetime.min.time())

            for hour, temp in enumerate(hourly_temps):
                Measurement.objects.create(
                    series=series,
                    timestamp=base_dt + timedelta(hours=hour),
                    value=temp
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Dzień {current_date.date()} | Min: {daily_min}°C | Max: {daily_max}°C | Kolor: {color}"
                )
            )

        self.stdout.write(self.style.SUCCESS("Gotowe! Wygenerowano 14 dni danych (22.11 – 05.12.2025)"))
