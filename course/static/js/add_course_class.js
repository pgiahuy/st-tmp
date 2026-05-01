document.addEventListener('DOMContentLoaded', function () {
    const slotPicker = document.getElementById('slots_picker');
    const roomSelect = document.getElementById('room') || document.getElementById('room_picker');
    const semesterSelect = document.getElementById('semester');

    if (!slotPicker || !roomSelect) {
        return;
    }

    slotPicker.addEventListener('change', async function () {
        const slotIds = Array.from(slotPicker.selectedOptions)
            .map(function (option) {
                return option.value;
            })
            .filter(Boolean);

        if (slotIds.length === 0) return;

        const semesterId = (semesterSelect && semesterSelect.value) || 1;

        try {
            const res = await fetch(
                `/api/admin/available-rooms?slot_ids=${slotIds.join(',')}&semester_id=${semesterId}`
            );

            const data = await res.json();

            roomSelect.innerHTML = '';

            if (data.length === 0) {
                roomSelect.insertAdjacentHTML('beforeend', '<option value="">Không có phòng trống</option>');
                return;
            }

            data.forEach(function (room) {
                roomSelect.insertAdjacentHTML(
                    'beforeend',
                    `<option value="${room.id}">${room.name}</option>`
                );
            });
        } catch (err) {
            console.error('Lỗi load room:', err);
        }
    });
});