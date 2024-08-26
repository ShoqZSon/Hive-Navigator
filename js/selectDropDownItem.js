document.addEventListener('DOMContentLoaded', function () {
    let dropdowns = document.querySelectorAll('.dropdown');

    dropdowns.forEach(function (dropdown) {
        let dropdownButton = dropdown.querySelector('.dropdown-toggle');
        let dropdownItems = dropdown.querySelectorAll('.dropdown-item');

        dropdownItems.forEach(function (item) {
            item.addEventListener('click', function () {
                dropdownButton.textContent = this.textContent;
            });
        });
    });
});