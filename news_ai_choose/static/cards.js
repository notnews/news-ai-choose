const slider = document.querySelector("#slider-sentiment");
slider.addEventListener("mouseup", renderSliderPage);
renderSliderPage(first_load=true);

// 1. send request to the backend
// 2. use data to build homepage dynamically
function renderSliderPage(first_load=false) {
    // sample function to show how we can use input to send a request
    const sent_slidr = document.querySelector("#slider-sentiment");
    const cardParent = document.querySelector("#card-parent");
    const selection = sent_slidr.value;
    let payload;
    if (first_load === true) {
        payload = {};
    } else {
        payload = {positivity: selection};
    }
    cardParent.innerHTML = ""
    postData("/articles", payload).then(d => renderCards(d, cardParent));
}

async function postData(url = '', data = {}) {
    // Default options are marked with *
    const response = await fetch(url, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, *cors, same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
        'Content-Type': 'application/json'
        },
        redirect: 'follow', // manual, *follow, error
        referrerPolicy: 'origin',
        body: JSON.stringify(data) // body data type must match "Content-Type" header
    });
    return response.json(); // parses JSON response into native JavaScript objects
}

function renderCards(data, cardParent) {
    data.forEach(art => {
        const card = getBootstrapCard(art.title, art.content, art.url);
        cardParent.appendChild(card); 
    });
}    
function getBootstrapCard(title, body, url) {
    const col = document.createElement("div");
    col.className = "col";
    const cardContainer = document.createElement("div");
    cardContainer.className = "card";
    cardContainer.stlye = "width: 18rem;"
    const cardBody = document.createElement("div");
    cardBody.className = "card-body";
    const cardTitle = document.createElement("h5");
    cardTitle.className = "card-title";
    cardTitle.textContent = title;
    const cardText = document.createElement("p");
    cardText.className = "card-text";
    cardText.textContent = body;
    const cardLink = document.createElement("a");
    cardLink.className = "btn btn-primary";
    cardLink.textContent = "Go to Article";
    cardLink.href = url;
    col.appendChild(cardContainer);
    cardContainer.appendChild(cardBody);
    cardBody.appendChild(cardTitle);
    cardBody.appendChild(cardText);
    cardBody.appendChild(cardLink);
    return col
}