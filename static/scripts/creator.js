const interactionsBtnClrear = document.getElementById('interactions-btn-clear');
const interactionsBtnSubmit = document.getElementById('interactions-btn-submit');

interactionsBtnClrear.addEventListener('click', () => {
    if(confirm('Вы уверены что хотите очистить поля?')){
        document.querySelector('.interactions-form').reset();
    }
})

function addAnswer(id){
    let checkboxes = document.querySelectorAll(`input[name="is-correct[${id}]"]`);
    let lastCheckboxValue = checkboxes.length > 0 ? checkboxes[checkboxes.length - 1].value : 0;
    let newCheckbox = parseInt(lastCheckboxValue) + 1;
    let answerOptions = document.getElementById(`answer-options-[${id}]`);
    let newAnswerDiv = document.createElement('div');
    newAnswerDiv.classList.add("interactions-form-questions-elem");
    newAnswerDiv.innerHTML = `
        <input type="checkbox" name="is-correct[${id}]" class="interactions-form-questions-elem-check" value="${newCheckbox}">
        <textarea type="text" name="answer-text[${id}]" class="interactions-form-questions-elem-input" placeholder="Вариант ответа ${newCheckbox}"></textarea><br>
    `;
    answerOptions.appendChild(newAnswerDiv);
}
function removeAnswer(id) {
    const answerOptions = document.getElementById(`answer-options-[${id}]`);
    const lastAnswerDiv = answerOptions.lastElementChild;
    if (lastAnswerDiv) {
      answerOptions.removeChild(lastAnswerDiv);
    }
}

function addQuestion(){
    let questions = document.querySelectorAll('.question-title');
    let lastQuestion = -1
    questions.forEach(q => {lastQuestion+=1;});
    let newQuestion = parseInt(lastQuestion) + 1;
    const questionList = document.querySelector('.add-question');
    const newQuestionDiv = document.createElement('div');
    newQuestionDiv.classList.add('interactions-form-group-container');
    const questionCount = document.getElementById('question-count');
    questionCount.value = parseInt(questionCount.value) + 1;
    newQuestionDiv.innerHTML = `
        <label for="lesson-questions" class="interactions-form-group-label question-title">Вопрос:</label>
                <textarea name="lesson-question[${newQuestion}]" class="interactions-form-group-input"></textarea>
                <div class="interactions-form-questions">
                    <p class="interactions-form-questions-title">Варианты ответов</p>
                    <p class="interactions-form-questions-title">Поставьте галочку у верных ответов</p>
                    <div class="interactions-form-questions-options" id="answer-options-[${newQuestion}]">
                        <div class="interactions-form-questions-elem">
                            <input type="checkbox" name="is-correct[${newQuestion}]" class="interactions-form-questions-elem-check" value="1">
                            <textarea type="text" name="answer-text[${newQuestion}]" class="interactions-form-questions-elem-input" placeholder="Вариант ответа 1"></textarea><br>
                        </div>
                        <div class="interactions-form-questions-elem">
                            <input type="checkbox" name="is-correct[${newQuestion}]" class="interactions-form-questions-elem-check" value="2">
                            <textarea type="text" name="answer-text[${newQuestion}]" class="interactions-form-questions-elem-input" placeholder="Вариант ответа 2"></textarea><br>
                        </div>
                    </div>
                    <button type="button" class="interactions-form-questions-btns" onclick="addAnswer(id=${newQuestion})">Добавить вариант</button>
                    <button type="button" class="interactions-form-questions-btns" onclick="removeAnswer(id=${newQuestion})">Удалить вариант</button>
                </div>
    `;
    questionList.appendChild(newQuestionDiv);
}

function removeQuestion() {
const elements = document.querySelectorAll('.interactions-form-group-container');
if (elements.length) {
    const questionCount = document.getElementById('question-count');
    questionCount.value = questionCount.value - 1;
    const elementToRemove = elements[elements.length - 1];
    elementToRemove.remove();
    }
}

interactionsBtnSubmit.addEventListener('click', function(event) {
    event.preventDefault();
    var form = document.querySelector('.interactions-form');
    if (!form.checkValidity()) {
        document.getElementById('interactions-message').textContent = 'Пожалуйста, заполните все обязательные поля.';
        document.getElementById('interactions-btn-submit').classList.add('bad-end'); 
            setTimeout(() => {
                document.getElementById('interactions-btn-submit').classList.remove('bad-end'); 
            }, 1000);
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
            document.getElementById('interactions-btn-submit').classList.add('good-end'); 
            setTimeout(() => {
                document.getElementById('interactions-btn-submit').classList.remove('good-end'); 
            }, 1000);
        } else {
            document.getElementById('interactions-message').textContent = 'Урок не добавлен! ' + data.message;
            document.getElementById('interactions-btn-submit').classList.add('bad-end'); 
            setTimeout(() => {
                document.getElementById('interactions-btn-submit').classList.remove('bad-end'); 
            }, 1000);
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
    if (isToggleCreate) {
        isToggleCreate = false;
        createChapterToggle.style.maxHeight = '0';
    }
    else {
        isToggleCreate = true;
        createChapterToggle.style.maxHeight ='200px';
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