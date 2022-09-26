function std_card(event) {
  content = `<div class="card mb-3 rounded-3">
                                <div class="card-header">
                                    ${event.categoria}
                                </div>
                                <div class="card-body">
                                    <div class="container">
                                        <div class="row g-3">
                                            <div class="col-lg-7 col-xxl-8">
                                                <h4 class="card-title">
                                                    <a class="link-dark" style="text-decoration: none" href="/visualizar_evento/${event._id.$oid}">
                                                        ${event.titulo}
                                                    </a>
                                                </h4>
                                                <p class="card-text">${event.descricao}</p>
                                            </div>
                                            <div class="col-lg-5 col-xxl-4">
                                                <div class="d-grid gap-2 d-lg-flex justify-content-lg-end">`;
  var options = Object.keys(event.opcoes);
  var nOptions = options.length;
  for (let i = 0; i < nOptions; i++) {
    content += `<a class="btn btn-outline-success p-3 rounded-3" href="/visualizar_evento/${
      event._id.$oid
    }?option=${i}">${options[i]}
                                    <br class="d-none d-lg-block">
                                    <span class="d-inline d-lg-none"> &nbsp; | &nbsp; </span>
                                    <strong>${event.opcoes[
                                      options[i]
                                    ].odd.toFixed(2)}</strong>
                                </a>`;
  }

  content += ` </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>`;
  return content;
}

function home_page() {
  const xhttp = new XMLHttpRequest();
  xhttp.onload = function () {
    var eventos = JSON.parse(this.responseText);
    eventos = eventos.events;

    var content = "";

    for (let event of eventos) {
      if (event.status == "ativo") {
        content += std_card(event);
      }
    }

    document.getElementById("mainBlock").innerHTML = content;
  };

  // Send a request
  xhttp.open("GET", "/showEvents?category=all&usage=home");
  xhttp.send();
}

function profile() {
  // Create an XMLHttpRequest object
  const xhttp = new XMLHttpRequest();

  // Define a callback function
  xhttp.onload = function () {
    // Here you can use the Data
    var eventos = JSON.parse(this.responseText);
    eventos = eventos.events;

    var content = `<h4 class='ms-3 mb-4 mt-2'>Apostas em aberto (${eventos.length})</h4>`;

    for (let event of eventos) {
      if (event.status == "ativo") {
        content += std_card(event);
      }
    }

    document.getElementById("open-bets").innerHTML = content;
  };

  // Send a request
  xhttp.open("GET", "/showEvents?usage=profile&status=active");
  xhttp.send();
}

function creator() {
  // Create an XMLHttpRequest object
  const xhttp = new XMLHttpRequest();

  // Define a callback function
  xhttp.onload = function () {
    // Here you can use the Data
    var eventos = JSON.parse(this.responseText);
    eventos = eventos.events;

    var content_aberto = "";
    var content_nPubli = "";
    var content_hist = "";

    // var content = `<h4 class='ms-3 mb-4 mt-2'>Apostas em aberto (${eventos.length})</h4>`

    for (let event of eventos) {
      if (event.status == "ativo") {
        content_aberto += std_card(event);
      } else if (event.status == "finalizado") {
        content_hist += std_card(event);
      } else {
        content_nPubli += std_card(event);
      }
    }

    console.log(this.responseText);
    document.getElementById("em-aberto").innerHTML = content_aberto;
    document.getElementById("historico").innerHTML = content_hist;
    document.getElementById("nao-publicado").innerHTML = content_nPubli;
  };

  // Send a request
  xhttp.open("GET", "/showEvents?usage=creator");
  xhttp.send();
}

switch (document.currentScript.getAttribute("trevousage")) {
  case "home":
    home_page();
    break;

  case "profile":
    profile();
    break;

  case "creator":
    creator();
    break;

  default:
    break;
}
