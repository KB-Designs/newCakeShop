from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from myshop.orders import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('checkout/', include('orders.urls')),
    path('mpesa/', include('mpesa.urls')),
    path('checkout/retry-payment/<int:order_id>/', views.retry_payment, name='retry_payment'),
    path('mpesa/', include('mpesa.urls')),  # Use mpesa (correct spelling)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)