/* ==========================================================================
   智配芯生 · ImpedanceMCP — application logic
   ========================================================================== */

(function () {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const STATE = {
    view: "agent",
    topology: "auto",
    design: null,
    config: null,
    status: null,
    chat: [],
    attachments: [],
    streaming: false,
    scan: null,
    models: [],
    lastAssistant: null,
  };

  const MCP_TOOLS = [
    ["design_matching_network", "设计匹配网络", "拓扑/频率/负载 → 元件值"],
    ["scan_matching_range", "扫描匹配范围", "正向覆盖区域"],
    ["evaluate_network", "复核网络性能", "节点法 Zin/VSWR"],
    ["convert_impedance_admittance", "阻抗导纳换算", "Z ↔ Y"],
    ["compute_voltage_stress", "计算元件耐压", "峰值 V/I"],
    ["analyze_bandwidth", "分析带宽", "VSWR 扫频"],
    ["compare_topologies", "比较拓扑方案", "五种拓扑排序"],
    ["get_topology_guide", "查询拓扑原理", "公式与适用条件"],
    ["get_smith_trajectory", "生成圆图轨迹", "Γ 采样点"],
    ["search_knowledge", "检索知识库", "本地微波知识"],
    ["validate_design", "工程校验", "风险清单"],
    ["export_design_report", "导出设计报告", "HTML / MD"],
    ["launch_classic_app", "启动原版软件", "Impedance_Matching.exe"],
    ["get_system_status", "检查系统状态", "MATLAB / LLM"],
    ["list_presets", "读取演示预设", "常用频段"],
  ];

  const VIEW_META = {
    agent: ["AI 智能体", "用自然语言驱动微波阻抗匹配计算、仿真与工程决策"],
    design: ["匹配设计", "五种拓扑 · 解析求解 · 完整网络节点法复核"],
    analysis: ["圆图分析", "正向扫描可匹配范围，比较拓扑与带宽"],
    stress: ["耐压分析", "峰值电压、RMS 电流与安全系数"],
    about: ["关于与团队", "智配芯生 · ImpedanceMCP v4.0.0"],
  };

  const TOPO_DESC = {
    auto: "自动比较五种拓扑，优先选择元件更少、可实现性更好的方案。",
    l_right: "L型（右）：源端并联 C1 + 串联 L/C2，适合 R_L < 50Ω 的低阻负载。",
    l_left: "L型（左）：串联 L/C2 + 负载端并联 C1，适合 R_L > 50Ω 的高阻负载。",
    t: "T型：源—串 C3—节点（并 L+C2）—串 C1—负载，三元件可调节带宽。",
    pi1: "π型Ⅰ：源端并 C3—串 L+C2—负载端并 C1，C-L-C 结构。",
    pi2: "π型Ⅱ：源端并 C1—串 L+C2—负载端并 C3，适合低阻负载。",
  };
  const TOPO_SHORT = { auto: "自动", l_right: "L·右", l_left: "L·左", t: "T", pi1: "πⅠ", pi2: "πⅡ" };
  const TOPO_HAS_C3 = { t: true, pi1: true, pi2: true };

  /* ------------------------------------------------------------------ */
  /* Utilities                                                          */
  /* ------------------------------------------------------------------ */
  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function fmt(x, digits = 3) {
    if (x === null || x === undefined || Number.isNaN(Number(x))) return "—";
    if (!isFinite(Number(x))) return "∞";
    const n = Number(x);
    if (Math.abs(n) >= 1000) return n.toFixed(0);
    if (Math.abs(n) > 0 && Math.abs(n) < 0.001) return n.toExponential(2);
    return n.toFixed(digits).replace(/\.?0+$/, "");
  }

  function fmtFixed(x, digits = 3) {
    if (x === null || x === undefined || Number.isNaN(Number(x))) return "—";
    if (!isFinite(Number(x))) return "∞";
    return Number(x).toFixed(digits);
  }

  function fmtS11(v) {
    const n = Number(v);
    if (!isFinite(n)) return "—";
    return n <= -60 ? "&lt; −60 dB" : `${n.toFixed(2)} dB`;
  }

  function fmtRL(v) {
    const n = Number(v);
    if (!isFinite(n)) return "—";
    return n >= 60 ? "&gt; 60 dB（理想）" : `${n.toFixed(2)} dB`;
  }

  function fmtComp(comps, key) {
    if (!comps) return "—";
    if (key === "L") {
      const uh = Number(comps.L_uH);
      if (!isFinite(uh)) return "—";
      if (uh < 1) return `${fmt(uh * 1000, 3)} nH`;
      return `${fmt(uh, 3)} µH`;
    }
    if (key === "C1") return `${fmt(comps.C1_pF, 4)} pF`;
    if (key === "C2") return `${fmt(comps.C2_pF, 4)} pF`;
    if (key === "C3") return Number(comps.C3_pF) > 0 ? `${fmt(comps.C3_pF, 4)} pF` : "—";
    return "—";
  }

  function vswrClass(v) {
    if (!isFinite(v)) return "bad";
    if (v <= 1.5) return "good";
    if (v <= 2) return "warn";
    return "bad";
  }

  function toast(title, message = "", type = "ok", ms = 3600) {
    const wrap = $("#toastWrap");
    const el = document.createElement("div");
    el.className = `toast ${type}`;
    el.innerHTML = `<b>${escapeHtml(title)}</b>${message ? escapeHtml(message) : ""}`;
    wrap.appendChild(el);
    setTimeout(() => {
      el.style.opacity = "0";
      el.style.transform = "translateY(6px)";
      el.style.transition = ".25s";
      setTimeout(() => el.remove(), 300);
    }, ms);
  }

  async function api(path, options = {}) {
    const opts = Object.assign({ headers: { "Content-Type": "application/json" } }, options);
    if (opts.body && typeof opts.body !== "string") opts.body = JSON.stringify(opts.body);
    const res = await fetch(path, opts);
    let data = {};
    try { data = await res.json(); } catch (e) { data = {}; }
    if (!res.ok || data.ok === false) {
      const err = new Error(data.message || data.error_message || `请求失败（HTTP ${res.status}）`);
      err.data = data;
      throw err;
    }
    return data;
  }

  function downloadUrl(url) {
    window.open(url, "_blank", "noopener");
  }

  async function copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
      toast("已复制", "MCP 配置已复制到剪贴板。", "ok");
    } catch (e) {
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); toast("已复制", "MCP 配置已复制到剪贴板。", "ok"); }
      catch (err) { toast("复制失败", "请手动选择文本复制。", "err"); }
      ta.remove();
    }
  }

  /* ------------------------------------------------------------------ */
  /* Markdown renderer                                                  */
  /* ------------------------------------------------------------------ */
  function inlineMd(text) {
    let s = escapeHtml(text);
    s = s.replace(/`([^`]+)`/g, (m, c) => `<code>${c}</code>`);
    s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    s = s.replace(/\*([^*]+)\*/g, "<em>$1</em>");
    s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
      '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
    return s;
  }

  function renderMarkdown(src) {
    if (!src) return "";
    const codeBlocks = [];
    let text = String(src).replace(/```([a-zA-Z0-9_+-]*)\n?([\s\S]*?)```/g, (m, lang, code) => {
      codeBlocks.push(`<pre><code>${escapeHtml(code.replace(/\n$/, ""))}</code></pre>`);
      return `@@CODEBLOCK${codeBlocks.length - 1}@@`;
    });
    const lines = text.split(/\r?\n/);
    const out = [];
    let para = [];
    let list = null;
    let table = null;

    const flushPara = () => {
      if (para.length) {
        out.push(`<p>${para.map(inlineMd).join("<br>")}</p>`);
        para = [];
      }
    };
    const flushList = () => {
      if (list) {
        out.push(`<${list.type}>${list.items.map((x) => `<li>${inlineMd(x)}</li>`).join("")}</${list.type}>`);
        list = null;
      }
    };
    const flushTable = () => {
      if (table) {
        const rows = table.rows.filter((r) => !r.separator);
        if (rows.length) {
          const head = rows[0];
          const body = rows.slice(1);
          out.push("<table><thead><tr>" + head.cells.map((c) => `<th>${inlineMd(c)}</th>`).join("") +
            "</tr></thead><tbody>" + body.map((r) => "<tr>" + r.cells.map((c) => `<td>${inlineMd(c)}</td>`).join("") + "</tr>").join("") +
            "</tbody></table>");
        }
        table = null;
      }
    };

    for (const rawLine of lines) {
      const line = rawLine.replace(/\s+$/, "");
      if (/^\s*\|.*\|\s*$/.test(line)) {
        flushPara(); flushList();
        const cells = line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());
        const separator = cells.every((c) => /^:?-{2,}:?$/.test(c));
        if (!table) table = { rows: [] };
        table.rows.push({ cells, separator });
        continue;
      }
      if (table) flushTable();
      if (!line.trim()) { flushPara(); flushList(); continue; }
      if (/^#{1,4}\s+/.test(line)) {
        flushPara(); flushList();
        const level = Math.min(4, (line.match(/^#+/) || ["#"])[0].length);
        out.push(`<h${level}>${inlineMd(line.replace(/^#+\s+/, ""))}</h${level}>`);
        continue;
      }
      if (/^>\s?/.test(line)) {
        flushPara(); flushList();
        out.push(`<blockquote>${inlineMd(line.replace(/^>\s?/, ""))}</blockquote>`);
        continue;
      }
      const ul = line.match(/^\s*[-*+]\s+(.*)$/);
      if (ul) {
        flushPara();
        if (!list || list.type !== "ul") { flushList(); list = { type: "ul", items: [] }; }
        list.items.push(ul[1]);
        continue;
      }
      const ol = line.match(/^\s*\d+[.)]\s+(.*)$/);
      if (ol) {
        flushPara();
        if (!list || list.type !== "ol") { flushList(); list = { type: "ol", items: [] }; }
        list.items.push(ol[1]);
        continue;
      }
      if (/^\s*([-*_])\1{2,}\s*$/.test(line)) {
        flushPara(); flushList(); out.push("<hr>"); continue;
      }
      flushList();
      para.push(line);
    }
    flushPara(); flushList(); flushTable();
    let html = out.join("");
    html = html.replace(/@@CODEBLOCK(\d+)@@/g, (m, i) => codeBlocks[Number(i)] || "");
    return html;
  }

  /* ------------------------------------------------------------------ */
  /* Navigation                                                         */
  /* ------------------------------------------------------------------ */
  function showView(name) {
    if (!VIEW_META[name]) name = "agent";
    STATE.view = name;
    $$(".nav-item").forEach((b) => b.classList.toggle("active", b.dataset.view === name));
    $$(".view").forEach((v) => v.classList.toggle("active", v.id === `view-${name}`));
    const [title, sub] = VIEW_META[name];
    $("#viewTitle").textContent = title;
    $("#viewSubtitle").textContent = sub;
    if (location.hash !== `#${name}`) history.replaceState(null, "", `#${name}`);
    if (name === "design" && !STATE.design) $("#emptyDesign").classList.remove("hidden");
    if (name === "about") refreshMcpCode();
    if (name === "design" && STATE.design) setTimeout(redrawDesignCharts, 50);
    if (name === "stress" && STATE.lastStress) setTimeout(() => renderStress(STATE.lastStress), 50);
  }

  function redrawDesignCharts() {
    if (lastBW) ChartKit.drawLineChart($("#bwCanvas"), Object.assign({ mark_mhz: STATE.design ? STATE.design.frequency_mhz : null }, lastBW));
    if (lastSens) drawSensitivity(lastSens);
  }

  function initNav() {
    $$(".nav-item").forEach((btn) => btn.addEventListener("click", () => showView(btn.dataset.view)));
    const hash = (location.hash || "").replace("#", "");
    if (VIEW_META[hash]) showView(hash);
    window.addEventListener("hashchange", () => {
      const h = (location.hash || "").replace("#", "");
      if (VIEW_META[h] && h !== STATE.view) showView(h);
    });
  }

  /* ------------------------------------------------------------------ */
  /* Status / settings                                                  */
  /* ------------------------------------------------------------------ */
  async function loadStatus() {
    try {
      const s = await api("/api/status");
      STATE.status = s;
      const llmOk = s.llm && s.llm.configured;
      $("#llmStatus").innerHTML = `<i class="dot ${llmOk ? "ok" : "warn"}"></i><span>${llmOk ? escapeHtml(s.llm.model || "DeepSeek") : "模型未配置"}</span>`;
      $("#llmStatus").title = llmOk ? `${s.llm.base_url} · ${s.llm.model}` : "点击设置填写 API Key";
      const mat = s.matlab || {};
      const matOk = !!mat.matlab_path;
      $("#matlabStatus").innerHTML = `<i class="dot ${matOk ? "ok" : ""}"></i><span>${matOk ? escapeHtml(mat.matlab_version || "MATLAB") : "MATLAB 未安装"}</span>`;
      $("#matlabStatus").title = mat.matlab_path || "未检测到 MATLAB";
      $("#mcpStatus").innerHTML = `<i class="dot ok"></i><span>MCP 就绪</span>`;
      $("#mcpStateText").textContent = "stdio · 15 个工具";
      const eng = $("#engineStatus");
      if (eng) {
        eng.innerHTML =
          `<b>Python 内核</b>：内置，已通过 300 组随机用例与 MATLAB 5/5 交叉验证<br>` +
          `<b>MATLAB</b>：${mat.matlab_path ? escapeHtml(mat.matlab_version || mat.matlab_path) : "未检测到"}<br>` +
          `<b>原版 exe</b>：${mat.classic_app_available ? "已找到 Impedance_Matching.exe" : "未找到"}<br>` +
          `<b>MATLAB Runtime</b>：${mat.mcr_installed ? "已安装" : "未检测到（安装包 MyAppInstaller_mcr.exe 已内置）"}`;
      }
      $("#modelSelect").innerHTML = `<option>${escapeHtml((s.llm && s.llm.model) || "deepseek-chat")}</option>`;
    } catch (e) {
      $("#llmStatus").innerHTML = `<i class="dot err"></i><span>服务未连接</span>`;
      $("#matlabStatus").innerHTML = `<i class="dot err"></i><span>状态未知</span>`;
      toast("无法连接本地服务", e.message, "err");
    }
  }

  async function loadConfig() {
    try {
      const r = await api("/api/config");
      STATE.config = r.config;
      fillSettings(r.config);
    } catch (e) { /* ignore */ }
  }

  function fillSettings(cfg) {
    if (!cfg) return;
    const llm = cfg.llm || {};
    $("#setBaseUrl").value = llm.base_url || "";
    $("#setApiKey").value = "";
    $("#setModelCustom").value = "";
    $("#setApiKey").placeholder = llm.has_key ? `已配置 ${llm.key_hint || ""}（留空不修改）` : "sk-…";
    $("#setTemp").value = llm.temperature != null ? llm.temperature : 0.25;
    $("#setMaxTokens").value = llm.max_tokens || 2600;
    const provider = llm.provider || (String(llm.base_url || "").includes("sjtu") ? "sjtu" : "deepseek");
    $("#setProvider").value = provider;
    populateModels(provider, llm.model);
    const eng = cfg.engine || "python";
    $$('input[name="engine"]').forEach((r) => { r.checked = r.value === eng; });
    const mat = (STATE.status && STATE.status.matlab) || {};
    $("#engineStatus").innerHTML =
      `<b>Python 内核</b>：内置，已通过 300 组随机用例与 MATLAB 5/5 交叉验证<br>` +
      `<b>MATLAB</b>：${mat.matlab_path ? escapeHtml(mat.matlab_version || mat.matlab_path) : "未检测到"}<br>` +
      `<b>原版 exe</b>：${mat.classic_app_available ? "已找到 Impedance_Matching.exe" : "未找到"}<br>` +
      `<b>MATLAB Runtime</b>：${mat.mcr_installed ? "已安装" : "未检测到（安装包 MyAppInstaller_mcr.exe 已内置）"}`;
  }

  function populateModels(provider, current) {
    const presets = {
      sjtu: ["deepseek-chat", "deepseek-reasoner", "qwen", "qwen3.8-27b"],
      deepseek: ["deepseek-chat", "deepseek-reasoner"],
      custom: STATE.models.length ? STATE.models : ["deepseek-chat"],
    };
    const list = presets[provider] || presets.custom;
    if (current && !list.includes(current)) list.unshift(current);
    $("#setModel").innerHTML = list.map((m) => `<option value="${escapeHtml(m)}">${escapeHtml(m)}</option>`).join("");
    $("#setModel").value = current || list[0];
    if (STATE.models.length) {
      $("#modelSelect").innerHTML = STATE.models.map((m) => `<option>${escapeHtml(m)}</option>`).join("");
      if (current) $("#modelSelect").value = current;
    }
  }

  async function loadModels() {
    try {
      const r = await api("/api/models", { method: "POST", body: {} });
      if (r.models && r.models.length) {
        STATE.models = r.models;
        populateModels($("#setProvider").value, $("#setModel").value);
      }
    } catch (e) { /* key may be absent */ }
  }

  function openSettings() {
    $("#settingsModal").classList.remove("hidden");
    loadConfig().then(() => { loadModels(); });
    loadMcpCode();
  }

  function closeSettings() {
    $("#settingsModal").classList.add("hidden");
    $("#saveHint").textContent = "";
  }

  async function saveSettings() {
    const provider = $("#setProvider").value;
    const llm = {
      provider,
      base_url: $("#setBaseUrl").value.trim(),
      model: ($("#setModelCustom").value.trim() || $("#setModel").value),
      temperature: Number($("#setTemp").value),
      max_tokens: Number($("#setMaxTokens").value),
    };
    const key = $("#setApiKey").value.trim();
    if (key) llm.api_key = key;
    const engine = ($$('input[name="engine"]').find((r) => r.checked) || {}).value || "python";
    try {
      const r = await api("/api/config", { method: "POST", body: { llm, engine } });
      STATE.config = r.config;
      $("#setApiKey").value = "";
      $("#saveHint").textContent = "已保存";
      toast("设置已保存", "模型服务与计算引擎配置已更新。", "ok");
      await loadStatus();
      if (key) loadModels();
    } catch (e) {
      toast("保存失败", e.message + (e.data && e.data.hint ? ` ${e.data.hint}` : ""), "err", 6000);
    }
  }

  async function testLlm() {
    const out = $("#llmTestResult");
    out.className = "inline-status";
    out.textContent = "测试中…";
    const llm = {
      provider: $("#setProvider").value,
      base_url: $("#setBaseUrl").value.trim(),
      model: ($("#setModelCustom").value.trim() || $("#setModel").value),
      temperature: Number($("#setTemp").value),
      max_tokens: Number($("#setMaxTokens").value),
    };
    const key = $("#setApiKey").value.trim();
    if (key) llm.api_key = key;
    try {
      const r = await api("/api/config/test", { method: "POST", body: { llm } });
      out.className = "inline-status ok";
      out.textContent = `连接成功 · ${r.model} · ${r.latency_s}s`;
      toast("模型连接成功", `${r.model}，延迟 ${r.latency_s}s。`, "ok");
    } catch (e) {
      out.className = "inline-status err";
      out.textContent = e.message + (e.data && e.data.hint ? `（${e.data.hint}）` : "");
    }
  }

  async function loadMcpCode() {
    try {
      const r = await api("/api/mcp/config");
      const snippet = r.snippet || "{}";
      $("#settingsMcpCode").textContent = snippet;
      $("#aboutMcpCode").textContent = snippet;
      return snippet;
    } catch (e) {
      return "{}";
    }
  }

  async function refreshMcpCode() {
    const snippet = await loadMcpCode();
    if (STATE.view === "about") $("#aboutMcpCode").textContent = snippet;
  }

  async function copyMcpConfig() {
    try {
      const r = await api("/api/mcp/config");
      await copyText(r.snippet || JSON.stringify(r.servers || {}, null, 2));
    } catch (e) { toast("复制失败", e.message, "err"); }
  }

  /* ------------------------------------------------------------------ */
  /* Agent chat                                                         */
  /* ------------------------------------------------------------------ */
  let chatAutoScroll = true;

  function initChat() {
    const input = $("#chatInput");
    input.addEventListener("input", () => {
      input.style.height = "auto";
      input.style.height = Math.min(180, input.scrollHeight) + "px";
    });
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendChat();
      }
    });
    $("#btnSend").addEventListener("click", sendChat);
    $("#btnAttach").addEventListener("click", () => $("#fileInput").click());
    $("#fileInput").addEventListener("change", handleFiles);
    $("#chatScroll").addEventListener("scroll", () => {
      const el = $("#chatScroll");
      chatAutoScroll = el.scrollHeight - el.scrollTop - el.clientHeight < 90;
    });
    $$("#suggestGrid .suggest").forEach((b) => b.addEventListener("click", () => {
      $("#chatInput").value = b.dataset.prompt || "";
      $("#chatInput").focus();
      sendChat();
    }));
    $("#btnCopyMcp").addEventListener("click", copyMcpConfig);
    $("#btnCopyMcpSide").addEventListener("click", copyMcpConfig);
    $("#btnCopyMcpAbout").addEventListener("click", copyMcpConfig);
    $("#btnCopyMcpSettings").addEventListener("click", copyMcpConfig);
    initToolList();
  }

  function initToolList() {
    const list = $("#toolList");
    list.innerHTML = MCP_TOOLS.map(([name, label, desc]) =>
      `<div class="tool-row"><span class="tiny-dot"></span><code>${escapeHtml(name)}</code><span>${escapeHtml(desc)}</span></div>`
    ).join("");
  }

  function scrollChat() {
    if (!chatAutoScroll) return;
    const el = $("#chatScroll");
    el.scrollTop = el.scrollHeight;
  }

  function addUserMessage(text, attachments) {
    const wrap = document.createElement("div");
    wrap.className = "msg msg-user";
    const files = (attachments || []).map((a) =>
      `<span class="attachment-chip">${escapeHtml(a.name || "附件")} · ${escapeHtml(a.kind || "")}</span>`).join("");
    wrap.innerHTML = `<div class="avatar">我</div><div class="msg-body"><div class="bubble">${escapeHtml(text).replace(/\n/g, "<br>")}${files ? `<div style="margin-top:6px">${files}</div>` : ""}</div></div>`;
    $("#messages").appendChild(wrap);
    scrollChat();
  }

  function addAssistantShell() {
    const wrap = document.createElement("div");
    wrap.className = "msg msg-assistant";
    wrap.innerHTML = `<div class="avatar"><svg><use href="#i-logo"/></svg></div><div class="msg-body"><div class="md"></div><div class="typing"><i></i><i></i><i></i></div></div>`;
    $("#messages").appendChild(wrap);
    scrollChat();
    return {
      wrap,
      body: $(".msg-body", wrap),
      md: $(".md", wrap),
      typing: $(".typing", wrap),
      buffer: "",
      lastRender: 0,
    };
  }

  function pushToken(assistant, text) {
    assistant.buffer += text;
    const now = performance.now();
    if (now - assistant.lastRender > 55) {
      assistant.md.innerHTML = renderMarkdown(assistant.buffer);
      assistant.lastRender = now;
      scrollChat();
    }
  }

  function finishAssistant(assistant, content) {
    if (assistant.typing) assistant.typing.remove();
    assistant.md.innerHTML = renderMarkdown(content || assistant.buffer || "");
    scrollChat();
  }

  function addToolCard(assistant, ev) {
    const card = document.createElement("div");
    card.className = "tool-card";
    card.dataset.callId = ev.id;
    card.innerHTML = `
      <div class="tool-card-head">
        <div class="tool-icon"><svg><use href="#i-settings"/></svg></div>
        <div><b>${escapeHtml(ev.label || ev.name)}</b><small>${escapeHtml(ev.name)}</small></div>
        <span class="spacer"></span>
        <span class="tool-state">运行中</span>
      </div>
      <div class="tool-card-body"><span class="tool-summary">正在调用本地引擎…</span></div>`;
    assistant.body.appendChild(card);
    scrollChat();
    return card;
  }

  function updateToolCard(assistant, ev) {
    const card = assistant.body.querySelector(`.tool-card[data-call-id="${CSS.escape(String(ev.id))}"]`);
    if (!card) return;
    const stateEl = $(".tool-state", card);
    stateEl.className = `tool-state ${ev.ok ? "ok" : "err"}`;
    stateEl.textContent = ev.ok ? `完成 · ${ev.elapsed_ms || 0}ms` : "失败";
    const body = $(".tool-card-body", card);
    body.innerHTML = `<span class="tool-summary">${escapeHtml(ev.summary || "无返回摘要")}</span>` +
      (ev.data ? `<details><summary>查看工具返回</summary><pre>${escapeHtml(JSON.stringify(ev.data, null, 2))}</pre></details>` : "");
    if (ev.ok && ev.data && ev.data.components) appendDesignCard(assistant.body, ev.data);
    scrollChat();
  }

  function appendDesignCard(container, d) {
    const comps = d.components || {};
    const bw = d.bandwidth || {};
    const values = [
      ["电感 L", fmtComp(comps, "L")],
      ["C1", fmtComp(comps, "C1")],
      ["C2", fmtComp(comps, "C2")],
    ];
    if (comps.C3_pF > 0) values.push(["C3", fmtComp(comps, "C3")]);
    else values.push(["拓扑", d.topology_name || d.topology || "—"]);
    const card = document.createElement("div");
    card.className = "design-card";
    card.innerHTML = `
      <div class="design-card-head">
        <svg style="width:16px;height:16px;color:var(--cyan)"><use href="#i-check"/></svg>
        <b>${escapeHtml(d.topology_name || d.topology || "匹配方案")}</b>
        <span class="tag green">节点法已复核</span>
      </div>
      <div class="design-values">
        ${values.map(([k, v]) => `<div class="design-value"><span>${escapeHtml(k)}</span><b>${escapeHtml(v)}</b></div>`).join("")}
      </div>
      <div class="design-card-foot">
        <span class="metric">VSWR <b>${fmtFixed(d.vswr, 4)}</b></span>
        <span class="metric">S11 <b>${fmtS11(d.s11_db)}</b></span>
        <span class="metric">带宽 <b>${fmt(bw.percent, 1)}%</b></span>
        <span class="metric">Q <b>${fmt(d.q, 2)}</b></span>
      </div>
      <div class="design-card-actions">
        <button class="btn tiny" data-action="open-design">在设计中打开</button>
        <button class="btn tiny ghost" data-action="report">导出报告</button>
      </div>`;
    container.appendChild(card);
  }

  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-action]");
    if (!btn) return;
    if (btn.dataset.action === "open-design" || btn.dataset.action === "report") {
      if (!STATE.design) { toast("暂无设计", "请先完成一次设计。", "amber"); return; }
      if (btn.dataset.action === "open-design") {
        fillFormFromDesign(STATE.design);
        showView("design");
        renderDesign(STATE.design);
      } else {
        exportReport();
      }
    }
  });

  async function handleFiles(e) {
    const files = Array.from(e.target.files || []);
    e.target.value = "";
    for (const file of files.slice(0, 6 - STATE.attachments.length)) {
      if (file.size > 25 * 1024 * 1024) {
        toast("文件过大", `${file.name} 超过 25 MB。`, "err");
        continue;
      }
      try {
        const b64 = await readFileBase64(file);
        const info = await api("/api/upload", {
          method: "POST",
          body: { name: file.name, content_base64: b64 },
        });
        info.name = info.name || file.name;
        STATE.attachments.push(info);
        renderAttachmentBar();
        toast("附件已解析", `${info.name} · ${info.chars || 0} 字符`, "ok");
      } catch (err) {
        toast("附件失败", `${file.name}：${err.message}`, "err", 6000);
      }
    }
  }

  function readFileBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const s = String(reader.result || "");
        resolve(s.includes(",") ? s.split(",")[1] : s);
      };
      reader.onerror = () => reject(new Error("读取文件失败"));
      reader.readAsDataURL(file);
    });
  }

  function renderAttachmentBar() {
    const bar = $("#attachmentBar");
    bar.innerHTML = STATE.attachments.map((a, i) =>
      `<span class="attachment-chip" title="${escapeHtml(a.preview || "")}">
        ${escapeHtml(a.name)} <small style="color:var(--muted-2)">${escapeHtml(a.kind || "")} · ${a.chars || 0} 字</small>
        <button data-remove-attach="${i}" title="移除"><svg><use href="#i-close"/></svg></button>
      </span>`).join("");
    $$("[data-remove-attach]", bar).forEach((b) => b.addEventListener("click", () => {
      STATE.attachments.splice(Number(b.dataset.removeAttach), 1);
      renderAttachmentBar();
    }));
  }

  async function sendChat() {
    if (STATE.streaming) return;
    const input = $("#chatInput");
    const text = input.value.trim();
    if (!text && !STATE.attachments.length) return;
    $("#chatWelcome").classList.add("hidden");
    const attachments = STATE.attachments.slice();
    const userText = text || "请阅读附件并总结与微波阻抗匹配相关的关键信息。";
    addUserMessage(userText, attachments);
    STATE.chat.push({ role: "user", content: userText });
    input.value = "";
    input.style.height = "auto";
    STATE.attachments = [];
    renderAttachmentBar();
    STATE.streaming = true;
    $("#btnSend").disabled = true;
    const assistant = addAssistantShell();
    STATE.lastAssistant = assistant;

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: STATE.chat.slice(-18),
          attachments: attachments.map((a) => ({ id: a.id, name: a.name })),
          model: $("#modelSelect").value,
        }),
      });
      if (!res.ok) {
        let detail = {};
        try { detail = await res.json(); } catch (e) { /* ignore */ }
        throw Object.assign(new Error(detail.message || `服务返回 HTTP ${res.status}`), { data: detail });
      }
      if (!res.body) throw new Error("浏览器不支持流式响应");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      let finalContent = "";
      let errored = false;
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        let idx;
        while ((idx = buf.indexOf("\n\n")) >= 0) {
          const chunk = buf.slice(0, idx);
          buf = buf.slice(idx + 2);
          const lines = chunk.split("\n");
          let event = "message", dataStr = "";
          for (const line of lines) {
            if (line.startsWith("event:")) event = line.slice(6).trim();
            else if (line.startsWith("data:")) dataStr += line.slice(5).trim();
          }
          if (!dataStr) continue;
          let data = {};
          try { data = JSON.parse(dataStr); } catch (e) { continue; }
          if (event === "error") errored = true;
          handleSseEvent(event, data, assistant);
          if (event === "token") finalContent += data.text || "";
          if (event === "done") finalContent = data.content || finalContent;
        }
      }
      if (assistant.typing) { assistant.typing.remove(); assistant.typing = null; }
      if (!errored) {
        assistant.md.innerHTML = renderMarkdown(finalContent || assistant.buffer || "（未收到回答）");
        STATE.chat.push({ role: "assistant", content: finalContent || assistant.buffer || "" });
        if (STATE.chat.length > 24) STATE.chat = STATE.chat.slice(-24);
      }
      scrollChat();
    } catch (e) {
      assistant.errored = true;
      if (assistant.typing) { assistant.typing.remove(); assistant.typing = null; }
      const hint = (e.data && e.data.hint) || "";
      assistant.md.innerHTML = `<div class="error-box"><b>智能体暂时不可用</b><p>${escapeHtml(e.message)}</p>${hint ? `<p class="muted">${escapeHtml(hint)}</p>` : ""}<button class="btn tiny" onclick="document.getElementById('btnSettings').click()">打开设置</button></div>`;
      toast("智能体调用失败", e.message, "err", 7000);
    } finally {
      STATE.streaming = false;
      $("#btnSend").disabled = false;
      scrollChat();
    }
  }

  function handleSseEvent(event, data, assistant) {
    if (event === "status") {
      if (assistant.typing && data.text) {
        assistant.typing.title = data.text;
      }
    } else if (event === "tool_call") {
      addToolCard(assistant, data);
    } else if (event === "tool_result") {
      updateToolCard(assistant, data);
    } else if (event === "design") {
      if (data.design) {
        STATE.design = mergeDesign(data.design);
        updateContext(STATE.design);
        if (data.design.steps && data.design.steps.length) {
          if (STATE.view === "design") renderDesign(STATE.design);
        } else {
          ensureFullDesign(data.design).catch(() => {});
        }
      }
    } else if (event === "token") {
      if (assistant.typing) { assistant.typing.remove(); assistant.typing = null; }
      pushToken(assistant, data.text || "");
    } else if (event === "attachments") {
      /* server echo, nothing to do */
    } else if (event === "error") {
      assistant.errored = true;
      if (assistant.typing) { assistant.typing.remove(); assistant.typing = null; }
      const hint = data.hint || "";
      assistant.md.innerHTML = `<div class="error-box"><b>智能体暂时不可用</b><p>${escapeHtml(data.message || "未知错误")}</p>${hint ? `<p class="muted">${escapeHtml(hint)}</p>` : ""}<button class="btn tiny" onclick="document.getElementById('btnSettings').click()">打开设置</button></div>`;
    } else if (event === "done") {
      if (assistant.typing) assistant.typing.remove();
    }
  }

  function mergeDesign(d) {
    // The chat tool result is compact; the design tab expects a full result.
    const existing = STATE.design;
    if (existing && existing.topology === d.topology &&
        existing.frequency_mhz === d.frequency_mhz &&
        existing.load && d.load && existing.load.r === d.load.r && existing.load.x === d.load.x) {
      return Object.assign({}, existing, d, {
        steps: existing.steps || d.steps,
        bandwidth: Object.assign({}, existing.bandwidth || {}, d.bandwidth || {}),
      });
    }
    return d;
  }

  /* ------------------------------------------------------------------ */
  /* Context rail                                                       */
  /* ------------------------------------------------------------------ */
  let miniChart = null;

  function initContext() {
    miniChart = new SmithChart($("#miniSmith"), { mini: true });
    $("#btnContextDesign").addEventListener("click", () => {
      if (!STATE.design) return toast("暂无设计", "先完成一次设计。", "amber");
      fillFormFromDesign(STATE.design);
      showView("design");
      ensureFullDesign(STATE.design);
    });
    $("#btnContextReport").addEventListener("click", exportReport);
  }

  function updateContext(d) {
    if (!d) return;
    const tag = $("#contextTag");
    tag.textContent = d.topology_name || d.topology || "已设计";
    tag.className = "tag green";
    const comps = d.components || {};
    $("#contextDesign").outerHTML = `
      <div id="contextDesign">
        <div class="context-values">
          <div><span>电感 L</span><b>${escapeHtml(fmtComp(comps, "L"))}</b></div>
          <div><span>VSWR</span><b>${fmtFixed(d.vswr, 4)}</b></div>
          <div><span>C1 / C2</span><b>${escapeHtml(fmtComp(comps, "C1"))} / ${escapeHtml(fmtComp(comps, "C2"))}</b></div>
          <div><span>带宽</span><b>${fmt((d.bandwidth || {}).percent, 1)}%</b></div>
        </div>
      </div>`;
    const steps = d.steps || [];
    miniChart.setData({
      steps: steps,
      load: d.load ? { re: d.load.r, im: d.load.x } : null,
      z0: d.z0 || 50,
    });
    miniChart.progress = 1;
    miniChart.draw();
  }

  async function ensureFullDesign(compact) {
    if (compact.steps && compact.steps.length) { renderDesign(compact); return; }
    try {
      const body = {
        topology: compact.topology,
        frequency_mhz: compact.frequency_mhz,
        load_r: compact.load.r,
        load_x: compact.load.x,
        z0: compact.z0 || 50,
        auto_fixed: false,
        L_uh: compact.components ? compact.components.L_uH : undefined,
      };
      if (compact.components && compact.components.C3_pF > 0) body.c3_pf = compact.components.C3_pF;
      const full = await api("/api/design", { method: "POST", body });
      STATE.design = full;
      renderDesign(full);
      updateContext(full);
    } catch (e) {
      toast("无法打开设计", e.message, "err");
    }
  }

  /* ------------------------------------------------------------------ */
  /* Design form                                                        */
  /* ------------------------------------------------------------------ */
  let smith = null;
  let lastBW = null;
  let lastSens = null;

  function designPayload(overrides = {}) {
    const topology = overrides.topology || STATE.topology;
    const autoFixed = overrides.auto_fixed !== undefined ? overrides.auto_fixed : $("#autoFixed").checked;
    const payload = {
      topology,
      frequency_mhz: overrides.frequency_mhz !== undefined ? Number(overrides.frequency_mhz) : Number($("#inFreq").value),
      load_r: overrides.load_r !== undefined ? Number(overrides.load_r) : Number($("#inR").value),
      load_x: overrides.load_x !== undefined ? Number(overrides.load_x) : Number($("#inX").value),
      z0: overrides.z0 !== undefined ? Number(overrides.z0) : Number($("#inZ0").value || 50),
      auto_fixed: autoFixed,
    };
    if (!autoFixed || overrides.L_uh !== undefined) {
      const l = overrides.L_uh !== undefined ? overrides.L_uh : $("#inL").value;
      if (l !== "" && Number(l) > 0) payload.L_uh = Number(l);
    }
    if (TOPO_HAS_C3[topology] && (!autoFixed || overrides.c3_pf !== undefined)) {
      const c3 = overrides.c3_pf !== undefined ? overrides.c3_pf : $("#inC3").value;
      if (c3 !== "" && Number(c3) > 0) payload.c3_pf = Number(c3);
    }
    return payload;
  }

  function setTopology(top) {
    STATE.topology = top;
    $$(".topo-pill").forEach((b) => b.classList.toggle("active", b.dataset.topology === top));
    $("#topoDesc").textContent = TOPO_DESC[top] || "";
    const c3Field = $("#c3Field");
    if (c3Field) {
      const visible = !!TOPO_HAS_C3[top];
      c3Field.style.display = visible ? "" : "none";
    }
  }

  function initDesignForm() {
    $$(".topo-pill").forEach((b) => b.addEventListener("click", () => {
      setTopology(b.dataset.topology);
      if (STATE.design) runDesign();
    }));
    $("#autoFixed").addEventListener("change", () => {
      const on = $("#autoFixed").checked;
      $("#inL").disabled = on;
      $("#inC3").disabled = on;
    });
    $("#btnDesign").addEventListener("click", runDesign);
    $("#btnDesignEmpty").addEventListener("click", () => {
      $("#inFreq").value = 2400; $("#inZ0").value = 50; $("#inR").value = 20; $("#inX").value = 5;
      setTopology("auto"); runDesign();
    });
    $("#btnScan").addEventListener("click", () => {
      if (!STATE.design && !$("#inL").value) return toast("需要电感 L", "先完成一次设计，或取消自动选值并填写 L。", "amber");
      fillAnalysisFromDesign();
      showView("analysis");
      runAnalysisScan();
    });
    $("#btnMatlabVerify").addEventListener("click", runMatlabVerify);
    $("#btnPlay").addEventListener("click", () => {
      if (!smith) return;
      if (smith.playing) smith.pause(); else smith.play();
    });
    $("#btnResetChart").addEventListener("click", () => smith && smith.reset());
    $("#speedRange").addEventListener("input", (e) => smith && smith.setSpeed(Number(e.target.value)));
  }

  async function runDesign() {
    const btn = $("#btnDesign");
    btn.disabled = true;
    btn.textContent = "计算中…";
    try {
      const payload = designPayload();
      const d = await api("/api/design", { method: "POST", body: payload });
      STATE.design = d;
      $("#emptyDesign").classList.add("hidden");
      $("#designResult").classList.remove("hidden");
      renderDesign(d);
      updateContext(d);
      toast("设计完成", `${d.topology_name}：VSWR ${fmtFixed(d.vswr, 4)}，${d.components_display ? Object.values(d.components_display).filter((x) => x !== "—").join(" / ") : ""}`, "ok", 4200);
      if (!STATE.config || !STATE.config.llm || !STATE.config.llm.has_key) {
        /* local design still works without an API key */
      }
    } catch (e) {
      showDesignError(e);
    } finally {
      btn.disabled = false;
      btn.textContent = "求解设计";
    }
  }

  function showDesignError(e) {
    $("#emptyDesign").classList.add("hidden");
    $("#designResult").classList.remove("hidden");
    $("#designKpis").innerHTML = `<div class="kpi-card bad"><span>计算失败</span><b>—</b><small>${escapeHtml(e.message)}</small></div>`;
    $("#stepList").innerHTML = `<div class="empty-mini">${escapeHtml(e.message)}${e.data && e.data.hint ? `<br><br>${escapeHtml(e.data.hint)}` : ""}</div>`;
    $("#warningList").innerHTML = `<li>${escapeHtml(e.message)}</li>${e.data && e.data.hint ? `<li>${escapeHtml(e.data.hint)}</li>` : ""}`;
    $("#warnCount").textContent = "!";
    if (smith) smith.setData({ steps: [], load: null, z0: 50 });
    $("#topoName").textContent = "—";
    $("#topoDiagram").innerHTML = "";
    $("#componentGrid").innerHTML = "";
    $("#bwTag").textContent = "—";
    $("#bwNote").textContent = "";
    $("#sensNote").textContent = "";
    $("#altGrid").innerHTML = "";
    $("#alternativesPanel").classList.add("hidden");
    toast("无法完成该设计", e.message + (e.data && e.data.hint ? ` ${e.data.hint}` : ""), "err", 7000);
  }

  function fillFormFromDesign(d) {
    if (!d) return;
    $("#inFreq").value = d.frequency_mhz;
    $("#inZ0").value = d.z0 || 50;
    $("#inR").value = d.load ? d.load.r : 20;
    $("#inX").value = d.load ? d.load.x : 0;
    if (d.components) {
      $("#inL").value = Number(d.components.L_uH).toFixed(5);
      $("#inC3").value = Number(d.components.C3_pF).toFixed(4);
    }
    if (d.topology && d.topology !== "auto") setTopology(d.topology);
    else setTopology("auto");
    $("#designResult").classList.remove("hidden");
    $("#emptyDesign").classList.add("hidden");
  }

  function renderDesign(d) {
    if (!d) return;
    $("#emptyDesign").classList.add("hidden");
    $("#designResult").classList.remove("hidden");
    const bw = d.bandwidth || {};
    const kpis = $("#designKpis");
    kpis.innerHTML = `
      <div class="kpi-card ${vswrClass(d.vswr)}"><span>VSWR</span><b>${fmtFixed(d.vswr, 4)}</b><small>目标 &lt; 1.5</small></div>
      <div class="kpi-card ${d.s11_db < -15 ? "good" : d.s11_db < -10 ? "warn" : "bad"}"><span>S11</span><b>${fmtS11(d.s11_db)}</b><small>回波损耗 ${fmtRL(d.return_loss_db)}</small></div>
      <div class="kpi-card ${bw.percent > 20 ? "good" : bw.percent > 8 ? "warn" : "bad"}"><span>带宽</span><b>${fmt(bw.percent, 1)}%</b><small>VSWR &lt; ${bw.vswr_limit || 2}</small></div>
      <div class="kpi-card ${d.q < 2 ? "good" : d.q < 5 ? "warn" : "bad"}"><span>设计 Q</span><b>${fmt(d.q, 2)}</b><small>越低越宽</small></div>`;

    $("#smithSub").textContent = `${d.topology_name || d.topology} · 匹配轨迹（负载 → 源）`;
    smith.setData({
      steps: d.steps || [],
      load: d.load ? { re: d.load.r, im: d.load.x } : null,
      z0: d.z0 || 50,
      scanPoints: [],
    });
    setTimeout(() => { smith.progress = 0; smith.play(); }, 180);

    const legend = $("#smithLegend");
    legend.innerHTML = `<span><i class="legend-dot" style="background:#fb923c"></i>负载</span><span><i class="legend-dot" style="background:#34d399"></i>匹配点 50Ω</span>` +
      (d.steps || []).map((s, i) => `<span><i class="legend-dot" style="background:${["#22d3ee", "#34d399", "#fbbf24", "#a78bfa", "#f87171"][i % 5]}"></i>${escapeHtml(s.label)}</span>`).join("");

    const stepList = $("#stepList");
    stepList.innerHTML = (d.steps || []).map((s, i) => `
      <div class="step-item" data-step="${i}">
        <div class="step-num">${i + 1}</div>
        <div class="step-body"><b>${escapeHtml(s.label)}</b><small>${escapeHtml(s.note || "")}</small></div>
        <span class="step-kind">${s.kind === "series" ? "串联" : "并联"}</span>
      </div>`).join("");
    $("#stepCount").textContent = `${(d.steps || []).length} 步`;
    $$(".step-item", stepList).forEach((el) => el.addEventListener("click", () => {
      $$(".step-item", stepList).forEach((x) => x.classList.remove("active"));
      el.classList.add("active");
      smith.progress = (Number(el.dataset.step) + 1) / Math.max(1, (d.steps || []).length);
      smith.draw();
    }));
    $("#formulaBox").innerHTML = `<b>设计公式</b><br>${escapeHtml(d.formulas || "—")}`;
    $("#topoName").textContent = d.topology_name || d.topology || "—";
    $("#topoDiagram").innerHTML = topologySVG(d.topology, d.components || {});
    renderComponentGrid(d.components || {}, d.topology, d);

    lastBW = d.bandwidth;
    ChartKit.drawLineChart($("#bwCanvas"), Object.assign({ mark_mhz: d.frequency_mhz }, d.bandwidth || {}));
    const bwRange = bw.low_mhz && bw.high_mhz ? `${fmt(bw.low_mhz, 2)} – ${fmt(bw.high_mhz, 2)} MHz` : "未找到合格频段";
    $("#bwTag").textContent = `${fmt(bw.percent, 1)}%`;
    $("#bwNote").textContent = `${bwRange} · 扫频范围 ±60% · 虚线为 VSWR=${bw.vswr_limit || 2}`;

    lastSens = d.sensitivity || [];
    drawSensitivity(lastSens);
    $("#sensNote").textContent = "每根柱为该元件 ±5% 偏差下的最差 VSWR；绿色 <1.5，黄色 <2，红色 ≥2。";

    const warnings = d.warnings || [];
    $("#warnCount").textContent = warnings.length ? `${warnings.length} 条` : "0";
    $("#warningList").innerHTML = warnings.length
      ? warnings.map((w) => `<li>${escapeHtml(w)}</li>`).join("")
      : `<li class="ok">节点法复核通过，未发现显著的元件可实现性风险。仍建议用实际元件模型复核。</li>`;

    const alts = d.alternatives || [];
    const altPanel = $("#alternativesPanel");
    if (alts.length) {
      altPanel.classList.remove("hidden");
      $("#altGrid").innerHTML = alts.map((a, i) => `
        <div class="alt-card ${i === 0 ? "best" : ""}">
          <div class="alt-card-head"><b>${escapeHtml(a.topology_name)}</b><span class="tag ${i === 0 ? "cyan" : ""}">${i === 0 ? "推荐" : ""}</span></div>
          <p>${escapeHtml(a.components_display ? Object.values(a.components_display).filter((x) => x !== "—").join(" / ") : "")}</p>
          <p class="alt-metric">带宽 ${fmt(a.bandwidth_percent, 1)}% · Q ${fmt(a.q, 2)}</p>
          <button class="btn tiny ghost" data-alt-topology="${escapeHtml(a.topology)}">应用此方案</button>
        </div>`).join("");
      $$("[data-alt-topology]").forEach((b) => b.addEventListener("click", () => {
        setTopology(b.dataset.altTopology);
        runDesign();
      }));
    } else {
      altPanel.classList.add("hidden");
    }

    // Update L/C3 inputs with the solved values (still disabled when auto).
    if (d.components) {
      $("#inL").value = Number(d.components.L_uH).toFixed(5);
      $("#inC3").value = Number(d.components.C3_pF).toFixed(4);
    }
    $("#designModeTag").textContent = d.engine && d.engine.includes("matlab") ? "MATLAB 内核" : "Python 内核";
    setTimeout(() => { smith._notify(); }, 0);
  }

  function renderComponentGrid(comps, topology, d) {
    const items = [
      ["L", "电感", fmtComp(comps, "L"), "串联电感"],
      ["C1", "电容 C1", fmtComp(comps, "C1"), topology === "l_right" || topology === "pi2" ? "源端并联" : topology === "l_left" || topology === "pi1" ? "负载端并联" : "串联/并联"],
      ["C2", "电容 C2", fmtComp(comps, "C2"), "串联匹配电容"],
    ];
    if (comps.C3_pF > 0) items.push(["C3", "电容 C3", fmtComp(comps, "C3"), topology === "t" ? "源端串联" : topology === "pi1" ? "源端并联" : "负载端并联"]);
    else items.push(["Zin", "输入阻抗", (d && d.input_impedance_display) || "—", "节点法复核值"]);
    $("#componentGrid").innerHTML = items.slice(0, 4).map(([sym, name, val, role]) =>
      `<div class="component-item"><span>${escapeHtml(name)}<small>${escapeHtml(sym)}</small></span><b>${escapeHtml(val)}</b><small>${escapeHtml(role)}</small></div>`
    ).join("");
  }

  function drawSensitivity(items) {
    const data = (items || []).map((s) => ({
      label: s.element,
      value: Number(s.worst_vswr) || 0,
      raw: s,
    }));
    ChartKit.drawBars($("#sensCanvas"), data, {
      unit: "",
      padLeft: 58,
      format: (v) => v.toFixed(2),
      colorFn: (d) => d.value <= 1.5 ? "#34d399" : d.value <= 2 ? "#fbbf24" : "#f87171",
    });
  }

  function topologySVG(topology, comps) {
    const L = fmtComp(comps, "L");
    const C1 = fmtComp(comps, "C1");
    const C2 = fmtComp(comps, "C2");
    const C3 = fmtComp(comps, "C3");
    const c = (label, value) => `${label} ${value}`;
    const W = 820, H = 190;
    const series = (x, label, value) => `
      <rect x="${x}" y="70" width="62" height="26" rx="5" fill="#0a1a2c" stroke="#2f4a68"/>
      <text x="${x + 31}" y="80" font-size="10" fill="#cfe3f7" text-anchor="middle">${escapeHtml(label)}</text>
      <text x="${x + 31}" y="91" font-size="8.5" fill="#7dd3fc" text-anchor="middle">${escapeHtml(value)}</text>`;
    const shunt = (x, label, value) => `
      <line x1="${x}" y1="83" x2="${x}" y2="126" stroke="#3c5978" stroke-width="1.6"/>
      <rect x="${x - 27}" y="126" width="54" height="26" rx="5" fill="#071725" stroke="#1f6f5c"/>
      <text x="${x}" y="136" font-size="9.5" fill="#cfe3f7" text-anchor="middle">${escapeHtml(label)}</text>
      <text x="${x}" y="147" font-size="8.5" fill="#5eead4" text-anchor="middle">${escapeHtml(value)}</text>
      <line x1="${x}" y1="152" x2="${x}" y2="164" stroke="#3c5978" stroke-width="1.6"/>
      <line x1="${x - 12}" y1="164" x2="${x + 12}" y2="164" stroke="#3c5978" stroke-width="2.6"/>`;
    let body = "";
    if (topology === "l_right") {
      body = shunt(180, "C1", C1) + `<line x1="120" y1="83" x2="700" y2="83" stroke="#3c5978" stroke-width="1.8"/>` + series(330, "L", L) + series(470, "C2", C2);
    } else if (topology === "l_left") {
      body = `<line x1="120" y1="83" x2="700" y2="83" stroke="#3c5978" stroke-width="1.8"/>` + series(320, "L", L) + series(440, "C2", C2) + shunt(640, "C1", C1);
    } else if (topology === "t") {
      body = series(170, "C3", C3) + `<line x1="232" y1="83" x2="700" y2="83" stroke="#3c5978" stroke-width="1.8"/>` + shunt(400, "L+C2", `${L} / ${C2}`) + series(540, "C1", C1);
    } else if (topology === "pi1") {
      body = shunt(180, "C3", C3) + `<line x1="120" y1="83" x2="700" y2="83" stroke="#3c5978" stroke-width="1.8"/>` + series(330, "L", L) + series(450, "C2", C2) + shunt(640, "C1", C1);
    } else if (topology === "pi2") {
      body = shunt(180, "C1", C1) + `<line x1="120" y1="83" x2="700" y2="83" stroke="#3c5978" stroke-width="1.8"/>` + series(330, "L", L) + series(450, "C2", C2) + shunt(640, "C3", C3);
    } else {
      body = `<line x1="120" y1="83" x2="700" y2="83" stroke="#3c5978" stroke-width="1.8"/>`;
    }
    return `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
      <defs><radialGradient id="srcG" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#164e63"/><stop offset="100%" stop-color="#082f49"/></radialGradient></defs>
      <circle cx="60" cy="83" r="20" fill="url(#srcG)" stroke="#22d3ee" stroke-width="1.4"/>
      <text x="60" y="87" font-size="11" fill="#a5f3fc" text-anchor="middle">50Ω</text>
      <line x1="80" y1="83" x2="120" y2="83" stroke="#3c5978" stroke-width="1.8"/>
      ${body}
      <line x1="700" y1="83" x2="744" y2="83" stroke="#3c5978" stroke-width="1.8"/>
      <rect x="744" y="63" width="50" height="40" rx="7" fill="#211a0a" stroke="#d97706" stroke-width="1.4"/>
      <text x="769" y="87" font-size="11" fill="#fcd34d" text-anchor="middle">Z_L</text>
      <text x="60" y="175" font-size="9" fill="#5c7694" text-anchor="middle">源</text>
      <text x="769" y="175" font-size="9" fill="#5c7694" text-anchor="middle">负载</text>
    </svg>`;
  }

  /* ------------------------------------------------------------------ */
  /* Report / MATLAB                                                    */
  /* ------------------------------------------------------------------ */
  async function exportReport() {
    const d = STATE.design;
    if (!d) return toast("暂无设计", "请先完成一次设计，再导出报告。", "amber");
    try {
      const r = await api("/api/report", {
        method: "POST",
        body: {
          topology: d.topology,
          frequency_mhz: d.frequency_mhz,
          load_r: d.load.r,
          load_x: d.load.x,
          z0: d.z0 || 50,
          L_uh: d.components.L_uH,
          C1_pF: d.components.C1_pF,
          C2_pF: d.components.C2_pF,
          c3_pf: d.components.C3_pF,
          note: "由「智配芯生 · ImpedanceMCP」生成",
        },
      });
      toast("报告已生成", "正在新窗口打开 HTML 报告。", "ok");
      downloadUrl(r.url);
    } catch (e) {
      toast("导出失败", e.message, "err");
    }
  }

  async function runMatlabVerify() {
    const btn = $("#btnMatlabVerify");
    btn.disabled = true;
    btn.textContent = "MATLAB 计算中…";
    try {
      const payload = designPayload();
      const actualTop = STATE.topology === "auto" && STATE.design ? STATE.design.topology : STATE.topology;
      const comps = STATE.design ? STATE.design.components : null;
      if (!comps) throw new Error("请先完成一次设计，再调用 MATLAB 复核。");
      const r = await api("/api/matlab/verify", {
        method: "POST",
        body: {
          topology: actualTop,
          frequency_mhz: payload.frequency_mhz,
          load_r: payload.load_r,
          load_x: payload.load_x,
          z0: payload.z0,
          L_uh: comps.L_uH,
          c3_pf: comps.C3_pF,
        },
      });
      toast("MATLAB 复核完成", `${r.summary || ""}`, r.ok ? "ok" : "err", 8000);
    } catch (e) {
      toast("MATLAB 复核失败", e.message + (e.data && e.data.hint ? ` ${e.data.hint}` : ""), "err", 8000);
    } finally {
      btn.disabled = false;
      btn.textContent = "MATLAB 复核";
    }
  }

  async function openMatlab() {
    try {
      const r = await api("/api/matlab/open", { method: "POST", body: {} });
      toast("原版软件已启动", r.summary || "Impedance_Matching.exe", "ok");
    } catch (e) {
      toast("无法启动原版软件", e.message + (e.data && e.data.hint ? ` ${e.data.hint}` : ""), "err", 7000);
    }
  }

  /* ------------------------------------------------------------------ */
  /* Analysis                                                           */
  /* ------------------------------------------------------------------ */
  let scanChart = null;

  function initAnalysis() {
    scanChart = new SmithChart($("#scanCanvas"), { tooltip: $("#scanTooltip") });
    $("#anTopology").addEventListener("change", () => {
      $("#anC3row").style.display = ["t", "pi1", "pi2"].includes($("#anTopology").value) ? "" : "none";
    });
    $("#btnRunScan").addEventListener("click", runAnalysisScan);
    $("#btnCompare").addEventListener("click", compareTopologies);
    $("#anTopology").dispatchEvent(new Event("change"));
  }

  function fillAnalysisFromDesign() {
    const d = STATE.design;
    if (d) {
      $("#anTopology").value = d.topology && d.topology !== "auto" ? d.topology : "l_right";
      $("#anFreq").value = d.frequency_mhz;
      $("#anZ0").value = d.z0 || 50;
      $("#anL").value = Number(d.components.L_uH).toFixed(5);
      $("#anR").value = d.load.r;
      $("#anX").value = d.load.x;
      $("#anTopology").dispatchEvent(new Event("change"));
    } else {
      $("#anFreq").value = $("#inFreq").value;
      $("#anZ0").value = $("#inZ0").value;
      $("#anL").value = $("#inL").value;
    }
  }

  async function runAnalysisScan() {
    const btn = $("#btnRunScan");
    btn.disabled = true;
    btn.textContent = "扫描中…";
    try {
      const topology = $("#anTopology").value;
      const body = {
        topology,
        frequency_mhz: Number($("#anFreq").value),
        z0: Number($("#anZ0").value || 50),
        L_uh: Number($("#anL").value),
        steps: Number($("#anSteps").value || 45),
        c1_range_pf: [Number($("#anC1min").value), Number($("#anC1max").value)],
        c2_range_pf: [Number($("#anC2min").value), Number($("#anC2max").value)],
      };
      if (["t", "pi1", "pi2"].includes(topology)) {
        body.c3_range_pf = [Number($("#anC3min").value), Number($("#anC3max").value)];
      }
      const r = await api("/api/scan", { method: "POST", body });
      STATE.scan = r;
      renderScan(r);
      compareTopologies();
    } catch (e) {
      toast("扫描失败", e.message + (e.data && e.data.hint ? ` ${e.data.hint}` : ""), "err", 7000);
      $("#scanSummary").textContent = e.message;
    } finally {
      btn.disabled = false;
      btn.textContent = "运行扫描";
    }
  }

  function renderScan(r) {
    const kpis = $("#scanKpis");
    kpis.innerHTML = `
      <div class="kpi-card"><span>R 范围</span><b>${fmt(r.r_min, 1)}–${fmt(r.r_max, 1)}</b><small>Ω · 5–95% ${fmt(r.r_p05, 1)}–${fmt(r.r_p95, 1)}</small></div>
      <div class="kpi-card"><span>X 范围</span><b>${fmt(r.x_min, 1)}–${fmt(r.x_max, 1)}</b><small>Ω · 5–95% ${fmt(r.x_p05, 1)}–${fmt(r.x_p95, 1)}</small></div>
      <div class="kpi-card"><span>有效点</span><b>${r.points_count || 0}</b><small>网格扫描</small></div>
      <div class="kpi-card"><span>采样点</span><b>${(r.points || []).length}</b><small>用于圆图绘制</small></div>`;
    $("#scanTopoTag").textContent = TOPO_SHORT[r.topology] || r.topology;
    scanChart.setData({
      steps: [],
      load: STATE.design && STATE.design.load ? { re: STATE.design.load.r, im: STATE.design.load.x } : null,
      z0: r.z0 || 50,
      scanPoints: r.points || [],
    });
    const cx = (r.r_max + r.r_min) / 2;
    const cy = (r.x_max + r.x_min) / 2;
    $("#scanSummary").innerHTML =
      `在 <b>${fmt(r.frequency_mhz, 1)} MHz</b>、L=<b>${fmt($("#anL").value, 4)} µH</b> 下，` +
      `<b>${escapeHtml(TOPO_SHORT[r.topology] || r.topology)}</b> 可覆盖的负载范围约为 ` +
      `R <b>${fmt(r.r_min, 2)}–${fmt(r.r_max, 2)} Ω</b>、X <b>${fmt(r.x_min, 2)}–${fmt(r.x_max, 2)} Ω</b>；` +
      `中心约 <b>${fmt(cx, 1)} ${cy >= 0 ? "+" : "−"} j${fmt(Math.abs(cy), 1)} Ω</b>。` +
      `若目标负载落在灰色区域之外，可调整 L、扩大电容范围或改用三元件拓扑。`;
  }

  async function compareTopologies() {
    const btn = $("#btnCompare");
    btn.disabled = true;
    btn.textContent = "比较中…";
    try {
      const r = await api("/api/suggest", {
        method: "POST",
        body: {
          frequency_mhz: Number($("#anFreq").value),
          load_r: Number($("#anR").value),
          load_x: Number($("#anX").value),
          z0: Number($("#anZ0").value || 50),
        },
      });
      const list = r.alternatives || [];
      if (!list.length) {
        $("#compareList").innerHTML = `<div class="empty-mini">五种拓扑均不可行，请尝试其他频率或含串联电感的方案。</div>`;
        return;
      }
      const maxBw = Math.max(...list.map((x) => x.bandwidth_percent || 0), 1);
      $("#compareList").innerHTML = list.map((a, i) => `
        <div class="compare-row">
          <div>
            <b>${escapeHtml(a.topology_name)}</b>
            <small>${escapeHtml(a.components_display ? Object.values(a.components_display).filter((x) => x !== "—").join(" / ") : "")}</small>
            <div class="compare-bar"><i style="width:${Math.max(4, (a.bandwidth_percent || 0) / maxBw * 100)}%"></i></div>
          </div>
          <div style="text-align:right">
            <div style="font-size:11px;color:var(--green)">${fmt(a.bandwidth_percent, 1)}%</div>
            <button class="btn tiny ghost" data-use-topology="${escapeHtml(a.topology)}">应用</button>
          </div>
        </div>`).join("");
      $$("[data-use-topology]").forEach((b) => b.addEventListener("click", () => {
        setTopology(b.dataset.useTopology);
        $("#inFreq").value = $("#anFreq").value;
        $("#inZ0").value = $("#anZ0").value;
        showView("design");
        runDesign();
      }));
    } catch (e) {
      toast("比较失败", e.message, "err");
    } finally {
      btn.disabled = false;
      btn.textContent = "重新比较";
    }
  }

  /* ------------------------------------------------------------------ */
  /* Stress                                                             */
  /* ------------------------------------------------------------------ */
  function initStress() {
    const syncC3 = () => {
      const show = ["t", "pi1", "pi2"].includes($("#stTopology").value);
      $("#stC3Field").style.display = show ? "" : "none";
      if (!show) $("#stC3").value = 0;
    };
    $("#stTopology").addEventListener("change", syncC3);
    syncC3();
    $("#btnStress").addEventListener("click", runStress);
    $("#btnStressFromDesign").addEventListener("click", () => {
      const d = STATE.design;
      if (!d) return toast("暂无设计", "请先在「匹配设计」中完成一次设计。", "amber");
      $("#stTopology").value = d.topology;
      $("#stFreq").value = d.frequency_mhz;
      $("#stR").value = d.load.r;
      $("#stX").value = d.load.x;
      $("#stL").value = Number(d.components.L_uH).toFixed(5);
      $("#stC1").value = Number(d.components.C1_pF).toFixed(4);
      $("#stC2").value = Number(d.components.C2_pF).toFixed(4);
      $("#stC3").value = Number(d.components.C3_pF).toFixed(4);
      syncC3();
      toast("已填入当前设计", "可以直接开始耐压分析。", "ok");
    });
  }

  async function runStress() {
    const btn = $("#btnStress");
    btn.disabled = true;
    btn.textContent = "计算中…";
    try {
      const r = await api("/api/stress", {
        method: "POST",
        body: {
          topology: $("#stTopology").value,
          frequency_mhz: Number($("#stFreq").value),
          load_r: Number($("#stR").value),
          load_x: Number($("#stX").value),
          L_uh: Number($("#stL").value),
          C1_pF: Number($("#stC1").value),
          C2_pF: Number($("#stC2").value),
          C3_pF: Number($("#stC3").value || 0),
          power_w: Number($("#stPower").value),
          rated_voltage: Number($("#stRated").value || 0),
        },
      });
      renderStress(r);
    } catch (e) {
      toast("耐压计算失败", e.message + (e.data && e.data.hint ? ` ${e.data.hint}` : ""), "err", 7000);
    } finally {
      btn.disabled = false;
      btn.textContent = "开始耐压分析";
    }
  }

  function renderStress(r) {
    STATE.lastStress = r;
    const els = r.elements || [];
    const maxV = els.length ? Math.max(...els.map((e) => e.voltage_peak)) : 0;
    const rated = Number($("#stRated").value || 0);
    const sfs = rated > 0 ? els.map((e) => rated / Math.max(1e-9, e.voltage_peak)) : [];
    const minSf = sfs.length ? Math.min(...sfs) : null;
    $("#stressKpis").innerHTML = `
      <div class="kpi-card"><span>输入峰值电压</span><b>${fmt(r.input_voltage_peak, 1)}</b><small>V · 源开路 ${fmt(r.source_voltage_peak, 1)} V</small></div>
      <div class="kpi-card"><span>负载峰值电压</span><b>${fmt(r.load_voltage_peak, 1)}</b><small>V</small></div>
      <div class="kpi-card ${maxV > 100 ? "warn" : ""}"><span>最大元件电压</span><b>${fmt(maxV, 1)}</b><small>V peak</small></div>
      <div class="kpi-card ${minSf !== null ? (minSf >= 2 ? "good" : minSf >= 1.3 ? "warn" : "bad") : ""}"><span>最小安全系数</span><b>${minSf === null ? "—" : fmt(minSf, 2)}</b><small>额定 / 峰值</small></div>`;
    $("#stressTag").textContent = `${TOPO_SHORT[r.topology] || r.topology} · ${fmt(r.power_w, 2)} W`;
    ChartKit.drawBars($("#stressCanvas"), els.map((e) => ({
      label: e.name, value: e.voltage_peak, raw: e,
    })), {
      unit: " V",
      padLeft: 58,
      format: (v) => `${v.toFixed(1)} V`,
      colorFn: (d) => {
        if (!rated) return "#22d3ee";
        const sf = rated / Math.max(1e-9, d.value);
        return sf >= 2 ? "#34d399" : sf >= 1.3 ? "#fbbf24" : "#f87171";
      },
    });
    const tbody = $("#stressTable tbody");
    tbody.innerHTML = els.map((e, i) => {
      const sf = rated > 0 ? rated / Math.max(1e-9, e.voltage_peak) : null;
      const cls = sf === null ? "" : sf >= 2 ? "good" : sf >= 1.3 ? "warn" : "bad";
      return `<tr><td>${escapeHtml(e.name)}</td><td>${fmt(e.voltage_peak, 2)}</td><td>${fmt(e.voltage_rms, 2)}</td><td>${fmt(e.current_peak, 3)}</td><td>${fmt(e.current_rms, 3)}</td><td class="${cls}">${sf === null ? "—" : fmt(sf, 2)}</td></tr>`;
    }).join("");

    const advice = [];
    if (r.vswr > 1.2) advice.push(`当前网络 VSWR=${fmt(r.vswr, 3)}，并非完全匹配；失配会在节点产生额外驻波电压，建议先复核元件值。`);
    if (maxV > 100) advice.push(`最高峰值电压 ${fmt(maxV, 1)} V，建议选用 C0G/NP0 高压电容与高 SRF 电感，并按额定值至少 2× 降额。`);
    if (maxV > 0 && maxV < 10) advice.push("峰值电压较低，常规 0402/0603 射频元件即可，但仍需检查 RMS 电流。");
    const maxI = els.length ? Math.max(...els.map((e) => e.current_peak)) : 0;
    if (maxI > 1) advice.push(`最大峰值电流 ${fmt(maxI, 2)} A，注意电感的饱和电流与电容的纹波电流额定值。`);
    if (minSf !== null && minSf < 2) advice.push(`最小安全系数 ${fmt(minSf, 2)} 小于 2，建议提高元件额定电压或降低输入功率。`);
    if (r.efficiency !== null && r.efficiency !== undefined && r.efficiency < 0.98) advice.push("网络效率低于 98%，可能由失配或数值截断导致；请用 evaluate_network 复核 Zin。");
    advice.push("本计算采用完整网络节点法，包含 50Ω 源阻抗的负载效应；实际选型还需考虑温度降额、寄生参数与 PCB 布局。");
    $("#stressAdvice").innerHTML = advice.map((a, i) => `<li class="${i === advice.length - 1 ? "" : ""}">${escapeHtml(a)}</li>`).join("");
  }

  /* ------------------------------------------------------------------ */
  /* Presets / misc                                                     */
  /* ------------------------------------------------------------------ */
  const PRESETS = [
    { name: "2.4G Wi-Fi", f: 2400, r: 20, x: 5, top: "auto" },
    { name: "2.4G 高阻", f: 2400, r: 100, x: -30, top: "auto" },
    { name: "433M", f: 433, r: 15, x: 0, top: "l_right" },
    { name: "915M", f: 915, r: 80, x: 20, top: "auto" },
    { name: "1.8G PA", f: 1800, r: 12, x: -8, top: "auto" },
    { name: "5.8G WLAN", f: 5800, r: 35, x: 12, top: "auto" },
  ];

  function initPresets() {
    $("#presetList").innerHTML = PRESETS.map((p, i) =>
      `<button class="preset-chip" data-preset="${i}">${escapeHtml(p.name)}</button>`).join("");
    $$("[data-preset]").forEach((b) => b.addEventListener("click", () => {
      const p = PRESETS[Number(b.dataset.preset)];
      $("#inFreq").value = p.f; $("#inR").value = p.r; $("#inX").value = p.x;
      setTopology(p.top);
      runDesign();
    }));
  }

  function initGlobal() {
    $("#btnSettings").addEventListener("click", openSettings);
    $("#btnCloseSettings").addEventListener("click", closeSettings);
    $("#btnCancelSettings").addEventListener("click", closeSettings);
    $("#btnSaveSettings").addEventListener("click", saveSettings);
    $("#btnTestLlm").addEventListener("click", testLlm);
    $("#btnRecheck").addEventListener("click", loadStatus);
    $("#btnOpenMatlab").addEventListener("click", openMatlab);
    $("#btnMatlab").addEventListener("click", openMatlab);
    $("#btnReport").addEventListener("click", exportReport);
    $("#settingsModal").addEventListener("click", (e) => {
      if (e.target === $("#settingsModal")) closeSettings();
    });
    $("#setProvider").addEventListener("change", () => {
      const p = $("#setProvider").value;
      const urls = {
        sjtu: "https://models.sjtu.edu.cn/api/v1",
        deepseek: "https://api.deepseek.com/v1",
        custom: $("#setBaseUrl").value,
      };
      $("#setBaseUrl").value = urls[p] || "";
      populateModels(p, "");
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !$("#settingsModal").classList.contains("hidden")) closeSettings();
    });
  }

  /* ------------------------------------------------------------------ */
  /* Boot                                                               */
  /* ------------------------------------------------------------------ */
  let booted = false;
  async function init() {
    if (booted) return;
    booted = true;
    initNav();
    initChat();
    initDesignForm();
    initAnalysis();
    initStress();
    initContext();
    initPresets();
    initGlobal();
    smith = new SmithChart($("#smithCanvas"), {
      tooltip: $("#smithTooltip"),
      onStateChange: (playing) => {
        $("#btnPlay").innerHTML = playing
          ? '<svg><use href="#i-pause"/></svg>'
          : '<svg><use href="#i-play"/></svg>';
      },
    });
    setTopology("auto");
    await loadStatus();
    await loadConfig();
    await loadMcpCode();
    // If the app opens with no design, show the empty state.
    $("#designResult").classList.add("hidden");
    $("#emptyDesign").classList.remove("hidden");
  }

  document.addEventListener("DOMContentLoaded", init);
  if (document.readyState !== "loading") init();
  window.__IMP = { state: STATE, updateContext, renderDesign, runDesign, ensureFullDesign };
  window.addEventListener("error", (e) => {
    if (e && e.message) toast("界面脚本错误", e.message, "err", 8000);
  });
  window.addEventListener("unhandledrejection", (e) => {
    const r = e && e.reason;
    if (r && r.message) toast("请求失败", r.message, "err", 8000);
  });
})();
