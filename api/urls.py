from django.urls import include, path 
from api import views
from api.views import about_us, add_to_cart, add_to_wishlist, ajax_add_review, ajax_contact_form, cart_view, checkout, contact, customer_dashboard, delete_item_from_cart, filter_product, index, order_detail, payment_completed_view, payment_failed_view, privacy_policy, product_list_view, category_list_view , category_product_list_view, purchase_guide, remove_wishlist, search_view, terms_of_service, update_cart, vendor_list_view, vendor_detail_view, product_detail_view, tag_list, make_address_default, wishlist_view

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

    path("checkout/<oid>/",checkout, name="checkout"),


    #Payment Integration
    path('paypal/', include('paypal.standard.ipn.urls')),
    
    #Payment Successful
    path("payment-completed/<oid>/", payment_completed_view, name="payment-completed"),
    
    #Payment Failed
    path("payment-failed/", payment_failed_view, name="payment-failed"),
    
    #Dashboard URL
    path("dashboard/", customer_dashboard, name="dashboard"),
    
    #Order Detail URL
    path("dashboard/order/<int:id>", order_detail, name="order-detail"),
    
    #Making address default
    path("make-default-address/", make_address_default, name="make-default-address"),

    # wishlist page
    path("wishlist/", wishlist_view, name="wishlist"),
    
    path("add-to-wishlist/", add_to_wishlist, name="add-to-wishlist"),

    
    # Removing from wishlist
    path("remove-from-wishlist/", remove_wishlist, name="remove-from-wishlist"),
    
    
    path("contact/", contact, name="contact"),
    path("ajax-contact-form/", ajax_contact_form, name="ajax-contact-form"),

    path("about_us/", about_us, name="about_us"),
    path("purchase_guide/", purchase_guide, name="purchase_guide"),
    path("privacy_policy/", privacy_policy, name="privacy_policy"),
    path("terms_of_service/", terms_of_service, name="terms_of_service"),

    path("save_checkout_info/", views.save_checkout_info, name="save_checkout_info"),
    path("api/create_checkout_session/<oid>", views.create_checkout_session, name="create_checkout_session"),

]