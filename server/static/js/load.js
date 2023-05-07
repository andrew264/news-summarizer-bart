function showLoadingPage() {
  const loadingPage = document.createElement("div");
  loadingPage.id = "loading-page";

  const spinner = document.createElement("div");
  spinner.className = "spinner";

  loadingPage.appendChild(spinner);

  document.body.appendChild(loadingPage);
}

function hideLoadingPage() {
  const loadingPage = document.getElementById("loading-page");
  loadingPage.remove();
}

function createSummary() {
  const summary = document.createElement("div");
  summary.id = "summary";
  document.body.appendChild(summary);
}

function updatePageContent(response) {
  console.log(response["summary"]);

  const summary = document.getElementById("summary");
  const ul = document.createElement("ul");
  summary.appendChild(ul);

  // set font size based on length of summary
  const summaryLength = response["summary"].length;

  if (summaryLength >= 2) {
    ul.style.fontSize = "1.5em";
  } else {
    ul.style.fontSize = "2em";
  }

  let i = 0;

  function addWord() {
    let summ = response["summary"];
    if (i >= summ.length) {
      return;
    }

    const li = document.createElement("li");
    ul.appendChild(li);

    const words = summ[i].split(" ");
    let j = 0;

    function typeWord() {
      if (j >= words.length) {
        i++;
        setTimeout(addWord, 200);
        return;
      }

      li.textContent += words[j] + " ";
      j++;
      setTimeout(typeWord, 1000 / 24); // 24 words per second
    }

    setTimeout(typeWord, 200);
  }

  addWord();
}

const audio = new Audio();
audio.src = "/audio";

function playAudio() {
  if (audio.readyState !== 4) {
    console.log("Audio not ready");
    return;
  }

  if (audio.paused) {
    audio.play().then((r) => console.log("Audio played"));
  } else {
    audio.pause();
  }
}

window.addEventListener("beforeunload", function () {
  audio.pause();
  audio.currentTime = 0;
});
