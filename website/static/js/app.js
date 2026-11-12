const pageTitles = {
  dashboard: "Dashboard",
  research: "New Research",
  agents: "AI Agents",
  analytics: "Analytics",
  reports: "Reports",
  about: "About Project"
};

let activeJobId = null;
let pollTimer = null;
let lastStatus = null;


function showPage(name) {

  document.querySelectorAll(".page").forEach(page => {
    page.classList.remove("active");
  });

  document.querySelectorAll(".nav-item").forEach(button => {
    button.classList.toggle(
      "active",
      button.dataset.page === name
    );
  });

  const page = document.getElementById(`page-${name}`);

  if (page) {
    page.classList.add("active");
  }

  document.getElementById("page-title").textContent =
    pageTitles[name] || "ResearchFlow AI";
}


document.querySelectorAll("[data-page]").forEach(button => {

  button.addEventListener("click", () => {
    showPage(button.dataset.page);
  });

});


document.querySelectorAll("[data-page-link]").forEach(link => {

  link.addEventListener("click", event => {

    event.preventDefault();

    showPage(link.dataset.pageLink);

  });

});


const fileInput = document.getElementById("dataset");

fileInput.addEventListener("change", () => {

  document.getElementById("file-name").textContent =

    fileInput.files.length
      ? fileInput.files[0].name
      : "Choose a CSV file or drag it here";

});


const form = document.getElementById("research-form");


form.addEventListener("submit", async event => {

  event.preventDefault();

  const errorBox = document.getElementById("form-error");

  const startButton = document.getElementById("start-btn");

  errorBox.textContent = "";

  const topic = document.getElementById("topic").value.trim();

  if (!topic) {

    errorBox.textContent = "Please enter a research topic.";

    return;

  }

  startButton.disabled = true;

  startButton.textContent = "Starting workflow...";

  const data = new FormData(form);

  try {

    const response = await fetch("/api/research", {

      method: "POST",

      body: data

    });

    const result = await response.json();

    if (!response.ok) {

      throw new Error(
        result.error || "Could not start the workflow."
      );

    }

    activeJobId = result.job_id;

    lastStatus = null;

    resetAgentCards();

    // Reset old report content

    document.getElementById("report-topic").textContent = topic;

    document.getElementById("report-content").textContent =
      "Your agents are working. The report will appear when the workflow completes.";

    document.getElementById("report-status").textContent =
      "● GENERATING";

    const downloadLink = document.getElementById("download-report");

    downloadLink.classList.add("disabled-link");

    downloadLink.setAttribute("aria-disabled", "true");

    // Clear previous analysis and insights

    document.getElementById("analysis-output").textContent =
      "Waiting for the Data Analyst...";

    document.getElementById("insights-output").textContent =
      "Waiting for the Insight Agent...";

    document.getElementById("critique-output").textContent =
      "Waiting for the Critic Agent...";

    // Set correct mode information

    document.getElementById("analytics-note").textContent =

      result.mode === "Web Research Only"

        ? "Web Research Only mode is active. No old dataset will be used. Numerical evidence will be extracted from current research."

        : "Research + Data Analysis mode is active. Only your newly uploaded CSV will be analysed.";

    // Hide all previous charts immediately

    hideAllCharts();

    showPage("agents");

    startPolling();

  } catch (error) {

    errorBox.textContent = error.message;

  } finally {

    startButton.disabled = false;

    startButton.innerHTML =
      'Generate research <span>→</span>';

  }

});


function resetAgentCards() {

  document.querySelectorAll(".agent-card").forEach(card => {

    card.classList.remove("running", "completed");

    card.querySelector(".agent-state").textContent =
      "WAITING";

  });

  document.getElementById("progress-number").textContent =
    "0%";

  document.getElementById("progress-bar").style.width =
    "0%";

  document.getElementById("run-state-title").textContent =
    "Starting research workflow";

  document.getElementById("run-state-subtitle").textContent =
    "The six agents are preparing to execute.";

  document.getElementById("run-state-dot").textContent =
    "● RUNNING";

}


function startPolling() {

  if (pollTimer) {

    clearInterval(pollTimer);

  }

  pollStatus();

  pollTimer = setInterval(pollStatus, 1600);

}


async function pollStatus() {

  if (!activeJobId) return;

  try {

    const response = await fetch(
      `/api/status/${activeJobId}`
    );

    const job = await response.json();

    if (!response.ok) {

      throw new Error(
        job.error || "Could not read workflow status."
      );

    }

    lastStatus = job;

    updateAgentView(job);

    updateOutputs(job);

    if (
      job.status === "completed" ||
      job.status === "failed"
    ) {

      clearInterval(pollTimer);

      pollTimer = null;

    }

  } catch (error) {

    document.getElementById("run-state-subtitle").textContent =
      error.message;

  }

}


