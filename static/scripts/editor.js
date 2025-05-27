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
const testBtn = document.querySelector('.lesson-test-form-button');
const nextLessonDiv = document.querySelector('.lesson-test-form-nextlesson');
testBtn.addEventListener('click', (event)=>{
    event.preventDefault()
    const lesson_id = testBtn.id;
    var form = document.querySelector('.lesson-test-form');
    if (!form.checkValidity()) {
        document.getElementById('test-message').textContent = 'Пожалуйста, выберите ответ.';
        return;
    }
    const formData = new FormData(form);
    
    fetch(`/test_verify/${lesson_id}`, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log(response.status);
        return response.json();
    })
    .then(data => {
        if (data.response) {
            document.getElementById('test-message').textContent = data.message;
            nextLessonDiv.style.height = 'fit-content'
        } else {
            document.getElementById('test-message').textContent = data.message;
        }
    })
    .catch(error => {
        document.getElementById('test-message').textContent = 'Произошла ошибка: ' + error.message;
    })
})

function deleteChapter(chapterId) {
    if (confirm('Вы уверены, что хотите удалить эту главу?  Все связанные уроки также будут удалены!')) {
        fetch(`/delete_chapter/${chapterId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.response) {
                document.getElementById(`chapter-row-${chapterId}`).remove();
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Ошибка:', error));
    }
}