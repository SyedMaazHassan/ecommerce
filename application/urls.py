from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name="index"),
    path('signup', views.signup, name="signup"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('authentication', views.authentication, name="authentication"),
    path('profile', views.profile, name="profile"),
    path('completeProfile', views.completeProfile, name="completeProfile"),
    path('addProduct', views.addProduct, name="addProduct"),
    path('product/<id>', views.product, name='product'),
    path('add_review', views.add_review, name='add_review'),
    path('all_products', views.all_products, name='all_products'),
    path('all_sellers', views.all_sellers, name='all_sellers'),
    path('update_cart', views.update_cart, name='update_cart'),
    path('delete_cart_item', views.delete_cart_item, name='delete_cart_item'),
    path('confirm_order', views.confirm_order, name="confirm_order"),
    path('complete_order', views.complete_order, name="complete_order"),
    path('order_received', views.order_received, name="order_received"),
    

    
]

urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
