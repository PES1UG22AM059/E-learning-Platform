document.addEventListener("DOMContentLoaded", () => {
    const formElements = document.querySelectorAll(".form");
    formElements.forEach((form) => {
        form.addEventListener("submit", (event) => {
            const passwordInput = form.querySelector('input[type="password"]');
            if (passwordInput.value.length < 8) {
                event.preventDefault();
                alert("Password must be at least 8 characters long.");
            }
        });
    });
});
