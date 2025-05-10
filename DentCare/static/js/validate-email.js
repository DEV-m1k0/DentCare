const emailInput = document.querySelector('#id_email')
const emailHelp = document.querySelector('#email-help')


emailInput.addEventListener('input', (e) => {
    const regularExpression = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    if (regularExpression.test(e.target.value)) {
        emailHelp.classList.remove('d-block')
        emailHelp.classList.add('d-none')

        emailInput.classList.remove('is-invalid')
        emailInput.classList.add('is-valid')
        
    } else {
        emailHelp.classList.add('d-block')
        emailHelp.classList.remove('d-none')
        
        emailInput.classList.remove('is-valid')
        emailInput.classList.add('is-invalid')
    }
})