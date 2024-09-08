document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("destTable");
    const destinationInput = document.getElementById("destination");

    // Add click event listener to each row in the table body
    table.querySelectorAll("tbody tr").forEach(row => {
        row.addEventListener("click", function () {
            // Get all cells data from the selected row
            const rowData = Array.from(this.cells).map(cell => cell.innerText);

            // Convert row data to a string (you can customize the format)
            const rowString = rowData.join(",");

            // Set the hidden input value to the row string
            destinationInput.value = rowString;

            // Optionally, add a selected class to highlight the selected row
            table.querySelectorAll("tbody tr").forEach(r => r.classList.remove("selected"));
            this.classList.add("selected");
        });
    });
});
