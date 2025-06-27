from django.contrib import admin
from .models import User, Review

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'city', 'created_at')
    search_fields = ('name', 'email', 'city', 'state', 'country')
    list_filter = ('city', 'state', 'country')
    ordering = ('-created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'user', 
        'platform', 
        'product_name', 
        'sentiment', 
        'product_url', 
        'date_created'
    )
    search_fields = (
        'user__name', 
        'product_name', 
        'text', 
        'keywords', 
        'product_url',
        'platform'
    )
    list_filter = ('platform', 'sentiment', 'date_created')
    ordering = ('-date_created',)
