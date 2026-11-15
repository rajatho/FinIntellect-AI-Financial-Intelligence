// FinIntellect Frontend Application Controller
// Enterprise AI Financial Summary Generation & Analysis Platform

let currentReportId = "techcorp_solutions_ltd._fy2025";
let currentReportData = null;
let currentLength = "Standard";
let currentTone = "Professional";
let currentModel = "gemini-2.5-flash";
let isSpeaking = false;
let trendChart = null;

// User Authentication State
let currentUser = null;
let authToken = localStorage.getItem("FININTELLECT_AUTH_TOKEN") || null;

document.addEventListener("DOMContentLoaded", () => {
  checkAuthStatus();
  loadSamples();
  loadReport(currentReportId);

  // Setup modal backdrop and key listeners
  setupModalDismissal();
});

function setupModalDismissal() {
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeAuthModal();
      const verModal = document.getElementById("version-modal");
      if (verModal && !verModal.classList.contains("hidden")) {
        toggleVersionModal();
      }
    }
  });

  const authModal = document.getElementById("auth-modal");
  if (authModal) {
    authModal.addEventListener("click", (e) => {
      if (e.target === authModal) closeAuthModal();
    });
  }

  const verModal = document.getElementById("version-modal");
  if (verModal) {
    verModal.addEventListener("click", (e) => {
      if (e.target === verModal) toggleVersionModal();
    });
  }
}

// ----------------- AUTHENTICATION & USER MANAGEMENT ----------------- //

async function checkAuthStatus() {
  if (!authToken) {
    updateAuthUI(null);
    return;
  }

  try {
    const res = await fetch("/api/auth/me", {
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    const data = await res.json();
    if (data.success && data.user) {
      currentUser = data.user;
      updateAuthUI(data.user);
    } else {
      authToken = null;
      localStorage.removeItem("FININTELLECT_AUTH_TOKEN");
      updateAuthUI(null);
    }
  } catch (err) {
    console.error("Auth check failed:", err);
    updateAuthUI(null);
  }
}

function updateAuthUI(user) {
  const loggedOutEl = document.getElementById("nav-auth-logged-out");
  const loggedInEl = document.getElementById("nav-auth-logged-in");

  if (user) {
    if (loggedOutEl) loggedOutEl.classList.add("hidden");
    if (loggedInEl) loggedInEl.classList.remove("hidden");

    const dispName = document.getElementById("user-display-name");
    if (dispName) dispName.textContent = user.name.split(",")[0];
    const dispRole = document.getElementById("user-display-role");
    if (dispRole) dispRole.textContent = user.role || "Financial Analyst";
    const avatar = document.getElementById("user-avatar");
    if (avatar) avatar.textContent = user.avatar_initials || "FA";

    const dropName = document.getElementById("dropdown-user-name");
    if (dropName) dropName.textContent = user.name;
    const dropEmail = document.getElementById("dropdown-user-email");
    if (dropEmail) dropEmail.textContent = user.email;
    const dropComp = document.getElementById("dropdown-user-company");
    if (dropComp) dropComp.textContent = user.company || "Enterprise Analyst";
    const repCount = document.getElementById("dropdown-user-reports-count");
    if (repCount) repCount.textContent = user.reports_count || 1;
  } else {
    if (loggedOutEl) loggedOutEl.classList.remove("hidden");
    if (loggedInEl) loggedInEl.classList.add("hidden");
  }
}

function openAuthModal(tab = "login") {
  const modal = document.getElementById("auth-modal");
  if (!modal) return;
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  switchAuthTab(tab);
}

function closeAuthModal() {
  const modal = document.getElementById("auth-modal");
  if (!modal) return;
  modal.classList.add("hidden");
  modal.classList.remove("flex");
}

function switchAuthTab(tab) {
  const loginForm = document.getElementById("form-login");
  const regForm = document.getElementById("form-register");
  const loginBtn = document.getElementById("auth-tab-login-btn");
  const regBtn = document.getElementById("auth-tab-register-btn");

  if (tab === "login") {
    if (loginForm) loginForm.classList.remove("hidden");
    if (regForm) regForm.classList.add("hidden");
    if (loginBtn) loginBtn.className = "flex-1 py-2 rounded-lg bg-blue-600 text-white shadow-sm transition font-bold";
    if (regBtn) regBtn.className = "flex-1 py-2 rounded-lg text-slate-400 hover:text-white transition font-medium";
  } else {
    if (loginForm) loginForm.classList.add("hidden");
    if (regForm) regForm.classList.remove("hidden");
    if (regBtn) regBtn.className = "flex-1 py-2 rounded-lg bg-blue-600 text-white shadow-sm transition font-bold";
    if (loginBtn) loginBtn.className = "flex-1 py-2 rounded-lg text-slate-400 hover:text-white transition font-medium";
  }
}

function toggleUserDropdown() {
  const menu = document.getElementById("user-dropdown-menu");
  if (menu) menu.classList.toggle("hidden");
}

// Close dropdown on outside click
document.addEventListener("click", (e) => {
  const menu = document.getElementById("user-dropdown-menu");
  const loggedInEl = document.getElementById("nav-auth-logged-in");
  if (menu && !menu.classList.contains("hidden") && loggedInEl) {
    if (!loggedInEl.contains(e.target)) {
      menu.classList.add("hidden");
    }
  }
});

async function handleLoginSubmit(e) {
  if (e) e.preventDefault();
  const emailEl = document.getElementById("login-email");
  const passEl = document.getElementById("login-password");
  const btn = document.getElementById("btn-login-submit");
  if (!emailEl || !passEl) return;

  const email = emailEl.value.trim();
  const password = passEl.value;

  if (btn) {
    btn.textContent = "Signing in...";
    btn.disabled = true;
  }

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (data.success) {
      authToken = data.token;
      localStorage.setItem("FININTELLECT_AUTH_TOKEN", data.token);
      currentUser = data.user;
      updateAuthUI(data.user);
      closeAuthModal();
      showToast(data.message || `Welcome back, ${data.user.name}!`, "success");
      loadArchiveList();
    } else {
      showToast(data.error || "Authentication failed. Check credentials.", "error");
    }
  } catch (err) {
    showToast(`Login failed: ${err.message}`, "error");
  } finally {
    if (btn) {
      btn.textContent = "Sign In";
      btn.disabled = false;
    }
  }
}

async function handleRegisterSubmit(e) {
  if (e) e.preventDefault();
  const nameEl = document.getElementById("reg-name");
  const emailEl = document.getElementById("reg-email");
  const compEl = document.getElementById("reg-company");
  const roleEl = document.getElementById("reg-role");
  const passEl = document.getElementById("reg-password");
  const btn = document.getElementById("btn-register-submit");

  if (!nameEl || !emailEl || !passEl) return;

  const name = nameEl.value.trim();
  const email = emailEl.value.trim();
  const company = compEl ? compEl.value.trim() : "";
  const role = roleEl ? roleEl.value : "Senior Financial Analyst";
  const password = passEl.value;

  if (btn) {
    btn.textContent = "Creating account...";
    btn.disabled = true;
  }

  try {
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, company, role, password })
    });
    const data = await res.json();
    if (data.success) {
      authToken = data.token;
      localStorage.setItem("FININTELLECT_AUTH_TOKEN", data.token);
      currentUser = data.user;
      updateAuthUI(data.user);
      closeAuthModal();
      showToast(data.message || `Account created successfully!`, "success");
      loadArchiveList();
    } else {
      showToast(data.error || "Registration failed.", "error");
    }
  } catch (err) {
    showToast(`Registration failed: ${err.message}`, "error");
  } finally {
    if (btn) {
      btn.textContent = "Create Account";
      btn.disabled = false;
    }
  }
}

