$(function () {
    $("button").click(function () {
        var district = $("#district").val();
        var price = $("#price").val();
        var priceUp = $("#priceUp").val();
        var area = $("#area").val();
        var areaUp = $("#areaUp").val();
        var floors = $("#floors").val();
        var floorsUp = $("#floorsUp").val();
        var bedrooms = $("#bedrooms").val();
        var bedroomsUp = $("#bedroomsUp").val();
        var direction = $("#direction").val();
        var directionUp = $("#directionUp").val();
        var placesNearby = $("#placesNearby").val();
        $.ajax({
            url: "/result",
            data: $("form").serialize(),
            type: "POST",
            success: function (response) {
                document.getElementById("result").innerHTML = response;
                // console.log(response);
            },
            error: function (error) {
                console.log(error);
            },
        });
    });
});
