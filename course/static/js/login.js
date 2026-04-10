const roleSelect = document.querySelector("select[name='role']");
    const usernameInput = document.getElementById("username");

    roleSelect.addEventListener("change", function () {
        if (this.value === "ADMIN") {
            usernameInput.type = "text";
            usernameInput.placeholder = "Tên đăng nhập";
        } else if (this.value === "USER") {
            usernameInput.type = "number";
            usernameInput.placeholder = "Mã số sinh viên";
        } else {
            usernameInput.type = "text";
            usernameInput.placeholder = "Nhập...";
        }
    });