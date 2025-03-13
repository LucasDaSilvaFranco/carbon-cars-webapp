document.getElementById('consultaForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const data = {
        data_inicio: document.getElementById('data_inicio').value,
        data_fim: document.getElementById('data_fim').value,
        fabrica: document.getElementById('fabrica').value,
        aprovacao: document.getElementById('aprovacao').value
    };

    // Validação das datas
    if (new Date(data.data_inicio) > new Date(data.data_fim)) {
        alert('Data inicial não pode ser maior que a data final!');
        return;
    }

    // Desabilita o botão durante a consulta
    const btnSubmit = this.querySelector('button[type="submit"]');
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = 'Consultando...';

    fetch('/consultar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const resultadoCard = document.getElementById('resultadoCard');
            const resultadoTotal = document.getElementById('resultadoTotal');
            const resultadoInfo = document.getElementById('resultadoInfo');

            // Formata o número
            const formattedResult = new Intl.NumberFormat('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(data.resultado);

            resultadoTotal.textContent = `${formattedResult} m²`;

            // Constrói o texto de informações
            let infoHTML = `<p><strong>Período:</strong> ${formatarData(data.data_inicio)} até ${formatarData(data.data_fim)}</p>`;
            if (data.fabrica !== 'Todas') {
                infoHTML += `<p><strong>Fábrica:</strong> ${data.fabrica}</p>`;
            }
            if (data.aprovacao !== 'Todas') {
                infoHTML += `<p><strong>Aprovados:</strong> ${data.aprovacao}</p>`;
            }

            resultadoInfo.innerHTML = infoHTML;
            resultadoCard.style.display = 'block';
        } else {
            alert('Erro ao consultar: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Erro ao realizar a consulta');
    })
    .finally(() => {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = 'Consultar';
    });
});

function formatarData(data) {
    return new Date(data).toLocaleDateString('pt-BR');
}

// Define a data máxima como hoje
document.getElementById('data_inicio').max = new Date().toISOString().split('T')[0];
document.getElementById('data_fim').max = new Date().toISOString().split('T')[0];