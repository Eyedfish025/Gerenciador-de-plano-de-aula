// Dashboard script para gerenciamento de planos de aula.
// Cuida da Listagem paginação e exebição das recomendações por ia.

document.addEventListener('DOMContentLoaded', () => {
    let planos = [];
    let currentPage = 1;
    const itemsPerPage = 5;
    let currentFilter = '';
    let editingId = null;
    const apiBase = '/api/planos';

    const elements = {
        totalPlanos: document.getElementById('total-planos'),
        planosSemana: document.getElementById('planos-semana'),
        disciplinasCount: document.getElementById('disciplinas-count'),
        planoList: document.getElementById('plano-list'),
        resultInfo: document.getElementById('result-info'),
        pageNumber: document.getElementById('page-number'),
        prevPage: document.getElementById('prev-page'),
        nextPage: document.getElementById('next-page'),
        searchInput: document.getElementById('search-plano'),
        modal: document.getElementById('modal-form-plano'),
        modalTitle: document.getElementById('modal-title'),
        btnNovoPlano: document.getElementById('btn-novo-plano'),
        btnFecharModal: document.getElementById('btn-fechar-modal'),
        btnCancelarModal: document.getElementById('btn-cancelar-modal'),
        form: document.getElementById('form-plano-aula'),
        inputId: document.getElementById('plano-id'),
        inputTitulo: document.getElementById('plano-titulo'),
        inputDisciplina: document.getElementById('plano-disciplina'),
        inputData: document.getElementById('plano-data'),
        inputTags: document.getElementById('plano-tags'),
        inputObjetivo: document.getElementById('plano-objetivo'),
        inputEmenta: document.getElementById('plano-ementa'),
        inputConteudos: document.getElementById('plano-conteudos'),
        inputRecursos: document.getElementById('plano-recursos'),
        btnGerarIA: document.getElementById('btn-gerar-ia')
    };

    function formatDate(date) {
        const d = new Date(date);
        return d.toLocaleDateString('pt-BR');
    }

    // Atualiza os indicadores de total, planos da semana e disciplinas.
    function updateMetrics() {
        elements.totalPlanos.textContent = planos.length;

        const hoje = new Date();
        const seteDias = new Date();
        seteDias.setDate(hoje.getDate() + 7);
        const semana = planos.filter((plano) => {
            const data = new Date(plano.dataPrevista);
            return data >= hoje && data <= seteDias;
        }).length;
        elements.planosSemana.textContent = semana;

        const disciplinas = new Set(planos.map((plano) => plano.disciplina.trim()));
        elements.disciplinasCount.textContent = disciplinas.size;
    }

    // Filtra os planos de aula de acordo com o termo de busca.
    function getFilteredPlanos() {
        const filtro = currentFilter.trim().toLowerCase();
        if (!filtro) return planos;
        return planos.filter((plano) => {
            return (
                plano.titulo.toLowerCase().includes(filtro) ||
                plano.disciplina.toLowerCase().includes(filtro) ||
                plano.objetivo.toLowerCase().includes(filtro) ||
                plano.ementa.toLowerCase().includes(filtro) ||
                plano.tags.some((tag) => tag.toLowerCase().includes(filtro))
            );
        });
    }

    function renderPlanos() {
        const filtered = getFilteredPlanos();
        const totalPages = Math.max(1, Math.ceil(filtered.length / itemsPerPage));
        currentPage = Math.min(currentPage, totalPages);

        const start = (currentPage - 1) * itemsPerPage;
        const pageItems = filtered.slice(start, start + itemsPerPage);
        elements.planoList.innerHTML = '';

        if (!pageItems.length) {
            elements.planoList.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-gray-500">Nenhum plano encontrado.</td></tr>';
        } else {
            pageItems.forEach((plano) => {
                const row = document.createElement('tr');
                row.className = 'hover:bg-gray-50 transition';
                row.innerHTML = `
                    <td class="px-6 py-4">
                        <div class="font-semibold text-gray-900">${plano.titulo}</div>
                        <div class="text-xs text-blue-600 font-medium mt-0.5">${plano.disciplina}</div>
                    </td>
                    <td class="px-6 py-4 max-w-xs hidden md:table-cell">
                        <div class="font-medium text-gray-600">${plano.objetivo}</div>
                        <div class="text-xs text-gray-400 mt-1">${plano.ementa}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700">${formatDate(plano.dataPrevista)}</span>
                    </td>
                    <td class="px-6 py-4 hidden sm:table-cell">
                        ${plano.tags.map((tag) => `<span class="bg-gray-100 text-gray-600 px-2 py-0.5 rounded text-xs mr-1 mb-1 inline-block">${tag}</span>`).join('')}
                    </td>
                    <td class="px-6 py-4 text-right whitespace-nowrap">
                        <button class="p-1 text-gray-500 hover:text-blue-600 btn-editar" data-id="${plano.id}" title="Editar"><i data-lucide="edit-3" class="w-4 h-4"></i></button>
                        <button class="p-1 text-gray-500 hover:text-red-600 btn-excluir" data-id="${plano.id}" title="Excluir"><i data-lucide="trash-2" class="w-4 h-4"></i></button>
                    </td>
                `;
                elements.planoList.appendChild(row);
            });
        }

        elements.resultInfo.textContent = `Mostrando ${pageItems.length} de ${filtered.length} resultados`;
        elements.pageNumber.textContent = `${currentPage} de ${totalPages}`;
        elements.prevPage.disabled = currentPage === 1;
        elements.nextPage.disabled = currentPage === totalPages;

        // Renderizar ícones Lucide após atualizar DOM
        if (typeof lucide !== 'undefined' && lucide.createIcons) {
            lucide.createIcons();
        }
    }

    // Busca os planos do usuário autenticado e atualiza a lista na interface.
    async function fetchPlanos() {
        try {
            const response = await fetch(apiBase);
            console.log('Fetch response status:', response.status);
            if (!response.ok) {
                throw new Error(`Erro ao carregar planos: ${response.status}`);
            }
            const data = await response.json();
            console.log('Planos recebidos:', data);
            planos = data.planos.map((plano) => ({
                ...plano,
                tags: plano.tags ? plano.tags.split(',').map((tag) => tag.trim()).filter(Boolean) : []
            }));
            console.log('Planos processados:', planos);
            updateMetrics();
            renderPlanos();
        } catch (error) {
            console.error('Erro ao buscar planos:', error);
            elements.planoList.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-red-500">Não foi possível carregar os planos.</td></tr>';
        }
    }

    // Cria ou atualiza um plano de aula no backend.
    async function savePlano(planoData) {
        const method = editingId ? 'PUT' : 'POST';
        const url = editingId ? `${apiBase}/${editingId}` : apiBase;
        console.log(`Salvando plano via ${method} em ${url}:`, planoData);
        
        try {
            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ...planoData,
                    tags: planoData.tags.join(', ')
                })
            });
            console.log(`Resposta ${method}: ${response.status}`);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                console.error('Erro na resposta:', errorData);
                throw new Error(`Erro ${response.status}: ${errorData.error || 'Falha ao salvar'}`);
            }
            console.log('Plano salvo com sucesso');
            return true;
        } catch (error) {
            console.error('Erro ao salvar plano:', error);
            alert(`Erro ao salvar: ${error.message}`);
            return false;
        }
    }

    // Controla o estado do botão de recomendação por IA para evitar múltiplos cliques.
    function setIAButtonState(isLoading) {
        if (!elements.btnGerarIA) return;
        elements.btnGerarIA.disabled = isLoading;
        elements.btnGerarIA.textContent = isLoading ? 'Gerando IA...' : 'Gerar Recomendações com IA';
    }

    // Envia dados ao backend para receber recomendações de IA.
    async function generateIARecommendations() {
        const titulo = elements.inputTitulo.value.trim();
        const disciplina = elements.inputDisciplina.value.trim();
        const ementa = elements.inputEmenta.value.trim();

        if (!titulo || !disciplina || !ementa) {
            alert('Preencha Título da Aula, Disciplina e Ementa antes de gerar recomendações.');
            return;
        }

        setIAButtonState(true);
        try {
            const response = await fetch('/api/ia-recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ titulo, disciplina, ementa })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || 'Falha ao obter recomendações de IA.');
            }

            const data = await response.json();
            elements.inputConteudos.value = data.conteudos || '';
            elements.inputRecursos.value = data.recursos || '';
            elements.inputTags.value = Array.isArray(data.tags) ? data.tags.join(', ') : data.tags || '';

            if (data.relatedTopics) {
                elements.inputObjetivo.value = data.relatedTopics;
            }

            alert('Recomendações de IA preenchidas com sucesso.');
        } catch (error) {
            console.error('Erro IA:', error);
            alert(`Erro ao gerar recomendações: ${error.message}`);
        } finally {
            setIAButtonState(false);
        }
    }

    async function handleDelete(id) {
        if (!confirm('Deseja realmente excluir este plano de aula?')) {
            return;
        }

        console.log(`Deletando plano ${id}`);
        try {
            const response = await fetch(`${apiBase}/${id}`, {
                method: 'DELETE'
            });
            console.log(`Resposta DELETE: ${response.status}`);
            
            if (response.ok) {
                console.log('Plano deletado com sucesso');
                await fetchPlanos();
            } else {
                alert('Não foi possível excluir o plano.');
            }
        } catch (error) {
            console.error('Erro ao deletar plano:', error);
            alert('Erro ao excluir plano: ' + error.message);
        }
    }

    function openModal(isEdit = false) {
        if (!isEdit) {
            elements.form.reset();
            editingId = null;
            elements.inputId.value = '';
        }
        elements.modal.classList.remove('hidden');
        elements.modal.classList.add('flex');
        elements.modalTitle.textContent = isEdit ? 'Editar Plano de Aula' : 'Criar Plano de Aula';
    }

    function closeModal() {
        elements.modal.classList.add('hidden');
        elements.modal.classList.remove('flex');
        elements.form.reset();
        editingId = null;
        elements.inputId.value = '';
    }

    function fillForm(plano) {
        elements.inputId.value = plano.id;
        elements.inputTitulo.value = plano.titulo;
        elements.inputDisciplina.value = plano.disciplina;
        elements.inputData.value = plano.dataPrevista;
        elements.inputTags.value = plano.tags.join(', ');
        elements.inputObjetivo.value = plano.objetivo;
        elements.inputEmenta.value = plano.ementa;
        elements.inputConteudos.value = plano.conteudos;
        elements.inputRecursos.value = plano.recursos;
    }

    function handleEdit(id) {
        const plano = planos.find((item) => item.id === Number(id));
        if (!plano) return;
        editingId = plano.id;
        fillForm(plano);
        openModal(true);
    }

    // Abre o modal para criar um novo plano.
    elements.btnNovoPlano.addEventListener('click', () => {
        openModal(false);
    });

    // Fecha o modal sem salvar alterações.
    elements.btnFecharModal.addEventListener('click', closeModal);
    elements.btnCancelarModal.addEventListener('click', closeModal);

    elements.searchInput.addEventListener('input', (event) => {
        currentFilter = event.target.value;
        currentPage = 1;
        renderPlanos();
    });

    // Conecta o botão IA ao manipulador de recomendações.
    if (elements.btnGerarIA) {
        elements.btnGerarIA.addEventListener('click', generateIARecommendations);
    }

    if (elements.btnGerarIA) {
        elements.btnGerarIA.addEventListener('click', generateIARecommendations);
    }

    elements.prevPage.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage -= 1;
            renderPlanos();
        }
    });

    elements.nextPage.addEventListener('click', () => {
        currentPage += 1;
        renderPlanos();
    });

    elements.form.addEventListener('submit', async (event) => {
        event.preventDefault();
        console.log('Formulário enviado');

        const newPlano = {
            titulo: elements.inputTitulo.value.trim(),
            disciplina: elements.inputDisciplina.value.trim(),
            dataPrevista: elements.inputData.value,
            tags: elements.inputTags.value.split(',').map((tag) => tag.trim()).filter(Boolean),
            objetivo: elements.inputObjetivo.value.trim(),
            ementa: elements.inputEmenta.value.trim(),
            conteudos: elements.inputConteudos.value.trim(),
            recursos: elements.inputRecursos.value.trim()
        };

        console.log('Dados do plano:', newPlano);
        const success = await savePlano(newPlano);
        if (success) {
            console.log('Plano salvo, recarregando lista');
            await fetchPlanos();
            closeModal();
        } else {
            alert('Não foi possível salvar o plano.');
        }
    });

    elements.planoList.addEventListener('click', (event) => {
        const button = event.target.closest('button');
        if (!button) return;

        const id = button.dataset.id;
        if (button.classList.contains('btn-editar')) {
            handleEdit(id);
        } else if (button.classList.contains('btn-excluir')) {
            handleDelete(id);
        }
    });

    fetchPlanos();
});
