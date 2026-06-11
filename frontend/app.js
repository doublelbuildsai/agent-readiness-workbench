const STEP_DELAY_MS = 500;

const FRIENDLY = {
  MonolithicAgent: "AI assistant",
  DealAgent: "Sales data",
  PolicyAgent: "Pricing rules",
  PricingAgent: "Quote builder",
  ComplianceAgent: "Approvals & records",
  Orchestrator: "Workflow",
  "HITL Gate": "Manager approval",
  Result: "Outcome",
  system: "Demo",
};

const state = {
  scenarios: [],
  selectedScenarioId: "high-northline",
  running: false,
  lastAudit: null,
  failedComplete: false,
  productionComplete: false,
  pendingHitl: false,
  currentStep: 1,
  useStatic: false,
  staticDemo: null,
};

const elements = {
  startGuided: document.querySelector("#start-guided"),
  stepRail: document.querySelector("#step-rail"),
  panelDeal: document.querySelector("#panel-deal"),
  panelCompare: document.querySelector("#panel-compare"),
  panelResults: document.querySelector("#panel-results"),
  btnStep2: document.querySelector("#btn-step2"),
  btnStep4: document.querySelector("#btn-step4"),
  runFailed: document.querySelector("#run-failed"),
  runProduction: document.querySelector("#run-production"),
  approveHitl: document.querySelector("#approve-hitl"),
  storyFailed: document.querySelector("#story-failed"),
  storyProduction: document.querySelector("#story-production"),
  verdictFailed: document.querySelector("#verdict-failed"),
  verdictProduction: document.querySelector("#verdict-production"),
  safeguards: document.querySelector("#safeguards-production"),
  columnProduction: document.querySelector("#column-production"),
  resultMarginRisk: document.querySelector("#result-margin-risk"),
  resultTimeSaved: document.querySelector("#result-time-saved"),
  exportAudit: document.querySelector("#export-audit"),
  restartDemo: document.querySelector("#restart-demo"),
};

init();

async function init() {
  state.useStatic = await detectStaticMode();
  if (state.useStatic) {
    const response = await fetch("./static-demo.json");
    state.staticDemo = await response.json();
    state.scenarios = state.staticDemo.scenarios;
  } else {
    await loadScenarios();
  }
  bindEvents();
}

async function detectStaticMode() {
  if (location.hostname.endsWith("github.io") || location.protocol === "file:") {
    return true;
  }
  try {
    const controller = new AbortController();
    setTimeout(() => controller.abort(), 1200);
    const response = await fetch("/api/health", { signal: controller.signal });
    return !response.ok;
  } catch {
    return true;
  }
}

async function loadScenarios() {
  const response = await fetch("/api/scenarios");
  state.scenarios = await response.json();
}

function bindEvents() {
  elements.startGuided.addEventListener("click", () => {
    goToStep(1);
    document.querySelector(".layout").scrollIntoView({ behavior: "smooth" });
  });
  elements.btnStep2.addEventListener("click", () => goToStep(2));
  elements.btnStep4.addEventListener("click", () => goToStep(4));
  elements.runFailed.addEventListener("click", () => runScenario("failed"));
  elements.runProduction.addEventListener("click", () => runScenario("production", false));
  elements.approveHitl.addEventListener("click", () => runScenario("production", true));
  elements.exportAudit.addEventListener("click", exportAudit);
  elements.restartDemo.addEventListener("click", restartDemo);
}

