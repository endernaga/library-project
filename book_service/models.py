from django.db import models


class Book(models.Model):

    class Cover(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=255, choices=Cover.choices)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(default=1, max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title