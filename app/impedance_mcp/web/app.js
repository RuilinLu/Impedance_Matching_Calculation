/* ==========================================================================
   Impedance Matching AI — application logic
   ========================================================================== */

(function () {
  "use strict";

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const T = (key, fallback) => (window.I18N ? window.I18N.t(key, fallback) : (fallback || key));

  const STATE = {
    view: "agent",
    topology: "auto",
    design: null,
    lastStress: null,
    config: null,
    status: null,
    chat: [],
    attachments: [],
    streaming: false,
    scan: null,
    models: [],
    providers: [],
    providerChanged: false,
    lastAssistant: null,
    lastStats: null,
    lastUsage: null,
    profileMeta: null,
    catalogLog: [],
    showThinking: false,
    showCitations: false,
    scanAbort: null,
    scanStreaming: false,
    stressAbort: null,
    stressStreaming: false,
    updateInfo: null,
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
    ["search_textbooks", "检索教材", "全文 / 模糊 / 引用"],
    ["read_textbook_page", "读取教材页", "文字 / OCR / 截图"],
    ["translate_textbook_page", "翻译教材页", "学术中文 / 英文"],
    ["search_docs", "检索软件文档", "功能 / 代码 / AI / MCP"],
    ["get_code_reference", "查询代码参考", "签名与参数"],
    ["get_library_status", "检查教材库", "索引 / OCR 状态"],
    ["get_system_status", "检查系统状态", "模型 / MCP / 目录"],
    ["list_presets", "读取演示预设", "常用频段"],
  ];

  const VIEW_META = {
    agent: {
      zh: ["AI 智能体", "用自然语言驱动微波阻抗匹配计算、仿真与教材检索"],
      en: ["AI Agent", "Drive matching design, simulation and textbook search with natural language"],
    },
    design: {
      zh: ["匹配设计", "五种拓扑 · 解析求解 · 完整网络节点法复核"],
      en: ["Design", "Five topologies · analytical solution · full nodal verification"],
    },
    analysis: {
      zh: ["圆图分析", "正向扫描可匹配范围，密度云与边界可视化"],
      en: ["Smith Analysis", "Forward scan of the matchable region with density and boundary"],
    },
    stress: {
      zh: ["耐压分析", "峰值电压、RMS 电流与安全系数"],
      en: ["Voltage Stress", "Peak voltage, RMS current and safety factor"],
    },
    library: {
      zh: ["教材库", "全文搜索 · OCR · 页面定位 · 学术翻译"],
      en: ["Textbook Library", "Full-text search · OCR · page location · academic translation"],
    },
    docs: {
      zh: ["文档中心", "软件功能 · 代码参考 · AI 接口 · MCP 协议"],
      en: ["Documentation", "Application · code reference · AI interface · MCP protocol"],
    },
    about: {
      zh: ["关于", "Impedance Matching AI v4.4.0"],
      en: ["About", "Impedance Matching AI v4.4.0"],
    },
  };

  const TOPO_DESC = {
    auto: "自动比较五种拓扑，优先选择元件更少、可实现性更好的方案。",
    l_right: "L型（右）：源端并联 C1 + 串联 L/C2，适合 R_L < 50Ω 的低阻负载。",
    l_left: "L型（左）：串联 L/C2 + 负载端并联 C1，适合 R_L > 50Ω 的高阻负载。",
    t: "T型：源—串 C3—节点（并 L+C2）—串 C1—负载，三元件可调节带宽。",
    pi1: "π型Ⅰ：源端并 C3—串 L+C2—负载端并 C1，C-L-C 结构。",
    pi2: "π型Ⅱ：源端并 C1—串 L+C2—负载端并 C3，适合低阻负载。",
  };
  const TOPO_DESC_EN = {
    auto: "Compares five topologies and prefers fewer components with practical values.",
    l_right: "L-right: shunt C1 at the source, then series L/C2; for R_L < 50 Ω.",
    l_left: "L-left: series L/C2, then shunt C1 at the load; for R_L > 50 Ω.",
    t: "T: series C3 — node (shunt L+C2) — series C1 — load; three elements for bandwidth control.",
    pi1: "π-I: shunt C3 — series L+C2 — shunt C1; C-L-C structure.",
    pi2: "π-II: shunt C1 — series L+C2 — shunt C3; for low-impedance loads.",
  };
  const TOPO_SHORT = { auto: "Auto", l_right: "L·R", l_left: "L·L", t: "T", pi1: "πⅠ", pi2: "πⅡ" };
  const TOPO_NAME_EN = {
    auto: "Auto", l_right: "L-type (right)", l_left: "L-type (left)",
    t: "T-type", pi1: "π-type I", pi2: "π-type II",
  };
  const TOPO_HAS_C3 = { t: true, pi1: true, pi2: true };
  let scanChart = null;
  let scanAnimation = null;

  function topologyName(design) {
    if (!design) return "—";
    if (window.I18N && window.I18N.lang === "en") {
      return TOPO_NAME_EN[design.topology] || design.topology_name || design.topology || "—";
    }
    return design.topology_name || design.topology || "—";
  }

  function stepLabel(step) {
    if (!step) return "—";
    if (!(window.I18N && window.I18N.lang === "en")) return step.label || "—";
    return `${step.kind === "series" ? "Series" : "Shunt"} ${step.element || ""}`.trim();
  }

  function stepNote(step) {
    if (!step) return "";
    if (!(window.I18N && window.I18N.lang === "en")) return step.note || "";
    const element = String(step.element || "").toUpperCase();
    if (step.kind === "series") {
      return element.includes("L")
        ? "Move along the constant-resistance circle; series inductance adds +jX."
        : "Move along the constant-resistance circle; series capacitance adds −jX.";
    }
    return element.includes("C")
      ? "Move along the constant-conductance circle; shunt capacitance adds +jB."
      : "Move along the constant-conductance circle; shunt inductance adds −jB.";
  }

  /* ------------------------------------------------------------------ */
  /* Utilities                                                          */
  /* ------------------------------------------------------------------ */
  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function fmt(value, digits = 3) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
    if (!isFinite(Number(value))) return "∞";
    const number = Number(value);
    if (Math.abs(number) >= 1000) return number.toFixed(0);
    if (Math.abs(number) > 0 && Math.abs(number) < 0.001) return number.toExponential(2);
    return number.toFixed(digits).replace(/\.?0+$/, "");
  }

  function fmtFixed(value, digits = 3) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
    if (!isFinite(Number(value))) return "∞";
    return Number(value).toFixed(digits);
  }

  function fmtS11(value) {
    const number = Number(value);
    if (!isFinite(number)) return "—";
    return number <= -60 ? "&lt; −60 dB" : `${number.toFixed(2)} dB`;
  }

  function fmtRL(value) {
    const number = Number(value);
    if (!isFinite(number)) return "—";
    return number >= 60 ? "&gt; 60 dB" : `${number.toFixed(2)} dB`;
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

  function vswrClass(value) {
    if (!isFinite(value)) return "bad";
    if (value <= 1.5) return "good";
    if (value <= 2) return "warn";
    return "bad";
  }

  function fmtTokens(value) {
    const number = Number(value) || 0;
    if (number >= 1e6) return (number / 1e6).toFixed(2) + "M";
    if (number >= 1000) return (number / 1000).toFixed(1) + "k";
    return String(Math.round(number));
  }

  function fmtMoney(value, currency, configured) {
    if (configured === false) return "—";
    const symbol = String(currency || "CNY").toUpperCase() === "USD" ? "$" : "¥";
    const number = Number(value) || 0;
    if (number > 0 && number < 0.01) return symbol + number.toFixed(5);
    if (number < 1) return symbol + number.toFixed(4);
    return symbol + number.toFixed(3);
  }

  function toast(title, message = "", type = "ok", ms = 3600) {
    const wrap = $("#toastWrap");
    if (!wrap) return;
    const element = document.createElement("div");
    element.className = `toast ${type}`;
    element.innerHTML = `<b>${escapeHtml(title)}</b>${message ? escapeHtml(message) : ""}`;
    wrap.appendChild(element);
    setTimeout(() => {
      element.style.opacity = "0";
      element.style.transform = "translateY(6px)";
      element.style.transition = ".25s";
      setTimeout(() => element.remove(), 300);
    }, ms);
  }

  async function api(path, options = {}) {
    const opts = Object.assign({ headers: { "Content-Type": "application/json" } }, options);
    if (opts.body && typeof opts.body !== "string") opts.body = JSON.stringify(opts.body);
    const response = await fetch(path, opts);
    let data = {};
    try { data = await response.json(); } catch (e) { data = {}; }
    if (!response.ok || data.ok === false) {
      const error = new Error(data.message || data.error_message || `Request failed (HTTP ${response.status})`);
      error.data = data;
      throw error;
    }
    return data;
  }

  async function streamEvents(path, payload, onEvent, signal) {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload || {}),
      signal,
    });
    if (!response.ok) {
      let detail = {};
      try { detail = await response.json(); } catch (e) { /* ignore */ }
      const error = new Error(detail.message || `服务返回 HTTP ${response.status}`);
      error.data = detail;
      throw error;
    }
    if (!response.body) throw new Error("当前浏览器不支持流式响应");
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let errorMessage = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let index;
      while ((index = buffer.indexOf("\n\n")) >= 0) {
        const chunk = buffer.slice(0, index);
        buffer = buffer.slice(index + 2);
        let eventName = "message";
        let dataString = "";
        for (const line of chunk.split("\n")) {
          if (line.startsWith("event:")) eventName = line.slice(6).trim();
          else if (line.startsWith("data:")) dataString += line.slice(5).trim();
        }
        if (!dataString) continue;
        let data = {};
        try { data = JSON.parse(dataString); } catch (e) { continue; }
        if (eventName === "error") errorMessage = data.message || "计算失败";
        if (onEvent) onEvent(eventName, data);
      }
    }
    if (errorMessage) throw new Error(errorMessage);
  }

  function formatBytes(value) {
    const size = Number(value) || 0;
    if (size >= 1024 * 1024) return (size / 1024 / 1024).toFixed(1) + " MB";
    if (size >= 1024) return (size / 1024).toFixed(0) + " KB";
    return size + " B";
  }

  function uploadBlobWithProgress(file, onProgress) {
    return new Promise(async (resolve, reject) => {
      try {
        const init = await api("/api/upload/init", {
          method: "POST",
          body: { name: file.name || "粘贴附件", size: file.size },
        });
        const uploadId = init.upload_id;
        const chunkSize = Number(init.chunk_size) || 2 * 1024 * 1024;
        let offset = 0;
        while (offset < file.size) {
          const end = Math.min(offset + chunkSize, file.size);
          const blob = file.slice(offset, end);
          await new Promise((done, fail) => {
            const xhr = new XMLHttpRequest();
            xhr.open("POST", `/api/upload/chunk?upload_id=${encodeURIComponent(uploadId)}`);
            xhr.setRequestHeader("Content-Type", "application/octet-stream");
            xhr.upload.onprogress = (event) => {
              if (event.lengthComputable && onProgress) {
                onProgress(Math.min(1, (offset + event.loaded) / Math.max(1, file.size)));
              }
            };
            xhr.onload = () => {
              if (xhr.status >= 200 && xhr.status < 300) return done();
              let message = `上传失败（HTTP ${xhr.status}）`;
              try { message = JSON.parse(xhr.responseText).message || message; } catch (e) { /* ignore */ }
              fail(new Error(message));
            };
            xhr.onerror = () => fail(new Error("网络中断，请重试"));
            xhr.send(blob);
          });
          offset = end;
          if (onProgress) onProgress(offset / Math.max(1, file.size));
        }
        const info = await api("/api/upload/complete", {
          method: "POST",
          body: { upload_id: uploadId },
        });
        resolve(info);
      } catch (error) {
        reject(error);
      }
    });
  }

  function openExternal(url) {
    if (!url) return;
    if (window.pywebview && window.pywebview.api && window.pywebview.api.open_external) {
      Promise.resolve(window.pywebview.api.open_external(url)).then((opened) => {
        if (!opened) window.open(url, "_blank", "noopener");
      }).catch(() => window.open(url, "_blank", "noopener"));
      return;
    }
    window.open(url, "_blank", "noopener");
  }

  function openLocalPath(path) {
    if (!path) return;
    if (window.pywebview && window.pywebview.api && window.pywebview.api.open_path) {
      Promise.resolve(window.pywebview.api.open_path(path)).then((opened) => {
        if (!opened) toast("无法打开目录", path, "amber");
      }).catch(() => toast("无法打开目录", path, "amber"));
      return;
    }
    toast("目录位置", path, "ok", 6000);
  }


  function openDocument(url) {
    let target;
    try { target = new URL(url, window.location.href).href; } catch (e) { target = url; }
    if (window.pywebview && window.pywebview.api && window.pywebview.api.open_window) {
      try {
        Promise.resolve(window.pywebview.api.open_window(target)).then((opened) => {
          if (!opened) window.open(target, "_blank", "noopener");
        }).catch(() => window.open(target, "_blank", "noopener"));
        return;
      } catch (e) { /* fall through */ }
    }
    window.open(target, "_blank", "noopener");
  }

  async function copyText(text, message) {
    try {
      await navigator.clipboard.writeText(text);
      toast(T("common.copied", "已复制"), message || "", "ok");
    } catch (e) {
      const area = document.createElement("textarea");
      area.value = text;
      document.body.appendChild(area);
      area.select();
      try { document.execCommand("copy"); toast(T("common.copied", "已复制"), message || "", "ok"); }
      catch (err) { toast("复制失败", "请手动选择文本复制。", "err"); }
      area.remove();
    }
  }

  /* ------------------------------------------------------------------ */
  /* Markdown renderer                                                  */
  /* ------------------------------------------------------------------ */
  function inlineMd(text) {
    let value = escapeHtml(text);
    value = value.replace(/`([^`]+)`/g, (match, code) => `<code>${code}</code>`);
    value = value.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    value = value.replace(/\*([^*]+)\*/g, "<em>$1</em>");
    value = value.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
      '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
    value = value.replace(/\[\[([^\]]+)\]\]/g, "<mark>$1</mark>");
    return value;
  }

  function renderMarkdown(source) {
    if (!source) return "";
    const codeBlocks = [];
    const inlineCodes = [];
    const mathItems = [];
    let text = String(source).replace(/```([a-zA-Z0-9_+-]*)\n?([\s\S]*?)```/g, (match, lang, code) => {
      codeBlocks.push(`<pre><code>${escapeHtml(code.replace(/\n$/, ""))}</code></pre>`);
      return `@@CODEBLOCK${codeBlocks.length - 1}@@`;
    });
    // Protect inline code and math before Markdown emphasis/list parsing.
    text = text.replace(/`([^`\n]+)`/g, (match, code) => {
      inlineCodes.push(code);
      return `@@INLINECODE${inlineCodes.length - 1}@@`;
    });
    const stashMath = (raw, display) => {
      mathItems.push({ raw, display: !!display });
      return `@@MATH${mathItems.length - 1}@@`;
    };
    text = text.replace(/\$\$([\s\S]+?)\$\$/g, (match, body) =>
      stashMath(`\\[${body}\\]`, true));
    text = text.replace(/\\\[([\s\S]+?)\\\]/g, (match, body) =>
      stashMath(`\\[${body}\\]`, true));
    text = text.replace(/\\\(([\s\S]+?)\\\)/g, (match, body) =>
      stashMath(`\\(${body}\\)`, false));
    text = text.replace(
      /\\begin\{(equation|align|aligned|gather|gathered|multline|split|matrix|pmatrix|bmatrix|vmatrix|cases|array)\*?\}[\s\S]+?\\end\{\1\*?\}/g,
      (match) => stashMath(`\\[${match}\\]`, true));
    text = text.replace(/\$([^$\n]+?)\$/g, (match, body) =>
      stashMath(`\\(${body}\\)`, false));
    const lines = text.split(/\r?\n/);
    const out = [];
    let paragraph = [];
    let list = null;
    let table = null;

    const flushParagraph = () => {
      if (paragraph.length) {
        out.push(`<p>${paragraph.map(inlineMd).join("<br>")}</p>`);
        paragraph = [];
      }
    };
    const flushList = () => {
      if (list) {
        out.push(`<${list.type}>${list.items.map((item) => `<li>${inlineMd(item)}</li>`).join("")}</${list.type}>`);
        list = null;
      }
    };
    const flushTable = () => {
      if (table) {
        const rows = table.rows.filter((row) => !row.separator);
        if (rows.length) {
          const head = rows[0];
          const body = rows.slice(1);
          out.push("<table><thead><tr>" + head.cells.map((cell) => `<th>${inlineMd(cell)}</th>`).join("") +
            "</tr></thead><tbody>" + body.map((row) => "<tr>" + row.cells.map((cell) => `<td>${inlineMd(cell)}</td>`).join("") + "</tr>").join("") +
            "</tbody></table>");
        }
        table = null;
      }
    };

    for (const rawLine of lines) {
      const line = rawLine.replace(/\s+$/, "");
      if (/^\s*\|.*\|\s*$/.test(line)) {
        flushParagraph(); flushList();
        const cells = line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
        const separator = cells.every((cell) => /^:?-{2,}:?$/.test(cell));
        if (!table) table = { rows: [] };
        table.rows.push({ cells, separator });
        continue;
      }
      if (table) flushTable();
      if (!line.trim()) { flushParagraph(); flushList(); continue; }
      if (/^#{1,6}\s+/.test(line)) {
        flushParagraph(); flushList();
        const level = Math.min(6, (line.match(/^#+/) || ["#"])[0].length);
        out.push(`<h${level}>${inlineMd(line.replace(/^#+\s+/, ""))}</h${level}>`);
        continue;
      }
      if (/^>\s?/.test(line)) {
        flushParagraph(); flushList();
        out.push(`<blockquote>${inlineMd(line.replace(/^>\s?/, ""))}</blockquote>`);
        continue;
      }
      const ul = line.match(/^\s*[-*+]\s+(.*)$/);
      if (ul) {
        flushParagraph();
        if (!list || list.type !== "ul") { flushList(); list = { type: "ul", items: [] }; }
        list.items.push(ul[1]);
        continue;
      }
      const ol = line.match(/^\s*\d+[.)]\s+(.*)$/);
      if (ol) {
        flushParagraph();
        if (!list || list.type !== "ol") { flushList(); list = { type: "ol", items: [] }; }
        list.items.push(ol[1]);
        continue;
      }
      if (/^\s*([-*_])\1{2,}\s*$/.test(line)) {
        flushParagraph(); flushList(); out.push("<hr>"); continue;
      }
      flushList();
      paragraph.push(line);
    }
    flushParagraph(); flushList(); flushTable();
    let html = out.join("");
    html = html.replace(/@@INLINECODE(\d+)@@/g, (match, index) => {
      const code = inlineCodes[Number(index)];
      return code === undefined ? "" : `<code>${escapeHtml(code)}</code>`;
    });
    html = html.replace(/@@MATH(\d+)@@/g, (match, index) => {
      const item = mathItems[Number(index)];
      if (!item) return "";
      return item.display
        ? `<span class="math-display">${escapeHtml(item.raw)}</span>`
        : `<span class="math-inline">${escapeHtml(item.raw)}</span>`;
    });
    html = html.replace(/@@CODEBLOCK(\d+)@@/g, (match, index) => codeBlocks[Number(index)] || "");
    return html;
  }

  function typesetMath(element) {
    if (!element || !window.MathJax) return;
    const run = () => {
      try {
        if (MathJax.typesetClear) MathJax.typesetClear([element]);
        MathJax.typesetPromise([element]).catch(() => {});
      } catch (error) {
        /* a malformed formula must never break the answer */
      }
    };
    if (MathJax.startup && MathJax.startup.promise) {
      MathJax.startup.promise.then(run).catch(() => {});
    } else {
      setTimeout(run, 300);
    }
  }

  /* ------------------------------------------------------------------ */
  /* Navigation                                                         */
  /* ------------------------------------------------------------------ */
  function viewMeta(name) {
    const meta = VIEW_META[name] || VIEW_META.agent;
    return (window.I18N && window.I18N.lang === "en") ? meta.en : meta.zh;
  }

  function showView(name, options = {}) {
    if (!VIEW_META[name]) name = "agent";
    STATE.view = name;
    $$(".nav-item").forEach((button) => button.classList.toggle("active", button.dataset.view === name));
    $$(".view").forEach((view) => view.classList.toggle("active", view.id === `view-${name}`));
    const [title, subtitle] = viewMeta(name);
    $("#viewTitle").textContent = title;
    $("#viewSubtitle").textContent = subtitle;
    if (location.hash !== `#${name}`) history.replaceState(null, "", `#${name}`);
    if (name === "design" && !STATE.design) $("#emptyDesign").classList.remove("hidden");
    if (name === "design" && STATE.design) setTimeout(redrawDesignCharts, 50);
    if (name === "analysis" && scanChart) setTimeout(() => scanChart.draw(), 60);
    if (name === "agent") setTimeout(() => typesetMath($("#messages")), 80);
    if (name === "docs") setTimeout(() => typesetMath($("#docsContent")), 120);
    if (name === "stress" && STATE.lastStress) setTimeout(() => renderStress(STATE.lastStress), 50);
    if (name === "library" && window.Library && !options.skipLibrary) {
      window.Library.onShow();
    }
    if (name === "docs" && window.Docs && !options.skipDocs) {
      window.Docs.onShow();
    }
    if (name === "about") refreshMcpCode();
    const quick = window.Assistant;
    if (quick && quick.updateContextLabel) quick.updateContextLabel();
  }

  function redrawDesignCharts() {
    if (lastBW) ChartKit.drawLineChart($("#bwCanvas"), Object.assign({ mark_mhz: STATE.design ? STATE.design.frequency_mhz : null }, lastBW));
    if (lastSens) drawSensitivity(lastSens);
  }

  function initNav() {
    $$(".nav-item").forEach((button) => button.addEventListener("click", () => showView(button.dataset.view)));
    const hash = (location.hash || "").replace("#", "");
    if (VIEW_META[hash]) showView(hash);
    window.addEventListener("hashchange", () => {
      const value = (location.hash || "").replace("#", "");
      if (VIEW_META[value] && value !== STATE.view) showView(value);
    });
  }

  /* ------------------------------------------------------------------ */
  /* Status / settings                                                  */
  /* ------------------------------------------------------------------ */
  async function loadProviders() {
    try {
      const result = await api("/api/providers");
      STATE.providers = result.providers || [];
      populateProviderSelect();
    } catch (error) {
      // Keep the last good catalog so a transient 5xx cannot empty the
      // provider selector or block saving other settings.
      toast("服务商目录加载失败", error.message, "err", 6000);
    }
  }

  function providerById(id) {
    return (STATE.providers || []).find((provider) => provider.id === id) || null;
  }

  function providerLabel(provider) {
    if (!provider) return "";
    const zh = provider.name_zh || provider.name || provider.id;
    if (provider.name && provider.name !== zh && !/[\u4e00-\u9fff]/.test(provider.name)) {
      return `${zh}（${provider.name}）`;
    }
    return zh;
  }

  function populateProviderSelect() {
    const select = $("#setProvider");
    if (!select) return;
    const current = select.value;
    const featured = STATE.providers.filter((provider) => provider.featured);
    const rest = STATE.providers.filter((provider) => !provider.featured);
    const option = (provider) => `<option value="${escapeHtml(provider.id)}">${escapeHtml(providerLabel(provider))}</option>`;
    select.innerHTML = `<option value="">请选择模型服务商</option>` +
      (featured.length ? `<optgroup label="常用 / Featured">${featured.map(option).join("")}</optgroup>` : "") +
      (rest.length ? `<optgroup label="全部 / All (${rest.length})">${rest.map(option).join("")}</optgroup>` : "") +
      `<option value="custom">自定义 OpenAI 兼容服务</option>`;
    select.value = current;
    if (select.value !== current) select.value = "";
  }

  function updateProviderNote(id) {
    const element = $("#providerNote");
    if (!element) return;
    const provider = providerById(id);
    if (!provider) {
      element.innerHTML = id === "custom"
        ? "填写完整端点、模型 ID 与 API Key；适用于任意 OpenAI 兼容或 Anthropic 兼容服务。"
        : "选择服务商后自动填入 Base URL 与模型列表。目录来自内置参考值，可一键更新。";
      return;
    }
    const env = (provider.env || []).join(", ");
    element.innerHTML = `${escapeHtml(provider.notes || "")}${provider.notes ? "<br>" : ""}` +
      `API Key 环境变量：<code>${escapeHtml(env || "—")}</code>` +
      ` · <a href="${escapeHtml(provider.doc || "#")}" target="_blank" rel="noreferrer">文档</a>` +
      ` · <a href="${escapeHtml(provider.release_url || provider.doc || "#")}" target="_blank" rel="noreferrer">发布公告</a>`;
  }

  function populateModels(providerId, current) {
    const select = $("#setModel");
    if (!select) return;
    const provider = providerById(providerId);
    let list = provider ? (provider.models || []).map((model) => ({
      id: model.id, name: model.name || model.id, meta: model,
    })) : [];
    if (providerId === "custom") {
      list = (STATE.models || []).map((id) => ({ id, name: id, meta: null }));
    }
    if (current && !list.some((item) => item.id === current) && providerId) {
      list.unshift({ id: current, name: current, meta: null });
    }
    select.innerHTML = `<option value="">请选择模型</option>` +
      list.map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.name)}${item.name !== item.id ? ` · ${escapeHtml(item.id)}` : ""}</option>`).join("");
    select.value = current && list.some((item) => item.id === current) ? current : "";
    updateProviderNote(providerId);
    syncChatModelSelect();
  }

  function syncChatModelSelect() {
    const select = $("#modelSelect");
    if (!select) return;
    const llm = (STATE.config && STATE.config.llm) || {};
    const provider = providerById(llm.provider);
    const isCustom = llm.provider === "custom";
    let list = provider ? (provider.models || []).map((model) => ({ id: model.id, name: model.name || model.id })) : [];
    if (isCustom) list = (STATE.models || []).map((id) => ({ id, name: id }));
    const current = llm.model || "";
    if (current && (provider || isCustom) && !list.some((item) => item.id === current)) {
      list.unshift({ id: current, name: current });
    }
    if (!list.length) {
      select.innerHTML = `<option value="">请先选择模型</option>`;
      return;
    }
    select.innerHTML = list.map((item) =>
      `<option value="${escapeHtml(item.id)}">${escapeHtml(item.name)}</option>`).join("");
    select.value = current && list.some((item) => item.id === current) ? current : list[0].id;
  }

  async function loadStatus() {
    try {
      const status = await api("/api/status");
      STATE.status = status;
      const llmOk = status.llm && status.llm.configured;
      const label = llmOk ? (status.llm.model || "模型") : T("top.noModel", "未选择模型服务");
      $("#llmStatus").innerHTML = `<i class="dot ${llmOk ? "ok" : "warn"}"></i><span>${escapeHtml(label)}</span>`;
      $("#llmStatus").title = llmOk
        ? `${status.llm.provider_name || status.llm.provider || ""} · ${status.llm.base_url} · ${status.llm.model}`
        : "点击设置选择服务商并填写 API Key";
      $("#mcpStatus").innerHTML = `<i class="dot ok"></i><span>MCP</span>`;
      $("#mcpStateText").textContent = "stdio / HTTP / SSE · 20 tools";
      const libraryInfo = status.library || {};
      const libPill = $("#libraryStatusPill");
      if (libPill) {
        const count = libraryInfo.docs || 0;
        const countText = count
          ? `${count} ${T("top.books", "本")}`
          : T("top.library", "教材库");
        libPill.innerHTML = `<i class="dot ${count ? "ok" : "warn"}"></i><span>${escapeHtml(countText)}</span>`;
        libPill.title = libraryInfo.running ? "正在建立索引…" : `已索引 ${libraryInfo.indexed_pages || 0} 页`;
      }
      syncChatModelSelect();
    } catch (error) {
      $("#llmStatus").innerHTML = `<i class="dot err"></i><span>服务未连接</span>`;
      toast("无法连接本地服务", error.message, "err");
    }
  }

  async function loadConfig() {
    try {
      const result = await api("/api/config");
      STATE.config = result.config;
      fillSettings(result.config);
      if (window.Library) window.Library.applyConfig(result.config);
    } catch (error) { /* ignore */ }
  }

  function fillSettings(cfg) {
    if (!cfg) return;
    const llm = cfg.llm || {};
    const providerId = llm.provider || "";
    $("#setProvider").value = providerId;
    if ($("#setProvider").value !== providerId) $("#setProvider").value = "";
    $("#setProtocol").value = llm.protocol || llm.api_style || "openai";
    $("#setBaseUrlOpenai").value = llm.base_url_openai || (llm.protocol !== "anthropic" ? (llm.base_url || "") : "");
    $("#setBaseUrlAnthropic").value = llm.base_url_anthropic || (llm.protocol === "anthropic" ? (llm.base_url || "") : "");
    $("#setBaseUrl").value = llm.base_url || "";
    $("#setApiKey").value = "";
    $("#setModelCustom").value = "";
    $("#setApiKey").placeholder = llm.has_key
      ? `已配置 ${llm.key_hint || ""}（留空不修改）`
      : "填写该服务商的 API Key";
    $("#setTemp").value = llm.temperature != null ? llm.temperature : 0.25;
    $("#setMaxTokens").value = llm.max_tokens || 16384;
    $("#setReasoning").value = llm.reasoning_effort || "";
    $("#setThinkingBudget").value = llm.thinking_budget || 0;
    populateModels(providerId, llm.model || "");
    STATE.providerChanged = false;
    fillProfileForm(profileFor(providerId, llm.model || ""));
    const ui = cfg.ui || {};
    const library = cfg.library || {};
    const usageCfg = cfg.usage || {};
    const updateCfg = cfg.update || {};
    $("#setLang").value = ui.lang || "zh";
    $("#setShowThinking").checked = ui.show_thinking === true;
    $("#setShowCitations").checked = ui.show_citations === true;
    $("#setAutoUpdate").checked = updateCfg.auto_check !== false;
    $("#setUpdateUseModel").checked = updateCfg.use_model !== false;
    $("#setAutoIndex").checked = library.auto_index !== false;
    $("#setOcrFirst").value = library.ocr_first_pages != null ? library.ocr_first_pages : 2;
    $("#setAutoPeak").checked = usageCfg.auto_peak !== false;
    if ($("#anPoints")) {
      $("#anPoints").value = Number(ui.scan_points) > 0 ? Number(ui.scan_points) : 10000;
    }
    if ($("#stSweep")) {
      $("#stSweep").checked = ui.stress_sweep_enabled !== false;
      $("#stSweepPoints").value = Number(ui.stress_sweep_points) > 0
        ? Number(ui.stress_sweep_points) : 21;
      $("#stSpan").value = Math.round((Number(ui.stress_freq_span) || 0.2) * 100);
    }
    STATE.showThinking = ui.show_thinking === true;
    STATE.showCitations = ui.show_citations === true;
    syncDisplayToggles();
    const paths = cfg.paths || {};
    const readout = $("#settingsPathReadout");
    if (readout) {
      readout.innerHTML = `<div><span>安装目录</span><b>${escapeHtml(paths.install_dir || "—")}</b></div>` +
        `<div><span>数据目录</span><b>${escapeHtml(paths.data_dir || "—")}</b></div>` +
        `<div><span>当前教材库</span><b>${escapeHtml(paths.current_library || "未设置")}</b></div>`;
    }
    $("#saveHint").textContent = "";
  }

  function settingsPayload() {
    const providerId = $("#setProvider").value;
    const provider = providerById(providerId);
    const protocol = $("#setProtocol").value || "openai";
    const model = ($("#setModelCustom").value.trim() || $("#setModel").value || "").trim();
    const baseOpenai = $("#setBaseUrlOpenai").value.trim();
    const baseAnthropic = $("#setBaseUrlAnthropic").value.trim();
    const baseTyped = $("#setBaseUrl").value.trim();
    let baseUrl = baseTyped;
    if (protocol === "openai" && baseOpenai) baseUrl = baseOpenai;
    if (protocol === "anthropic" && baseAnthropic) baseUrl = baseAnthropic;
    const profile = profileFromForm();
    const profiles = {};
    if (providerId && model) profiles[`${providerId}/${model}`] = profile;
    const llm = {
      provider: providerId,
      provider_name: provider ? providerLabel(provider) : (providerId === "custom" ? "Custom" : ""),
      protocol,
      api_style: protocol === "custom" ? "as_is" : protocol,
      base_url: baseUrl,
      base_url_openai: baseOpenai,
      base_url_anthropic: baseAnthropic,
      model,
      temperature: Number($("#setTemp").value),
      max_tokens: Number($("#setMaxTokens").value),
      reasoning_effort: $("#setReasoning").value || "",
      thinking_budget: Number($("#setThinkingBudget").value || 0),
      auth_header: provider ? provider.auth_header : "Authorization",
      auth_prefix: provider ? provider.auth_prefix : "Bearer ",
      chat_path: provider ? provider.chat_path : "",
      extra_headers: {},
      model_profile: profile,
      profiles,
    };
    const key = $("#setApiKey").value.trim();
    if (key) llm.api_key = key;
    return { llm, key, providerId, provider, model, protocol };
  }

  async function openSettings() {
    $("#settingsModal").classList.remove("hidden");
    if (!STATE.providers.length) await loadProviders();
    await loadConfig();
    loadMcpCode();
    loadCatalogStatus();
    loadUsage();
    switchSettingsTab("service");
  }

  function closeSettings() {
    $("#settingsModal").classList.add("hidden");
    $("#saveHint").textContent = "";
  }

  function switchSettingsTab(name) {
    $$(".settings-tab").forEach((button) => button.classList.toggle("active", button.dataset.tab === name));
    $$(".settings-pane").forEach((pane) => pane.classList.toggle("active", pane.dataset.pane === name));
  }

  async function saveSettings() {
    const { llm, key, providerId, provider, model } = settingsPayload();
    if (providerId) {
      if (!llm.base_url || !model) {
        return toast("配置不完整", "请填写 Base URL 和模型 ID。", "amber");
      }
      const existingKey = !!(STATE.config && STATE.config.llm && STATE.config.llm.has_key);
      if (!key && (!existingKey || STATE.providerChanged)) {
        return toast("请填写 API Key", "每个服务商都需要使用你自己的 Key；本软件不内置任何厂商密钥。", "amber", 5000);
      }
    }
    const payload = {
      ui: {
        lang: $("#setLang").value || "zh",
        assistant_open: !!STATE.config?.ui?.assistant_open,
        show_thinking: $("#setShowThinking").checked,
        show_citations: $("#setShowCitations").checked,
      },
      library: {
        auto_index: $("#setAutoIndex").checked,
        ocr_first_pages: Number($("#setOcrFirst").value || 0),
      },
      update: {
        auto_check: $("#setAutoUpdate").checked,
        use_model: $("#setUpdateUseModel").checked,
      },
      usage: {
        auto_peak: $("#setAutoPeak").checked,
      },
    };
    if (providerId) payload.llm = llm;
    try {
      const result = await api("/api/config", { method: "POST", body: payload });
      STATE.config = result.config;
      $("#setApiKey").value = "";
      $("#saveHint").textContent = "已保存";
      STATE.showThinking = $("#setShowThinking").checked;
      STATE.showCitations = $("#setShowCitations").checked;
      syncDisplayToggles();
      if (window.Library) window.Library.applyConfig(result.config);
      if (window.I18N) {
        window.I18N.setLang(payload.ui.lang);
      }
      await loadStatus();
      await loadConfig();
      toast("设置已保存", providerId
        ? `${provider ? providerLabel(provider) : "自定义服务"} · ${model}`
        : "界面、教材与更新设置已保存", "ok");
    } catch (error) {
      toast("保存失败", error.message + (error.data && error.data.hint ? ` ${error.data.hint}` : ""), "err", 6000);
    }
  }

  async function testLlm() {
    const output = $("#llmTestResult");
    output.className = "inline-status";
    output.textContent = "测试中…";
    const { llm, key, providerId } = settingsPayload();
    if (!providerId || !llm.base_url || !llm.model) {
      output.className = "inline-status err";
      output.textContent = "请先选择服务商，并填写 Base URL 与模型 ID。";
      return;
    }
    const existingKey = !!(STATE.config && STATE.config.llm && STATE.config.llm.has_key);
    if (!key && (!existingKey || STATE.providerChanged)) {
      output.className = "inline-status err";
      output.textContent = "请填写该服务商的 API Key。";
      return;
    }
    try {
      const result = await api("/api/config/test", { method: "POST", body: { llm } });
      output.className = "inline-status ok";
      output.textContent = `连接成功 · ${result.model} · ${result.latency_s}s`;
      toast("模型连接成功", `${result.model}，延迟 ${result.latency_s}s。`, "ok");
    } catch (error) {
      output.className = "inline-status err";
      output.textContent = error.message + (error.data && error.data.hint ? `（${error.data.hint}）` : "");
    }
  }

  function modelMeta(providerId, modelId) {
    const provider = providerById(providerId);
    if (!provider) return null;
    return (provider.models || []).find((model) => model.id === modelId) || null;
  }

  function profileFor(providerId, modelId) {
    const base = modelMeta(providerId, modelId) || {};
    const llm = (STATE.config && STATE.config.llm) || {};
    const saved = (llm.profiles || {})[`${providerId}/${modelId}`] ||
      (llm.model_profile || {});
    const profile = Object.assign({}, base, saved || {});
    profile.pricing = Object.assign({}, base.pricing || {}, (saved && saved.pricing) || {});
    return profile;
  }

  function setProfileField(id, value) {
    const element = $(id);
    if (!element) return;
    element.value = value == null ? "" : value;
  }

  function fillProfileForm(profile) {
    profile = profile || {};
    const pricing = profile.pricing || {};
    const peak = pricing.peak || {};
    const off = pricing.off_peak || {};
    STATE.profileMeta = profile;
    $("#profileName").textContent = `${profile.name || profile.id || "—"}${profile.id && profile.name && profile.name !== profile.id ? ` · ${profile.id}` : ""}`;
    $("#profileNote").textContent = `${providerById($("#setProvider").value)?.name_zh || ""} ${profile.notes || ""}`.trim();
    setProfileField("#mpContext", profile.context || 0);
    setProfileField("#mpMaxOutput", profile.max_output || 0);
    setProfileField("#mpConcurrency", profile.concurrency || 0);
    $("#mpVision").checked = !!profile.vision;
    $("#mpAudio").checked = !!profile.audio;
    $("#mpTools").checked = profile.tool_call !== false;
    $("#mpJson").checked = profile.json_output !== false;
    $("#mpReasoning").checked = !!profile.reasoning;
    $("#mpResponses").checked = !!profile.responses_api;
    $("#mpAnthropic").checked = !!profile.anthropic_api;
    $("#mpFim").checked = !!profile.fim;
    $("#mpCurrency").value = pricing.currency || "CNY";
    setProfileField("#mpCacheHit", pricing.input_cache_hit ?? 0);
    setProfileField("#mpCacheMiss", pricing.input_cache_miss ?? 0);
    setProfileField("#mpOutput", pricing.output ?? 0);
    setProfileField("#mpPeakHit", peak.input_cache_hit ?? "");
    setProfileField("#mpPeakMiss", peak.input_cache_miss ?? "");
    setProfileField("#mpPeakOutput", peak.output ?? "");
    setProfileField("#mpOffHit", off.input_cache_hit ?? "");
    setProfileField("#mpOffMiss", off.input_cache_miss ?? "");
    setProfileField("#mpOffOutput", off.output ?? "");
    const schedule = profile.pricing_schedule || {};
    setProfileField("#mpOffStart", schedule.off_peak_start || "00:30");
    setProfileField("#mpOffEnd", schedule.off_peak_end || "08:30");
    setProfileField("#mpTimezone", schedule.timezone || "Asia/Shanghai");
    setProfileField("#mpRelease", profile.release || "");
    setProfileField("#mpNotes", profile.notes || "");
  }

  function profileFromForm() {
    const numberOrEmpty = (id) => {
      const value = ($(id).value || "").trim();
      return value === "" ? undefined : Number(value);
    };
    const profile = {
      context: Number($("#mpContext").value || 0),
      max_output: Number($("#mpMaxOutput").value || 0),
      concurrency: Number($("#mpConcurrency").value || 0),
      vision: $("#mpVision").checked,
      audio: $("#mpAudio").checked,
      tool_call: $("#mpTools").checked,
      json_output: $("#mpJson").checked,
      reasoning: $("#mpReasoning").checked,
      responses_api: $("#mpResponses").checked,
      anthropic_api: $("#mpAnthropic").checked,
      fim: $("#mpFim").checked,
      release: $("#mpRelease").value.trim(),
      notes: $("#mpNotes").value.trim(),
      pricing: {
        currency: $("#mpCurrency").value || "CNY",
        input_cache_hit: Number($("#mpCacheHit").value || 0),
        input_cache_miss: Number($("#mpCacheMiss").value || 0),
        output: Number($("#mpOutput").value || 0),
      },
    };
    const h = numberOrEmpty("#mpPeakHit");
    const m = numberOrEmpty("#mpPeakMiss");
    const o = numberOrEmpty("#mpPeakOutput");
    if (h !== undefined || m !== undefined || o !== undefined) {
      profile.pricing.peak = {
        input_cache_hit: h || 0, input_cache_miss: m || 0, output: o || 0,
      };
    }
    const oh = numberOrEmpty("#mpOffHit");
    const om = numberOrEmpty("#mpOffMiss");
    const oo = numberOrEmpty("#mpOffOutput");
    if (oh !== undefined || om !== undefined || oo !== undefined) {
      profile.pricing.off_peak = {
        input_cache_hit: oh || 0, input_cache_miss: om || 0, output: oo || 0,
      };
    }
    profile.pricing_schedule = {
      off_peak_start: $("#mpOffStart").value || "00:30",
      off_peak_end: $("#mpOffEnd").value || "08:30",
      timezone: $("#mpTimezone").value.trim() || "Asia/Shanghai",
    };
    return profile;
  }

  async function loadMcpCode() {
    try {
      const result = await api("/api/mcp/config");
      const snippet = result.snippet || "{}";
      $("#settingsMcpCode").textContent = snippet;
      $("#aboutMcpCode").textContent = snippet;
      return snippet;
    } catch (error) {
      return "{}";
    }
  }

  async function refreshMcpCode() {
    const snippet = await loadMcpCode();
    if (STATE.view === "about") $("#aboutMcpCode").textContent = snippet;
  }

  async function copyMcpConfig() {
    try {
      const result = await api("/api/mcp/config");
      await copyText(result.snippet || JSON.stringify(result.servers || {}, null, 2), "MCP 配置已复制。");
    } catch (error) { toast("复制失败", error.message, "err"); }
  }

  /* ------------------------------------------------------------------ */
  /* Catalog and usage settings                                         */
  /* ------------------------------------------------------------------ */
  function catalogLog(line) {
    STATE.catalogLog.push(`[${new Date().toLocaleTimeString()}] ${line}`);
    const element = $("#catalogLog");
    if (element) element.textContent = STATE.catalogLog.slice(-80).join("\n");
  }

  async function loadCatalogStatus() {
    try {
      const summary = await api("/api/providers/summary");
      const element = $("#catalogStatus");
      if (element) {
        const en = window.I18N && window.I18N.lang === "en";
        element.innerHTML = `${en ? "Built-in" : "内置"} <b>${summary.providers}</b> ${en ? "providers" : "家"} · <b>${summary.models}</b> ${en ? "models" : "个模型"}` +
          (summary.override_updated_at ? ` · ${en ? "override updated" : "覆盖层更新于"} ${escapeHtml(summary.override_updated_at)}` : "") +
          (summary.backup_available ? ` · ${en ? "rollback available" : "可回滚"}` : "");
      }
      return summary;
    } catch (error) {
      const element = $("#catalogStatus");
      if (element) element.textContent = error.message;
      return null;
    }
  }

  async function catalogUpdate(mode) {
    const labels = {
      models_dev: "从 models.dev 更新",
      provider_api: "读取当前厂商 /models",
      announcements: "读取官方公告",
      ai: "AI 校对更新",
    };
    if (mode === "ai" && !window.confirm("AI 校对更新会把当前目录与官方公告摘要发送给模型。AI 可能出错，需要逐项核对。继续？")) {
      return;
    }
    catalogLog(`${labels[mode]}：开始…`);
    try {
      const body = { mode };
      if (mode === "announcements") body.provider_id = $("#setProvider").value;
      if (mode === "ai") body.provider_ids = $("#setProvider").value ? [$("#setProvider").value] : [];
      const result = await api("/api/providers/update", { method: "POST", body });
      if (result.ok === false) {
        catalogLog(`${labels[mode]} 失败：${result.message || "未知错误"}`);
        toast("目录更新失败", result.message || "", "err", 7000);
      } else {
        catalogLog(`${labels[mode]} 完成：${result.message || ""}`);
        if (result.warnings && result.warnings.length) {
          catalogLog(`警告：${result.warnings.slice(0, 12).join("；")}`);
        }
        if (result.candidates && result.candidates.length) {
          catalogLog(`候选模型：${result.candidates.slice(0, 30).join(", ")}`);
        }
        if (result.added != null) catalogLog(`新增模型：${result.added}`);
        toast("目录更新完成", result.message || "", "ok", 6000);
        await loadProviders();
        await loadCatalogStatus();
      }
    } catch (error) {
      catalogLog(`${labels[mode]} 失败：${error.message}`);
      toast("目录更新失败", error.message, "err", 7000);
    }
  }

  async function catalogRollback() {
    try {
      const result = await api("/api/providers/rollback", { method: "POST", body: {} });
      catalogLog(result.message || "已回滚");
      toast(result.ok ? "已回滚" : "无法回滚", result.message || "", result.ok ? "ok" : "amber");
      await loadProviders();
      await loadCatalogStatus();
    } catch (error) { toast("回滚失败", error.message, "err"); }
  }

  async function catalogReset() {
    try {
      const result = await api("/api/providers/reset", { method: "POST", body: {} });
      catalogLog(result.message || "已恢复内置目录");
      toast("已恢复内置目录", result.message || "", "ok");
      await loadProviders();
      await loadCatalogStatus();
    } catch (error) { toast("恢复失败", error.message, "err"); }
  }

  async function loadUsage() {
    try {
      const data = await api("/api/usage/summary");
      const cards = $("#usageCards");
      if (cards) {
        const item = (label, value, sub) =>
          `<div class="usage-card"><span>${escapeHtml(label)}</span><b>${escapeHtml(value)}</b><small>${escapeHtml(sub || "")}</small></div>`;
        const all = data.all || {};
        const today = data.today || {};
        const en = window.I18N && window.I18N.lang === "en";
        const todayReq = en ? "Today requests" : "今日请求";
        const todayCost = en ? "Today cost" : "今日费用";
        const allReq = en ? "Total requests" : "累计请求";
        const allCost = en ? "Total cost" : "累计费用";
        const cacheLabel = en ? "cache hit" : "缓存命中";
        cards.innerHTML =
          item(todayReq, String(today.requests || 0), `${fmtTokens(today.total_tokens)} tokens`) +
          item(todayCost, fmtMoney(today.cost, Object.keys(today.currencies || {})[0] || "CNY"), `${cacheLabel} ${(100 * (today.cache_hit_rate || 0)).toFixed(1)}%`) +
          item(allReq, String(all.requests || 0), `${fmtTokens(all.total_tokens)} tokens`) +
          item(allCost, fmtMoney(all.cost, Object.keys(all.currencies || {})[0] || "CNY"), `${cacheLabel} ${(100 * (all.cache_hit_rate || 0)).toFixed(1)}%`);
      }
      const tbody = $("#usageTable");
      if (tbody) {
        const rows = (data.recent || []).map((row) =>
          `<tr><td>${escapeHtml(String(row.time || "").replace("T", " "))}</td><td>${escapeHtml(row.model || "")}</td>` +
          `<td>${fmtTokens(row.prompt_tokens)}</td><td>${fmtTokens(row.completion_tokens)}</td>` +
          `<td>${(100 * (row.cache_hit_rate || 0)).toFixed(1)}%</td>` +
          `<td>${fmtMoney(row.cost, row.currency)}</td></tr>`).join("");
        tbody.innerHTML = rows || `<tr><td colspan="6">暂无记录</td></tr>`;
      }
      if ($("#usagePath")) $("#usagePath").textContent = data.log_path || "";
    } catch (error) { /* ignore */ }
  }

  /* ------------------------------------------------------------------ */
  /* Agent chat                                                         */
  /* ------------------------------------------------------------------ */
  let chatAutoScroll = true;

  function syncDisplayToggles() {
    $$("#btnToggleThinking, #qaToggleThinking").forEach((button) =>
      button.classList.toggle("active", !!STATE.showThinking));
    $$("#btnToggleCitations, #qaToggleCitations").forEach((button) =>
      button.classList.toggle("active", !!STATE.showCitations));
  }

  function toggleDisplay(kind) {
    if (kind === "thinking") STATE.showThinking = !STATE.showThinking;
    else STATE.showCitations = !STATE.showCitations;
    $$(".thinking-block").forEach((block) => { block.open = !!STATE.showThinking; });
    $$(".sources-block").forEach((block) => { block.open = !!STATE.showCitations; });
    syncDisplayToggles();
    api("/api/config", {
      method: "POST",
      body: { ui: { show_thinking: !!STATE.showThinking, show_citations: !!STATE.showCitations } },
    }).catch(() => {});
  }

  function initDisplayToggles() {
    ["#btnToggleThinking", "#qaToggleThinking"].forEach((selector) => {
      const button = $(selector);
      if (button) button.addEventListener("click", () => toggleDisplay("thinking"));
    });
    ["#btnToggleCitations", "#qaToggleCitations"].forEach((selector) => {
      const button = $(selector);
      if (button) button.addEventListener("click", () => toggleDisplay("citations"));
    });
    syncDisplayToggles();
  }

  function initChat() {
    const input = $("#chatInput");
    input.addEventListener("input", () => {
      input.style.height = "auto";
      input.style.height = Math.min(200, input.scrollHeight) + "px";
    });
    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendChat();
      }
    });
    input.addEventListener("paste", handlePaste);
    $("#btnSend").addEventListener("click", sendChat);
    $("#btnAttach").addEventListener("click", () => $("#fileInput").click());
    $("#fileInput").addEventListener("change", handleFiles);
    $("#chatScroll").addEventListener("scroll", () => {
      const element = $("#chatScroll");
      chatAutoScroll = element.scrollHeight - element.scrollTop - element.clientHeight < 90;
    });
    $$("#suggestGrid .suggest").forEach((button) => button.addEventListener("click", () => {
      $("#chatInput").value = button.dataset.prompt || "";
      $("#chatInput").focus();
      sendChat();
    }));
    ["#btnCopyMcp", "#btnCopyMcpSide", "#btnCopyMcpAbout", "#btnCopyMcpSettings"].forEach((selector) => {
      const button = $(selector);
      if (button) button.addEventListener("click", copyMcpConfig);
    });
    const composer = $(".composer-box");
    if (composer) {
      composer.addEventListener("dragover", (event) => {
        event.preventDefault();
        composer.classList.add("dragging");
      });
      composer.addEventListener("dragleave", () => composer.classList.remove("dragging"));
      composer.addEventListener("drop", (event) => {
        event.preventDefault();
        composer.classList.remove("dragging");
        handleFiles({ target: { files: event.dataTransfer.files, value: "" } });
      });
    }
    initToolList();
  }

  function initToolList() {
    const list = $("#toolList");
    if (!list) return;
    list.innerHTML = MCP_TOOLS.map(([name, label, description]) =>
      `<div class="tool-row" title="${escapeHtml(description)}"><span class="tiny-dot"></span><code>${escapeHtml(name)}</code><span>${escapeHtml(description)}</span></div>`
    ).join("");
  }

  function scrollChat() {
    if (!chatAutoScroll) return;
    const element = $("#chatScroll");
    element.scrollTop = element.scrollHeight;
  }

  function addUserMessage(container, text, attachments) {
    const wrap = document.createElement("div");
    wrap.className = "msg msg-user";
    const files = (attachments || []).map((attachment) =>
      `<span class="attachment-chip">${escapeHtml(attachment.name || "附件")} · ${escapeHtml(attachment.kind || "")}${attachment.image_count ? ` · ${attachment.image_count} img` : ""}</span>`).join("");
    wrap.innerHTML = `<div class="avatar">我</div><div class="msg-body"><div class="bubble">${escapeHtml(text).replace(/\n/g, "<br>")}${files ? `<div class="bubble-files">${files}</div>` : ""}</div></div>`;
    (container || $("#messages")).appendChild(wrap);
    scrollChat();
    return wrap;
  }

  function makeAssistant(container) {
    const wrap = document.createElement("div");
    wrap.className = "msg msg-assistant";
    wrap.innerHTML = `<div class="avatar"><svg><use href="#i-logo"/></svg></div>
      <div class="msg-body">
        <details class="thinking-block hidden">
          <summary><span>思考过程</span><small class="thinking-size"></small></summary>
          <pre class="thinking-text"></pre>
        </details>
        <div class="md"></div>
        <div class="typing"><i></i><i></i><i></i></div>
        <details class="sources-block hidden">
          <summary><span>参考来源</span><span class="source-count">0</span></summary>
          <div class="sources-list"></div>
        </details>
      </div>`;
    (container || $("#messages")).appendChild(wrap);
    scrollChat();
    return {
      wrap,
      body: $(".msg-body", wrap),
      md: $(".md", wrap),
      typing: $(".typing", wrap),
      thinking: $(".thinking-block", wrap),
      thinkingText: $(".thinking-text", wrap),
      thinkingSize: $(".thinking-size", wrap),
      sources: $(".sources-block", wrap),
      sourcesList: $(".sources-list", wrap),
      sourceCount: $(".source-count", wrap),
      buffer: "",
      reasoning: "",
      lastRender: 0,
      citations: new Set(),
      citationList: [],
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

  function pushReasoning(assistant, text) {
    if (!assistant || !assistant.thinking) return;
    assistant.reasoning += String(text || "");
    if (!assistant.reasoning) return;
    assistant.thinking.classList.remove("hidden");
    assistant.thinkingText.textContent = assistant.reasoning;
    assistant.thinkingSize.textContent = `${assistant.reasoning.length} 字`;
    assistant.thinking.open = !!STATE.showThinking;
    scrollChat();
  }

  function finalizeSources(assistant) {
    if (!assistant || !assistant.sources) return;
    const list = assistant.citationList || [];
    if (!list.length) {
      assistant.sources.classList.add("hidden");
      return;
    }
    assistant.sources.classList.remove("hidden");
    assistant.sourceCount.textContent = String(list.length);
    assistant.sourcesList.innerHTML = list.map((citation) => citationCard(citation)).join("");
    assistant.sources.open = !!STATE.showCitations;
  }

  function finishAssistant(assistant, content, reasoning) {
    if (assistant.typing) assistant.typing.remove();
    assistant.md.innerHTML = renderMarkdown(content || assistant.buffer || "");
    typesetMath(assistant.md);
    if (reasoning) pushReasoning(assistant, reasoning);
    if (assistant.thinking && !assistant.reasoning) assistant.thinking.classList.add("hidden");
    finalizeSources(assistant);
    scrollChat();
  }

  function addToolCard(assistant, event) {
    const card = document.createElement("div");
    card.className = "tool-card";
    card.dataset.callId = event.id;
    card.innerHTML = `
      <div class="tool-card-head">
        <div class="tool-icon"><svg><use href="#i-settings"/></svg></div>
        <div><b>${escapeHtml(event.label || event.name)}</b><small>${escapeHtml(event.name)}</small></div>
        <span class="spacer"></span><span class="tool-state">运行中</span>
      </div>
      <div class="tool-card-body"><span class="tool-summary">正在调用本地引擎…</span></div>`;
    assistant.body.appendChild(card);
    scrollChat();
    return card;
  }

  function updateToolCard(assistant, event) {
    const card = assistant.body.querySelector(`.tool-card[data-call-id="${CSS.escape(String(event.id))}"]`);
    if (!card) return;
    const state = $(".tool-state", card);
    state.className = `tool-state ${event.ok ? "ok" : "err"}`;
    state.textContent = event.ok ? `完成 · ${event.elapsed_ms || 0}ms` : "失败";
    const body = $(".tool-card-body", card);
    body.innerHTML = `<span class="tool-summary">${escapeHtml(event.summary || "无返回摘要")}</span>` +
      (event.data ? `<details><summary>查看工具返回</summary><pre>${escapeHtml(JSON.stringify(event.data, null, 2))}</pre></details>` : "");
    if (event.ok && event.data && event.data.components) appendDesignCard(assistant.body, event.data);
    scrollChat();
  }

  function appendDesignCard(container, design) {
    const components = design.components || {};
    const bandwidth = design.bandwidth || {};
    const values = [
      ["L", fmtComp(components, "L")],
      ["C1", fmtComp(components, "C1")],
      ["C2", fmtComp(components, "C2")],
    ];
    if (components.C3_pF > 0) values.push(["C3", fmtComp(components, "C3")]);
    else values.push([T("design.topology", "拓扑"), topologyName(design)]);
    const card = document.createElement("div");
    card.className = "design-card";
    card.innerHTML = `
      <div class="design-card-head">
        <svg style="width:16px;height:16px;color:var(--cyan)"><use href="#i-check"/></svg>
        <b>${escapeHtml(topologyName(design))}</b>
        <span class="tag green">节点法已复核</span>
      </div>
      <div class="design-values">${values.map(([key, value]) => `<div class="design-value"><span>${escapeHtml(key)}</span><b>${escapeHtml(value)}</b></div>`).join("")}</div>
      <div class="design-card-foot">
        <span class="metric">VSWR <b>${fmtFixed(design.vswr, 4)}</b></span>
        <span class="metric">S11 <b>${fmtS11(design.s11_db)}</b></span>
        <span class="metric">BW <b>${fmt(bandwidth.percent, 1)}%</b></span>
        <span class="metric">Q <b>${fmt(design.q, 2)}</b></span>
      </div>
      <div class="design-card-actions">
        <button class="btn tiny" data-action="open-design">在设计中打开</button>
        <button class="btn tiny ghost" data-action="report">导出报告</button>
      </div>`;
    container.appendChild(card);
  }

  function citationCard(citation) {
    if (!citation) return "";
    const snippet = escapeHtml(String(citation.snippet || "").slice(0, 500))
      .replace(/\[\[([^\]]+)\]\]/g, "<mark>$1</mark>");
    if (citation.kind === "textbook") {
      return `<div class="citation-card" data-citation-kind="textbook" data-doc-id="${citation.doc_id}" data-page="${citation.page}" data-rects="${escapeHtml(JSON.stringify(citation.rects || []))}">
        <img src="${escapeHtml(citation.crop_url || citation.thumb_url || "")}" alt="page">
        <div class="citation-copy"><b>${escapeHtml(citation.title || "教材")}</b><small>第 ${citation.page} 页</small><p>${snippet}</p></div>
        <button class="btn tiny" data-open-citation="1">打开</button>
      </div>`;
    }
    return `<div class="citation-card" data-citation-kind="documentation" data-category="${escapeHtml(citation.category || "")}" data-block="${escapeHtml(citation.block_id || "")}" data-line="${citation.line || 0}">
      <div class="citation-doc-icon"><svg><use href="#i-docs"/></svg></div>
      <div class="citation-copy"><b>${escapeHtml(citation.title || "文档")}</b><small>第 ${citation.line || 0} 行</small><p>${snippet}</p></div>
      <button class="btn tiny" data-open-citation="1">打开</button>
    </div>`;
  }

  function addCitationCard(assistant, citation) {
    if (!citation || !assistant) return;
    const key = citation.kind === "textbook"
      ? `t:${citation.doc_id}:${citation.page}:${citation.snippet || ""}`
      : `d:${citation.category}:${citation.block_id}`;
    if (assistant.citations.has(key)) return;
    assistant.citations.add(key);
    assistant.citationList.push(citation);
    if (assistant.sourceCount) assistant.sourceCount.textContent = String(assistant.citationList.length);
    if (STATE.showCitations) finalizeSources(assistant);
  }

  document.addEventListener("click", (event) => {
    const action = event.target.closest("[data-action]");
    if (action) {
      if (!STATE.design) { toast("暂无设计", "请先完成一次设计。", "amber"); return; }
      if (action.dataset.action === "open-design") {
        fillFormFromDesign(STATE.design);
        showView("design");
        renderDesign(STATE.design);
      } else {
        exportReport();
      }
      return;
    }
    const citationButton = event.target.closest("[data-open-citation]");
    if (citationButton) {
      const card = citationButton.closest(".citation-card");
      if (!card) return;
      if (card.dataset.citationKind === "textbook" && window.Library) {
        let rects = [];
        try { rects = JSON.parse(card.dataset.rects || "[]"); } catch (e) { rects = []; }
        showView("library");
        window.Library.openPage(Number(card.dataset.docId), Number(card.dataset.page), rects);
      } else if (window.Docs) {
        showView("docs");
        window.Docs.openCitation(card.dataset.category, card.dataset.block, Number(card.dataset.line || 0));
      }
    }
  });

  function handlePaste(event) {
    const items = event.clipboardData && event.clipboardData.items;
    if (!items) return;
    const files = [];
    for (const item of items) {
      if (item.kind === "file") {
        const file = item.getAsFile();
        if (file) files.push(file);
      }
    }
    if (files.length) {
      event.preventDefault();
      handleFiles({ target: { files, value: "" } });
      return;
    }
    const text = event.clipboardData.getData("text/plain") || "";
    if (text.length > 20000) {
      event.preventDefault();
      uploadText(text);
    }
  }

  async function uploadText(text, name) {
    try {
      const info = await api("/api/upload-text", {
        method: "POST",
        body: { text, name: name || "" },
      });
      STATE.attachments.push(info);
      renderAttachmentBar();
      toast("剪贴板已作为附件", `${info.name} · ${info.chars || 0} 字符`, "ok");
    } catch (error) { toast("剪贴板附件失败", error.message, "err"); }
  }

  async function handleFiles(event) {
    const files = Array.from(event.target.files || []);
    if (event.target) event.target.value = "";
    const room = Math.max(0, 8 - STATE.attachments.length);
    for (const file of files.slice(0, room)) {
      if (file.size > 60 * 1024 * 1024) {
        toast("文件过大", `${file.name} 超过 60 MB。`, "err");
        continue;
      }
      const name = file.name || (file.type && file.type.startsWith("image/")
        ? `粘贴图片_${Date.now()}.png` : "粘贴附件");
      const placeholder = {
        id: null, name, kind: "上传中", chars: 0, uploading: true,
        progress: 0, size: file.size,
      };
      STATE.attachments.push(placeholder);
      renderAttachmentBar();
      try {
        const info = await uploadBlobWithProgress(file, (progress) => {
          placeholder.progress = progress;
          placeholder.kind = `上传中 ${Math.round(progress * 100)}%`;
          renderAttachmentBar();
        });
        const index = STATE.attachments.indexOf(placeholder);
        if (index >= 0) STATE.attachments[index] = info;
        renderAttachmentBar();
        const extra = info.note ? ` · ${info.note}` : "";
        toast("附件已解析", `${info.name} · ${info.kind} · ${info.chars || 0} 字符${info.image_count ? ` · ${info.image_count} 图` : ""}${extra}`, "ok", 5000);
      } catch (error) {
        const index = STATE.attachments.indexOf(placeholder);
        if (index >= 0) STATE.attachments.splice(index, 1);
        renderAttachmentBar();
        toast("附件失败", `${name}：${error.message}`, "err", 7000);
      }
    }
  }

  function readFileBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const value = String(reader.result || "");
        resolve(value.includes(",") ? value.split(",")[1] : value);
      };
      reader.onerror = () => reject(new Error("读取文件失败"));
      reader.readAsDataURL(file);
    });
  }

  function renderAttachmentBar() {
    const bar = $("#attachmentBar");
    if (!bar) return;
    bar.innerHTML = STATE.attachments.map((attachment, index) => {
      if (attachment.uploading) {
        const percent = Math.round((attachment.progress || 0) * 100);
        return `<span class="attachment-chip uploading" data-attach-index="${index}">
          <span class="attach-spinner"></span>
          ${escapeHtml(attachment.name)}
          <small>${percent}% · ${formatBytes(attachment.size)}</small>
          <span class="attach-progress"><i style="width:${percent}%"></i></span>
          <button data-remove-attach="${index}" title="Remove"><svg><use href="#i-close"/></svg></button>
        </span>`;
      }
      return `<span class="attachment-chip" data-attach-index="${index}" title="${escapeHtml(attachment.preview || "")}">
        ${escapeHtml(attachment.name)} <small>${escapeHtml(attachment.kind || "")} · ${attachment.chars || 0} 字${attachment.image_count ? ` · ${attachment.image_count} 图` : ""}</small>
        <button data-remove-attach="${index}" title="Remove"><svg><use href="#i-close"/></svg></button>
      </span>`;
    }).join("");
    $$("[data-remove-attach]", bar).forEach((button) => button.addEventListener("click", () => {
      STATE.attachments.splice(Number(button.dataset.removeAttach), 1);
      renderAttachmentBar();
    }));
  }

  function buildContext() {
    const context = { view: STATE.view, lang: window.I18N ? window.I18N.lang : "zh" };
    if (STATE.design) {
      context.design = {
        topology: STATE.design.topology,
        topology_name: STATE.design.topology_name,
        frequency_mhz: STATE.design.frequency_mhz,
        load: STATE.design.load,
        components: STATE.design.components,
        vswr: STATE.design.vswr,
        bandwidth_percent: (STATE.design.bandwidth || {}).percent,
      };
    }
    const selection = String(window.getSelection ? window.getSelection().toString() : "").slice(0, 1200);
    if (STATE.view === "library" && window.Library && window.Library.current()) {
      const current = window.Library.current();
      context.library = {
        doc_id: current.docId, page: current.page, title: current.title,
        selection: selection || "",
      };
    }
    if (STATE.view === "docs" && window.Docs && window.Docs.current()) {
      const current = window.Docs.current();
      context.docs = {
        category: current.category, title: current.title,
        heading: current.heading || "", line: current.line || 0,
        selection: selection || "",
      };
    }
    return context;
  }

  async function streamChat(payload, handlers = {}) {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      let detail = {};
      try { detail = await response.json(); } catch (e) { /* ignore */ }
      throw Object.assign(new Error(detail.message || `服务返回 HTTP ${response.status}`), { data: detail });
    }
    if (!response.body) throw new Error("浏览器不支持流式响应");
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let content = "";
    let errored = false;
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let index;
      while ((index = buffer.indexOf("\n\n")) >= 0) {
        const chunk = buffer.slice(0, index);
        buffer = buffer.slice(index + 2);
        let eventName = "message";
        let dataString = "";
        for (const line of chunk.split("\n")) {
          if (line.startsWith("event:")) eventName = line.slice(6).trim();
          else if (line.startsWith("data:")) dataString += line.slice(5).trim();
        }
        if (!dataString) continue;
        let data = {};
        try { data = JSON.parse(dataString); } catch (e) { continue; }
        if (eventName === "error") errored = true;
        if (eventName === "token") content += data.text || "";
        if (eventName === "done" && data.content) content = data.content;
        if (handlers.onEvent) handlers.onEvent(eventName, data);
      }
    }
    return { content, errored };
  }

  function handleChatEvent(eventName, data, assistant, options = {}) {
    if (eventName === "status") {
      if (assistant.typing && data.text) assistant.typing.title = data.text;
    } else if (eventName === "tool_call") {
      addToolCard(assistant, data);
    } else if (eventName === "tool_result") {
      updateToolCard(assistant, data);
    } else if (eventName === "design") {
      if (data.design) {
        STATE.design = mergeDesign(data.design);
        updateContext(STATE.design);
        if (data.design.steps && data.design.steps.length && STATE.view === "design") {
          renderDesign(STATE.design);
        } else {
          ensureFullDesign(data.design).catch(() => {});
        }
      }
    } else if (eventName === "token") {
      if (assistant.typing) { assistant.typing.remove(); assistant.typing = null; }
      pushToken(assistant, data.text || "");
    } else if (eventName === "reasoning") {
      pushReasoning(assistant, data.text || "");
    } else if (eventName === "citation") {
      addCitationCard(assistant, data);
    } else if (eventName === "usage") {
      STATE.lastStats = data;
      renderChatStats(data, options.statsTarget || "#chatStats");
    } else if (eventName === "error") {
      assistant.errored = true;
      if (assistant.typing) { assistant.typing.remove(); assistant.typing = null; }
      const hint = data.hint || "";
      assistant.md.innerHTML = `<div class="error-box"><b>智能体暂时不可用</b><p>${escapeHtml(data.message || "未知错误")}</p>${hint ? `<p class="muted">${escapeHtml(hint)}</p>` : ""}<button class="btn tiny" onclick="document.getElementById('btnSettings').click()">打开设置</button></div>`;
    } else if (eventName === "done") {
      if (assistant.typing) assistant.typing.remove();
    }
  }

  function renderChatStats(stats, target) {
    const element = typeof target === "string" ? $(target) : target;
    if (!element || !stats) return;
    const cache = (100 * (stats.cache_hit_rate || 0)).toFixed(1);
    const context = (100 * (stats.context_pct || 0)).toFixed(1);
    element.innerHTML =
      `<span class="stat-chip" title="Input / output tokens">↑${fmtTokens(stats.prompt_tokens)} ↓${fmtTokens(stats.completion_tokens)}</span>` +
      `<span class="stat-chip" title="Cache hit rate">${T("stats.cache", "缓存")} ${cache}%</span>` +
      `<span class="stat-chip" title="Context usage">${T("stats.context", "上下文")} ${context}%</span>` +
      `<span class="stat-chip" title="Estimated cost">${fmtMoney(stats.total_cost, stats.currency, stats.pricing_configured)}</span>` +
      `<span class="stat-chip ${stats.price_bucket === "off_peak" ? "off" : ""}">${escapeHtml(stats.price_bucket || "")}</span>`;
  }

  async function sendChat() {
    if (STATE.streaming) return;
    const input = $("#chatInput");
    const text = input.value.trim();
    if (!text && !STATE.attachments.length) return;
    if (STATE.attachments.some((item) => item.uploading)) {
      toast("附件仍在上传", "请等待上传百分比到 100% 后再发送。", "amber");
      return;
    }
    const llm = (STATE.config && STATE.config.llm) || {};
    if (!llm.provider || !llm.has_key || !llm.base_url || !llm.model) {
      toast("请先配置模型服务", "点击设置，选择服务商并填写你自己的 API Key。", "amber", 5000);
      openSettings();
      return;
    }
    if (!$("#modelSelect").value) {
      toast("请先选择模型", "在输入框下方选择模型。", "amber");
      return;
    }
    $("#chatWelcome").classList.add("hidden");
    const attachments = STATE.attachments.filter((item) => !item.uploading);
    const userText = text || "请阅读附件并总结与微波阻抗匹配相关的关键信息。";
    addUserMessage($("#messages"), userText, attachments);
    STATE.chat.push({
      role: "user",
      content: userText + (attachments.length ? `\n[附件: ${attachments.map((item) => item.name).join(", ")}]` : ""),
    });
    input.value = "";
    input.style.height = "auto";
    STATE.attachments = [];
    renderAttachmentBar();
    STATE.streaming = true;
    $("#btnSend").disabled = true;
    const assistant = makeAssistant($("#messages"));
    STATE.lastAssistant = assistant;

    try {
      const result = await streamChat({
        messages: STATE.chat.slice(-18),
        attachments: attachments.map((item) => ({ id: item.id, name: item.name })),
        model: $("#modelSelect").value,
        context: buildContext(),
      }, {
        onEvent: (eventName, data) => handleChatEvent(eventName, data, assistant),
      });
      if (assistant.typing) { assistant.typing.remove(); assistant.typing = null; }
      if (!assistant.errored) {
        finishAssistant(assistant, result.content || assistant.buffer || "（未收到回答）",
          result.reasoning || "");
        STATE.chat.push({ role: "assistant", content: result.content || assistant.buffer || "" });
        if (STATE.chat.length > 24) STATE.chat = STATE.chat.slice(-24);
      }
      scrollChat();
    } catch (error) {
      assistant.errored = true;
      if (assistant.typing) { assistant.typing.remove(); assistant.typing = null; }
      const hint = (error.data && error.data.hint) || "";
      assistant.md.innerHTML = `<div class="error-box"><b>智能体暂时不可用</b><p>${escapeHtml(error.message)}</p>${hint ? `<p class="muted">${escapeHtml(hint)}</p>` : ""}<button class="btn tiny" onclick="document.getElementById('btnSettings').click()">打开设置</button></div>`;
      toast("智能体调用失败", error.message, "err", 7000);
    } finally {
      STATE.streaming = false;
      $("#btnSend").disabled = false;
      scrollChat();
    }
  }

  function mergeDesign(design) {
    const existing = STATE.design;
    if (existing && existing.topology === design.topology &&
        existing.frequency_mhz === design.frequency_mhz &&
        existing.load && design.load && existing.load.r === design.load.r && existing.load.x === design.load.x) {
      return Object.assign({}, existing, design, {
        steps: existing.steps || design.steps,
        bandwidth: Object.assign({}, existing.bandwidth || {}, design.bandwidth || {}),
      });
    }
    return design;
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

  function updateContext(design) {
    if (!design) return;
    const tag = $("#contextTag");
    tag.textContent = topologyName(design);
    tag.className = "tag green";
    const components = design.components || {};
    $("#contextDesign").outerHTML = `
      <div id="contextDesign">
        <div class="context-values">
          <div><span>L</span><b>${escapeHtml(fmtComp(components, "L"))}</b></div>
          <div><span>VSWR</span><b>${fmtFixed(design.vswr, 4)}</b></div>
          <div><span>C1 / C2</span><b>${escapeHtml(fmtComp(components, "C1"))} / ${escapeHtml(fmtComp(components, "C2"))}</b></div>
          <div><span>BW</span><b>${fmt((design.bandwidth || {}).percent, 1)}%</b></div>
        </div>
      </div>`;
    miniChart.setData({
      steps: design.steps || [],
      load: design.load ? { re: design.load.r, im: design.load.x } : null,
      z0: design.z0 || 50,
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
    } catch (error) {
      toast("无法打开设计", error.message, "err");
    }
  }

  /* ------------------------------------------------------------------ */
  /* Design                                                             */
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
      if (overrides.L_uh !== undefined) {
        if (overrides.L_uh !== "" && Number(overrides.L_uh) > 0) {
          payload.L_uh = Number(overrides.L_uh);
        }
      } else {
        const value = $("#inL").value;
        if (value !== "" && Number(value) > 0) payload.L_uh = Number(value) / 1000;
      }
    }
    if (TOPO_HAS_C3[topology] && (!autoFixed || overrides.c3_pf !== undefined)) {
      const value = overrides.c3_pf !== undefined ? overrides.c3_pf : $("#inC3").value;
      if (value !== "" && Number(value) > 0) payload.c3_pf = Number(value);
    }
    return payload;
  }

  function setTopology(topology) {
    STATE.topology = topology;
    $$(".topo-pill").forEach((button) => button.classList.toggle("active", button.dataset.topology === topology));
    const desc = (window.I18N && window.I18N.lang === "en") ? TOPO_DESC_EN : TOPO_DESC;
    $("#topoDesc").textContent = desc[topology] || "";
    const c3Field = $("#c3Field");
    if (c3Field) c3Field.style.display = TOPO_HAS_C3[topology] ? "" : "none";
  }

  function localizeSelects() {
    const en = window.I18N && window.I18N.lang === "en";
    const names = {
      l_right: ["L-type (right)", "L型（右）"],
      l_left: ["L-type (left)", "L型（左）"],
      t: ["T-type", "T型"],
      pi1: ["π-type I", "π型Ⅰ"],
      pi2: ["π-type II", "π型Ⅱ"],
    };
    ["#anTopology", "#stTopology"].forEach((selector) => {
      const select = $(selector);
      if (!select) return;
      $$("option", select).forEach((option) => {
        const pair = names[option.value];
        if (pair) option.textContent = en ? pair[0] : pair[1];
      });
    });
  }

  function initDesignForm() {
    $$(".topo-pill").forEach((button) => button.addEventListener("click", () => {
      setTopology(button.dataset.topology);
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
      setTopology("auto");
      runDesign();
    });
    $("#btnScan").addEventListener("click", () => {
      if (!STATE.design && !$("#inL").value) return toast("需要电感 L", "先完成一次设计，或取消自动选值并填写 L。", "amber");
      fillAnalysisFromDesign();
      showView("analysis");
      runAnalysisScan();
    });
    $("#btnDesignToStress").addEventListener("click", () => {
      if (!STATE.design) return toast("暂无设计", "先完成一次设计。", "amber");
      fillStressFromDesign();
      showView("stress");
    });
    $("#btnPlay").addEventListener("click", () => {
      if (!smith) return;
      if (smith.playing) smith.pause(); else smith.play();
    });
    $("#btnResetChart").addEventListener("click", () => smith && smith.reset());
    $("#speedRange").addEventListener("input", (event) => smith && smith.setSpeed(Number(event.target.value)));
  }

  async function runDesign() {
    const button = $("#btnDesign");
    button.disabled = true;
    button.textContent = T("design.calculating", "计算中…");
    try {
      const payload = designPayload();
      const design = await api("/api/design", { method: "POST", body: payload });
      STATE.design = design;
      $("#emptyDesign").classList.add("hidden");
      $("#designResult").classList.remove("hidden");
      renderDesign(design);
      updateContext(design);
      toast(T("design.done", "设计完成"), `${topologyName(design)}：VSWR ${fmtFixed(design.vswr, 4)}，${design.components_display ? Object.values(design.components_display).filter((value) => value !== "—").join(" / ") : ""}`, "ok", 4200);
    } catch (error) {
      showDesignError(error);
    } finally {
      button.disabled = false;
      button.textContent = T("design.solve", "求解设计");
    }
  }

  function showDesignError(error) {
    $("#emptyDesign").classList.add("hidden");
    $("#designResult").classList.remove("hidden");
    $("#designKpis").innerHTML = `<div class="kpi-card bad"><span>计算失败</span><b>—</b><small>${escapeHtml(error.message)}</small></div>`;
    $("#stepList").innerHTML = `<div class="empty-mini">${escapeHtml(error.message)}${error.data && error.data.hint ? `<br><br>${escapeHtml(error.data.hint)}` : ""}</div>`;
    $("#warningList").innerHTML = `<li>${escapeHtml(error.message)}</li>${error.data && error.data.hint ? `<li>${escapeHtml(error.data.hint)}</li>` : ""}`;
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
    toast("无法完成该设计", error.message + (error.data && error.data.hint ? ` ${error.data.hint}` : ""), "err", 7000);
  }

  function fillFormFromDesign(design) {
    if (!design) return;
    $("#inFreq").value = design.frequency_mhz;
    $("#inZ0").value = design.z0 || 50;
    $("#inR").value = design.load ? design.load.r : 20;
    $("#inX").value = design.load ? design.load.x : 0;
    if (design.components) {
      $("#inL").value = (Number(design.components.L_uH) * 1000).toFixed(3);
      $("#inC3").value = Number(design.components.C3_pF).toFixed(4);
    }
    setTopology(design.topology && design.topology !== "auto" ? design.topology : "auto");
    $("#designResult").classList.remove("hidden");
    $("#emptyDesign").classList.add("hidden");
  }

  function renderDesign(design) {
    if (!design) return;
    $("#emptyDesign").classList.add("hidden");
    $("#designResult").classList.remove("hidden");
    const bandwidth = design.bandwidth || {};
    $("#designKpis").innerHTML = `
      <div class="kpi-card ${vswrClass(design.vswr)}"><span>VSWR</span><b>${fmtFixed(design.vswr, 4)}</b><small>target &lt; 1.5</small></div>
      <div class="kpi-card ${design.s11_db < -15 ? "good" : design.s11_db < -10 ? "warn" : "bad"}"><span>S11</span><b>${fmtS11(design.s11_db)}</b><small>RL ${fmtRL(design.return_loss_db)}</small></div>
      <div class="kpi-card ${bandwidth.percent > 20 ? "good" : bandwidth.percent > 8 ? "warn" : "bad"}"><span>${T("design.bw", "带宽")}</span><b>${fmt(bandwidth.percent, 1)}%</b><small>VSWR &lt; ${bandwidth.vswr_limit || 2}</small></div>
      <div class="kpi-card ${design.q < 2 ? "good" : design.q < 5 ? "warn" : "bad"}"><span>${T("design.q", "设计 Q")}</span><b>${fmt(design.q, 2)}</b><small>${T("design.qSub", "越低越宽")}</small></div>`;

    $("#smithSub").textContent = `${topologyName(design)} · ${T("design.trajectory", "匹配轨迹（负载 → 源）")}`;
    smith.setData({
      steps: design.steps || [],
      load: design.load ? { re: design.load.r, im: design.load.x } : null,
      z0: design.z0 || 50,
      scanPoints: [],
    });
    setTimeout(() => { smith.progress = 0; smith.play(); }, 180);

    $("#smithLegend").innerHTML = `<span><i class="legend-dot" style="background:#fb923c"></i>${T("design.load", "负载")}</span><span><i class="legend-dot" style="background:#34d399"></i>${T("design.match", "匹配点 50Ω")}</span>` +
      (design.steps || []).map((step, index) => `<span><i class="legend-dot" style="background:${["#22d3ee", "#34d399", "#fbbf24", "#a78bfa", "#f87171"][index % 5]}"></i>${escapeHtml(stepLabel(step))}</span>`).join("");

    const stepList = $("#stepList");
    stepList.innerHTML = (design.steps || []).map((step, index) => `
      <div class="step-item" data-step="${index}">
        <div class="step-num">${index + 1}</div>
        <div class="step-body"><b>${escapeHtml(stepLabel(step))}</b><small>${escapeHtml(stepNote(step))}</small></div>
        <span class="step-kind">${step.kind === "series" ? T("design.series", "串联") : T("design.shunt", "并联")}</span>
      </div>`).join("");
    $("#stepCount").textContent = `${(design.steps || []).length}`;
    $$(".step-item", stepList).forEach((element) => element.addEventListener("click", () => {
      $$(".step-item", stepList).forEach((item) => item.classList.remove("active"));
      element.classList.add("active");
      smith.progress = (Number(element.dataset.step) + 1) / Math.max(1, (design.steps || []).length);
      smith.draw();
    }));
    $("#formulaBox").innerHTML = `<b>${T("design.formula", "设计公式")}</b><br>${escapeHtml(design.formulas || "—")}`;
    $("#topoName").textContent = topologyName(design);
    $("#topoDiagram").innerHTML = topologySVG(design.topology, design.components || {});
    renderComponentGrid(design.components || {}, design.topology, design);

    lastBW = design.bandwidth;
    ChartKit.drawLineChart($("#bwCanvas"), Object.assign({ mark_mhz: design.frequency_mhz }, design.bandwidth || {}));
    const range = bandwidth.low_mhz && bandwidth.high_mhz ? `${fmt(bandwidth.low_mhz, 2)} – ${fmt(bandwidth.high_mhz, 2)} MHz` : T("design.noBand", "未找到合格频段");
    $("#bwTag").textContent = `${fmt(bandwidth.percent, 1)}%`;
    $("#bwNote").textContent = `${range} · ±60% · VSWR=${bandwidth.vswr_limit || 2}`;

    lastSens = design.sensitivity || [];
    drawSensitivity(lastSens);
    $("#sensNote").textContent = T("design.sensNote", "每根柱为该元件 ±5% 偏差下的最差 VSWR；绿色 <1.5，黄色 <2，红色 ≥2。");

    const warnings = (window.I18N && window.I18N.lang === "en" && (design.warnings_en || []).length)
      ? design.warnings_en
      : (design.warnings || []);
    $("#warnCount").textContent = warnings.length ? `${warnings.length}` : "0";
    $("#warningList").innerHTML = warnings.length
      ? warnings.map((warning) => `<li>${escapeHtml(warning)}</li>`).join("")
      : `<li class="ok">${T("design.noWarnings", "节点法复核通过，未发现显著的元件可实现性风险。仍建议用实际元件模型复核。")}</li>`;

    const alternatives = design.alternatives || [];
    const alternativePanel = $("#alternativesPanel");
    if (alternatives.length) {
      alternativePanel.classList.remove("hidden");
      $("#altGrid").innerHTML = alternatives.map((alternative, index) => `
        <div class="alt-card ${index === 0 ? "best" : ""}">
          <div class="alt-card-head"><b>${escapeHtml(topologyName({topology: alternative.topology, topology_name: alternative.topology_name}))}</b><span class="tag ${index === 0 ? "cyan" : ""}">${index === 0 ? T("design.recommended", "推荐") : ""}</span></div>
          <p>${escapeHtml(alternative.components_display ? Object.values(alternative.components_display).filter((value) => value !== "—").join(" / ") : "")}</p>
          <p class="alt-metric">BW ${fmt(alternative.bandwidth_percent, 1)}% · Q ${fmt(alternative.q, 2)}</p>
          <button class="btn tiny ghost" data-alt-topology="${escapeHtml(alternative.topology)}">${T("design.apply", "应用此方案")}</button>
        </div>`).join("");
      $$("[data-alt-topology]").forEach((button) => button.addEventListener("click", () => {
        setTopology(button.dataset.altTopology);
        runDesign();
      }));
    } else {
      alternativePanel.classList.add("hidden");
    }

    if (design.components) {
      $("#inL").value = (Number(design.components.L_uH) * 1000).toFixed(3);
      $("#inC3").value = Number(design.components.C3_pF).toFixed(4);
    }
    $("#designModeTag").textContent = "Python";
    setTimeout(() => smith._notify(), 0);
  }

  function renderComponentGrid(components, topology, design) {
    const en = window.I18N && window.I18N.lang === "en";
    const labels = en
      ? {
          L: "Inductor", C1: "Capacitor C1", C2: "Capacitor C2", C3: "Capacitor C3",
          Zin: "Input impedance", seriesL: "Series inductor", seriesC: "Series matching capacitor",
          srcShunt: "Shunt at source", loadShunt: "Shunt at load", either: "Series / shunt",
          srcSeries: "Series at source", checked: "Nodal verification",
        }
      : {
          L: "电感", C1: "电容 C1", C2: "电容 C2", C3: "电容 C3",
          Zin: "输入阻抗", seriesL: "串联电感", seriesC: "串联匹配电容",
          srcShunt: "源端并联", loadShunt: "负载端并联", either: "串联/并联",
          srcSeries: "源端串联", checked: "节点法复核值",
        };
    const shunt = topology === "l_right" || topology === "pi2"
      ? labels.srcShunt
      : topology === "l_left" || topology === "pi1" ? labels.loadShunt : labels.either;
    const items = [
      ["L", labels.L, fmtComp(components, "L"), labels.seriesL],
      ["C1", labels.C1, fmtComp(components, "C1"), shunt],
      ["C2", labels.C2, fmtComp(components, "C2"), labels.seriesC],
    ];
    if (components.C3_pF > 0) {
      const c3role = topology === "t" ? labels.srcSeries
        : topology === "pi1" ? labels.srcShunt : labels.loadShunt;
      items.push(["C3", labels.C3, fmtComp(components, "C3"), c3role]);
    } else {
      const zin = design && (design.input_impedance_display
        || (design.verification && design.verification.input_impedance
          ? `Z = ${Number(design.verification.input_impedance.re).toFixed(2)}${design.verification.input_impedance.im >= 0 ? "+" : ""}${Number(design.verification.input_impedance.im).toFixed(2)} Ω`
          : ""));
      items.push(["Zin", labels.Zin, zin || "—", labels.checked]);
    }
    $("#componentGrid").innerHTML = items.slice(0, 4).map(([symbol, name, value, role]) =>
      `<div class="component-item"><span>${escapeHtml(name)}<small>${escapeHtml(symbol)}</small></span><b>${escapeHtml(value)}</b><small>${escapeHtml(role)}</small></div>`
    ).join("");
  }

  function drawSensitivity(items) {
    const data = (items || []).map((item) => ({
      label: item.element,
      value: Number(item.worst_vswr) || 0,
      raw: item,
    }));
    ChartKit.drawBars($("#sensCanvas"), data, {
      unit: "",
      padLeft: 58,
      format: (value) => value.toFixed(2),
      colorFn: (item) => item.value <= 1.5 ? "#34d399" : item.value <= 2 ? "#fbbf24" : "#f87171",
    });
  }

  function topologySVG(topology, components) {
    const L = fmtComp(components, "L");
    const C1 = fmtComp(components, "C1");
    const C2 = fmtComp(components, "C2");
    const C3 = fmtComp(components, "C3");
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
    if (topology === "l_right") body = shunt(180, "C1", C1) + `<line x1="120" y1="83" x2="700" y2="83" stroke="#3c5978" stroke-width="1.8"/>` + series(330, "L", L) + series(470, "C2", C2);
    else if (topology === "l_left") body = `<line x1="120" y1="83" x2="700" y2="83" stroke="#3c5978" stroke-width="1.8"/>` + series(320, "L", L) + series(440, "C2", C2) + shunt(640, "C1", C1);
    else if (topology === "t") body = `<line x1="120" y1="83" x2="170" y2="83" stroke="#3c5978" stroke-width="1.8"/>` + series(170, "C3", C3) + `<line x1="232" y1="83" x2="700" y2="83" stroke="#3c5978" stroke-width="1.8"/>` + shunt(400, "L+C2", `${L} / ${C2}`) + series(540, "C1", C1);
    else if (topology === "pi1") body = shunt(180, "C3", C3) + `<line x1="120" y1="83" x2="700" y2="83" stroke="#3c5978" stroke-width="1.8"/>` + series(330, "L", L) + series(450, "C2", C2) + shunt(640, "C1", C1);
    else if (topology === "pi2") body = shunt(180, "C1", C1) + `<line x1="120" y1="83" x2="700" y2="83" stroke="#3c5978" stroke-width="1.8"/>` + series(330, "L", L) + series(450, "C2", C2) + shunt(640, "C3", C3);
    else body = `<line x1="120" y1="83" x2="700" y2="83" stroke="#3c5978" stroke-width="1.8"/>`;
    return `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
      <defs><radialGradient id="srcG" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#164e63"/><stop offset="100%" stop-color="#082f49"/></radialGradient></defs>
      <circle cx="60" cy="83" r="20" fill="url(#srcG)" stroke="#22d3ee" stroke-width="1.4"/>
      <text x="60" y="87" font-size="11" fill="#a5f3fc" text-anchor="middle">50Ω</text>
      <line x1="80" y1="83" x2="120" y2="83" stroke="#3c5978" stroke-width="1.8"/>
      ${body}
      <line x1="700" y1="83" x2="744" y2="83" stroke="#3c5978" stroke-width="1.8"/>
      <rect x="744" y="63" width="50" height="40" rx="7" fill="#211a0a" stroke="#d97706" stroke-width="1.4"/>
      <text x="769" y="87" font-size="11" fill="#fcd34d" text-anchor="middle">Z_L</text>
      <text x="60" y="175" font-size="9" fill="#5c7694" text-anchor="middle">SRC</text>
      <text x="769" y="175" font-size="9" fill="#5c7694" text-anchor="middle">LOAD</text>
    </svg>`;
  }

  /* ------------------------------------------------------------------ */
  /* Report                                                             */
  /* ------------------------------------------------------------------ */
  async function exportReport() {
    const design = STATE.design;
    if (!design) return toast("暂无设计", "请先完成一次设计，再导出报告。", "amber");
    try {
      const result = await api("/api/report", {
        method: "POST",
        body: {
          topology: design.topology,
          frequency_mhz: design.frequency_mhz,
          load_r: design.load.r,
          load_x: design.load.x,
          z0: design.z0 || 50,
          L_uh: design.components.L_uH,
          C1_pF: design.components.C1_pF,
          C2_pF: design.components.C2_pF,
          c3_pf: design.components.C3_pF,
          note: "Generated by Impedance Matching AI",
        },
      });
      toast("报告已生成", "正在新窗口打开 HTML 报告。", "ok");
      openDocument(result.url);
    } catch (error) {
      toast("导出失败", error.message, "err");
    }
  }

  /* ------------------------------------------------------------------ */
  /* Analysis                                                           */
  /* ------------------------------------------------------------------ */

  function initAnalysis() {
    scanChart = new SmithChart($("#scanCanvas"), { tooltip: $("#scanTooltip") });
    $("#anTopology").addEventListener("change", () => {
      $("#anC3row").style.display = ["t", "pi1", "pi2"].includes($("#anTopology").value) ? "" : "none";
    });
    $("#btnRunScan").addEventListener("click", runAnalysisScan);
    $("#btnStopScan").addEventListener("click", () => {
      if (STATE.scanAbort) STATE.scanAbort.abort();
    });
    $("#btnCompare").addEventListener("click", compareTopologies);
    $("#anTopology").dispatchEvent(new Event("change"));
  }

  function fillAnalysisFromDesign() {
    const design = STATE.design;
    if (design) {
      $("#anTopology").value = design.topology && design.topology !== "auto" ? design.topology : "l_right";
      $("#anFreq").value = design.frequency_mhz;
      $("#anZ0").value = design.z0 || 50;
      $("#anL").value = (Number(design.components.L_uH) * 1000).toFixed(3);
      $("#anR").value = design.load.r;
      $("#anX").value = design.load.x;
      $("#anTopology").dispatchEvent(new Event("change"));
    } else {
      $("#anFreq").value = $("#inFreq").value;
      $("#anZ0").value = $("#inZ0").value;
      $("#anL").value = $("#inL").value;
    }
  }

  function setProgressBar(prefix, done, total, label) {
    const bar = $(`#${prefix}Bar`);
    const text = $(`#${prefix}Text`);
    const pct = $(`#${prefix}Pct`);
    const wrap = $(`#${prefix}`);
    const percent = total > 0 ? Math.max(0, Math.min(100, 100 * done / total)) : 0;
    if (bar) bar.style.width = `${percent.toFixed(1)}%`;
    if (pct) pct.textContent = `${percent.toFixed(0)}%`;
    if (text) text.textContent = label || `${Math.round(done)} / ${Math.round(total)}`;
    if (wrap) wrap.classList.remove("hidden");
  }

  function stopScanAnimation() {
    if (!scanAnimation) return;
    if (scanAnimation.raf) clearTimeout(scanAnimation.raf);
    if (scanAnimation.resolve) scanAnimation.resolve(null);
    scanAnimation = null;
  }

  function startScanAnimation() {
    if (!scanAnimation || scanAnimation.raf) return;
    const anim = scanAnimation;
    anim.last = performance.now();
    const tick = (now) => {
      if (scanAnimation !== anim) return;
      const dt = Math.min(1000, Math.max(0, now - anim.last));
      anim.last = now;
      // Reveal at a human-visible pace, but finish a large scan in ~4 s.
      const rate = Math.max(2200, anim.total / 4);
      const count = Math.max(1, Math.round(rate * dt / 1000));
      const batch = anim.queue.splice(0, count);
      if (batch.length) scanChart.addScanPoints(batch);
      anim.revealed += batch.length;
      setProgressBar("scanProgress", anim.revealed, anim.total,
        `${anim.revealed} / ${anim.total} · 有效 ${anim.valid}`);
      if (anim.queue.length) {
        anim.raf = setTimeout(() => tick(performance.now()), 16);
        return;
      }
      anim.raf = null;
      if (anim.done) {
        const done = anim.done;
        anim.done = null;
        scanAnimation = null;
        scanChart.finishScan(done);
        done.__streamed = true;
        STATE.scan = done;
        renderScan(done);
        if (anim.resolve) anim.resolve(done);
        compareTopologies();
      }
    };
    anim.raf = setTimeout(() => tick(performance.now()), 16);
  }

  async function runAnalysisScan() {
    if (STATE.scanStreaming) {
      if (STATE.scanAbort) STATE.scanAbort.abort();
      return;
    }
    const button = $("#btnRunScan");
    const stop = $("#btnStopScan");
    const errorBox = $("#scanError");
    errorBox.textContent = "";
    button.disabled = true;
    button.textContent = T("analysis.running", "扫描中…");
    stop.classList.remove("hidden");
    STATE.scanStreaming = true;
    STATE.scanAbort = new AbortController();
    const topology = $("#anTopology").value;
    const z0 = Number($("#anZ0").value || 50);
    const body = {
      topology,
      frequency_mhz: Number($("#anFreq").value),
      z0,
      L_uh: Number($("#anL").value) / 1000,
      points_budget: Number($("#anPoints").value || 10000),
      c1_range_pf: [Number($("#anC1min").value), Number($("#anC1max").value)],
      c2_range_pf: [Number($("#anC2min").value), Number($("#anC2max").value)],
    };
    if (["t", "pi1", "pi2"].includes(topology)) {
      body.c3_range_pf = [Number($("#anC3min").value), Number($("#anC3max").value)];
    }
    let total = Number(body.points_budget) || 0;
    api("/api/config", {
      method: "POST",
      body: { ui: { scan_points: Number(body.points_budget) || 10000 } },
    }).catch(() => {});
    let evaluated = 0;
    let valid = 0;
    let finished = null;
    let animationDone;
    const animationPromise = new Promise((resolve) => { animationDone = resolve; });
    scanAnimation = {
      queue: [], total, revealed: 0, valid: 0, done: null,
      raf: null, last: 0, resolve: animationDone,
    };
    scanChart.beginScan(z0,
      STATE.design && STATE.design.load ? { re: STATE.design.load.r, im: STATE.design.load.x } : null);
    setProgressBar("scanProgress", 0, total, `0 / ${total}`);
    try {
      await streamEvents("/api/scan/stream", body, (eventName, data) => {
        if (eventName === "meta") {
          total = Number(data.total) || total;
          if (scanAnimation) scanAnimation.total = total;
          setProgressBar("scanProgress", 0, total,
            `0 / ${total} · ${data.per_dimension}^${data.dims}`);
        } else if (eventName === "points") {
          evaluated = Number(data.evaluated || evaluated);
          valid = Number(data.valid || valid);
          if (!scanAnimation) return;
          scanAnimation.valid = valid;
          scanAnimation.total = Math.max(scanAnimation.total, evaluated);
          const points = data.points || [];
          scanAnimation.queue.push(...points);
          startScanAnimation();
        } else if (eventName === "done") {
          finished = data;
          evaluated = Number(data.evaluated_count || evaluated);
          valid = Number(data.points_count || valid);
          if (!scanAnimation) return;
          scanAnimation.valid = valid;
          scanAnimation.total = Math.max(scanAnimation.total, evaluated);
          scanAnimation.done = data;
          if (!scanAnimation.queue.length && !scanAnimation.raf) {
            const done = scanAnimation.done;
            scanAnimation.done = null;
            scanAnimation = null;
            scanChart.finishScan(done);
            done.__streamed = true;
            STATE.scan = done;
            renderScan(done);
            animationDone(done);
            compareTopologies();
          } else {
            startScanAnimation();
          }
        }
      }, STATE.scanAbort.signal);
      if (!finished) throw new Error("扫描未返回结果");
      if (scanAnimation) await animationPromise;
      if (finished && !STATE.scan) {
        finished.__streamed = true;
        STATE.scan = finished;
        renderScan(finished);
      }
    } catch (error) {
      stopScanAnimation();
      if (error.name === "AbortError") {
        toast("扫描已停止", `已计算并显示 ${evaluated} 个真实点。`, "amber");
      } else {
        errorBox.textContent = error.message + (error.data && error.data.hint ? ` ${error.data.hint}` : "");
        toast("扫描失败", error.message + (error.data && error.data.hint ? ` ${error.data.hint}` : ""), "err", 7000);
        $("#scanSummary").textContent = error.message;
      }
    } finally {
      stopScanAnimation();
      STATE.scanStreaming = false;
      STATE.scanAbort = null;
      stop.classList.add("hidden");
      button.disabled = false;
      button.textContent = T("analysis.run", "运行扫描");
    }
  }

  function renderScan(result) {
    const coverage = Number(result.coverage_fraction || 0) * 100;
    $("#scanKpis").innerHTML = `
      <div class="kpi-card"><span>R</span><b>${fmt(result.r_min, 1)}–${fmt(result.r_max, 1)}</b><small>Ω · 5–95% ${fmt(result.r_p05, 1)}–${fmt(result.r_p95, 1)}</small></div>
      <div class="kpi-card"><span>X</span><b>${fmt(result.x_min, 1)}–${fmt(result.x_max, 1)}</b><small>Ω · 5–95% ${fmt(result.x_p05, 1)}–${fmt(result.x_p95, 1)}</small></div>
      <div class="kpi-card"><span>${T("analysis.evaluated", "真实计算")}</span><b>${Number(result.evaluated_count || 0).toLocaleString()}</b><small>${T("analysis.points", "个")} · 有效 ${Number(result.points_count || 0).toLocaleString()}</small></div>
      <div class="kpi-card"><span>${T("analysis.coverage", "圆图覆盖率")}</span><b>${coverage.toFixed(2)}%</b><small>${Number(result.elapsed_ms || 0)} ms · 网格 ${result.grid_size || 0}</small></div>`;
    $("#scanTopoTag").textContent = TOPO_SHORT[result.topology] || result.topology;
    if (!result.__streamed) {
      scanChart.setData({
        steps: [],
        load: STATE.design && STATE.design.load ? { re: STATE.design.load.r, im: STATE.design.load.x } : null,
        z0: result.z0 || 50,
        scanPoints: result.points || [],
        coverage: result.coverage,
        gridSize: result.grid_size,
      });
    }
    const centerX = Number.isFinite(result.r_p05) && Number.isFinite(result.r_p95)
      ? (result.r_p05 + result.r_p95) / 2 : (result.r_max + result.r_min) / 2;
    const centerY = Number.isFinite(result.x_p05) && Number.isFinite(result.x_p95)
      ? (result.x_p05 + result.x_p95) / 2 : (result.x_max + result.x_min) / 2;
    const en = window.I18N && window.I18N.lang === "en";
    const topology = escapeHtml(TOPO_SHORT[result.topology] || result.topology);
    const dims = (result.grid_steps || []).join(" × ");
    $("#scanSummary").innerHTML = en
      ? `At <b>${fmt(result.frequency_mhz, 1)} MHz</b>, L=<b>${fmt($("#anL").value, 4)} nH</b>, ` +
        `<b>${topology}</b> simulated <b>${Number(result.evaluated_count || 0).toLocaleString()}</b> real component combinations ` +
        `(${escapeHtml(dims)} grid) in <b>${Number(result.elapsed_ms || 0)} ms</b>. ` +
        `The matchable load spans R <b>${fmt(result.r_min, 2)}–${fmt(result.r_max, 2)} Ω</b> and X <b>${fmt(result.x_min, 2)}–${fmt(result.x_max, 2)} Ω</b>; ` +
        `the occupancy grid covers <b>${coverage.toFixed(2)}%</b> of the Smith chart. The grey area is the union of all evaluated cells, not a convex hull.`
      : `在 <b>${fmt(result.frequency_mhz, 1)} MHz</b>、L=<b>${fmt($("#anL").value, 4)} nH</b> 下，` +
        `<b>${topology}</b> 实际计算了 <b>${Number(result.evaluated_count || 0).toLocaleString()}</b> 个元件组合` +
        `（${escapeHtml(dims)} 网格，用时 <b>${Number(result.elapsed_ms || 0)} ms</b>）。` +
        `可匹配负载覆盖 R <b>${fmt(result.r_min, 2)}–${fmt(result.r_max, 2)} Ω</b>、X <b>${fmt(result.x_min, 2)}–${fmt(result.x_max, 2)} Ω</b>；` +
        `在圆图上占据 <b>${coverage.toFixed(2)}%</b> 的有效面积。灰色区域由所有真实计算命中的网格单元组成，不再使用凸包近似。` +
        `扩大电容范围时若点数不变，密度会下降但覆盖范围不应缩小；把“仿真点数”调大可以获得更平滑的边界。`;
  }

  async function compareTopologies() {
    const button = $("#btnCompare");
    button.disabled = true;
    button.textContent = T("analysis.comparing", "比较中…");
    try {
      const result = await api("/api/suggest", {
        method: "POST",
        body: {
          frequency_mhz: Number($("#anFreq").value),
          load_r: Number($("#anR").value),
          load_x: Number($("#anX").value),
          z0: Number($("#anZ0").value || 50),
        },
      });
      const list = result.alternatives || [];
      if (!list.length) {
        $("#compareList").innerHTML = `<div class="empty-mini">${T("analysis.noTopology", "五种拓扑均不可行，请尝试其他频率或含串联电感的方案。")}</div>`;
        return;
      }
      const maxBandwidth = Math.max(...list.map((item) => item.bandwidth_percent || 0), 1);
      $("#compareList").innerHTML = list.map((alternative) => `
        <div class="compare-row">
          <div>
            <b>${escapeHtml(topologyName({topology: alternative.topology, topology_name: alternative.topology_name}))}</b>
            <small>${escapeHtml(alternative.components_display ? Object.values(alternative.components_display).filter((value) => value !== "—").join(" / ") : "")}</small>
            <div class="compare-bar"><i style="width:${Math.max(4, (alternative.bandwidth_percent || 0) / maxBandwidth * 100)}%"></i></div>
          </div>
          <div style="text-align:right">
            <div style="font-size:11px;color:var(--green)">${fmt(alternative.bandwidth_percent, 1)}%</div>
            <button class="btn tiny ghost" data-use-topology="${escapeHtml(alternative.topology)}">${T("design.apply", "应用")}</button>
          </div>
        </div>`).join("");
      $$("[data-use-topology]").forEach((buttonElement) => buttonElement.addEventListener("click", () => {
        setTopology(buttonElement.dataset.useTopology);
        $("#inFreq").value = $("#anFreq").value;
        $("#inZ0").value = $("#anZ0").value;
        showView("design");
        runDesign();
      }));
    } catch (error) {
      toast("比较失败", error.message, "err");
    } finally {
      button.disabled = false;
      button.textContent = T("analysis.recompare", "重新比较");
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
      if (!STATE.design) return toast("暂无设计", "请先在匹配设计中完成一次设计。", "amber");
      fillStressFromDesign();
      toast("已填入当前设计", "可以直接开始耐压分析。", "ok");
    });
  }

  function fillStressFromDesign() {
    const design = STATE.design;
    if (!design) return;
    $("#stTopology").value = design.topology;
    $("#stFreq").value = design.frequency_mhz;
    $("#stR").value = design.load.r;
    $("#stX").value = design.load.x;
    $("#stL").value = (Number(design.components.L_uH) * 1000).toFixed(3);
    $("#stC1").value = Number(design.components.C1_pF).toFixed(4);
    $("#stC2").value = Number(design.components.C2_pF).toFixed(4);
    $("#stC3").value = Number(design.components.C3_pF).toFixed(4);
    $("#stTopology").dispatchEvent(new Event("change"));
  }

  async function runStress() {
    if (STATE.stressStreaming) return;
    const button = $("#btnStress");
    button.disabled = true;
    button.textContent = T("stress.running", "计算中…");
    STATE.stressStreaming = true;
    STATE.stressAbort = new AbortController();
    const body = {
      topology: $("#stTopology").value,
      frequency_mhz: Number($("#stFreq").value),
      load_r: Number($("#stR").value),
      load_x: Number($("#stX").value),
      L_uh: Number($("#stL").value) / 1000,
      C1_pF: Number($("#stC1").value),
      C2_pF: Number($("#stC2").value),
      C3_pF: Number($("#stC3").value || 0),
      power_w: Number($("#stPower").value),
      rated_voltage: Number($("#stRated").value || 0),
      sweep: $("#stSweep").checked,
      sweep_points: Number($("#stSweepPoints").value || 21),
      frequency_span: Number($("#stSpan").value || 0) / 100,
    };
    const total = body.sweep ? Math.max(2, Math.min(body.sweep_points, 41)) ** 2 + 1 : 1;
    api("/api/config", {
      method: "POST",
      body: { ui: {
        stress_sweep_enabled: body.sweep,
        stress_sweep_points: body.sweep_points,
        stress_freq_span: body.frequency_span,
      } },
    }).catch(() => {});
    setProgressBar("stressProgress", 0, total, `0 / ${total} 次节点求解`);
    let result = null;
    try {
      await streamEvents("/api/stress/stream", body, (eventName, data) => {
        if (eventName === "meta") {
          setProgressBar("stressProgress", 0, Number(data.total) || total,
            `0 / ${Number(data.total) || total} 次节点求解`);
        } else if (eventName === "progress") {
          setProgressBar("stressProgress", data.solves, data.total || total,
            `节点求解 ${data.solves} / ${data.total || total} · 最坏 ${fmt(data.max_voltage_peak, 1)} V`);
        } else if (eventName === "done") {
          result = data;
          setProgressBar("stressProgress", data.solves || total, data.solves || total,
            `完成 ${data.solves || total} 次求解 · ${data.elapsed_ms || 0} ms`);
        }
      }, STATE.stressAbort.signal);
      if (!result) throw new Error("耐压分析未返回结果");
      renderStress(result);
    } catch (error) {
      if (error.name === "AbortError") {
        toast("耐压分析已停止", "", "amber");
      } else {
        toast("耐压计算失败", error.message + (error.data && error.data.hint ? ` ${error.data.hint}` : ""), "err", 7000);
      }
    } finally {
      STATE.stressStreaming = false;
      STATE.stressAbort = null;
      button.disabled = false;
      button.textContent = T("stress.run", "开始耐压分析");
    }
  }

  function renderStress(result) {
    STATE.lastStress = result;
    const elements = result.elements || [];
    const worstVoltage = elements.length
      ? Math.max(...elements.map((element) => Number(element.voltage_peak_worst ?? element.voltage_peak))) : 0;
    const maxVoltage = elements.length
      ? Math.max(...elements.map((element) => element.voltage_peak)) : 0;
    const rated = Number($("#stRated").value || 0);
    const factors = rated > 0 ? elements.map((element) =>
      rated / Math.max(1e-9, Number(element.voltage_peak_worst ?? element.voltage_peak))) : [];
    const minFactor = factors.length ? Math.min(...factors) : null;
    $("#stressKpis").innerHTML = `
      <div class="kpi-card"><span>${T("stress.sourceV", "源峰值电压")}</span><b>${fmt(result.input_voltage_peak, 1)}</b><small>V · source open ${fmt(result.source_voltage_peak, 1)} V</small></div>
      <div class="kpi-card"><span>${T("stress.loadV", "负载峰值电压")}</span><b>${fmt(result.load_voltage_peak, 1)}</b><small>V · 标称点</small></div>
      <div class="kpi-card ${worstVoltage > 100 ? "warn" : ""}"><span>${T("stress.maxV", "最大元件电压")}</span><b>${fmt(worstVoltage, 1)}</b><small>V peak · 标称 ${fmt(maxVoltage, 1)} V</small></div>
      <div class="kpi-card ${minFactor !== null ? (minFactor >= 2 ? "good" : minFactor >= 1.3 ? "warn" : "bad") : ""}"><span>${T("stress.sf", "最小安全系数")}</span><b>${minFactor === null ? "—" : fmt(minFactor, 2)}</b><small>${Number(result.solves || 1)} 次求解 · ${Number(result.elapsed_ms || 0)} ms</small></div>`;
    $("#stressTag").textContent = `${TOPO_SHORT[result.topology] || result.topology} · ${fmt(result.power_w, 2)} W · ${Number(result.solves || 1)} solves`;
    ChartKit.drawBars($("#stressCanvas"), elements.map((element) => ({
      label: element.name,
      value: Number(element.voltage_peak_worst ?? element.voltage_peak),
      raw: element,
    })), {
      unit: " V",
      padLeft: 58,
      format: (value) => `${value.toFixed(1)} V`,
      colorFn: (item) => {
        if (!rated) return "#22d3ee";
        const factor = rated / Math.max(1e-9, item.value);
        return factor >= 2 ? "#34d399" : factor >= 1.3 ? "#fbbf24" : "#f87171";
      },
    });
    $("#stressTable tbody").innerHTML = elements.map((element) => {
      const worst = Number(element.voltage_peak_worst ?? element.voltage_peak);
      const factor = rated > 0 ? rated / Math.max(1e-9, worst) : null;
      const cls = factor === null ? "" : factor >= 2 ? "good" : factor >= 1.3 ? "warn" : "bad";
      return `<tr><td>${escapeHtml(element.name)}</td><td title="标称 ${fmt(element.voltage_peak, 2)} V">${fmt(worst, 2)} *</td><td>${fmt(element.voltage_rms, 2)}</td><td title="最坏 ${fmt(element.current_peak_worst ?? element.current_peak, 3)} A">${fmt(element.current_peak, 3)}</td><td>${fmt(element.current_rms, 3)}</td><td class="${cls}">${factor === null ? "—" : fmt(factor, 2)}</td></tr>`;
    }).join("");

    const sweep = result.sweep || {};
    const curvePower = sweep.curve_power || [];
    const curveFreq = sweep.curve_freq || [];
    const worst = sweep.worst || {};
    $("#stressSweepTag").textContent = `${Number(result.solves || 1)} 次 · ${Number(result.elapsed_ms || 0)} ms`;
    if (curvePower.length || curveFreq.length) {
      const powerSeries = curvePower.map((point) => ({ x: point.power_w, y: point.max_voltage_peak }));
      const freqSeries = curveFreq.map((point) => ({ x: point.frequency_mhz, y: point.max_voltage_peak }));
      const useFreq = curveFreq.length > 1 && (curvePower.length <= 1 || freqSeries.length > powerSeries.length);
      const series = useFreq
        ? [{ label: "最大元件电压", color: "#22d3ee", points: freqSeries }]
        : [{ label: "最大元件电压", color: "#22d3ee", points: powerSeries }];
      ChartKit.drawSeries($("#stressSweepCanvas"), series, {
        xLabel: useFreq ? "频率 MHz" : "输入功率 W",
        yLabel: "峰值电压 V",
      });
      $("#stressSweepNote").textContent = useFreq
        ? `标称功率下的频率扫描；最坏点 ${fmt(worst.voltage_peak, 1)} V @ ${fmt(worst.frequency_mhz, 1)} MHz / ${fmt(worst.power_w, 2)} W（${worst.element || "—"}）。`
        : `标称频率下的功率扫描；最坏点 ${fmt(worst.voltage_peak, 1)} V @ ${fmt(worst.frequency_mhz, 1)} MHz / ${fmt(worst.power_w, 2)} W（${worst.element || "—"}）。`;
    } else {
      const ctx = $("#stressSweepCanvas").getContext("2d");
      const rect = $("#stressSweepCanvas").getBoundingClientRect();
      ctx.clearRect(0, 0, rect.width, rect.height);
      $("#stressSweepNote").textContent = "未开启扫描：单点结果只需一次线性节点求解，因此返回很快；勾选“频率 × 功率扫描”可执行完整网格。";
    }

    const maxCurrent = elements.length ? Math.max(...elements.map((element) =>
      Number(element.current_peak_worst ?? element.current_peak))) : 0;
    const en = window.I18N && window.I18N.lang === "en";
    const advice = [];
    if (en) {
      advice.push(`Performed ${Number(result.solves || 1)} real nodal solves in ${Number(result.elapsed_ms || 0)} ms; element voltages below are worst-case over the swept frequency and power grid.`);
      if (result.vswr > 1.2) advice.push(`The network VSWR is ${fmt(result.vswr, 3)}; mismatch creates additional standing-wave voltage at the nodes.`);
      if (worstVoltage > 100) advice.push(`Peak voltage reaches ${fmt(worstVoltage, 1)} V. Use C0G/NP0 high-voltage capacitors and high-SRF inductors with at least 2× derating.`);
      if (worstVoltage > 0 && worstVoltage < 10) advice.push("Peak voltage is low; standard 0402/0603 RF components are usually sufficient, but still check RMS current.");
      if (maxCurrent > 1) advice.push(`Peak current reaches ${fmt(maxCurrent, 2)} A; check inductor saturation and capacitor ripple-current ratings.`);
      if (minFactor !== null && minFactor < 2) advice.push(`The minimum safety factor ${fmt(minFactor, 2)} is below 2; raise the voltage rating or reduce input power.`);
      if (result.efficiency !== null && result.efficiency !== undefined && result.efficiency < 0.98) advice.push("Network efficiency is below 98%, possibly due to mismatch or numerical truncation; recheck Zin with evaluate_network.");
      advice.push("This calculation uses the complete nodal model including the 50 Ω source loading. Real selection must also consider temperature derating, parasitics and PCB layout.");
    } else {
      advice.push(`本次共完成 ${Number(result.solves || 1)} 次真实节点求解，用时 ${Number(result.elapsed_ms || 0)} ms；下表元件电压取扫描网格中的最坏值。`);
      if (result.vswr > 1.2) advice.push(`当前网络 VSWR=${fmt(result.vswr, 3)}，并非完全匹配；失配会在节点产生额外驻波电压。`);
      if (worstVoltage > 100) advice.push(`最高峰值电压 ${fmt(worstVoltage, 1)} V，建议选用 C0G/NP0 高压电容与高 SRF 电感，并按额定值至少 2× 降额。`);
      if (worstVoltage > 0 && worstVoltage < 10) advice.push("峰值电压较低，常规 0402/0603 射频元件即可，但仍需检查 RMS 电流。");
      if (maxCurrent > 1) advice.push(`最大峰值电流 ${fmt(maxCurrent, 2)} A，注意电感的饱和电流与电容的纹波电流额定值。`);
      if (minFactor !== null && minFactor < 2) advice.push(`最小安全系数 ${fmt(minFactor, 2)} 小于 2，建议提高元件额定电压或降低输入功率。`);
      if (result.efficiency !== null && result.efficiency !== undefined && result.efficiency < 0.98) advice.push("网络效率低于 98%，可能由失配或数值截断导致；请用 evaluate_network 复核 Zin。");
      advice.push("本计算采用完整网络节点法，包含 50Ω 源阻抗的负载效应；实际选型还需考虑温度降额、寄生参数与 PCB 布局。");
    }
    $("#stressAdvice").innerHTML = advice.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  }

  /* ------------------------------------------------------------------ */
  /* Presets / settings wiring                                          */
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
    $("#presetList").innerHTML = PRESETS.map((preset, index) =>
      `<button class="preset-chip" data-preset="${index}">${escapeHtml(preset.name)}</button>`).join("");
    $$("[data-preset]").forEach((button) => button.addEventListener("click", () => {
      const preset = PRESETS[Number(button.dataset.preset)];
      $("#inFreq").value = preset.f;
      $("#inR").value = preset.r;
      $("#inX").value = preset.x;
      setTopology(preset.top);
      runDesign();
    }));
  }

  /* ------------------------------------------------------------------ */
  /* Update check                                                       */
  /* ------------------------------------------------------------------ */
  let updatePollTimer = null;

  function hideUpdateModal() {
    $("#updateModal").classList.add("hidden");
    if (updatePollTimer) {
      clearInterval(updatePollTimer);
      updatePollTimer = null;
    }
  }

  function showUpdateModal(info) {
    STATE.updateInfo = info;
    $("#updateCurrent").textContent = `v${info.current || "—"}`;
    $("#updateLatest").textContent = `v${info.version || "—"}`;
    $("#updateSub").textContent = info.name
      ? `${info.name} · ${info.published_at ? info.published_at.slice(0, 10) : ""}`
      : (info.html_url || "");
    const review = info.ai_review;
    const reviewBox = $("#updateReview");
    if (review && (review.summary || review.compatibility)) {
      reviewBox.classList.remove("hidden");
      $("#updateReviewModel").textContent = review.model || "AI";
      $("#updateReviewSummary").textContent = review.summary || "";
      $("#updateReviewHighlights").innerHTML = (review.highlights || [])
        .map((item) => `<li>${escapeHtml(item)}</li>`).join("");
      $("#updateReviewCompat").textContent = [
        review.compatibility ? `兼容性：${review.compatibility}` : "",
        review.recommendation ? `建议：${review.recommendation}` : "",
      ].filter(Boolean).join(" · ");
    } else {
      reviewBox.classList.add("hidden");
    }
    const notes = String(info.notes || "").trim();
    $("#updateNotes").innerHTML = notes
      ? `<h3>版本说明</h3><div class="md">${renderMarkdown(notes.slice(0, 8000))}</div>`
      : `<p class="muted">此版本没有提供发布说明。</p>`;
    const hasSetup = !!(info.setup_asset && info.setup_asset.url);
    $("#btnUpdateDownload").disabled = false;
    $("#btnUpdateDownload").textContent = hasSetup ? T("update.download", "下载并安装") : T("update.page", "打开发布页");
    $("#updateProgress").classList.add("hidden");
    $("#updateHint").textContent = info.from_cache ? "来自本地缓存（6 小时内）" : "来自 GitHub Releases";
    $("#updateModal").classList.remove("hidden");
    if (notes && window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise([$("#updateNotes")]).catch(() => {});
    }
  }

  async function checkForUpdates(manual = false) {
    if (manual) {
      const status = $("#updateCheckStatus");
      if (status) { status.className = "inline-status"; status.textContent = "正在检查…"; }
    }
    try {
      const updateCfg = (STATE.config && STATE.config.update) || {};
      const result = await api("/api/update/check", {
        method: "POST",
        body: { force: !!manual, use_model: updateCfg.use_model !== false },
      });
      if (!result.ok) {
        if (manual) toast("检查更新失败", result.error || "未知错误", "err");
        if ($("#updateCheckStatus")) $("#updateCheckStatus").textContent = result.error || "";
        return;
      }
      if (!result.has_update) {
        if (manual) toast("已是最新版本", `当前 v${result.current} · GitHub ${result.version}`, "ok");
        if ($("#updateCheckStatus")) {
          $("#updateCheckStatus").className = "inline-status ok";
          $("#updateCheckStatus").textContent = `已是最新版本（v${result.current}）`;
        }
        return;
      }
      if ($("#updateCheckStatus")) {
        $("#updateCheckStatus").className = "inline-status warn";
        $("#updateCheckStatus").textContent = `发现 v${result.version}`;
      }
      const skipped = !!result.skipped;
      if (!manual && skipped) return;
      showUpdateModal(result);
    } catch (error) {
      if (manual) toast("检查更新失败", error.message, "err", 6000);
      if ($("#updateCheckStatus")) $("#updateCheckStatus").textContent = error.message;
    }
  }

  function pollUpdateDownload() {
    if (updatePollTimer) clearInterval(updatePollTimer);
    updatePollTimer = setInterval(async () => {
      try {
        const progress = await api("/api/update/progress");
        const percent = Number(progress.percent || 0);
        $("#updateProgress").classList.remove("hidden");
        $("#updateProgressBar").style.width = `${percent}%`;
        $("#updateProgressPct").textContent = `${percent.toFixed(1)}%`;
        $("#updateProgressText").textContent = progress.state === "done"
          ? `下载完成 · ${formatBytes(progress.downloaded)}`
          : `正在下载 · ${formatBytes(progress.downloaded)} / ${formatBytes(progress.total)}`;
        if (progress.state === "done") {
          clearInterval(updatePollTimer);
          updatePollTimer = null;
          $("#btnUpdateDownload").disabled = false;
          $("#btnUpdateDownload").textContent = T("update.installNow", "立即安装并关闭程序");
          $("#btnUpdateDownload").dataset.ready = "1";
        } else if (progress.state === "error") {
          clearInterval(updatePollTimer);
          updatePollTimer = null;
          $("#btnUpdateDownload").disabled = false;
          toast("更新包下载失败", progress.error || "", "err", 7000);
        }
      } catch (error) {
        clearInterval(updatePollTimer);
        updatePollTimer = null;
      }
    }, 600);
  }

  async function startUpdateDownload() {
    const info = STATE.updateInfo || {};
    const button = $("#btnUpdateDownload");
    if (button.dataset.ready === "1") {
      try {
        button.disabled = true;
        await api("/api/update/install", { method: "POST", body: {} });
        toast("安装程序已启动", "程序会随安装完成自动关闭；用户数据将保留。", "ok", 6000);
      } catch (error) {
        toast("启动安装失败", error.message, "err");
        button.disabled = false;
      }
      return;
    }
    if (!info.setup_asset || !info.setup_asset.url) {
      openExternal(info.html_url);
      return;
    }
    button.disabled = true;
    $("#updateProgress").classList.remove("hidden");
    try {
      await api("/api/update/download", {
        method: "POST",
        body: { url: info.setup_asset.url },
      });
      pollUpdateDownload();
    } catch (error) {
      button.disabled = false;
      toast("下载失败", error.message, "err", 6000);
    }
  }

  async function skipUpdateVersion() {
    const info = STATE.updateInfo || {};
    try {
      await api("/api/update/skip", { method: "POST", body: { version: info.version || "" } });
      toast("已跳过此版本", `v${info.version || ""} 不再主动提醒。`, "ok");
    } catch (e) { /* ignore */ }
    hideUpdateModal();
  }

  function initUpdateFlow() {
    const close = $("#btnCloseUpdate");
    if (close) close.addEventListener("click", hideUpdateModal);
    const later = $("#btnUpdateLater");
    if (later) later.addEventListener("click", hideUpdateModal);
    const skip = $("#btnUpdateSkip");
    if (skip) skip.addEventListener("click", skipUpdateVersion);
    const page = $("#btnUpdatePage");
    if (page) page.addEventListener("click", () => openExternal((STATE.updateInfo || {}).html_url));
    const download = $("#btnUpdateDownload");
    if (download) download.addEventListener("click", startUpdateDownload);
    const about = $("#btnAboutUpdate");
    if (about) about.addEventListener("click", () => checkForUpdates(true));
    const now = $("#btnCheckUpdateNow");
    if (now) now.addEventListener("click", () => checkForUpdates(true));
    const modal = $("#updateModal");
    if (modal) modal.addEventListener("click", (event) => {
      if (event.target === modal) hideUpdateModal();
    });
  }

  function initGlobal() {
    $("#btnSettings").addEventListener("click", openSettings);
    $("#btnCloseSettings").addEventListener("click", closeSettings);
    $("#btnCancelSettings").addEventListener("click", closeSettings);
    $("#btnSaveSettings").addEventListener("click", saveSettings);
    $("#btnTestLlm").addEventListener("click", testLlm);
    $("#btnReport").addEventListener("click", exportReport);
    $("#settingsModal").addEventListener("click", (event) => {
      if (event.target === $("#settingsModal")) closeSettings();
    });
    $$(".settings-tab").forEach((button) => button.addEventListener("click", () => switchSettingsTab(button.dataset.tab)));
    $("#btnLang").addEventListener("click", switchLanguage);
    $("#setProvider").addEventListener("change", () => {
      const providerId = $("#setProvider").value;
      const provider = providerById(providerId);
      $("#setBaseUrlOpenai").value = provider ? (provider.api || "") : "";
      $("#setBaseUrlAnthropic").value = provider ? (provider.api_anthropic || "") : "";
      const protocol = provider && provider.api_style === "anthropic" ? "anthropic" : "openai";
      $("#setProtocol").value = providerId === "custom" ? "custom" : protocol;
      $("#setBaseUrl").value = $("#setProtocol").value === "anthropic"
        ? $("#setBaseUrlAnthropic").value : $("#setBaseUrlOpenai").value;
      $("#setApiKey").value = "";
      const saved = (STATE.config && STATE.config.llm) || {};
      if (providerId && saved.provider === providerId && saved.has_key) {
        $("#setApiKey").placeholder = `已配置 ${saved.key_hint || ""}（留空不修改）`;
      } else {
        $("#setApiKey").placeholder = `填写 ${(provider && provider.env && provider.env[0]) || "API Key"}`;
      }
      populateModels(providerId, "");
      STATE.providerChanged = providerId !== (saved.provider || "");
      fillProfileForm(profileFor(providerId, $("#setModel").value || ""));
    });
    $("#setProtocol").addEventListener("change", () => {
      const protocol = $("#setProtocol").value;
      $("#setBaseUrl").value = protocol === "anthropic"
        ? $("#setBaseUrlAnthropic").value
        : protocol === "custom" ? $("#setBaseUrl").value : $("#setBaseUrlOpenai").value;
    });
    $("#setModel").addEventListener("change", () => {
      const model = $("#setModel").value;
      $("#setModelCustom").value = "";
      fillProfileForm(profileFor($("#setProvider").value, model));
      syncChatModelSelect();
    });
    $("#btnProfileReset").addEventListener("click", () => {
      const providerId = $("#setProvider").value;
      const model = $("#setModelCustom").value.trim() || $("#setModel").value;
      fillProfileForm(profileFor(providerId, model));
    });
    $("#btnCatalogModelsDev").addEventListener("click", () => catalogUpdate("models_dev"));
    $("#btnCatalogProvider").addEventListener("click", () => catalogUpdate("provider_api"));
    $("#btnCatalogAnnounce").addEventListener("click", () => catalogUpdate("announcements"));
    $("#btnCatalogAI").addEventListener("click", () => catalogUpdate("ai"));
    $("#btnCatalogRollback").addEventListener("click", catalogRollback);
    $("#btnCatalogReset").addEventListener("click", catalogReset);
    $("#btnUsageClear").addEventListener("click", async () => {
      try {
        await api("/api/usage/clear", { method: "POST", body: {} });
        toast("用量日志已清空", "", "ok");
        loadUsage();
      } catch (error) { toast("清空失败", error.message, "err"); }
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !$("#settingsModal").classList.contains("hidden")) closeSettings();
    });
    document.addEventListener("langchange", () => {
      const [title, subtitle] = viewMeta(STATE.view);
      $("#viewTitle").textContent = title;
      $("#viewSubtitle").textContent = subtitle;
      setTopology(STATE.topology);
      localizeSelects();
    });
  }

  async function switchLanguage() {
    const next = (window.I18N && window.I18N.lang === "en") ? "zh" : "en";
    window.I18N.setLang(next);
    try {
      await api("/api/config", { method: "POST", body: { ui: { lang: next } } });
    } catch (error) { /* non-fatal */ }
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
    initDisplayToggles();
    initDesignForm();
    initAnalysis();
    initStress();
    initContext();
    initPresets();
    initGlobal();
    initUpdateFlow();
    smith = new SmithChart($("#smithCanvas"), {
      tooltip: $("#smithTooltip"),
      onStateChange: (playing) => {
        $("#btnPlay").innerHTML = playing
          ? '<svg><use href="#i-pause"/></svg>'
          : '<svg><use href="#i-play"/></svg>';
      },
    });
    setTopology("auto");
    localizeSelects();
    await loadProviders();
    await loadStatus();
    await loadConfig();
    await loadMcpCode();
    $("#designResult").classList.add("hidden");
    $("#emptyDesign").classList.remove("hidden");
    if (window.Library) window.Library.init();
    if (window.Docs) window.Docs.init();
    if (window.Assistant) window.Assistant.init();
    if (window.I18N) window.I18N.setLang(window.I18N.lang);
    const updateCfg = (STATE.config && STATE.config.update) || {};
    if (updateCfg.auto_check !== false) {
      setTimeout(() => checkForUpdates(false), 2200);
    }
  }

  document.addEventListener("DOMContentLoaded", init);
  if (document.readyState !== "loading") init();

  window.IMP = {
    state: STATE,
    api,
    toast,
    t: T,
    escapeHtml,
    renderMarkdown,
    typesetMath,
    showView,
    streamChat,
    streamEvents,
    uploadBlobWithProgress,
    formatBytes,
    makeAssistant,
    addUserMessage,
    handleChatEvent,
    finishAssistant,
    pushReasoning,
    finalizeSources,
    addCitationCard,
    renderChatStats,
    syncDisplayToggles,
    toggleDisplay,
    openExternal,
    openLocalPath,
    checkForUpdates,
    showUpdateModal,
    hideUpdateModal,
    buildContext,
    openSettings,
    loadProviders,
    loadConfig,
    loadStatus,
    providerById,
    providerLabel,
    syncChatModelSelect,
    updateContext,
    renderDesign,
    runDesign,
    ensureFullDesign,
    exportReport,
    fillStressFromDesign,
    fmt,
    fmtComp,
    fmtTokens,
    fmtMoney,
  };
})();
