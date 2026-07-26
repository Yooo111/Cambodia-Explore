document.addEventListener('DOMContentLoaded', function () {
    const filterForm = document.getElementById('user-filter-form');
    if (filterForm) {
        const checkboxes = filterForm.querySelectorAll('.filter-chip-checkbox');
        checkboxes.forEach(function (cb) {
            cb.addEventListener('change', function () {
                filterForm.submit();
            });
        });
    }
});
