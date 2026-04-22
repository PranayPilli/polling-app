const API = "http://127.0.0.1:8000";

// Add option input
function addOption() {
  const div = document.createElement("div");
  div.innerHTML = `<input class="opt" placeholder="Option">`;
  document.getElementById("options").appendChild(div);
}

// Create poll
async function createPoll() {
  const question = document.getElementById("question").value;
  const options = [...document.querySelectorAll(".opt")]
    .map(o => o.value)
    .filter(o => o.trim() !== "");

  if (!question || options.length < 2) {
    alert("Enter valid question and at least 2 options");
    return;
  }

  await fetch(`${API}/polls`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ question, options })
  });

  document.getElementById("question").value = "";
  document.getElementById("options").innerHTML = "";

  loadPolls();
}

// Vote
async function vote(id, index) {
  if (localStorage.getItem(id)) {
    alert("You already voted!");
    return;
  }

  const res = await fetch(`${API}/polls/${id}/vote`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ optionIndex: index })
  });

  const data = await res.json();

  if (data.error) {
    alert(data.error);
    return;
  }

  localStorage.setItem(id, true);
  loadPolls();
}

// Delete poll
async function deletePoll(id) {
  await fetch(`${API}/polls/${id}`, { method: "DELETE" });
  loadPolls();
}

// Load polls
async function loadPolls() {
  const res = await fetch(`${API}/polls`);
  const polls = await res.json();

  const container = document.getElementById("polls");
  container.innerHTML = "";

  polls.forEach(p => {
    const total = p.options.reduce((sum, o) => sum + o.votes, 0);

    let html = `<div class="poll">
      <h3>${p.question}</h3>`;

    p.options.forEach((o, i) => {
      const percent = total ? (o.votes / total) * 100 : 0;

      html += `
        <div class="option-box">
          <button onclick="vote('${p.id}', ${i})">${o.text}</button>
          
          <div class="bar-container">
            <div class="bar" style="width:${percent}%">
              ${percent.toFixed(1)}%
            </div>
          </div>

          <div class="vote-text">
            ${o.votes} votes
          </div>
        </div>
      `;
    });

    html += `
      <p><strong>Total Votes:</strong> ${total}</p>
      <button class="delete-btn" onclick="deletePoll('${p.id}')">Delete</button>
    </div>
    `;

    container.innerHTML += html;
  });
}

loadPolls();