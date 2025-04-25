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