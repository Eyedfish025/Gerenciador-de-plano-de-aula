document.addEventListener("DOMContentLoaded", () => {
    // Inicializa os ícones da página
    lucide.createIcons();

    const formLogin = document.getElementById("form-login");

    formLogin.addEventListener("submit", (event) => {
        event.preventDefault();

        const email = document.getElementById("login-email").value;
        const senha = document.getElementById("login-senha").value;

        // Aqui você inserirá a lógica de autenticação com sua API futuramente
        console.log("Tentativa de login com:", email);

        // Simulação de login bem-sucedido direcionando para o Dashboard
        window.location.href = "dashboard.html";
    });
});