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