from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("suggest/", views.suggest, name="suggest"),
    path("past/", views.past, name="past"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("register/", views.register_user, name="register"),
    path("delete_past/<Past_id>", views.delete_past, name="delete_past"),
]
