// checkbox register
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
    });
});


// confirm
document.getElementById('confirmBtn').onclick = async () => {
    try {
        const res = await fetch('/api/register-course/confirm', {
            method: 'POST'
        });

        const data = await res.json();

        if (data.success) {
            alert("✔ " + data.message);
        } else {
            alert("❌ " + data.message);
        }

    } catch (err) {
        alert("Server error");
    }
};

//document.addEventListener('DOMContentLoaded', function() {
//    const filterType = document.getElementById('filterType');
//    const courseBox = document.getElementById('courseBox');
//    const classBox = document.getElementById('classBox');
//
//    function updateVisibility(value) {
//        courseBox.classList.add('d-none');
//        classBox.classList.add('d-none');
//
//        if (value === 'course') {
//            courseBox.classList.remove('d-none');
//        } else if (value === 'class') {
//            classBox.classList.remove('d-none');
//        }
//    }
//
//    if (filterType.value) {
//        updateVisibility(filterType.value);
//    }
//
//    filterType.addEventListener('change', function () {
//        updateVisibility(this.value);
//    });
//});
//
//
