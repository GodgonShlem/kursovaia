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
})