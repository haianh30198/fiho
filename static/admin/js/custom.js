// thông báo kích hoạt tạo gợi ý mới
function active() {
    if (confirm("Bạn có chắc muốn tạo lại các gợi ý ?")) {
        return true;
    } else {
        return false;
    }
}

// thông báo tải file
function downloadFile() {
    if (confirm("Bạn có chắc muốn tải tệp gợi ý này không ?")) {
        return true;
    } else {
        return false;
    }
}

// thông báo xóa file
function deleteFile() {
    if (confirm("Bạn có chắc muốn xóa tệp này không ?")) {
        return true;
    } else {
        return false;
    }
}

// thông báo xóa thành viên
function deleteMember() {
    if (confirm("Bạn có chắc muốn xóa thành viên này không ?")) {
        return true;
    } else {
        return false;
    }
}

// Đồng hồ
function Dong_ho() {
    var gio = document.getElementById("gio");
    var phut = document.getElementById("phut");
    var giay = document.getElementById("giay");
    var Gio_hien_tai = new Date().getHours();
    var Phut_hien_tai = new Date().getMinutes();
    var Giay_hien_tai = new Date().getSeconds();
    gio.innerHTML = Gio_hien_tai;
    phut.innerHTML = Phut_hien_tai;
    giay.innerHTML = Giay_hien_tai;
}
var Dem_gio = setInterval(Dong_ho, 1000);