function updateAgentView(job) {

  const statuses = job.agent_status || {};

  let completed = 0;

  document.querySelectorAll(".agent-card").forEach(card => {

    const name = card.dataset.agent;

    const status = statuses[name] || "waiting";

    card.classList.toggle(
      "running",
      status === "running"
    );

    card.classList.toggle(
      "completed",
      status === "completed"
    );

    card.querySelector(".agent-state").textContent =
      status.toUpperCase();

    if (status === "completed") {
      completed++;
    }

  });

  const percent = Math.round(
    (completed / 6) * 100
  );

  document.getElementById("progress-number").textContent =
    `${percent}%`;

  document.getElementById("progress-bar").style.width =
    `${percent}%`;


  if (job.status === "completed") {

    document.getElementById("run-state-title").textContent =
      "Research workflow completed";

    document.getElementById("run-state-subtitle").textContent =
      `Mode: ${job.mode || "Research"} · All six agents finished.`;

    document.getElementById("run-state-dot").textContent =
      "● COMPLETED";

  }

  else if (job.status === "failed") {

    document.getElementById("run-state-title").textContent =
      "Workflow stopped";

    document.getElementById("run-state-subtitle").textContent =
      job.error || "An unexpected error occurred.";

    document.getElementById("run-state-dot").textContent =
      "● ERROR";

  }

  else {

    const current = job.current_agent || "starting";

    const labels = {

      planner: "Planner Agent",

      researcher: "Research Agent",

      data_analyst: "Data Analyst Agent",

      insight: "Insight Agent",

      critic: "Critic Agent",

      report: "Report Agent"

    };

    document.getElementById("run-state-title").textContent =
      `${labels[current] || "Workflow"} is working`;

    document.getElementById("run-state-subtitle").textContent =

      `Research attempt: ${job.research_round || 0} · ${job.mode || "Research mode"}`;

    document.getElementById("run-state-dot").textContent =
      "● RUNNING";

  }

}


function updateOutputs(job) {

  const summary = job.summary || {};

  document.getElementById("analysis-output").textContent =

    summary.analysis ||
    "The Data Analyst output will appear here.";

  document.getElementById("insights-output").textContent =

    summary.insights ||
    "Insights are being generated.";

  document.getElementById("critique-output").textContent =

    summary.critique ||
    "The Critic review is pending.";


  if (job.status === "completed") {

    document.getElementById("report-status").textContent =
      "● REPORT READY";

    document.getElementById("report-topic").textContent =
      job.topic || "Research report";

    document.getElementById("report-content").textContent =
      job.report || "Report file was not found.";

    const link = document.getElementById("download-report");

    link.href =
      `/api/report/${job.job_id}/download`;

    link.classList.remove("disabled-link");

    link.setAttribute("aria-disabled", "false");


    // Only show charts if a CSV was uploaded

    if (job.mode === "Research + Data Analysis") {

      loadCharts();

    } else {

      hideAllCharts();

    }

  }

  else if (job.status === "failed") {

    document.getElementById("report-status").textContent =
      "● WORKFLOW ERROR";

    document.getElementById("report-content").textContent =
      job.error || "Workflow failed.";

    hideAllCharts();

  }

}


function hideAllCharts() {

  const charts = [

    ["chart-total", "empty-total"],

    ["chart-category", "empty-category"],

    ["chart-share", "empty-share"]

  ];

  charts.forEach(([imageId, emptyId]) => {

    const img = document.getElementById(imageId);

    const empty = document.getElementById(emptyId);

    if (img) {

      img.onload = null;

      img.onerror = null;

      img.removeAttribute("src");

      img.hidden = true;

    }

    if (empty) {

      empty.hidden = false;

      empty.textContent =
        "Charts will appear here when a relevant CSV dataset is analysed.";

    }

  });

}


function loadCharts() {

  const charts = [

    ["chart-total", "empty-total", "charts/total_trend.png"],

    ["chart-category", "empty-category", "charts/category_trends.png"],

    ["chart-share", "empty-share", "charts/latest_share.png"]

  ];

  charts.forEach(([imageId, emptyId, path]) => {

    const img = document.getElementById(imageId);

    const empty = document.getElementById(emptyId);

    if (!img || !empty) return;

    img.onload = () => {

      img.hidden = false;

      empty.hidden = true;

    };

    img.onerror = () => {

      img.hidden = true;

      empty.hidden = false;

      empty.textContent =
        "No chart was generated for this dataset.";

    };

    img.hidden = true;

    empty.hidden = false;

    img.src = `/outputs/${path}?v=${Date.now()}`;

  });

}


function loadExistingHealth() {

  fetch("/api/health")

    .then(response => {

      if (!response.ok) {
        throw new Error("offline");
      }

    })

    .catch(() => {

      const status = document.querySelector(".status-pill");

      if (status) {

        status.innerHTML = "● Backend unavailable";

      }

    });

}


loadExistingHealth();