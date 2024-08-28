// dropdownSync.js

document.addEventListener('DOMContentLoaded', function () {
    let dropdowns = document.querySelectorAll('.dropdown');

    dropdowns.forEach(function (dropdown) {
        let dropdownItems = dropdown.querySelectorAll('.dropdown-item');
        let hiddenInput = dropdown.querySelector('input[type="hidden"]');

        dropdownItems.forEach(function (item) {
            // Only add listener if item is not a reset option
            if (!item.classList.contains('dropdown-divider') && !item.hasAttribute('onclick')) {
                item.addEventListener('click', function () {
                    // Set the value of the corresponding hidden input
                    hiddenInput.value = this.getAttribute('data-value');
                });
            }
        });
    });
});
