document.addEventListener('DOMContentLoaded', function () {
    let dropdowns = document.querySelectorAll('.dropdown');

    dropdowns.forEach(function (dropdown) {
        let dropdownButton = dropdown.querySelector('.dropdown-toggle');
        let dropdownItems = dropdown.querySelectorAll('.dropdown-item');

        for (let i = 0; i < dropdownItems.length - 1; i++) {
            dropdownItems[i].addEventListener('click', function () {
                dropdownButton.textContent = this.textContent;
            });
        }
    });
});