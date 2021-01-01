$(function () {
    $("button").click(function () {
        $("#loading").show();
        // setTimeout(function () {
        //     $("#loading").hide();
        // }, 1000);
        sessionStorage.setItem("home", uuidv4());
        // var district = $("#district").val();
        // var price = $("#price").val();
        // var priceUp = $("#priceUp").val();
        // var area = $("#area").val();
        // var areaUp = $("#areaUp").val();
        // var floors = $("#floors").val();
        // var floorsUp = $("#floorsUp").val();
        // var bedrooms = $("#bedrooms").val();
        // var bedroomsUp = $("#bedroomsUp").val();
        // var direction = $("#direction").val();
        // var directionUp = $("#directionUp").val();
        // var placesNearby = $("#placesNearby").val();
        $.ajax({
            url: "/result",
            data: $("form").serialize(),
            type: "POST",
            success: function (response) {
                $("#loading").hide();
                document.getElementById("result").innerHTML = response;
                // console.log(response);
                $(document).ready(function () {
                    $("a[name='clicked']").click(function () {
                        var homeItem = $(this).attr("value");
                        console.log("Giá trị trong thẻ a:", homeItem);
                        $.ajax({
                            url: "/rating",
                            contentType: "application/json;charset=UTF-8",
                            data: JSON.stringify({
                                top: homeItem,
                                sessionTop: sessionStorage.getItem("home"),
                            }),
                            type: "POST",
                            success: function (response) {
                                // $("#loading").hide();
                                console.log(response);
                            },
                            error: function (error) {
                                // $("#loading").hide();
                                console.log(error);
                            },
                        });
                    });
                });
            },
            error: function (error) {
                console.log(error);
            },
        });
    });
});
