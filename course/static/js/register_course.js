document.getElementById('filterType').addEventListener('change', function() {
    const courseBox = document.getElementById('courseBox');
    const classBox = document.getElementById('classBox');

    if (this.value === 'course') {
        courseBox.classList.remove('d-none');
        classBox.classList.add('d-none');
    } else if (this.value === 'class') {
        classBox.classList.remove('d-none');
        courseBox.classList.add('d-none');
    } else {
        courseBox.classList.add('d-none');
        classBox.classList.add('d-none');
    }
});

const tableBody = document.querySelector('table tbody');
tableBody.addEventListener('change', async function(e) {
    const checkbox = e.target;
    if (!checkbox.classList.contains('register-checkbox')) return;

    const classId = checkbox.dataset.classId;
    if (!classId) return;

    if (checkbox.dataset.processing === '1') return;
    checkbox.dataset.processing = '1';

    const isChecked = checkbox.checked;
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
        }

    } catch (err) {
        alert('Lỗi server, vui lòng thử lại');
        checkbox.checked = !isChecked;
    } finally {
        checkbox.disabled = false;
        checkbox.dataset.processing = '0';
    }
});

document.getElementById('confirmBtn').addEventListener('click', async () => {
    try {
        const res = await fetch('/api/register-course/confirm', { method: 'POST' });
        const data = await res.json();
        alert(data.success ? "Success: " + data.message : "Failure: " + data.message);
    } catch (err) {
        alert("Server error");
    }
});