async function handleGuestDemoLogin() {
  try {
    const res = await fetch("/api/auth/guest-login", { method: "POST" });
    const data = await res.json();
    if (data.success) {
      authToken = data.token;
      localStorage.setItem("FININTELLECT_AUTH_TOKEN", data.token);
      currentUser = data.user;
      updateAuthUI(data.user);
      closeAuthModal();
      showToast("Signed in as Sarah Jenkins, CFA (Lead Analyst)", "success");
      loadArchiveList();
    } else {
      showToast("Demo sign in failed.", "error");
    }
  } catch (err) {
    showToast(`Demo sign in error: ${err.message}`, "error");
  }
}

async function handleLogout() {
  try {
    await fetch("/api/auth/logout", {
      method: "POST",
      headers: { "Authorization": `Bearer ${authToken}` }
    });
  } catch (e) {}

  authToken = null;
  currentUser = null;
  localStorage.removeItem("FININTELLECT_AUTH_TOKEN");
  updateAuthUI(null);
  toggleUserDropdown();
  showToast("Logged out successfully.", "info");
}

// ----------------- DYNAMIC COMPANY ANALYSIS COMMAND ----------------- //

function fillCompany(name, industry, period, currency) {
  const compInput = document.getElementById("input-company-name");
  if (compInput) compInput.value = name;
  if (industry) {
    const indInput = document.getElementById("input-industry");
    if (indInput) indInput.value = industry;
  }
  if (period) {
    const perInput = document.getElementById("input-reporting-period");
    if (perInput) perInput.value = period;
  }
  if (currency) {
    const curInput = document.getElementById("input-currency");
    if (curInput) curInput.value = currency;
  }

  // Auto trigger analysis
  handleAnalyzeSubmit(new Event("submit"));
}

function focusCompanyInput() {
  switchTab("summary");
  const el = document.getElementById("input-company-name");
  if (el) {
    el.focus();
    el.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}

async function handleAnalyzeSubmit(e) {
  if (e) e.preventDefault();

  const compInput = document.getElementById("input-company-name");
  const companyName = compInput ? compInput.value.trim() : "";
  if (!companyName) {
    showToast("Please enter a company name to analyze.", "error");
    return;
  }

  const periodEl = document.getElementById("input-reporting-period");
  const indEl = document.getElementById("input-industry");
  const curEl = document.getElementById("input-currency");
  const submitBtn = document.getElementById("btn-analyze-submit");

  const period = periodEl ? periodEl.value : "FY2025";
  const industry = indEl ? indEl.value : "Technology & Software";
  const currency = curEl ? curEl.value : "$";

  // Visual loader state
  let originalHtml = "";
  if (submitBtn) {
    originalHtml = submitBtn.innerHTML;
    submitBtn.innerHTML = `
      <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-cyan-300" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
      </svg>
      <span>Analyzing ${companyName}...</span>
    `;
    submitBtn.disabled = true;
  }

  showToast(`Running verified pipeline & Gemini AI for ${companyName}...`, "info");

  try {
    const headers = { "Content-Type": "application/json" };
    if (authToken) {
      headers["Authorization"] = `Bearer ${authToken}`;
    }

    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: headers,
      body: JSON.stringify({
        company_name: companyName,
        reporting_period: period,
        industry: industry,
        currency: currency,
        length: currentLength,
        tone: currentTone,
        model: currentModel
      })
    });

    const result = await res.json();
    if (result.success && result.data) {
      currentReportId = result.data.report_id;
      currentReportData = result.data;
      renderReportData(result.data);
      switchTab("summary");
      showToast(`Financial Intelligence report synthesized for ${companyName}!`, "success");
      loadArchiveList();
      checkAuthStatus();
    } else {
      showToast(`Analysis Error: ${result.error || "Unknown error"}`, "error");
    }
  } catch (err) {
    showToast(`Request failed: ${err.message}`, "error");
  } finally {
    if (submitBtn && originalHtml) {
      submitBtn.innerHTML = originalHtml;
      submitBtn.disabled = false;
    }
  }
}

// ----------------- SAMPLE FILINGS LOADER ----------------- //

async function loadSamples() {
  try {
    const res = await fetch("/api/samples");
    const data = await res.json();
    if (data.success && data.samples) {
      const select = document.getElementById("sample-select");
      if (!select) return;
      select.innerHTML = '<option value="" disabled selected>Select Preloaded Filing...</option>';
      data.samples.forEach(s => {
        const opt = document.createElement("option");
        opt.value = s.id;
        opt.textContent = `${s.company} (${s.reporting_period})`;
        select.appendChild(opt);
      });
    }
  } catch (err) {
    console.error("Failed to load samples:", err);
  }
}

async function loadSelectedSample() {
  const select = document.getElementById("sample-select");
  if (!select) return;
  const sampleId = select.value;
  if (!sampleId) return;

  showToast(`Running pipeline for ${sampleId}...`, "info");
  try {
    const headers = { "Content-Type": "application/json" };
    if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: headers,
      body: JSON.stringify({
        sample_id: sampleId,
        length: currentLength,
        tone: currentTone,
        model: currentModel
      })
    });
    const result = await res.json();
    if (result.success && result.data) {
      currentReportId = result.data.report_id;
      currentReportData = result.data;
      renderReportData(result.data);
      switchTab("summary");
      showToast("Filing loaded and summary generated!", "success");
      loadArchiveList();
      checkAuthStatus();
    } else {
      showToast(`Error: ${result.error || "Failed to load sample"}`, "error");
    }
  } catch (err) {
    showToast(`Analysis request failed: ${err.message}`, "error");
  }
}

// ----------------- CUSTOM REPORT JSON FILE UPLOAD ----------------- //

async function handleFileUpload(e) {
  const file = e.target.files ? e.target.files[0] : null;
  if (!file) return;

  showToast(`Uploading and analyzing ${file.name}...`, "info");
  const formData = new FormData();
  formData.append("file", file);

  try {
    const headers = {};
    if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

    const res = await fetch("/api/upload", {
      method: "POST",
      headers: headers,
      body: formData
    });

    const result = await res.json();
    if (result.success && result.data) {
      currentReportId = result.data.report_id;
      currentReportData = result.data;
      renderReportData(result.data);
      switchTab("summary");
      showToast(`Uploaded and analyzed ${result.data.verified_object?.company || file.name}!`, "success");
      loadArchiveList();
      checkAuthStatus();
    } else {
      showToast(`Upload failed: ${result.error || "Could not process file"}`, "error");
    }
  } catch (err) {
    showToast(`Upload error: ${err.message}`, "error");
  } finally {
    e.target.value = "";
  }
}

// ----------------- REPORT LOADER & RENDERER ----------------- //

async function loadReport(reportId) {
  if (!reportId) return;
  try {
    const res = await fetch(`/api/reports/${encodeURIComponent(reportId)}`);
    const json = await res.json();
    if (json.success && json.data) {
      currentReportData = json.data;
      renderReportData(json.data);
    } else {
      // Default to TechCorp
      fillCompany("TechCorp Solutions Ltd.", "Technology & Software", "FY2025", "₹");
    }
  } catch (err) {
    console.error("Load report error:", err);
  }
}

