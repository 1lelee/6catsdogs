function displayFileName() {
    var input = document.getElementById('file');
    var displayName = document.getElementById('file_name');
    if (input.files && input.files[0]) {
        displayName.textContent = input.files[0].name;
    }
}