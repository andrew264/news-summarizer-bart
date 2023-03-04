function showLoadingPage() {
    const loadingPage = document.createElement('div');
    loadingPage.id = 'loading-page';

    const spinner = document.createElement('div');
    spinner.className = 'spinner';

    loadingPage.appendChild(spinner);

    document.body.appendChild(loadingPage);
}

function hideLoadingPage() {
    const loadingPage = document.getElementById('loading-page');
    const title = document.getElementById('title');
    loadingPage.remove();
    title.remove();
}

function updatePageContent(response) {
    console.log(response);

    const summary = document.createElement('div');
    summary.id = 'summary';

    const ul = document.createElement('ul');
    for (let i = 0; i < response.length; i++) {
        const li = document.createElement('li');
        li.textContent = response[i];
        ul.appendChild(li);
    }
    summary.appendChild(ul);
    document.body.appendChild(summary);
}