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
    $(".loader").hide()
    $(".filter-checkbox").on("click", function(){
    let filter_object = {}
    $(".filter-checkbox").each(function(index){
    let filter_value = $(this).val()
    let filter_key = $(this).data("filter")
    console.log(filter_value, filter_key);
    filter_object[filter_key] =
    Array.from(document.querySelectorAll('input[data-filter='+filter_key+']:checked')).map(function
    (element){
    return element.value
    })
    })
    console.log(filter_object);
    })
})