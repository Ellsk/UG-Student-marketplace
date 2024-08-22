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
});


// Add to cart functionality
$("#add-to-cart-btn").on("click", function(){
    let quantity = $("#product-quantity").val();  // Gets value from quantity input
    let product_title = $(".product-title").val();  // Gets value from title input
    let product_id = $(".product-id").val();  // Gets value from ID input
    let product_price = $("#current-product-price").text();
    let this_val = $(this);  // References the current button

    // Debugging
    console.log("Quantity:", quantity);
    console.log("Title:", product_title);
    console.log("Price:", product_price);
    console.log("ID:", product_id);
    console.log("Current Element:", this_val);

    $.ajax({
        url: '/add-to-cart',
        data: {
            'id': product_id,
            'qty': quantity,
            'title': product_title,
            'price': product_price
        },
        dataType: 'json',
        beforeSend: function(){
            this_val.html("Adding To Cart");
        },
        success: function(response){
            this_val.html("Added To Cart");

            // Update the cart count
            if (response.totalcartitems !== undefined) {
                $(".cart-items-count").text(response.totalcartitems);
            } else {
                console.error("totalcartitems not found in response:", response);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);  // Debugging errors
            this_val.html("Error Adding To Cart");
        }
    });
});
