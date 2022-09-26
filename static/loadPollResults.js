polls = document.currentScript.getAttribute("polls");
//polls = JSON.parse(polls);
espace = document.getElementById("poll-content");

function progressBar(votePercentage) {
  return `<div class="progress mt-0">
                <div 
                    class="progress-bar"
                    role="progressbar" 
                    aria-label="Basic example" 
                    style="width: ${votePercentage}%" 
                    aria-valuenow="${votePercentage}" 
                    aria-valuemin="0" 
                    aria-valuemax="100"
                    id="">
                </div>
            </div>`;
}

function pollOptions(optionName, numVotes, progressBarHTML) {
  return `<div class="mb-3 text-start">
                <span class="ps-1">${optionName}</span>
                <span class="pe-1" style="float: right;">${numVotes} votos</span>
                ${progressBarHTML}
            </div>`;
}

function pollBlock(pollQuestion, pollOptionsHTML) {
  return `<p class="mt-3 fw-light fs-6 text-start">${pollQuestion}</p>
            <div class="row g-1 mt-1">
            ${pollOptionsHTML}
            </div>`;
}

function getNumberOfVotes(poll) {
  let nVotes = 0;
  for (let option of poll.options) {
    nVotes += option.numVotes;
  }
  return nVotes;
}

// console.log(getNumberOfVotes(polls[0]));
function teste(obj) {
  console.log(obj.length);
  console.log(getNumberOfVotes(obj[0]));
}

function makeSinglePoll(poll) {
  const nVotes = getNumberOfVotes(poll);
  var pollOptionsHTML = "";
  var progBarHTML = "";
  for (let option of poll.options) {
    progBarHTML = progressBar((option.numVotes / nVotes) * 100);
    pollOptionsHTML += pollOptions(
      option.optionName,
      option.numVotes,
      progBarHTML
    );
  }
  return pollOptionsHTML;
}

function completePollResult(polls) {
  if (polls.length == 0) {
    return "<br>Nenhuma enquete cadastrada :/";
  }

  resultHTML = "";
  for (let poll of polls) {
    resultHTML += pollBlock(poll.question, makeSinglePoll(poll));
  }
  return resultHTML;
}

function showPollResults(event_id, container_id) {
  const xhttp = new XMLHttpRequest();
  xhttp.onload = function () {
    document.getElementById(container_id).innerHTML = completePollResult(
      JSON.parse(this.responseText).polls
    );
  };

  console.log(event_id);
  // Send a request
  xhttp.open("GET", `/api/evento/${event_id}/polls`);
  xhttp.send();
}
