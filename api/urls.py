from django.urls import path 
from api import views
from api.views import index


app_name = "api" # For demo purpose api is used, once app name is decided upon needs to be here

urlpatterns = [
    path("", index)
]