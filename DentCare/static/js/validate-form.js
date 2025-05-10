const btn = document.querySelector('#btn')

const firstNameInput = document.querySelector('#id_first_name')
const lastNameInput = document.querySelector('#id_last_name')
const patronymicInput = document.querySelector('#id_patronymic')
const usernameInput = document.querySelector('#id_username')

const inputs = document.querySelectorAll("input")


function checkValid() {
    if (
        passwordInput.classList.contains('is-valid') &&
        emailInput.classList.contains('is-valid') &&
        usernameInput.value.length > 0 &&
        patronymicInput.value.length > 0 &&
        firstNameInput.value.length > 0 &&
        lastNameInput.value.length > 0
        ) {
        btn.classList.remove('disabled')
    } else {
        btn.classList.add('disabled')
    }
}

inputs.forEach(function (input) {
    input.addEventListener('input', (event) => {
        checkValid()
    })
})