from django.urls import path
from userauths import views

app_name = 'userauths'

urlpatterns = [
    path("sign-up", views.register_views, name="sign-up")
]
