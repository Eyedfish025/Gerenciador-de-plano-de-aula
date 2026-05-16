document.addEventListener("DOMContentLoaded", () => {
    lucide.createIcons();

    const formCadastro = document.getElementById("form-cadastro");

    formCadastro.addEventListener("submit", (event) => {
        event.preventDefault();

        const nome = document.getElementById("cad-nome").value;
        const email = document.getElementById("cad-email").value;
        const senha = document.getElementById("cad-senha").value;

        // Lógica de envio de dados para API aqui
        console.log("Cadastro solicitado:", { nome, email, senha });

        alert("Conta criada com sucesso!");
        // Redireciona o usuário para realizar o login
        window.location.href = "login.html";
    });
});