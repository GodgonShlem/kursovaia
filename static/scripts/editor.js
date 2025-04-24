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

function deleteLesson(lessonId) {
    if (confirm('Вы уверены, что хотите удалить этот урок?')) {
        fetch(`/delete_lesson/${lessonId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                document.getElementById(`interactions-edit-table-str${lessonId}`).remove(); 
            } else {
                alert('Ошибка при удалении урока');
            }
        })
        .catch(error => console.error('Ошибка:', error));
    }
}

function editorSubmit(lesson_id, event) {
    event.preventDefault();
    var form = document.querySelector('.interactions-form');
    if (!form.checkValidity()) {
        document.getElementById('interactions-message').textContent = 'Пожалуйста, заполните все обязательные поля.';
        return;
    }
    const formData = new FormData(form);

    const files = document.querySelector('input[name="lesson-images"]').files;
    if (files.length === 0) {
        formData.append('has_images', 'false');
    } else {
        formData.append('has_images', 'true'); 
    }

    fetch(`/edit_lesson/${lesson_id}`, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log(response.status);
        return response.json();
    })
    .then(data => {
        if (data.response) {
            document.getElementById('interactions-message').textContent = 'Урок успешно изменен';
        } else {
            document.getElementById('interactions-message').textContent = 'Урок не изменен! ' + data.message;
        }
    })
    .catch(error => {
        document.getElementById('interactions-message').textContent = 'Произошла ошибка: ' + error.message;
    });
};
