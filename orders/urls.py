from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('success/<int:order_id>/', views.order_success, name='success'),
    path('county-stations/', views.get_county_stations, name='county_stations'),
    path('payment-status/<int:order_id>/', views.payment_status, name='payment_status'),
    path('simulate-cancel/<int:order_id>/', views.simulate_payment_cancel, name='simulate_cancel'),
]