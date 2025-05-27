const interactionsBtnClrear = document.getElementById('interactions-btn-clear');
const interactionsBtnSubmit = document.getElementById('interactions-btn-submit');

interactionsBtnClrear.addEventListener('click', () => {
    if(confirm('Вы уверены что хотите очистить поля?')){
        document.querySelector('.interactions-form').reset();
    }
})

function addAnswer(){
    const checkboxes = document.querySelectorAll('input[name="is-correct"]');
    const lastCheckboxValue = checkboxes.length > 0 ? checkboxes[checkboxes.length - 1].value : 0;
    const newCheckbox = parseInt(lastCheckboxValue) + 1;
    const answerOptions = document.getElementById('answer-options');
    const newAnswerDiv = document.createElement('div');
    newAnswerDiv.classList.add("interactions-form-questions-elem");
    newAnswerDiv.innerHTML = `
        <input type="checkbox" name="is-correct" class="interactions-form-questions-elem-check" value="${newCheckbox}">
        <textarea type="text" name="answer-text" class="interactions-form-questions-elem-input" placeholder="Вариант ответа ${newCheckbox}"></textarea><br>
    `;
    answerOptions.appendChild(newAnswerDiv);
}
function removeAnswer() {
    const answerOptions = document.getElementById('answer-options');
    const lastAnswerDiv = answerOptions.lastElementChild;
    if (lastAnswerDiv) {
      answerOptions.removeChild(lastAnswerDiv);
    }
}

interactionsBtnSubmit.addEventListener('click', function(event) {
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

    fetch('/create_lesson', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log(response.status);
        return response.json();
    })
    .then(data => {
        if (data.response) {
            document.getElementById('interactions-message').textContent = 'Урок успешно добавлен!';
            document.querySelector('.interactions-form').reset();
        } else {
            document.getElementById('interactions-message').textContent = 'Урок не добавлен! ' + data.message;
        }
    })
    .catch(error => {
        document.getElementById('interactions-message').textContent = 'Произошла ошибка: ' + error.message;
    })
});

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
let isToggleCreate = false;
const createChapterToggle = document.querySelector('.interactions-create-chapter');
function toggleCreate(){
    console.log('gsdsdfg')
    if (isToggleCreate) {
        isToggleCreate = false;
        createChapterToggle.style.display = 'none';
    }
    else {
        isToggleCreate = true;
        createChapterToggle.style.display = 'block';
    }
   
}

function createChapter() {
    const chapterTitle = document.getElementById('chapter-title').value;
    if (!chapterTitle) {
        document.getElementById('chapter-message').textContent = 'Введите название главы.';
        return;
    }
    const formData = new FormData();
    formData.append('chapter-title', chapterTitle);
    fetch('/create_chapter', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.response) {
            document.getElementById('chapter-message').textContent = data.message;
            document.getElementById('chapter-title').value = '';
            location.reload();
        } else {
            document.getElementById('chapter-message').textContent = data.message;
        }
    })
    .catch(error => {
        document.getElementById('chapter-message').textContent = 'Ошибка: ' + error;
    });
}

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