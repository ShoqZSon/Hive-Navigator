document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('submitForm');

    form.addEventListener('submit', function(event) {
        const location = document.getElementById("location");
        const destination = document.getElementById("destination");
        alert(location.value + " " + destination.value)
        // Define your condition
        if (location.value.trim() === "" || destination.value.trim() === "") {
            alert("Please choose your location and your desired destination.");
            event.preventDefault(); // Prevents form submission
        }
    });
});
