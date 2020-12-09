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
