# models.py

from django.db import models
from django.contrib.auth.models import User
class Superserver(models.Model):  # Capital S
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name
class HallBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    guests = models.IntegerField()
    date = models.DateField()
    days = models.IntegerField()
    # Store selected food items as a simple text field (comma/newline separated)
    food_items = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.name} on {self.date}"

    class Meta:
        ordering = ['-created_at']


class Feedback(models.Model):
    RATING_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    experience = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    image = models.ImageField(upload_to='feedback_images/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name}"

    class Meta:
        ordering = ['-submitted_at']