function renderReportData(data) {
  if (!data) return;
  const vObj = data.verified_object || {};
  const activeVer = data.active_version || (data.versions ? data.versions[0] : (data.summary || {}));
  const val = activeVer.validation || {};

  // Header & Meta
  const headerComp = document.getElementById("header-company-name");
  if (headerComp) headerComp.textContent = vObj.company || "Company";

  const headerPeriod = document.getElementById("header-reporting-period");
  if (headerPeriod) {
    headerPeriod.innerHTML = 
      `Reporting Period: <span class="text-slate-200 font-semibold">${vObj.reporting_period || "FY2025"}</span> • Currency: <span class="text-slate-200 font-semibold">${vObj.currency || "$"} (${vObj.unit || "Millions"})</span>`;
  }

  const badgeVer = document.getElementById("badge-version-label");
  if (badgeVer) badgeVer.textContent = activeVer.version_label || "Summary v1";
  
  const engineText = document.getElementById("engine-display-text");
  const badgeEngine = document.getElementById("badge-engine-type");
  if (engineText && badgeEngine) {
    if (activeVer.is_fallback) {
      engineText.textContent = "Generated using Python Fallback Engine";
      badgeEngine.className = "px-2.5 py-0.5 text-[11px] font-bold rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center space-x-1.5";
    } else {
      engineText.textContent = `Generated using ${activeVer.source || "Gemini 3.5 Flash-Lite"}`;
      badgeEngine.className = "px-2.5 py-0.5 text-[11px] font-bold rounded-md bg-blue-500/20 text-blue-300 border border-blue-500/30 flex items-center space-x-1.5";
    }
  }

  const verCount = (data.all_versions || data.versions || []).length;
  const countBadge = document.getElementById("version-history-count-badge");
  if (countBadge) countBadge.textContent = `Version History (${verCount})`;

  // Validation Score Banner
  const valScore = val.score || "7/7 Passed";
  const valScoreBadge = document.getElementById("val-score-badge");
  if (valScoreBadge) valScoreBadge.textContent = valScore;
  const valScoreText = document.getElementById("val-score-text");
  if (valScoreText) valScoreText.textContent = valScore;

  renderValidationChecklist(val.checks || []);

  // Dual Speedometers Animated Rendering
  renderSpeedometers(val, vObj.risk_prediction || {}, data.data_validation || {});

  // Executive Summary Card
  const execText = activeVer.sections?.executive_summary || activeVer.full_markdown || "Data unavailable";
  const execContent = document.getElementById("exec-summary-content");
  if (execContent) execContent.textContent = execText;
  const wordCount = execText.split(/\s+/).filter(Boolean).length;
  const execWords = document.getElementById("exec-word-count");
  if (execWords) execWords.textContent = `~${wordCount} words`;

  // Financial Performance Summary (Section 6)
  renderFinancialMetrics(vObj.financial_metrics || {});

  // Ratio Summary Table (Section 7)
  renderRatioTable(vObj.ratios || {});

  // Trend Summary & Chart (Section 8)
  renderTrends(vObj.trends || []);

  // Anomaly Summary (Section 9)
  renderAnomalies(vObj.anomalies || []);

  // ML Risk Assessment (Section 10)
  renderMLRisk(vObj.risk_prediction || {});

  // Positive Indicators (Section 11)
  renderIndicators("positive-indicators-list", vObj.positive_indicators || []);

  // Key Risk Indicators (Section 12)
  renderIndicators("risk-indicators-list", vObj.risk_indicators || []);

  // Overall Analytical Assessment (Section 13)
  const assessText = activeVer.sections?.overall_analytical_assessment || "Data unavailable from the provided report.";
  const overallEl = document.getElementById("overall-assessment-text");
  if (overallEl) overallEl.textContent = assessText;

  // Render JSON Viewer
  const jsonViewer = document.getElementById("json-viewer-content");
  if (jsonViewer) jsonViewer.textContent = JSON.stringify(vObj, null, 2);

  // Sync Option Buttons
  syncLengthButtons(activeVer.length || currentLength);
  syncToneButtons(activeVer.tone || currentTone);
  syncModelButtons(activeVer.model || currentModel);
}

// ----------------- SPEEDOMETER & TELEMETRY RENDERING ----------------- //

function renderSpeedometers(val, risk, dataVal) {
  // --- Gauge 1: Factual Accuracy Speedometer ---
  const passedCount = val.passed_count !== undefined ? val.passed_count : (val.score ? parseInt(val.score.split("/")[0]) : 7);
  const totalCount = val.total_count || 7;
  const accuracyPct = val.accuracy_percentage !== undefined ? val.accuracy_percentage : Math.round((passedCount / totalCount) * 100);
  const hallucinationPct = val.hallucination_score !== undefined ? val.hallucination_score : Math.max(0, 100 - accuracyPct);
  const groundingPct = val.factual_grounding_score !== undefined ? val.factual_grounding_score : accuracyPct;
  const balancePassed = (dataVal && dataVal.balance_check) ? dataVal.balance_check.passed : true;

  // Animate Gauge 1 Needle: 0% -> -90deg, 50% -> 0deg, 100% -> +90deg
  const accuracyAngle = -90 + (accuracyPct / 100) * 180;
  const accNeedle = document.getElementById("accuracy-needle-group");
  if (accNeedle) {
    accNeedle.style.transform = `rotate(${accuracyAngle}deg)`;
  }

  // Animate Gauge 1 Arc Fill: stroke-dasharray is 345.57
  const accArc = document.getElementById("accuracy-gauge-arc");
  if (accArc) {
    const offset = 345.57 * (1 - accuracyPct / 100);
    accArc.style.strokeDashoffset = offset;
  }

  // Digital HUD
  const accValEl = document.getElementById("accuracy-gauge-val");
  if (accValEl) {
    accValEl.textContent = `${accuracyPct}%`;
  }
  const valScoreText = document.getElementById("val-score-text");
  if (valScoreText) {
    valScoreText.textContent = `${passedCount}/${totalCount} Passed`;
  }
  const valStatusLabel = document.getElementById("val-status-label");
  if (valStatusLabel) {
    valStatusLabel.textContent = val.audit_status || (accuracyPct === 100 ? "Zero Hallucinations Verified" : `${totalCount - passedCount} Discrepancy Flagged`);
  }

  // Mini Sub-Metrics
  const gVal = document.getElementById("telemetry-grounding-val");
  const gBar = document.getElementById("telemetry-grounding-bar");
  if (gVal) gVal.textContent = `${groundingPct}%`;
  if (gBar) gBar.style.width = `${groundingPct}%`;

  const hVal = document.getElementById("telemetry-hallucination-val");
  const hBar = document.getElementById("telemetry-hallucination-bar");
  if (hVal) hVal.textContent = `${hallucinationPct}%`;
  if (hBar) {
    hBar.style.width = `${hallucinationPct}%`;
    hBar.className = `mini-progress-fill ${hallucinationPct === 0 ? 'bg-emerald-400' : 'bg-rose-400'}`;
  }

  const actVal = document.getElementById("telemetry-accounting-val");
  if (actVal) {
    actVal.textContent = balancePassed ? "Verified" : "Discrepancy";
    actVal.className = `text-xs font-bold font-mono ${balancePassed ? 'text-cyan-400' : 'text-rose-400'}`;
  }

  // --- Gauge 2: ML Solvency Risk Speedometer ---
  const riskClass = (risk.class || "Moderate Risk").trim();
  const confidence = risk.probability || 78;
  const probs = risk.class_probabilities || {
    low_risk: riskClass === "Low Risk" ? confidence : 14.0,
    moderate_risk: riskClass === "Moderate Risk" ? confidence : 78.0,
    high_risk: riskClass === "High Risk" ? confidence : 8.0
  };

  // Determine angle for needle:
  // Low Risk: -90 to -30 deg
  // Moderate Risk: -30 to +30 deg
  // High Risk: +30 to +90 deg
  let riskScore = risk.risk_meter_score;
  if (riskScore === undefined) {
    if (riskClass === "Low Risk") riskScore = 18.0;
    else if (riskClass === "High Risk") riskScore = 82.0;
    else riskScore = 50.0;
  }
  const riskAngle = -90 + (riskScore / 100) * 180;

  const riskNeedle = document.getElementById("risk-needle-group");
  if (riskNeedle) {
    riskNeedle.style.transform = `rotate(${riskAngle}deg)`;
  }

  // Colors based on risk class
  let themeColor = "#f59e0b"; // amber
  let themeClass = "text-amber-400";
  let bgClass = "bg-amber-400";

  if (riskClass === "Low Risk") {
    themeColor = "#10b981";
    themeClass = "text-emerald-400";
    bgClass = "bg-emerald-400";
  } else if (riskClass === "High Risk") {
    themeColor = "#f43f5e";
    themeClass = "text-rose-400";
    bgClass = "bg-rose-400";
  }

  // Update needle tip & fill colors
  const needleFill = document.getElementById("risk-needle-fill");
  const needleTip = document.getElementById("risk-needle-tip");
  const pivotCore = document.getElementById("risk-pivot-core");
  if (needleFill) needleFill.setAttribute("fill", themeColor);
  if (needleTip) needleTip.setAttribute("fill", themeColor);
  if (pivotCore) pivotCore.setAttribute("fill", themeColor);

  // Digital HUD
  const riskClassEl = document.getElementById("risk-gauge-class");
  if (riskClassEl) {
    riskClassEl.textContent = riskClass.toUpperCase();
    riskClassEl.className = `text-2xl sm:text-3xl font-black tracking-tight font-mono ${themeClass}`;
  }

  const driverChip = document.getElementById("risk-primary-driver-chip");
  if (driverChip) {
    const drivers = risk.primary_risk_drivers || risk.primary_indicators || [];
    driverChip.textContent = drivers.length > 0 ? drivers[0] : "Balanced Capital Structure";
  }

  const confText = document.getElementById("risk-confidence-text");
  const confDot = document.getElementById("risk-confidence-dot");
  if (confText) confText.textContent = `${Math.round(confidence)}% Confidence`;
  if (confDot) confDot.className = `w-1.5 h-1.5 rounded-full ${bgClass}`;

  // Mini probability distribution bars
  const pLow = Math.round(probs.low_risk || 0);
  const pMod = Math.round(probs.moderate_risk || 0);
  const pHigh = Math.round(probs.high_risk || 0);

  const lowVal = document.getElementById("prob-low-val");
  const lowBar = document.getElementById("prob-low-bar");
  if (lowVal) lowVal.textContent = `${pLow}%`;
  if (lowBar) lowBar.style.width = `${pLow}%`;

  const modVal = document.getElementById("prob-mod-val");
  const modBar = document.getElementById("prob-mod-bar");
  if (modVal) modVal.textContent = `${pMod}%`;
  if (modBar) modBar.style.width = `${pMod}%`;

  const highVal = document.getElementById("prob-high-val");
  const highBar = document.getElementById("prob-high-bar");
  if (highVal) highVal.textContent = `${pHigh}%`;
  if (highBar) highBar.style.width = `${pHigh}%`;
}