function goToStep(step) {
  state.currentStep = step;
  elements.stepRail.querySelectorAll(".step-item").forEach((item) => {
    const n = Number(item.dataset.step);
    item.classList.toggle("active", n === step);
    item.classList.toggle("done", n < step);
  });

  elements.panelDeal.classList.toggle("hidden", step !== 1);
  elements.panelCompare.classList.toggle("hidden", step !== 2 && step !== 3);
  elements.panelResults.classList.toggle("hidden", step !== 4);

  updateActionButtons();

  if (step === 1) {
    window.scrollTo({ top: 0, behavior: "smooth" });
  } else if (step <= 3) {
    elements.panelCompare.scrollIntoView({ behavior: "smooth", block: "start" });
  } else {
    elements.panelResults.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function updateActionButtons() {
  const showFailed = !state.failedComplete;
  const showProduction = state.failedComplete && !state.productionComplete && !state.pendingHitl;
  const showResults = state.productionComplete;

  elements.runFailed.classList.toggle("hidden", !showFailed);
  elements.runProduction.classList.toggle("hidden", !showProduction);
  elements.btnStep4.classList.toggle("hidden", !showResults);

  elements.runFailed.textContent = "▶ Play: Typical pilot";
  elements.runProduction.textContent = showProduction
    ? "▶ Next: See what works →"
    : "▶ Play: Production approach";

  elements.columnProduction?.classList.toggle("highlight-next", showProduction);
}

function restartDemo() {
  state.failedComplete = false;
  state.productionComplete = false;
  state.pendingHitl = false;
  state.lastAudit = null;
  clearStory(elements.storyFailed);
  clearStory(elements.storyProduction);
  elements.verdictFailed.classList.add("hidden");
  elements.verdictProduction.classList.add("hidden");
  elements.approveHitl.classList.add("hidden");
  elements.exportAudit.hidden = true;
  resetSafeguards();
  updateActionButtons();
  goToStep(1);
}

function clearStory(container) {
  container.innerHTML = '<p class="story-placeholder">Press play to watch what happens…</p>';
}

function resetSafeguards() {
  elements.safeguards.querySelectorAll(".safeguard").forEach((el) => el.classList.remove("on"));
}

async function runScenario(mode, approved = false) {
  if (state.running) return;

  state.running = true;
  elements.runFailed.disabled = true;
  elements.runProduction.disabled = true;
  elements.approveHitl.classList.add("hidden");

  const container = mode === "failed" ? elements.storyFailed : elements.storyProduction;
  if (!approved) {
    clearStory(container);
  }

  if (mode === "failed") {
    goToStep(2);
    addStoryStep(container, "start", "Sarah submits the discount request. The AI pilot kicks in…", "running");
  } else if (!approved) {
    goToStep(3);
    addStoryStep(container, "start", "Same request. This time the system is built with business guardrails.", "running");
  }

  try {
    if (state.useStatic) {
      await runStaticScenario(mode, approved, container);
    } else {
      await runApiScenario(mode, approved, container);
    }
  } catch (error) {
    addStoryStep(container, "error", error.message, "error");
  } finally {
    state.running = false;
    elements.runFailed.disabled = false;
    elements.runProduction.disabled = false;
  }
}

async function runApiScenario(mode, approved, container) {
  const response = await fetch("/api/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      scenario_id: state.selectedScenarioId,
      mode,
      approved,
    }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() || "";

    for (const chunk of chunks) {
      const line = chunk.trim();
      if (!line.startsWith("data: ")) continue;
      const event = JSON.parse(line.slice(6));
      handleEvent(event, mode, container);
    }
  }
}

async function runStaticScenario(mode, approved, container) {
  let events;
  if (mode === "failed") {
    events = state.staticDemo.failed;
  } else if (approved) {
    events = state.staticDemo.production_approved_tail;
  } else {
    events = state.staticDemo.production;
  }

  for (const event of events) {
    await sleep(STEP_DELAY_MS);
    handleEvent(event, mode, container);
    if (event.type === "hitl_required") {
      break;
    }
  }
}

function handleEvent(event, mode, container) {
  if (event.type === "trace") {
    const friendly = translateTrace(event, mode);
    if (friendly) {
      addStoryStep(container, event.agent, friendly.text, friendly.status, friendly.detail);
    }
    return;
  }

  if (event.type === "hitl_required") {
    state.pendingHitl = true;
    updateActionButtons();
    addStoryStep(
      container,
      "Manager approval",
      "This deal needs your sign-off. VP Sales and Finance are reviewing in parallel.",
      "waiting"
    );
    elements.approveHitl.classList.remove("hidden");
    elements.verdictProduction.classList.remove("hidden");
    elements.verdictProduction.innerHTML = `
      <strong>What leadership sees:</strong>
      <p>The AI did the homework — flagged 3 policy issues and prepared a deal brief. Now a leader decides. This is how you keep speed <em>and</em> control.</p>
    `;
    return;
  }

  if (event.type === "complete") {
    renderComplete(event, mode, container);
  }
}

function translateTrace(event, mode) {
  if (mode === "failed" && event.agent === "MonolithicAgent") {
    if (event.message.includes("STACKED")) {
      return { text: "Stacks promo + rebate — not allowed by policy.", status: "error", detail: "$24K hidden conflict" };
    }
    if (event.message.includes("Tier-1 cap")) {
      return { text: "Auto-approves 22% — but your Tier-1 cap is 15%.", status: "error", detail: "$34K over policy cap" };
    }
    if (event.message.includes("skipping policy")) {
      return { text: "Never checks company pricing rules.", status: "warning" };
    }
    if (event.message.includes("sequential")) {
      return { text: "Approvals still go one at a time. Deal waits days.", status: "warning" };
    }
    if (event.message.includes("no audit")) {
      return { text: "No approval record kept. Finance can't verify later.", status: "error" };
    }
    if (event.status === "running") {
      return { text: "One AI has access to everything — pricing, CRM, approvals.", status: "warning" };
    }
  }

  if (mode === "production") {
    if (event.agent === "Orchestrator") {
      return { text: "Breaks the request into clear, reviewable steps.", status: "ok" };
    }
    if (event.agent === "DealAgent") {
      return { text: "Looks up the deal: Northline Retail, $480K, closes Friday.", status: "ok" };
    }
    if (event.agent === "PolicyAgent" && event.status === "complete" && event.message.includes("citations")) {
      return { text: "Checks pricing rules — finds issues that need attention.", status: "ok", detail: `${event.citations?.length || 3} policies checked` };
    }
    if (event.agent === "PolicyAgent" && event.status === "warning") {
      return { text: event.message.replace("Policy flag: ", ""), status: "warning" };
    }
    if (event.agent === "PricingAgent" && event.message.includes("validate")) {
      return { text: "Validates products and line items.", status: "ok" };
    }
    if (event.agent === "ComplianceAgent" && event.message.includes("risk_score")) {
      return { text: "Flags this as high-risk — needs leadership approval.", status: "waiting" };
    }
    if (event.agent === "ComplianceAgent" && event.message.includes("route_parallel")) {
      return { text: "Sends to VP Sales + Finance at the same time (not one after another).", status: "ok" };
    }
    if (event.agent === "ComplianceAgent" && event.message.includes("HITL approval")) {
      return { text: "You approved. Quote moves forward.", status: "ok" };
    }
    if (event.agent === "PricingAgent" && event.message.includes("generate_quote")) {
      const net = event.message.match(/\$[\d,]+/)?.[0] || "";
      return { text: `Quote ready at approved pricing ${net}.`, status: "ok" };
    }
    if (event.agent === "ComplianceAgent" && event.message.includes("audit_event")) {
      return { text: "Full approval record saved for Finance.", status: "ok" };
    }
  }

  return null;
}

function addStoryStep(container, label, text, status, detail = "") {
  if (container.querySelector(".story-placeholder")) {
    container.innerHTML = "";
  }

  const step = document.createElement("div");
  step.className = `story-step status-${status}`;
  const icons = { ok: "✓", error: "✗", warning: "!", waiting: "◷", running: "●" };
  step.innerHTML = `
    <span class="step-icon">${icons[status] || "•"}</span>
    <div class="step-body">
      <span class="step-label">${escapeHtml(FRIENDLY[label] || label)}</span>
      <p class="step-text">${text}</p>
      ${detail ? `<span class="step-detail">${escapeHtml(detail)}</span>` : ""}
    </div>
  `;
  container.appendChild(step);
  step.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function renderComplete(event, mode, container) {
  if (event.quote) {
    const discount = (event.quote.discount_pct * 100).toFixed(0);
    const net = Number(event.quote.net_price).toLocaleString();
    addStoryStep(
      container,
      "Outcome",
      mode === "failed"
        ? `Quote sent at ${discount}% off ($${net}) — but RevOps will likely block it.`
        : `Quote approved at ${discount}% off ($${net}) — ready to send.`,
      mode === "failed" ? "error" : "ok"
    );
  }

  if (mode === "failed") {
    state.failedComplete = true;
    elements.verdictFailed.classList.remove("hidden");
    elements.verdictFailed.innerHTML = `
      <strong>What leadership sees:</strong>
      <p>${escapeHtml(event.outcome)}</p>
    `;
    const marginRisk = Number(event.margin_at_risk || 57600);
    elements.resultMarginRisk.textContent = `$${Math.round(marginRisk / 1000)}K`;
    updateActionButtons();
    elements.columnProduction.scrollIntoView({ behavior: "smooth", block: "nearest" });
    markStepDone(2);
  }

  if (mode === "production") {
    state.pendingHitl = false;
    state.productionComplete = true;
    elements.verdictProduction.classList.remove("hidden");
    elements.verdictProduction.innerHTML = `
      <strong>What leadership sees:</strong>
      <p>${escapeHtml(event.outcome)}</p>
    `;
    elements.approveHitl.classList.add("hidden");
    updateActionButtons();

    if (event.governance) {
      elements.safeguards.querySelectorAll(".safeguard").forEach((el) => {
        const key = el.dataset.key;
        if (event.governance[key]) el.classList.add("on");
      });
    }

    const manualDays = Math.round(event.manual_hours / 24);
    elements.resultTimeSaved.textContent = `${manualDays} days → ${event.turnaround_hours} hours`;
    state.lastAudit = event.audit || null;
    elements.exportAudit.hidden = !state.lastAudit?.length;
    markStepDone(3);
  }
}

function markStepDone(step) {
  elements.stepRail.querySelectorAll(".step-item").forEach((item) => {
    const n = Number(item.dataset.step);
    item.classList.toggle("done", n <= step);
    item.classList.toggle("active", n === step + 1);
  });
}

function exportAudit() {
  if (!state.lastAudit) return;
  const blob = new Blob([JSON.stringify(state.lastAudit, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "northline-approval-record.json";
  anchor.click();
  URL.revokeObjectURL(url);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}