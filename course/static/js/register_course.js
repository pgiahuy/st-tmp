document.addEventListener('DOMContentLoaded', function () {

    const courseSelect = document.getElementById('courseSelect');
    if (courseSelect) {
        courseSelect.addEventListener('change', function () {
            const courseId = this.value;
            window.location.href = '/register-course?course_id=' + courseId;
        });
    }


    const tableBody = document.querySelector('table tbody');

    tableBody.addEventListener('change', async function(e) {
        const checkbox = e.target;
        if (!checkbox.classList.contains('register-checkbox')) return;

        const classId = checkbox.dataset.classId;
        if (!classId) return;

        if (checkbox.dataset.processing === '1') return;
        checkbox.dataset.processing = '1';
        const isChecked = checkbox.checked;

        if (!isChecked) {
            const confirmCancel = confirm('Bạn có chắc muốn huỷ lớp này?');
            if (!confirmCancel) {
                checkbox.checked = true;
                checkbox.dataset.processing = '0';
                return;
            }
        }

        checkbox.disabled = true;

        try {
            const res = await fetch('/api/course-register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    course_class_id: classId,
                    action: isChecked ? 'register' : 'unregister'
                })
            });

            const result = await res.json();

            if (!result.success) {
                alert(result.message || 'Đăng ký thất bại');
                checkbox.checked = !isChecked;
            } else {
                window.location.reload();
            }
        } catch (err) {
            alert('Lỗi server, vui lòng thử lại');
            checkbox.checked = !isChecked;
        } finally {
            checkbox.disabled = false;
            checkbox.dataset.processing = '0';
        }
    });


    const confirmBtn = document.getElementById('confirmBtn');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', async () => {
            try {
                const res = await fetch('/api/register-course/confirm', { method: 'POST' });
                const data = await res.json();
                alert(data.success ? "Success: " + data.message : "Failure: " + data.message);

                if (data.success) {
                    window.location.reload();
                }
            } catch (err) {
                alert("Server error");
            }
        });
    }


    document.querySelectorAll('.unregister-icon').forEach(icon => {
        icon.addEventListener('click', function () {
            const classId = this.dataset.classId;

            if (!confirm('Bạn có chắc muốn huỷ lớp này?')) return;

            fetch(`/api/course-register/${classId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(resp => resp.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } else {
                    alert('Lỗi: ' + data.message);
                }
            })
            .catch(err => alert('Lỗi kết nối: ' + err));
        });
    });

});