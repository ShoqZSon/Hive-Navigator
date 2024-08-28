function resetLocDest() {
    resetLoc();
    resetDest();
}

function resetLoc() {
    const location = document.getElementById("dropdown_loc");
    location.textContent = "Select your location";
}

function resetDest() {
    const destination = document.getElementById("dropdown_dest");
    destination.textContent = "Select your destination";
}
