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
            
            resultadoCard.style.display = 'block';
            
            if (data.aprovacao === 'Todas') {
                resultadoTotal.textContent = `${data.resultado.toFixed(2)} m²`;
                resultadoInfo.innerHTML = `
                    <p>Período: ${formatarData(data.data_inicio)} a ${formatarData(data.data_fim)}</p>
                    <p>Fábrica: ${data.fabrica}</p>
                    <p>Aprovados: ${data.resultado_sim.toFixed(2)} m²</p>
                    <p>Não Aprovados: ${data.resultado_nao.toFixed(2)} m²</p>
                `;
            } else {
                resultadoTotal.textContent = `${data.resultado.toFixed(2)} m²`;
                resultadoInfo.innerHTML = `
                    <p>Período: ${formatarData(data.data_inicio)} a ${formatarData(data.data_fim)}</p>
                    <p>Fábrica: ${data.fabrica}</p>
                    <p>Status: ${data.aprovacao}</p>
                `;
            }
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