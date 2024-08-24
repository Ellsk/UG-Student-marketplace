from django.urls import path 
from api import views
from api.views import add_to_cart, ajax_add_review, cart_view, checkout_view, delete_item_from_cart, filter_product, index, product_list_view, category_list_view , category_product_list_view, search_view, update_cart, vendor_list_view, vendor_detail_view, product_detail_view, tag_list


app_name = "api"


urlpatterns = [
    #Homepage
    path("", index, name="index"),
    path("products/", product_list_view, name="product-list"),
    path("product/<pid>", product_detail_view, name="product-detail"),
    #Category
    path("category/", category_list_view, name="category-list"),
    path("category/<cid>/", category_product_list_view, name="category-product-list"),
    
    #Vendor
    path("vendors/", vendor_list_view, name="vendor-list"),
    path("vendors/<vid>/", vendor_detail_view, name="vendor-detail"),
    
    #Tag
    path("products/tag/<slug:tag_slug>/", tag_list, name="tags"),
        
    #Add Review
    path("ajax-add-review/<int:pid>/", ajax_add_review, name="ajax-add-review"),
    
    #Search View
    path("search/", search_view, name="search"),
    
    #Filtered product
    path("filter-products/", filter_product, name="filter-product"),
    
    path("add-to-cart/", add_to_cart, name="add-to-cart"),
    
    #Cart view
    path("cart/", cart_view, name="cart"),
    
    #Delete from cart
    path("delete-from-cart/", delete_item_from_cart, name="delete-from-cart"),
    
    #update product
    path("update-cart/",update_cart, name="update-cart"),

    path("checkout/",checkout_view, name="checkout"),
]