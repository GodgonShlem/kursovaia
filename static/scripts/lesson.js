const testBtn = document.querySelector('.test-submit-btn');
const nextLessonDiv = document.querySelector('.lesson-test-nextlesson');
testBtn.addEventListener('click', (event)=>{
    event.preventDefault();
    const lesson_id = testBtn.id;
    const form = document.getElementById('test-form');
    const formData = new FormData(form);
    
    fetch(`/test_verify/${lesson_id}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.results) {
            data.results.forEach(result => {
                const resultElem = document.getElementById(`question-result-${result.question_id}`);
                const textEl = resultElem.querySelector('.result-text');
                
                resultElem.style.display = 'flex';
                resultElem.style.alignItems = 'center';
                resultElem.style.margin = '10px 0';
                
                if (result.is_correct) {
                    textEl.textContent = 'Верно!';
                    textEl.style.color = 'green';
                } else {
                    textEl.textContent = 'Неверно!';
                    textEl.style.color = 'red';
                }
            });
        }
        const generalMessage = document.getElementById('general-message');
        if (data.response) {
            generalMessage.textContent = data.message;
            generalMessage.style.backgroundColor = '#d4edda';
            generalMessage.style.color = '#155724';
            nextLessonDiv.style.height = '50px';
        } else {
            generalMessage.textContent = data.message;
            generalMessage.style.backgroundColor = '#f8d7da';
            generalMessage.style.color = '#721c24';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const generalMessage = document.createElement('div');
        generalMessage.textContent = 'Произошла ошибка при отправке теста';
        generalMessage.style.color = 'red';
        form.parentNode.insertBefore(generalMessage, form);
    });
});

const showTestBtn = document.querySelector('.test-show-btn');
let isTestShow = false;
const testForm = document.getElementById('test-form');
function showTest() {
    if(isTestShow) {
        isTestShow = false;
        testForm.style.maxHeight = '0';
    } else {
        isTestShow = true;
        testForm.style.maxHeight = '5000px';
    }
}