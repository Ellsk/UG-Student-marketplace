console.log("Working Fine")

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

            if (res.bool == true) {
                
            }
        },
        error: function(xhr, status, error){
            console.log("Error:", status, error);
        }
    });    
});
