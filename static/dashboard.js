document.addEventListener("DOMContentLoaded", () => {
    // Renderiza ícones do Lucide
    lucide.createIcons();

    // Seletores Elementos do DOM
    const modal = document.getElementById("modal-form-plano");
    const modalTitle = document.getElementById("modal-title");
    const formPlano = document.getElementById("form-plano-aula");
    
    const btnNovoPlano = document.getElementById("btn-novo-plano");
    const btnFecharModal = document.getElementById("btn-fechar-modal");
    const btnCancelarModal = document.getElementById("btn-cancelar-modal");
    
    const botoesEditar = document.querySelectorAll(".btn-editar");
    const botoesExcluir = document.querySelectorAll(".btn-excluir");

    // Funções de Controle do Modal
    function abrirModal(modo = "create") {
        if (modo === "edit") {
            modalTitle.innerText = "Editar Plano de Aula";
        } else {
            modalTitle.innerText = "Criar Novo Plano de Aula";
            formPlano.reset(); // Limpa dados anteriores no cadastro
        }
        modal.classList.remove("hidden");
    }

    function fecharModal() {
        modal.classList.add("hidden");
    }

    // Ouvintes de Evento (Listeners)
    btnNovoPlano.addEventListener("click", () => abrirModal("create"));
    btnFecharModal.addEventListener("click", fecharModal);
    btnCancelarModal.addEventListener("click", fecharModal);

    // Mapeamento dos botões existentes de Edição na tabela
    botoesEditar.forEach(botao => {
        botao.addEventListener("click", () => {
            abrirModal("edit");
            // Nota: Futuramente, você preencherá os inputs com dados do banco aqui.
        });
    });

    // Mapeamento dos botões de Exclusão
    botoesExcluir.forEach(botao => {
        botao.addEventListener("click", () => {
            if (confirm("Tem certeza que deseja remover este plano de aula? Essa ação não pode ser desfeita.")) {
                alert("Plano de aula removido com sucesso!");
                // Lógica de deleção via API ou alteração de estado do DOM aqui
            }
        });
    });

    // Submissão do Formulário de Plano de Aula
    formPlano.addEventListener("submit", (event) => {
        event.preventDefault();

        // Captura todos os campos obrigatórios e opcionais solicitados
        const dadosPlano = {
            titulo: document.getElementById("plano-titulo").value,
            disciplina: document.getElementById("plano-disciplina").value,
            data: document.getElementById("plano-data").value,
            tags: document.getElementById("plano-tags").value,
            objetivo: document.getElementById("plano-objetivo").value,
            ementa: document.getElementById("plano-ementa").value,
            conteudos: document.getElementById("plano-conteudos").value,
            recursos: document.getElementById("plano-recursos").value
        };

        console.log("Dados do Plano prontos para salvar:", dadosPlano);
        alert("Plano salvo com sucesso!");
        fecharModal();
    });
});