console.log("Working Fine");

$("#commentForm").submit(function(e){
    e.preventDefault();

    $.ajax({
        data: $(this).serialize(),
        method: $(this).attr("method"),
        url: $(this).attr("action"),
        dataType: "json",
        headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        success: function(res){
            console.log("Comment saved to db....");

            if (res.bool) {
                $("#review-res").html("Review added successfully");
                $(".hide-comment-form").hide();
                $(".add_review").hide();

                // Construct the HTML for the new review
                let _html = `
                    <div class="single-comment justify-content-between d-flex mb-30">
                        <div class="user justify-content-between d-flex">
                            <div class="thumb text-center">
                                <img src="{% static 'assets/imgs/shop/User_1.jpeg' %}" alt="User Image" />
                                <a href="#" class="font-heading text-brand">
                                    ${res.context.user ? res.context.user : 'Unknown User'}
                                </a>
                            </div>

                            <div class="desc">
                                <div class="d-flex justify-content-between mb-10">
                                    <div class="d-flex align-items-center">
                                        <span class="font-xs text-muted">${res.context.date || 'N/A'}</span>
                                    </div>
                                    <div class="product-rate d-inline-block">
                                        <div class="product-rating" style="width: ${res.context.rating * 20}%">
                                            <!-- This assumes rating is out of 5 -->
                                            ${[...Array(res.context.rating)].map(() => '<i class="fa fa-star text-warning"></i>').join('')}
                                        </div>
                                    </div>
                                </div>
                                <p class="mb-10">${res.context.review}</p>
                            </div>
                        </div>
                    </div>
                `;

                // Prepend the new review to the comment list
                $(".comment-list").prepend(_html);
            }
        },
        error: function(xhr, status, error){
            console.log("Error:", status, error);
        }
    });
});

$(document).ready(function(){
    $(".loader").hide();

    $(".filter-checkbox, #price-filter-btn").on("click", function(){
        let filter_object = {};

        let min_price = $("#max_price").attr("min")
        let max_price = $("#max_price").val()

        filter_object.min_price = min_price;
        filter_object.max_price = max_price;

        $(".filter-checkbox").each(function(index){
            let filter_key = $(this).data("filter");  // vendor or category
            filter_object[filter_key] = Array.from(
                document.querySelectorAll('input[data-filter=' + filter_key + ']:checked')
            ).map(function(element){
                return element.value;
            });
        });

        $.ajax({
            url: '/filter-products',
            data: filter_object,
            dataType: 'json',
            beforeSend: function(){
                $(".loader").show();
            },
            success: function(res){
                console.log(res);
                $("#filtered-product").html(res.data);  // Update the product list with the filtered products
                $(".loader").hide();
            },
            error: function(xhr, status, error){
                console.log("Error:", status, error);
                $(".loader").hide();
            }
        });
    });

    $("#max_price").on("blur", function() {
        // Getting the attr value from the product list
        let min_price = parseInt($(this).attr("min"));
        let max_price = parseInt($(this).attr("max"));
        let current_price = parseInt($(this).val());
    
        if (current_price < min_price || current_price > max_price) {
            // Round the prices to two decimal places if necessary
            min_price = Math.round(min_price * 100) / 100;
            max_price = Math.round(max_price * 100) / 100;
    
            // Show an alert with the price range
            alert("Prices must be between " + min_price + " and " + max_price);
    
            // Set the value to the minimum price if out of range
            $(this).val(min_price);
            
            $("#range").val(min_price)
            // Focus back on the input field

            $(this).focus();

            return false;
        }
    });

    //Add to cart functionality
    $(".add-to-cart-btn").on("click", function(){
        let this_val = $(this);
        let _index = this_val.attr("data-index");
    
        let quantity = $(".product-quantity-" + _index).val();
        let product_title = $(".product-title-" + _index).val();
        let product_image = $(".product-image-" + _index).val();
        let product_pid = $(".product-pid-" + _index).val();
        let product_id = $(".product-id-" + _index).val();
        let product_price = $(".current-product-price-" + _index).text();
    
        $.ajax({
            url: '/add-to-cart',
            data: {
                'id': product_id,
                'pid': product_pid,
                'image': product_image,
                'qty': quantity,
                'title': product_title,
                'price': product_price
            },
            dataType: 'json',
            beforeSend: function(){
                this_val.html("Adding To Cart");
            },
            success: function(response){
                this_val.html("✓");
    
                // Update the cart count
                if (response.totalcartitems !== undefined) {
                    $(".cart-items-count").text(response.totalcartitems);
                } else {
                    console.error("totalcartitems not found in response:", response);
                }
    
                // Re-render the cart list dynamically without refreshing
                $("#cartList").html(response.cart_html);
    
                // Revert back to "Add to Cart" after a short delay
                setTimeout(function() {
                    this_val.html('<i class="fi-rs-shopping-cart mr-5"></i>Add');
                }.bind(this_val), 2000); // Using .bind to maintain the context
                
            },
            error: function (xhr, status, error) {
                console.error('Error:', error);
                this_val.html("Error Adding To Cart");
            }
        });
    });
        
    $(document).on("click", ".delete-product", function(){
        let product_id = $(this).attr("data-product");
        let this_val = $(this);
    
        $.ajax({
            url: '/delete-from-cart/',
            data: {
                'id': product_id,
            },
            dataType: 'json',
            beforeSend: function(){
                this_val.attr('disabled', true);
            },
            success: function(response){
                console.log(response);
                // Update the cart item count and re-render the cart list
                $(".cart-items-count").text(response.totalcartitems);
                $("#cartList").html(response.cart_html);
                this_val.attr('disabled', false);
            },
            error: function(xhr, status, error) {
                console.error("Error:", error);
                this_val.attr('disabled', false);
            }
        });
    });
    
    $(document).on("click", ".update-product", function(){
        let product_id = $(this).attr("data-product");
        let this_val = $(this);
        let product_quantity = $(".product-qty-" + product_id).val();
    
        // Debugging console logs
        console.log("Product ID:", product_id);
        console.log("Product Quantity:", product_quantity);
    
        $.ajax({
            url: '/update-cart/',
            data: {
                'id': product_id,
                'qty': product_quantity,
            },
            dataType: 'json',
            beforeSend: function(){
                this_val.attr('disabled', true);
            },
            success: function(response){
                console.log(response);
                $(".cart-items-count").text(response.totalcartitems);
                $("#cartList").html(response.cart_html);
                this_val.attr('disabled', false);
            },
            error: function(xhr, status, error) {
                console.error("Error:", error);
                this_val.attr('disabled', false);
            }
        });
    });
});

