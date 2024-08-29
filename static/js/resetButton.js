function resetLocDest() {
    resetLoc();
    //resetDest();
    resetDestTable();
}

function resetLoc() {
    const location = document.getElementById("dropdown_loc");
    location.textContent = "Select your location";
}

function resetDest() {
    const destination = document.getElementById("dropdown_dest");
    destination.textContent = "Select your destination";
}

function resetDestTable() {
    const destTable = document.getElementById("destTable");

    // Remove 'selected' class from all rows
    destTable.querySelectorAll("tbody tr").forEach(row => {
        row.classList.remove("selected");
    });
}
