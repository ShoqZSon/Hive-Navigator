document.addEventListener('DOMContentLoaded', function () {
    // Select the button and dropdowns
    const sendButton = document.querySelector('.btn-success');
    const locationDropdownButton = document.getElementById('dropdown_loc');
    const destinationDropdownButton = document.getElementById('dropdown_dest');

    sendButton.addEventListener('click', function () {
        // Get the selected texts from the dropdown buttons
        const location = locationDropdownButton.textContent.trim();
        const destination = destinationDropdownButton.textContent.trim();

        if (location === "Select your location" || destination === "Select your destination") {
            alert("Please choose your location and your desired destination.");
            return;
        }

        // Build the JSON object
        const data = {
            location: location,
            destination: destination
        };

        // Display the JSON object
        const userRequest = JSON.stringify(data, null, 2)

        console.log('Generated JSON:', userRequest);

        // Optional: Display JSON on the page
        let resultDiv = document.getElementById('jsonResult');
        if (!resultDiv) {
            resultDiv = document.createElement('div');
            resultDiv.id = 'jsonResult';
            resultDiv.style.whiteSpace = 'pre-wrap'; // Ensure proper formatting
            document.body.appendChild(resultDiv);
        }
        resultDiv.textContent = 'Generated JSON:\n' + JSON.stringify(data, null, 2);
    });
});
