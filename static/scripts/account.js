document.addEventListener('DOMContentLoaded', function() {
    const $btnReg = document.getElementById('btn-reg');
    const $btnLog = document.getElementById('btn-log');
    const $formReg = document.getElementById('form-reg');
    const $formLog = document.getElementById('form-log');

    $btnReg.addEventListener('click', function() {
        $formLog.style.display = 'none'
        $formReg.style.display = 'block'
        $btnReg.style.display = 'none'
        $btnLog.style.display = 'block'
    })
    $btnLog.addEventListener('click', function() {
        $formLog.style.display = 'block'
        $formReg.style.display = 'none'
        $btnReg.style.display = 'block'
        $btnLog.style.display = 'none'
    })
    $formReg.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);
    
        fetch('/register', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.response) {
                document.getElementById('reg-elem').textContent = 'Регистрация успешна';
                setTimeout(function() {
                    window.location.href = 'account'; 
                }, 1000); 
            } else if (data.error) {
                document.getElementById('reg-elem').textContent = data.error;
                $formReg.style.display = 'block'; 
            }
        })
        .catch(error => console.error('Ошибка:', error));
    });
    $formLog.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);
    
        fetch('/login', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.response) {
                document.getElementById('log-elem').textContent = data.message;
                setTimeout(function() {
                    window.location.href = 'account'; 
                }, 1000); 
            } else {
                document.getElementById('log-elem').textContent = data.message;
            }
        })
        .catch(error => console.error('Ошибка:', error));
    });
})