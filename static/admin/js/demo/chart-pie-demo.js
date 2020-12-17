// Set new default font family and font color to mimic Bootstrap's default styling
(Chart.defaults.global.defaultFontFamily = "Nunito"),
    '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = "#858796";

// Pie Chart Example
var ctx = document.getElementById("myPieChart");
var myPieChart = new Chart(ctx, {
    type: "doughnut",
    data: {
        labels: [
            "Ninh Kiều",
            "Cái Răng",
            "Bình Thủy",
            "Ô Môn",
            "Thốt Nốt",
            "Vĩnh Thạnh",
            "Thới Lai",
            "Cờ Đỏ",
            "Phong Điền",
        ],
        datasets: [
            {
                data: dataCountDistrict,
                backgroundColor: [
                    "#00876c",
                    "#4f996a",
                    "#7ea96c",
                    "#abb973",
                    "#d7c781",
                    "#d9a963",
                    "#db8950",
                    "#db664b",
                    "#d43d51",
                ],
                hoverBackgroundColor: [
                    "#00876c",
                    "#489a68",
                    "#78ab63",
                    "#a8ba61",
                    "#dac767",
                    "#dfa850",
                    "#e18745",
                    "#de6347",
                    "#d43d51",
                ],
                hoverBorderColor: "rgba(0, 0, 0, 1)",
            },
        ],
    },
    options: {
        maintainAspectRatio: false,
        tooltips: {
            backgroundColor: "rgb(255,255,255)",
            bodyFontColor: "#858796",
            borderColor: "#dddfeb",
            borderWidth: 1,
            xPadding: 15,
            yPadding: 15,
            displayColors: false,
            caretPadding: 10,
        },
        legend: {
            display: false,
        },
        cutoutPercentage: 80,
    },
});
