
document.querySelectorAll('.register-checkbox').forEach(cb => {
    cb.addEventListener('change', async function () {

        const classId = this.dataset.classId;
        const isChecked = this.checked;

        this.disabled = true;

        try {
            const res = await fetch('/api/course-register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    course_class_id: classId,
                    action: isChecked ? 'register' : 'unregister'
                })
            });

            const data = await res.json();

            if (!data.success) {
                alert(data.message || "Lỗi");
                this.checked = !isChecked;
            }

        } catch (err) {
            alert("Server error");
            this.checked = !isChecked;
        }

        this.disabled = false;


// confirm
document.getElementById('confirmBtn').onclick = async () => {
    try {
        const res = await fetch('/api/register-course/confirm', {
            method: 'POST'
        });

        const data = await res.json();

        if (data.success) {
            alert("success " + data.message);
        } else {
            alert("failure " + data.message);
        }

    } catch (err) {
        alert("Server error");
    }
};
