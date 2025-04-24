function previewImages() {
    const previewContainer = document.getElementById('image-preview');
    previewContainer.innerHTML = '';
    const files = document.getElementById('lesson-images').files;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const reader = new FileReader();

        reader.onload = function(event) {
            const img = document.createElement('img');
            img.src = event.target.result;
            img.style.maxWidth = '100px';
            img.style.margin = '5px'; 
            previewContainer.appendChild(img);
        }

        reader.readAsDataURL(file);
    }
}