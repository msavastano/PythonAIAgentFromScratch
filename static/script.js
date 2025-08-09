document.getElementById('research-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const query = document.getElementById('query').value;
    const responseDiv = document.getElementById('response');
    responseDiv.innerHTML = 'Researching...';

    const response = await fetch('/research', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: query })
    });

    const data = await response.json();
    let html = `<h2>${data.topic}</h2><p>${data.summary}</p><h3>Sources:</h3><ul>`;
    for (const source of data.sources) {
        html += `<li><a href="${source}" target="_blank">${source}</a></li>`;
    }
    html += '</ul>';
    responseDiv.innerHTML = html;
});
