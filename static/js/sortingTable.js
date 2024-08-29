$(document).ready(function() {
    $('#destTable').DataTable({
        paging: false,       // Enable pagination
        searching: true,    // Enable searching
        ordering: true,     // Enable column ordering
        info: true,         // Show table information
        pageLength: 5,       // Number of rows per page
        highlightSearchWords: false
    });
});