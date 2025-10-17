# admin.py

from django.contrib import admin
from .models import HallBooking, Feedback

@admin.register(HallBooking)
class HallBookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'phone', 'date', 'days', 'guests', 'created_at']
    list_filter = ['date', 'created_at', 'days']
    search_fields = ['name', 'email', 'phone']
    date_hierarchy = 'date'
    ordering = ['-created_at']
    readonly_fields = ['created_at']

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'rating', 'submitted_at']
    list_filter = ['rating', 'submitted_at']
    search_fields = ['name', 'experience']
    date_hierarchy = 'submitted_at'
    ordering = ['-submitted_at']
    readonly_fields = ['submitted_at']