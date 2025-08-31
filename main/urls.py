from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('apply', views.apply, name='apply'),
    path('members', views.members, name='members'),
    path('portal', views.portal, name='portal'),
    path('register', views.register, name='register'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),

]
