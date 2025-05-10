const passwordInput = document.querySelector('#id_password')
const passHelp = document.querySelector('#password-help')


passwordInput.addEventListener('input', (e) => {
    const regularExpression = /^[a-zA-Z0-9!@#$%^&*]{8,}$/;

    if (regularExpression.test(e.target.value)) {
        passHelp.classList.remove('d-block')
        passHelp.classList.add('d-none')

        passwordInput.classList.remove('is-invalid')
        passwordInput.classList.add('is-valid')
        
        btn.classList.remove('disabled')

    } else {
        passHelp.classList.add('d-block')
        passHelp.classList.remove('d-none')
        
        btn.classList.add('disabled')
        
        passwordInput.classList.remove('is-valid')
        passwordInput.classList.add('is-invalid')
    }
})