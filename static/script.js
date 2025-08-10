document.getElementById('research-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const topic = document.getElementById('topic').value;
    const questions = document.getElementById('questions').value.split('\n').filter(q => q.trim() !== '');
    const responseDiv = document.getElementById('response');
    const toolsOutputDiv = document.getElementById('tools-output');
    const toggleToolsBtn = document.getElementById('toggle-tools');

    // Reset UI for new request
    responseDiv.innerHTML = 'Researching...';
    toggleToolsBtn.classList.add('hidden');
    toolsOutputDiv.innerHTML = '';
    toolsOutputDiv.classList.add('hidden');
    toggleToolsBtn.textContent = 'Show Tools Used';

    try {
        const response = await fetch('/research', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ topic: topic, questions: questions })
        });

        const data = await response.json();

        if (data.error) {
            responseDiv.innerHTML = `<p>An error occurred: ${data.error}</p><p>Raw response: <pre>${JSON.stringify(data.raw_response, null, 2)}</pre></p>`;
            return;
        }

        // Populate main response content
        let html = `<h2>${data.topic}</h2><p>${data.summary}</p><h3>Sources:</h3><ul>`;
        for (const source of data.sources) {
            html += `<li><a href="${source}" target="_blank">${source}</a></li>`;
        }
        html += '</ul>';
        responseDiv.innerHTML = html;

        // Populate tool details if they exist
        if (data.tool_details && data.tool_details.length > 0) {
            let toolsHtml = '<dl>';
            for (const toolCall of data.tool_details) {
                toolsHtml += `<dt><strong>Tool:</strong> ${toolCall.tool_name}</dt>`;
                toolsHtml += `<dd><strong>Input:</strong> <pre>${JSON.stringify(toolCall.tool_input, null, 2)}</pre></dd>`;
                toolsHtml += `<dd><strong>Output:</strong> <pre>${toolCall.tool_output}</pre></dd>`;
            }
            toolsHtml += '</dl>';
            toolsOutputDiv.innerHTML = toolsHtml;
            toggleToolsBtn.classList.remove('hidden'); // Show the button
        }

    } catch (error) {
        responseDiv.innerHTML = `<p>An unexpected error occurred: ${error.message}</p>`;
    }
});

document.getElementById('toggle-tools').addEventListener('click', function() {
    const toolsOutputDiv = document.getElementById('tools-output');
    const isHidden = toolsOutputDiv.classList.toggle('hidden');
    this.textContent = isHidden ? 'Show Tools Used' : 'Hide Tools Used';
});