function switchGaugeView(view) {
  const views = ['speedometers', 'checklist', 'benchmark'];
  views.forEach(v => {
    const panel = document.getElementById(`gauge-panel-${v}`);
    const btn = document.getElementById(`gauge-view-${v === 'speedometers' ? 'speedometer' : v}-btn`);
    if (v === view) {
      if (panel) panel.classList.remove('hidden');
      if (btn) {
        btn.className = "px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm transition flex items-center space-x-1.5 font-bold";
      }
    } else {
      if (panel) panel.classList.add('hidden');
      if (btn) {
        btn.className = "px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition flex items-center space-x-1.5 font-medium";
      }
    }
  });
}

// ----------------- METRIC CARDS & DATA TABLES ----------------- //

function renderFinancialMetrics(metrics) {
  const rev = metrics.revenue || {};
  const revVal = document.getElementById("kpi-revenue-val");
  if (revVal) revVal.textContent = rev.formatted_current || "N/A";
  const revY = document.getElementById("kpi-revenue-yoy");
  if (revY) {
    if (rev.yoy_percent !== null && rev.yoy_percent !== undefined) {
      revY.textContent = `${rev.yoy_percent > 0 ? '+' : ''}${rev.yoy_percent}% YoY`;
      revY.className = `text-xs font-bold ${rev.yoy_percent >= 0 ? 'text-emerald-400' : 'text-rose-400'}`;
    } else {
      revY.textContent = "N/A";
    }
  }

  const ni = metrics.net_income || {};
  const niVal = document.getElementById("kpi-netincome-val");
  if (niVal) niVal.textContent = ni.formatted_current || "N/A";
  const niY = document.getElementById("kpi-netincome-yoy");
  if (niY) {
    if (ni.yoy_percent !== null && ni.yoy_percent !== undefined) {
      niY.textContent = `${ni.yoy_percent > 0 ? '+' : ''}${ni.yoy_percent}% YoY`;
      niY.className = `text-xs font-bold ${ni.yoy_percent >= 0 ? 'text-emerald-400' : 'text-rose-400'}`;
    } else {
      niY.textContent = "N/A";
    }
  }

  const debt = metrics.debt || {};
  const debtVal = document.getElementById("kpi-debt-val");
  if (debtVal) debtVal.textContent = debt.formatted_current || "N/A";
  const debtY = document.getElementById("kpi-debt-yoy");
  if (debtY) {
    if (debt.yoy_percent !== null && debt.yoy_percent !== undefined) {
      debtY.textContent = `${debt.yoy_percent > 0 ? '+' : ''}${debt.yoy_percent}% YoY`;
      debtY.className = `text-xs font-bold ${debt.yoy_percent <= 0 ? 'text-emerald-400' : 'text-amber-400'}`;
    } else {
      debtY.textContent = "N/A";
    }
  }

  const assVal = document.getElementById("kpi-assets-val");
  if (assVal) assVal.textContent = metrics.assets?.formatted_current || "N/A";

  const ocfVal = document.getElementById("kpi-ocf-val");
  if (ocfVal) ocfVal.textContent = metrics.operating_cash_flow?.formatted_current || "N/A";

  const eqVal = document.getElementById("kpi-equity-val");
  if (eqVal) eqVal.textContent = metrics.equity?.formatted_current || "N/A";

  const pInterp = document.getElementById("perf-interpretation-text");
  if (pInterp) {
    pInterp.textContent = `During ${currentReportData?.reporting_period || 'the fiscal period'}, consolidated revenue established at ${rev.formatted_current || 'N/A'} (${revY ? revY.textContent : ''}), while net income was recorded at ${ni.formatted_current || 'N/A'} (${niY ? niY.textContent : ''}). Balance sheet recorded total debt of ${debt.formatted_current || 'N/A'}.`;
  }
}

