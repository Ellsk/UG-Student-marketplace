from django.urls import path 
from api import views
from api.views import index, product_list_view  


app_name = "api"

urlpatterns = [
    path("", index, name="index"),
    path("products/", product_list_view, name="product-list"),
    # path("category/", category_list_view, name="category-list")
]