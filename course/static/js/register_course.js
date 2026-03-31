document.addEventListener('DOMContentLoaded', function() {
    const filterType = document.getElementById('filterType');
    const courseBox = document.getElementById('courseBox');
    const classBox = document.getElementById('classBox');

    function updateVisibility(value) {
        courseBox.classList.add('d-none');
        classBox.classList.add('d-none');

        if (value === 'course') {
            courseBox.classList.remove('d-none');
        } else if (value === 'class') {
            classBox.classList.remove('d-none');
        }
    }

    if (filterType.value) {
        updateVisibility(filterType.value);
    }

    filterType.addEventListener('change', function () {
        updateVisibility(this.value);
    });
});


