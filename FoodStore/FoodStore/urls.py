"""FoodStore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin

from FoodStore import settings
from main import views
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('product/<int:product_id>', views.product, name='product'),
    path('authorize', views.authorize, name='homepage'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('cart', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>', views.addToCart, name='addToCart'),
    path('update-cart-product-amount/<int:cart_id>/<int:amount>', views.updateCartProductAmount, name='updateCartProductAmount'),
    path('remove-from-cart/<int:cart_id>', views.removeFromCart, name='removeFromCart'),
    path('addProduct', views.addProduct, name='addProduct'),
    path('payment', views.payment, name='payment'),
    path('proceed/<int:price>', views.proceed, name='proceed'),
    path('addDish', views.addDish, name='addDish'),
    path('addComment', views.addComment, name='addComment'),
    path('addStep', views.addStep, name='addStep'),
    path('dish/<int:dish_id>', views.dishPage, name='dishPage'),
    path('about_us', views.about_us, name='aboutUsPage'),

    path('search-products', views.searchProduct, name='searchProduct')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)