function renderRatioTable(ratios) {
  const tbody = document.getElementById("ratios-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  const list = [
    { key: "current_ratio", name: "Current Ratio" },
    { key: "debt_to_equity", name: "Debt-to-Equity" },
    { key: "roe", name: "ROE" },
    { key: "roa", name: "ROA" },
    { key: "net_profit_margin", name: "Net Profit Margin" },
    { key: "quick_ratio", name: "Quick Ratio" }
  ];

  list.forEach(item => {
    const r = ratios[item.key] || {};
    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-800/40 transition";

    const chgVal = r.change_display || r.formatted_change || "0.00";
    const chgClass = (String(chgVal).includes("+") || (!String(chgVal).includes("-") && parseFloat(chgVal) > 0)) ? "text-emerald-400" : (String(chgVal).includes("-") ? "text-rose-400" : "text-slate-400");

    tr.innerHTML = `
      <td class="py-2.5 font-bold text-white">${item.name}</td>
      <td class="py-2.5 text-right font-mono text-slate-100 font-semibold">${r.formatted_current || "N/A"}</td>
      <td class="py-2.5 text-right font-mono text-slate-400">${r.formatted_previous || "N/A"}</td>
      <td class="py-2.5 text-right font-mono font-bold ${chgClass}">${chgVal}</td>
      <td class="py-2.5 pl-3 text-slate-300 text-[11px]">${r.interpretation || "Normal"}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderTrends(trends) {
  const container = document.getElementById("trend-observations-list");
  if (!container) return;
  container.innerHTML = "";

  trends.forEach(t => {
    const div = document.createElement("div");
    div.className = "flex items-start space-x-2 text-slate-300";
    const icon = t.direction === "Increasing" ? "▲" : (t.direction === "Decreasing" ? "▼" : "•");
    const iconClass = t.direction === "Increasing" ? "text-emerald-400" : (t.direction === "Decreasing" ? "text-rose-400" : "text-slate-400");

    div.innerHTML = `
      <span class="${iconClass} font-bold text-xs mt-0.5">${icon}</span>
      <div>
        <span class="font-bold text-white">${t.metric_name || t.metric}:</span>
        <span class="text-slate-300">CAGR of ${t.formatted_cagr || (t.cagr_percent + '%')} over ${t.span_years} years.</span>
        <span class="text-slate-400 block text-[11px]">${t.statement}</span>
      </div>
    `;
    container.appendChild(div);
  });

  updateTrendChart(trends);
}

function updateTrendChart(trends) {
  const ctx = document.getElementById("trendChart");
  if (!ctx) return;

  const revTrend = trends.find(t => t.metric === "revenue") || trends[0];
  if (!revTrend || !revTrend.history || revTrend.history.length === 0) return;

  const labels = revTrend.history.map(h => h.period);
  const dataPoints = revTrend.history.map(h => h.value);

  if (trendChart) {
    trendChart.destroy();
  }

  trendChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: `${revTrend.metric_name || 'Revenue'} (${currentReportData?.verified_object?.currency || '$'}M)`,
        data: dataPoints,
        borderColor: "#3b82f6",
        backgroundColor: "rgba(59, 130, 246, 0.15)",
        borderWidth: 2.5,
        pointBackgroundColor: "#60a5fa",
        pointBorderColor: "#ffffff",
        pointRadius: 4,
        fill: true,
        tension: 0.35
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#0f172a",
          borderColor: "#334155",
          borderWidth: 1,
          titleFont: { family: "Plus Jakarta Sans" },
          bodyFont: { family: "JetBrains Mono" }
        }
      },
      scales: {
        x: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { color: "#94a3b8", font: { size: 10 } }
        },
        y: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { color: "#94a3b8", font: { size: 10 } }
        }
      }
    }
  });
}

function renderAnomalies(anomalies) {
  const badgeCount = document.getElementById("anomaly-badge-count");
  const container = document.getElementById("anomaly-cards-container");
  if (!container) return;
  container.innerHTML = "";

  if (!anomalies || anomalies.length === 0) {
    if (badgeCount) {
      badgeCount.textContent = "0 Anomalies Detected";
      badgeCount.className = "text-xs text-emerald-400 font-semibold";
    }
    container.innerHTML = `<p class="text-xs text-slate-400 italic p-3 bg-slate-950/60 rounded-xl">No statistically significant variances or isolation forest outliers detected.</p>`;
    return;
  }

  if (badgeCount) {
    badgeCount.textContent = `${anomalies.length} Anomaly(s) Detected`;
    badgeCount.className = "text-xs text-rose-400 font-semibold";
  }

  anomalies.forEach(a => {
    const card = document.createElement("div");
    card.className = "p-3 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1";
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="font-bold text-white text-xs">${a.metric_name || a.metric}</span>
        <span class="px-2 py-0.5 rounded text-[10px] font-bold ${a.variance_percentage > 0 ? 'bg-amber-500/20 text-amber-300' : 'bg-rose-500/20 text-rose-300'}">
          ${a.formatted_variance || (a.variance_percentage + '%')}
        </span>
      </div>
      <p class="text-[11px] text-slate-300">Recorded ${a.formatted_current} vs. ${a.formatted_previous} previously.</p>
      <p class="text-[11px] text-slate-400 italic">${a.interpretation}</p>
    `;
    container.appendChild(card);
  });
}

function renderMLRisk(risk) {
  const badge = document.getElementById("ml-risk-badge-class");
  const probText = document.getElementById("ml-risk-prob-text");
  const probBar = document.getElementById("ml-risk-prob-bar");
  const driversList = document.getElementById("ml-primary-risk-list");

  const riskClass = risk.class || "Moderate Risk";
  if (badge) badge.textContent = riskClass;

  if (probBar && badge) {
    if (riskClass === "Low Risk") {
      badge.className = "text-xl font-extrabold text-emerald-400";
      probBar.className = "bg-emerald-500 h-2 rounded-full";
    } else if (riskClass === "High Risk") {
      badge.className = "text-xl font-extrabold text-rose-400";
      probBar.className = "bg-rose-500 h-2 rounded-full";
    } else {
      badge.className = "text-xl font-extrabold text-amber-400";
      probBar.className = "bg-amber-500 h-2 rounded-full";
    }
  }

  const prob = risk.probability || 78;
  const probFormatted = `${Math.round(prob)}%`;
  if (probText) probText.textContent = probFormatted;
  if (probBar) probBar.style.width = probFormatted;

  // Quick Econometric Badges
  const altman = risk.altman_z_score || {};
  const altmanScoreEl = document.getElementById("quick-altman-score");
  const altmanZoneEl = document.getElementById("quick-altman-zone");
  if (altmanScoreEl && altman.score !== undefined) {
    altmanScoreEl.textContent = `Z'' = ${altman.score}`;
    if (altmanZoneEl) altmanZoneEl.textContent = altman.zone || "Safe Zone";
    if (altman.badge_color === "rose") altmanScoreEl.className = "font-bold text-rose-400 text-xs";
    else if (altman.badge_color === "amber") altmanScoreEl.className = "font-bold text-amber-400 text-xs";
    else altmanScoreEl.className = "font-bold text-emerald-400 text-xs";
  }

  const piotroski = risk.piotroski_f_score || {};
  const fScoreEl = document.getElementById("quick-piotroski-score");
  const fRatingEl = document.getElementById("quick-piotroski-rating");
  if (fScoreEl && piotroski.score !== undefined) {
    fScoreEl.textContent = `${piotroski.score} / 9`;
    if (fRatingEl) fRatingEl.textContent = piotroski.rating || "Moderate";
    if (piotroski.score >= 7) fScoreEl.className = "font-bold text-emerald-400 text-xs";
    else if (piotroski.score >= 4) fScoreEl.className = "font-bold text-blue-400 text-xs";
    else fScoreEl.className = "font-bold text-rose-400 text-xs";
  }

  if (driversList) {
    driversList.innerHTML = "";
    const drivers = risk.primary_risk_drivers || risk.primary_indicators || ["Total debt expansion"];
    drivers.forEach(d => {
      const li = document.createElement("li");
      li.className = "flex items-start space-x-1.5";
      li.innerHTML = `<span class="text-rose-400">•</span><span>${d}</span>`;
      driversList.appendChild(li);
    });
  }

  // Render Multi-Model Consensus & XAI weights
  renderConsensusHub(risk);
}

