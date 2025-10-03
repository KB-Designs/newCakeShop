from django.urls import path
from . import views

app_name = 'mpesa'

urlpatterns = [
    path('callback/', views.MpesaCallbackView.as_view(), name='callback'),
    path('stk_push/', views.stk_push, name='stk_push'),
]