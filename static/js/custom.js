$(document).on("input", "#priceUp", function () {
    var coins = $("#priceUp").val();
    $("#slider_label_price").text(coins);
});

$(document).on("input", "#areaUp", function () {
    var coins = $("#areaUp").val();
    $("#slider_label_area").text(coins);
});

$(document).on("input", "#bedroomsUp", function () {
    var coins = $("#bedroomsUp").val();
    $("#slider_label_beds").text(coins);
});

$(document).on("input", "#floorsUp", function () {
    var coins = $("#floorsUp").val();
    $("#slider_label_floors").text(coins);
});

$(document).on("input", "#directionUp", function () {
    var coins = $("#directionUp").val();
    $("#slider_label_direc").text(coins);
});

$(function () {
    $('[data-toggle="tooltip"]').tooltip();
});
