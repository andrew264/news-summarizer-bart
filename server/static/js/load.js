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
    loadingPage.remove();
}

function createSummary() {
    const summary = document.createElement('div');
    summary.id = 'summary';
    document.body.appendChild(summary);
}

function updatePageContent(response) {
    console.log(response['summary']);

    const summary = document.getElementById('summary');
    const ul = document.createElement('ul');
    summary.appendChild(ul);

    let i = 0;

    function addWord() {
        let summ = response['summary'];
        if (i >= summ.length) {
            return;
        }

        const li = document.createElement('li');
        ul.appendChild(li);

        const words = summ[i].split(' ');
        let j = 0;

        function typeWord() {
            if (j >= words.length) {
                i++;
                setTimeout(addWord, 200);
                return;
            }

            li.textContent += words[j] + ' ';
            j++;
            setTimeout(typeWord, 1000 / 24); // 24 words per second
        }

        setTimeout(typeWord, 200);
    }

    addWord();
}