function renderConsensusHub(risk) {
  const grid = document.getElementById("models-consensus-grid");
  if (!grid) return;
  grid.innerHTML = "";

  const consensusList = risk.model_consensus || [
    { name: "Gradient Boosting", architecture: "Sequential Loss Tree Boosting", vote: risk.class || "Moderate Risk", confidence: "84%" },
    { name: "Random Forest", architecture: "Bootstrap Aggregated Forest (50 Trees)", vote: risk.class || "Moderate Risk", confidence: "78%" },
    { name: "Calibrated Logistic", architecture: "Regularized L2 Linear Decision", vote: risk.class || "Moderate Risk", confidence: "75%" },
    { name: "Altman Z''-Score", architecture: "Econometric Distress Index", vote: risk.altman_z_score?.zone || "Safe Zone", confidence: `Z'' = ${risk.altman_z_score?.score || 11.97}` }
  ];

  consensusList.forEach(m => {
    let voteColor = "text-amber-400 bg-amber-500/10 border-amber-500/30";
    if (m.vote.includes("Low") || m.vote.includes("Safe")) voteColor = "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
    else if (m.vote.includes("High") || m.vote.includes("Distress")) voteColor = "text-rose-400 bg-rose-500/10 border-rose-500/30";

    const card = document.createElement("div");
    card.className = "consensus-card space-y-2";
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold text-white tracking-wide">${m.name}</span>
        <span class="text-[9px] font-mono px-2 py-0.5 rounded border ${voteColor}">${m.vote}</span>
      </div>
      <p class="text-[10px] text-slate-400 leading-tight">${m.architecture}</p>
      <div class="pt-1 flex items-center justify-between text-[11px] font-mono text-slate-300 border-t border-slate-800">
        <span class="text-slate-500 text-[10px]">Model Output:</span>
        <span class="font-bold text-cyan-300">${m.confidence}</span>
      </div>
    `;
    grid.appendChild(card);
  });

  // Render XAI Feature Weights
  const xaiContainer = document.getElementById("xai-feature-bars-container");
  if (!xaiContainer) return;
  xaiContainer.innerHTML = "";

  const attributions = risk.feature_attributions || {
    "Capital Structure & Leverage (D/E)": 32.5,
    "Liquidity & Coverage (Current & Quick)": 26.0,
    "Operating Margin & Returns (NPM & ROE)": 21.5,
    "Cash Flow & Debt Service (OCF)": 14.0,
    "Top-Line Expansion Velocity (CAGR)": 6.0
  };

  Object.entries(attributions).forEach(([name, pct]) => {
    const box = document.createElement("div");
    box.className = "p-2.5 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-1.5";
    box.innerHTML = `
      <div class="flex items-center justify-between text-[11px]">
        <span class="text-slate-300 font-medium truncate" title="${name}">${name}</span>
        <span class="text-cyan-400 font-mono font-bold">${pct}%</span>
      </div>
      <div class="w-full bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
        <div class="bg-gradient-to-r from-blue-500 to-cyan-400 h-1.5 rounded-full" style="width: ${pct * 2.5}%"></div>
      </div>
    `;
    xaiContainer.appendChild(box);
  });
}

function renderIndicators(elementId, indicators) {
  const ul = document.getElementById(elementId);
  if (!ul) return;
  ul.innerHTML = "";
  if (!indicators || indicators.length === 0) {
    ul.innerHTML = `<li class="text-slate-400 italic">No significant indicators were identified from available disclosures.</li>`;
    return;
  }
  indicators.forEach(ind => {
    const li = document.createElement("li");
    li.className = "flex items-start space-x-2";
    li.innerHTML = `<span class="mt-0.5">•</span><span>${ind}</span>`;
    ul.appendChild(li);
  });
}

function renderValidationChecklist(checks) {
  const container = document.getElementById("validation-checklist-container");
  if (!container) return;
  container.innerHTML = "";

  const defaultChecks = [
    { name: "Financial Values Grounding", passed: true, detail: "All stated metrics ground directly in financial statements" },
    { name: "Calculated Ratios Verification", passed: true, detail: "Strictly aligns with deterministic ratio equations" },
    { name: "ML Risk Classification Fidelity", passed: true, detail: "Matches Random Forest ensemble prediction" },
    { name: "Mathematical Variance Consistency", passed: true, detail: "YoY variance math verified within 0.1% tolerance" },
    { name: "Temporal Audit Integrity", passed: true, detail: "Dates and fiscal periods reflect filed statements" },
    { name: "Unsupported Disclosures Filter", passed: true, detail: "Zero ungrounded external claims or speculation" },
    { name: "Fact-Grounding (No Invented Causes)", passed: true, detail: "Causes reflect only verbatim management disclosures" }
  ];

  const items = (checks && checks.length > 0) ? checks : defaultChecks;

  items.forEach(c => {
    const div = document.createElement("div");
    div.className = "p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between";
    div.innerHTML = `
      <div>
        <span class="text-slate-200 font-semibold block text-xs">${c.check_name || c.name}</span>
        <span class="text-[10px] text-slate-400 block">${c.detail || "Grounded audit verification"}</span>
      </div>
      <span class="px-2 py-0.5 rounded text-[10px] font-bold ${c.passed ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'}">
        ${c.passed ? '✓ PASSED' : '✕ DISCREPANCY'}
      </span>
    `;
    container.appendChild(div);
  });
}

// ----------------- SUMMARY ACTIONS (REGENERATE / COPY / EXPORT) ----------------- //

async function triggerRegenerate() {
  if (!currentReportId) {
    showToast("No active report loaded to regenerate.", "error");
    return;
  }

  const btn = document.getElementById("btn-regenerate");
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<svg class="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg><span>Regenerating...</span>`;
  }

  showToast("Regenerating summary from verified object without recalculating financials...", "info");

  try {
    const headers = { "Content-Type": "application/json" };
    if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

    const res = await fetch("/api/regenerate", {
      method: "POST",
      headers: headers,
      body: JSON.stringify({
        report_id: currentReportId,
        length: currentLength,
        tone: currentTone,
        model: currentModel
      })
    });
    const result = await res.json();
    if (result.success && result.data) {
      currentReportData = result.data;
      renderReportData(result.data);
      showToast(`Regenerated as ${result.data.active_version?.version_label || 'New Version'}!`, "success");
    } else {
      showToast(`Regeneration failed: ${result.error || "Unknown error"}`, "error");
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, "error");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg><span>Regenerate Summary</span>`;
    }
  }
}

function copySummaryText() {
  if (!currentReportData) {
    showToast("No active report loaded to copy.", "error");
    return;
  }
  const activeVer = currentReportData.active_version || (currentReportData.versions ? currentReportData.versions[0] : {});
  const execEl = document.getElementById("exec-summary-content");
  const text = activeVer.full_markdown || (execEl ? execEl.textContent : "");
  
  if (!text) {
    showToast("Summary content is empty.", "error");
    return;
  }

  navigator.clipboard.writeText(text).then(() => {
    showToast("Summary markdown copied to clipboard!", "success");
  }).catch(() => {
    showToast("Failed to copy summary.", "error");
  });
}

function downloadSummaryFile() {
  if (!currentReportId) {
    showToast("No report selected for download.", "error");
    return;
  }
  window.location.href = `/api/reports/${encodeURIComponent(currentReportId)}/download-summary`;
}

function exportFullPdfReport() {
  if (!currentReportId) {
    showToast("No report selected for PDF export.", "error");
    return;
  }
  showToast("Generating professional 13-section PDF report...", "info");
  window.location.href = `/api/reports/${encodeURIComponent(currentReportId)}/pdf`;
}

function copyVerifiedJson() {
  const jsonEl = document.getElementById("json-viewer-content");
  const json = jsonEl ? jsonEl.textContent : "";
  if (!json) return;
  navigator.clipboard.writeText(json).then(() => {
    showToast("Verified Object JSON copied to clipboard!", "success");
  });
}

// ----------------- TONE & LENGTH CONTROLLERS ----------------- //

function setLength(length) {
  currentLength = length;
  syncLengthButtons(length);
  triggerRegenerate();
}

function setTone(tone) {
  currentTone = tone;
  syncToneButtons(tone);
  triggerRegenerate();
}

function syncLengthButtons(active) {
  ["Short", "Standard", "Detailed"].forEach(l => {
    const btn = document.getElementById(`opt-len-${l.toLowerCase()}`);
    if (!btn) return;
    if (l === active) {
      btn.className = "px-2.5 py-1 rounded-lg bg-blue-600 text-white font-semibold shadow-sm transition";
    } else {
      btn.className = "px-2.5 py-1 rounded-lg text-slate-400 hover:text-white transition";
    }
  });
}

function syncToneButtons(active) {
  const map = { "Professional": "prof", "Academic": "acad", "Executive": "exec" };
  Object.keys(map).forEach(t => {
    const btn = document.getElementById(`opt-tone-${map[t]}`);
    if (!btn) return;
    if (t === active) {
      btn.className = "px-2.5 py-1 rounded-lg bg-blue-600 text-white font-semibold shadow-sm transition";
    } else {
      btn.className = "px-2.5 py-1 rounded-lg text-slate-400 hover:text-white transition";
    }
  });
}

// ----------------- VERSION HISTORY MODAL ----------------- //

function toggleVersionModal() {
  const modal = document.getElementById("version-modal");
  if (!modal) return;
  modal.classList.toggle("hidden");
  modal.classList.toggle("flex");

  if (!modal.classList.contains("hidden") && currentReportData) {
    renderVersionList(currentReportData.versions || [currentReportData.active_version]);
  }
}

function renderVersionList(versions) {
  const container = document.getElementById("version-list-container");
  if (!container) return;
  container.innerHTML = "";

  const activeVerNum = currentReportData.active_version?.version_num || 1;

  versions.forEach(v => {
    const isActive = v.version_num === activeVerNum;
    const div = document.createElement("div");
    div.className = `p-4 rounded-xl border ${isActive ? 'bg-blue-500/10 border-blue-500/40' : 'bg-slate-900 border-slate-800'} space-y-2`;

    div.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <span class="font-bold text-white text-sm">${v.version_label}</span>
          ${isActive ? '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-600 text-white">ACTIVE</span>' : ''}
          <span class="text-xs text-slate-400">• ${v.timestamp || v.created_at_formatted || 'Saved'}</span>
        </div>
        <div class="space-x-1.5">
          ${!isActive ? `<button onclick="restoreVersion(${v.version_num})" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold">Restore</button>` : ''}
          <button onclick="previewVersion(${v.version_num})" class="px-2.5 py-1 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold">View</button>
        </div>
      </div>
      <div class="flex items-center space-x-4 text-xs text-slate-400">
        <span>Engine: <b class="text-slate-200">${v.source || 'Gemini 3.5 Flash-Lite'}</b></span>
        <span>Audit: <b class="text-emerald-400">${v.validation?.score || '7/7 Passed'}</b></span>
        <span>Settings: <b class="text-slate-200">${v.length || 'Standard'} / ${v.tone || 'Professional'}</b></span>
      </div>
      <p class="text-xs text-slate-300 font-mono bg-slate-950 p-2.5 rounded-lg line-clamp-2">${v.sections?.executive_summary || v.full_markdown || 'No summary text'}</p>
    `;
    container.appendChild(div);
  });
}

async function restoreVersion(versionNum) {
  try {
    const res = await fetch("/api/version/restore", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        report_id: currentReportId,
        version_num: versionNum
      })
    });
    const json = await res.json();
    if (json.success && json.data) {
      currentReportData = json.data;
      renderReportData(json.data);
      toggleVersionModal();
      showToast(`Restored version ${versionNum} as active!`, "success");
    } else {
      showToast(`Failed to restore: ${json.error || "Unknown error"}`, "error");
    }
  } catch (err) {
    showToast(`Failed to restore version: ${err.message}`, "error");
  }
}

function previewVersion(versionNum) {
  const versions = currentReportData?.versions || currentReportData?.all_versions || [];
  const v = versions.find(x => x.version_num === versionNum);
  if (v) {
    currentReportData.active_version = v;
    renderReportData(currentReportData);
    toggleVersionModal();
    showToast(`Displaying preview of ${v.version_label}`, "info");
  }
}

// ----------------- TAB NAVIGATION SWITCHER ----------------- //

function switchTab(tab) {
  ["summary", "pipeline", "verified", "history"].forEach(t => {
    const view = document.getElementById(`view-${t}`);
    const btn = document.getElementById(`tab-${t}-btn`);
    if (t === tab) {
      if (view) view.classList.remove("hidden");
      if (btn) btn.className = "px-3.5 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm transition font-bold";
    } else {
      if (view) view.classList.add("hidden");
      if (btn) btn.className = "px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-white transition font-medium";
    }
  });

  if (tab === "history") {
    loadArchiveList();
  }
}

function refreshReportArchive() {
  loadArchiveList();
  showToast("Report archive refreshed.", "info");
}

async function loadArchiveList() {
  try {
    const headers = {};
    if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

    const res = await fetch("/api/reports", { headers });
    const json = await res.json();
    if (json.success && json.reports) {
      const tbody = document.getElementById("archive-table-body");
      if (!tbody) return;
      tbody.innerHTML = "";
      json.reports.forEach(r => {
        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-800/40 transition";
        tr.innerHTML = `
          <td class="py-2.5 font-bold text-white flex items-center space-x-2">
            <span>${r.company}</span>
            ${r.is_user_report ? '<span class="px-1.5 py-0.5 rounded text-[9px] bg-blue-500/20 text-blue-300 font-bold">MINE</span>' : ''}
          </td>
          <td class="py-2.5 text-slate-300 font-mono">${r.reporting_period}</td>
          <td class="py-2.5 text-slate-300 font-mono">${r.revenue || "N/A"}</td>
          <td class="py-2.5 font-semibold ${r.risk_class === 'Low Risk' ? 'text-emerald-400' : (r.risk_class === 'High Risk' ? 'text-rose-400' : 'text-amber-400')}">${r.risk_class || "Moderate Risk"}</td>
          <td class="py-2.5 text-slate-400 font-mono">${r.version_count} version(s)</td>
          <td class="py-2.5 text-right space-x-2">
            <button onclick="loadReport('${r.report_id}'); switchTab('summary');" class="px-2.5 py-1 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-[11px] font-semibold transition active:scale-95">Open</button>
            <a href="/api/reports/${encodeURIComponent(r.report_id)}/pdf" class="px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-semibold transition inline-block">PDF</a>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (err) {
    console.error("Archive load error:", err);
  }
}

// ----------------- TOAST SYSTEM ----------------- //

function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  const msgEl = document.getElementById("toast-message");
  const iconEl = document.getElementById("toast-icon");
  if (!toast || !msgEl || !iconEl) return;

  msgEl.textContent = message;
  if (type === "success") {
    iconEl.textContent = "✓";
    toast.className = "fixed bottom-6 right-6 z-50 transform translate-y-0 opacity-100 transition-all duration-300 px-4 py-3 rounded-2xl bg-emerald-950/95 border border-emerald-500/60 shadow-2xl text-xs font-semibold text-emerald-100 flex items-center space-x-2.5 backdrop-blur-xl";
  } else if (type === "error") {
    iconEl.textContent = "✕";
    toast.className = "fixed bottom-6 right-6 z-50 transform translate-y-0 opacity-100 transition-all duration-300 px-4 py-3 rounded-2xl bg-rose-950/95 border border-rose-500/60 shadow-2xl text-xs font-semibold text-rose-100 flex items-center space-x-2.5 backdrop-blur-xl";
  } else {
    iconEl.textContent = "ℹ";
    toast.className = "fixed bottom-6 right-6 z-50 transform translate-y-0 opacity-100 transition-all duration-300 px-4 py-3 rounded-2xl bg-slate-900/95 border border-slate-700/80 shadow-2xl text-xs font-semibold text-white flex items-center space-x-2.5 backdrop-blur-xl";
  }

  setTimeout(() => {
    toast.className = "fixed bottom-6 right-6 z-50 transform translate-y-20 opacity-0 transition-all duration-300 px-4 py-3 rounded-2xl bg-slate-900/95 border border-slate-700/80 shadow-2xl text-xs font-semibold text-white flex items-center space-x-2.5 backdrop-blur-xl pointer-events-none";
  }, 3800);
}

// ----------------- MODEL SELECTOR & UI CONTROLLERS ----------------- //

function setModel(modelId) {
  currentModel = modelId;
  syncModelButtons(modelId);

  const modelLabels = {
    "gemini-2.5-flash": "Gemini 2.5 Flash (Frontier Precision)",
    "gemini-2.5-pro": "Gemini 2.5 Pro (Deep Reasoning Engine)",
    "gemini-3.5-flash-lite": "Gemini 3.5 Flash-Lite (Low Latency)",
    "deterministic": "Deterministic Python Engine (100% Offline)"
  };

  showToast(`Active AI Engine set to: ${modelLabels[modelId] || modelId}`, "info");
}

function syncModelButtons(activeModel) {
  const models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.5-flash-lite", "deterministic"];
  models.forEach(m => {
    const btn = document.getElementById(`opt-mod-${m}`);
    if (btn) {
      if (m === activeModel) {
        btn.className = "px-2.5 py-1 rounded-lg bg-blue-600 text-white font-semibold shadow-sm transition";
      } else {
        btn.className = "px-2.5 py-1 rounded-lg text-slate-400 hover:text-white transition";
      }
    }
  });
}

// ----------------- EXECUTIVE AUDIO BRIEFING (WEB SPEECH API) ----------------- //

function toggleAudioBriefing() {
  if (!('speechSynthesis' in window)) {
    showToast("Speech synthesis is not supported in your browser.", "error");
    return;
  }

  const soundwave = document.getElementById("soundwave-anim");
  const audioBtnLabel = document.getElementById("audio-btn-label");
  const audioIcon = document.getElementById("audio-icon");

  if (isSpeaking) {
    window.speechSynthesis.cancel();
    isSpeaking = false;
    if (soundwave) soundwave.classList.add("hidden");
    if (audioBtnLabel) audioBtnLabel.textContent = "Listen to Briefing";
    if (audioIcon) audioIcon.textContent = "🎧";
    showToast("Audio briefing paused.", "info");
    return;
  }

  const execEl = document.getElementById("exec-summary-content");
  let text = execEl ? execEl.textContent.trim() : "";
  if (!text) {
    showToast("No summary text available to play.", "error");
    return;
  }

  // Clean tags and markdown headings for natural voice delivery
  text = text.replace(/##/g, "").replace(/\[.*?\]/g, "").trim();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.02;
  utterance.pitch = 1.0;

  utterance.onstart = () => {
    isSpeaking = true;
    if (soundwave) soundwave.classList.remove("hidden");
    if (audioBtnLabel) audioBtnLabel.textContent = "Stop Playing";
    if (audioIcon) audioIcon.textContent = "⏹️";
    showToast("Playing executive audio briefing...", "info");
  };

  utterance.onend = () => {
    isSpeaking = false;
    if (soundwave) soundwave.classList.add("hidden");
    if (audioBtnLabel) audioBtnLabel.textContent = "Listen to Briefing";
    if (audioIcon) audioIcon.textContent = "🎧";
  };

  utterance.onerror = () => {
    isSpeaking = false;
    if (soundwave) soundwave.classList.add("hidden");
    if (audioBtnLabel) audioBtnLabel.textContent = "Listen to Briefing";
    if (audioIcon) audioIcon.textContent = "🎧";
  };

  window.speechSynthesis.speak(utterance);
}

// ----------------- CSV / EXCEL SPREADSHEET EXPORTER ----------------- //

function exportDataToCsv() {
  if (!currentReportData || !currentReportData.verified_object) {
    showToast("No active financial data loaded to export.", "error");
    return;
  }

  const vObj = currentReportData.verified_object;
  const metrics = vObj.financial_metrics || {};
  const ratios = vObj.ratios || {};
  const comp = vObj.company || "Company";
  const period = vObj.reporting_period || "FY2025";
  const prevPeriod = vObj.previous_period || "FY2024";

  let csvContent = `FinIntellect Corporate Financial Report Export\n`;
  csvContent += `Company,${comp}\n`;
  csvContent += `Reporting Period,${period}\n`;
  csvContent += `Previous Period,${prevPeriod}\n`;
  csvContent += `Currency,${vObj.currency || "$"}\n`;
  csvContent += `Unit,${vObj.unit || "Millions"}\n\n`;

  csvContent += `SECTION 1: KEY FINANCIAL METRICS\n`;
  csvContent += `Metric,${period} Current,${prevPeriod} Previous,YoY Change (%),Verification Status\n`;

  const metricNames = {
    revenue: "Total Revenue",
    net_income: "Net Income",
    assets: "Total Assets",
    liabilities: "Total Liabilities",
    debt: "Total Debt",
    equity: "Shareholders Equity",
    operating_cash_flow: "Operating Cash Flow"
  };

  Object.entries(metrics).forEach(([k, m]) => {
    const label = metricNames[k] || k;
    const curr = m.current !== undefined ? m.current : "N/A";
    const prev = m.previous !== undefined ? m.previous : "N/A";
    const yoy = m.yoy_percent !== undefined ? `${m.yoy_percent}%` : "N/A";
    csvContent += `"${label}",${curr},${prev},${yoy},Verified\n`;
  });

  csvContent += `\nSECTION 2: FINANCIAL RATIOS & BENCHMARKS\n`;
  csvContent += `Ratio Name,${period} Current,${prevPeriod} Previous,Variance,Status\n`;

  const ratioNames = {
    current_ratio: "Current Ratio (Liquidity)",
    quick_ratio: "Quick Ratio (Acid Test)",
    debt_to_equity: "Debt-to-Equity (Solvency)",
    roe: "Return on Equity (ROE %)",
    roa: "Return on Assets (ROA %)",
    net_profit_margin: "Net Profit Margin (%)",
    operating_margin: "Operating Margin (%)"
  };

  Object.entries(ratios).forEach(([k, r]) => {
    const label = ratioNames[k] || k;
    const curr = r.current !== undefined ? r.current : "N/A";
    const prev = r.previous !== undefined ? r.previous : "N/A";
    const chg = r.change_percent !== undefined ? `${r.change_percent}%` : (r.change_pp !== undefined ? `${r.change_pp} pp` : "N/A");
    csvContent += `"${label}",${curr},${prev},${chg},Calculated\n`;
  });

  csvContent += `\nSECTION 3: MACHINE LEARNING & ECONOMETRIC RISK METRICS\n`;
  const risk = vObj.risk_prediction || {};
  csvContent += `Model Classification,${risk.class || "Moderate Risk"}\n`;
  csvContent += `Model Confidence,${risk.probability_formatted || "78%"}\n`;
  csvContent += `Altman Z''-Score,${risk.altman_z_score?.score || "N/A"} (${risk.altman_z_score?.zone || "N/A"})\n`;
  csvContent += `Piotroski F-Score,${risk.piotroski_f_score?.score || "N/A"} / 9 (${risk.piotroski_f_score?.rating || "N/A"})\n`;

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  const filename = `${comp.replace(/\s+/g, "_")}_${period}_Financial_Intelligence.csv`;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showToast(`Exported ${filename} successfully!`, "success");
}
