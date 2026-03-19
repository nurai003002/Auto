from django.contrib import admin
from .models import Car, TypeOfFix, Fix
# Register your models here.

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('marka', 'model', 'gos_munber', 'year')
    search_fields = ('marka', 'model', 'gos_munber')
    list_filter = ('marka', 'year')
    
@admin.register(TypeOfFix)
class TypeOfFixAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)   
    
@admin.register(Fix)
class FixAdmin(admin.ModelAdmin):
    list_display = ('car', 'repair_type', 'date', 'next_date')
    search_fields = ('car__marka', 'car__model', 'repair_type')
    list_filter = ('repair_type', 'date')
    
    