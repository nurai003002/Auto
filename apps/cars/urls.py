from django.urls import path
from apps.cars import views

urlpatterns = [
    path('', views.index, name='index'),

    # Cars API
    path('api/cars/', views.cars_list, name='api-cars-list'),
    path('api/cars/<int:pk>/', views.cars_detail, name='api-cars-detail'),

    # Repairs API
    path('api/repairs/', views.repairs_list, name='api-repairs-list'),
    path('api/repairs/<int:pk>/', views.repairs_detail, name='api-repairs-detail'),

    # Export
    path('api/reports/<str:report_type>/export/xlsx/', views.export_excel, name='export-excel'),
    path('api/reports/<str:report_type>/export/docx/', views.export_word, name='export-word'),
]
