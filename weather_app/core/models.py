from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Min, Max
from django.db import transaction
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] 

    def save(self, *args, **kwargs):
        if not self.username or self.username != self.email:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

class Series(models.Model):
    """
    Seria = jeden dzień.
    min_temp i max_temp są obliczane z Measurement.
    """
    date = models.DateField(unique=True, db_index=True)
    color = models.CharField(max_length=7, default="#1f77b4")

    class Meta:
        verbose_name_plural = "series"
        ordering = ['-date']

    def __str__(self):
        return self.date.isoformat()

    def get_min_temp(self):
        """Zwraca aktualne minimum z pomiarów lub None."""
        return self.measurements.aggregate(min_val=Min('value'))['min_val']

    def get_max_temp(self):
        """Zwraca aktualne maksimum z pomiarów lub None."""
        return self.measurements.aggregate(max_val=Max('value'))['max_val']

    def update_min_max(self):
        """Aktualizuje min/max na podstawie wszystkich pomiarów."""
        min_val = self.get_min_temp()
        max_val = self.get_max_temp()
        # Zapisujemy jako adnotacje – nie pola w DB
        self._current_min = min_val
        self._current_max = max_val

    def save(self, *args, **kwargs):
        if not self.color:
            palette = [
                "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
                "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
            ]
            self.color = palette[Series.objects.count() % len(palette)]
        super().save(*args, **kwargs)

class Measurement(models.Model):
    """
    Jeden pomiar temperatury.
    Automatycznie aktualizuje min/max w Series.
    """
    series = models.ForeignKey(
        Series, on_delete=models.CASCADE, related_name="measurements"
    )
    timestamp = models.DateTimeField(db_index=True)
    value = models.FloatField(
        validators=[MinValueValidator(-100), MaxValueValidator(100)]
    )

    class Meta:
        unique_together = ('series', 'timestamp')
        indexes = [
            models.Index(fields=['series', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.timestamp} | {self.value}°C | {self.series}"

    def clean(self):
        # Czy timestamp jest w dniu serii
        if self.timestamp.date() != self.series.date:
            raise ValidationError("Data pomiaru musi zgadzać się z datą serii.")

    def save(self, *args, **kwargs):
        # Utwórz serię, jeśli nie istnieje
        if not self.series_id:
            series, created = Series.objects.get_or_create(
                date=self.timestamp.date(),
                defaults={'color': '#1f77b4'}
            )
            self.series = series

        if not (-100 <= self.value <= 100):
            raise ValidationError("Temperatura musi być w zakresie -100 do 100°C.")

        with transaction.atomic():
            super().save(*args, **kwargs)
            self._update_series_min_max()

    def _update_series_min_max(self):
        """Aktualizuje min/max serii na podstawie wszystkich pomiarów."""
        current_min = self.series.get_min_temp()
        current_max = self.series.get_max_temp()

        # Porównaj z nowym pomiarem
        new_min = min(current_min, self.value) if current_min is not None else self.value
        new_max = max(current_max, self.value) if current_max is not None else self.value

        self.series._current_min = new_min
        self.series._current_max = new_max


# Create your models here.
