// Mostrar/ocultar resultados de busca
document.getElementById('search1')?.addEventListener('input', function() {
    const query = this.value.toLowerCase();
    const resultsContainer = document.getElementById('search_results');
    
    if (resultsContainer) {
        const resultsList = resultsContainer.querySelector('ul');
        
        // Clear previous results
        resultsList.innerHTML = '';
        
        if (query.length > 0) {
            fetch(`/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.length > 0) {
                        data.forEach(tweet => {
                            const li = document.createElement('li');
                            li.textContent = `${tweet.content} - por ${tweet.user.username}`;
                            resultsList.appendChild(li);
                        });
                    } else {
                        const li = document.createElement('li');
                        li.textContent = 'Nenhum resultado encontrado.';
                        resultsList.appendChild(li);
                    }
                    
                    resultsContainer.style.display = 'block';
                });
        } else {
            resultsContainer.style.display = 'none';
        }
    }
});

// Fechar resultados de busca ao clicar fora
document.addEventListener('click', function(event) {
    const searchContainer = document.getElementById('search_results');
    const searchInput = document.getElementById('search1');
    
    if (searchContainer && searchInput && 
        !searchContainer.contains(event.target) && 
        event.target !== searchInput) {
        searchContainer.style.display = 'none';
    }
});

// Mostrar mensagens flash
document.addEventListener('DOMContentLoaded', function() {
    const flashes = document.querySelectorAll('.alert');
    
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 500);
        }, 3000);
    });
});