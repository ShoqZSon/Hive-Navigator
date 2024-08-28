document.addEventListener('DOMContentLoaded', function () {
    let dropdowns = document.querySelectorAll('.dropdown');

    dropdowns.forEach(function (dropdown) {
        let dropdownButton = dropdown.querySelector('.dropdown-toggle');
        let dropdownItems = dropdown.querySelectorAll('.dropdown-item');

        dropdownItems.forEach(function (item) {
            // Only add listener if item is not a reset option
            if (!item.classList.contains('dropdown-divider') && !item.hasAttribute('onclick')) {
                item.addEventListener('click', function () {
                    // Update the button text to the selected item's text
                    dropdownButton.textContent = this.textContent;
                });
            }
        });
    });
});
