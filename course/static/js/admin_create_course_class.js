document.addEventListener("DOMContentLoaded", function () {
    const input = document.querySelector('input[name="max_students"]');

    if (!input) return;

    input.addEventListener("input", function () {
        let value = parseInt(this.value);

        if (isNaN(value)) return;

        if (value < 1) this.value = 1;
        if (value > 50) this.value = 50;
    });
});