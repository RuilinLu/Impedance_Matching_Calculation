/* Shared chat sessions: streaming, stop, edit, clear, tool cards, media, model switching. */
(function () {
  "use strict";

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const IMP = () => window.IMP;
  const S = () => IMP().state;
  const T = (key, fallback) => IMP().t(key, fallback);
  const esc = (value) => IMP().escapeHtml(value);

  const MEDIA_PREFIX = /^(?:https?:\/\/|data:(?:image|audio|video|application)\/|\/api\/(?:media|report)\/)/i;
  let mainSession = null;

  function toast(title, message, type, ms) {
    IMP().toast(title, message, type, ms);
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

  function fmtComp(comps, key) {
    if (!comps) return "—";
    if (key === "L") {
      const micro = Number(comps.L_uH);
      if (!isFinite(micro)) return "—";
      return micro < 1 ? `${fmt(micro * 1000, 3)} nH` : `${fmt(micro, 3)} µH`;
    }
    if (key === "C1") return `${fmt(comps.C1_pF, 4)} pF`;
    if (key === "C2") return `${fmt(comps.C2_pF, 4)} pF`;
    if (key === "C3") return Number(comps.C3_pF) > 0 ? `${fmt(comps.C3_pF, 4)} pF` : "—";
    return "—";
  }

  function copyText(text, message) {
    return IMP().copyText(text, message);
  }

  function safeMediaUrl(url) {
    const text = String(url || "").trim();
    if (!text || text.length > 8_000_000) return "";
    return MEDIA_PREFIX.test(text) ? text : "";
  }

  function mediaKind(url, fallback) {
    const text = String(url || "");
    const lower = text.toLowerCase();
    if (/^data:image\//.test(lower) || /\.(png|jpe?g|gif|webp|svg|bmp)(\?|#|$)/.test(lower)) return "image";
    if (/^data:video\//.test(lower) || /\.(mp4|webm|ogv|mov)(\?|#|$)/.test(lower)) return "video";
    if (/^data:audio\//.test(lower) || /\.(mp3|wav|ogg|m4a|flac|aac)(\?|#|$)/.test(lower)) return "audio";
    return fallback || "file";
  }

  function mediaName(url, fallback) {
    try {
      const clean = String(url || "").split("?")[0].split("#")[0];
      const name = decodeURIComponent(clean.split("/").pop() || "");
      return name && name.length <= 120 ? name : (fallback || "文件");
    } catch (error) {
      return fallback || "文件";
    }
  }

  function mediaActions(url, kind, name) {
    const safe = esc(url);
    const label = esc(name);
    const copyImage = kind === "image"
      ? `<button class="btn tiny ghost" data-media-copy="${safe}">复制图片</button>` : "";
    return `<div class="media-actions">
      <a class="btn tiny" href="${safe}" download="${label}" target="_blank" rel="noreferrer"><svg><use href="#i-download"/></svg>下载</a>
      ${copyImage}
      <button class="btn tiny ghost" data-media-copy-link="${safe}">复制链接</button>
      <a class="btn tiny ghost" href="${safe}" target="_blank" rel="noreferrer"><svg><use href="#i-external"/></svg>打开</a>
    </div>`;
  }

  function mediaFigureHtml(item) {
    const url = safeMediaUrl(item.url);
    if (!url) return "";
    const kind = item.kind || mediaKind(url, item.type);
    const name = mediaName(url, item.name || item.title || "媒体");
    const title = item.title || name;
    let body = "";
    if (kind === "image") {
      body = `<img loading="lazy" src="${esc(url)}" alt="${esc(title)}">`;
    } else if (kind === "video") {
      body = `<video controls preload="metadata" src="${esc(url)}"></video>`;
    } else if (kind === "audio") {
      body = `<audio controls preload="metadata" src="${esc(url)}"></audio>`;
    } else {
      body = `<div class="file-card-icon"><svg><use href="#i-docs"/></svg></div>`;
    }
    return `<figure class="md-media ${kind}" data-media-url="${esc(url)}">
      <div class="media-frame">${body}</div>
      <figcaption><b>${esc(title)}</b><small>${esc(kind.toUpperCase())}</small></figcaption>
      ${mediaActions(url, kind, name)}
    </figure>`;
  }

  function applyToolVisibility() {
    const hidden = !S().showTools;
    $$(".messages, .qa-messages").forEach((element) => {
      element.classList.toggle("hide-tool-cards", hidden);
    });
  }

  function syncDisplayChips() {
    $$("#btnToggleTools, #qaToggleTools").forEach((button) =>
      button.classList.toggle("active", !!S().showTools));
    applyToolVisibility();
  }

  function initDisplay() {
    ["#btnToggleTools", "#qaToggleTools"].forEach((selector) => {
      const button = $(selector);
      if (!button || button.dataset.bound === "1") return;
      button.dataset.bound = "1";
      button.addEventListener("click", () => {
        S().showTools = !S().showTools;
        syncDisplayChips();
        IMP().api("/api/config", { method: "POST", body: { ui: { show_tools: !!S().showTools } } })
          .catch(() => {});
      });
    });
    syncDisplayChips();
  }

  /* ------------------------------------------------------------------ */
  /* Model connections                                                  */
  /* ------------------------------------------------------------------ */
  function connections() {
    const llm = (S().config && S().config.llm) || {};
    return Array.isArray(llm.connections) ? llm.connections : [];
  }

  function chatModelGroups() {
    const llm = (S().config && S().config.llm) || {};
    const groups = [];
    connections().forEach((conn) => {
      const provider = IMP().providerById(conn.provider) || {};
      const models = [];
      const push = (id) => {
        const text = String(id || "").trim();
        if (text && text.length <= 120 && !models.includes(text)) models.push(text);
      };
      push(conn.model);
      (conn.models || []).forEach(push);
      (provider.models || []).forEach((model) => push(model.id));
      const label = conn.label || `${conn.provider_name || conn.provider || "模型"}${conn.key_hint ? ` · ${conn.key_hint}` : ""}`;
      groups.push({ connection: conn, label, models });
    });
    if (!groups.length && llm.model) {
      groups.push({
        connection: { id: "", provider: llm.provider, provider_name: llm.provider_name, model: llm.model, has_key: llm.has_key },
        label: `${llm.provider_name || llm.provider || "当前模型"} · 当前配置`,
        models: [llm.model],
      });
    }
    return groups.filter((group) => group.models.length);
  }

  function populateModelSelects() {
    const llm = (S().config && S().config.llm) || {};
    const activeId = String(llm.active_connection || "");
    const activeModel = String(llm.model || "");
    const groups = chatModelGroups();
    [$("#modelSelect"), $("#qaModelSelect")].filter(Boolean).forEach((select) => {
      if (!groups.length) {
        select.innerHTML = `<option value="">请先在设置中添加模型服务</option>`;
        return;
      }
      select.innerHTML = groups.map((group) => {
        const options = group.models.map((model) =>
          `<option value="${esc(`${group.connection.id}|||${model}`)}">${esc(model)}</option>`).join("");
        return `<optgroup label="${esc(group.label)}">${options}</optgroup>`;
      }).join("");
      const current = groups.some((group) => group.connection.id === activeId &&
        group.models.includes(activeModel))
        ? `${activeId}|||${activeModel}`
        : `${groups[0].connection.id}|||${groups[0].models[0]}`;
      select.value = current;
    });
  }

  function parseModelValue(value) {
    const text = String(value || "");
    const index = text.indexOf("|||");
    if (index < 0) return { connectionId: "", model: text };
    return { connectionId: text.slice(0, index), model: text.slice(index + 3) };
  }

  async function activateModel(select) {
    const target = parseModelValue(select.value);
    if (!target.model) return;
    try {
      let result;
      if (target.connectionId) {
        result = await IMP().api("/api/connections/activate", {
          method: "POST", body: { id: target.connectionId, model: target.model },
        });
      } else {
        result = await IMP().api("/api/config", {
          method: "POST", body: { llm: { model: target.model } },
        });
      }
      if (result.config) S().config = result.config;
      await IMP().loadStatus();
      populateModelSelects();
      toast("已切换模型", target.model, "ok", 2200);
    } catch (error) {
      toast("切换模型失败", error.message, "err", 5000);
      populateModelSelects();
    }
  }

  function bindModelSelect(select) {
    if (!select || select.dataset.modelBound === "1") return;
    select.dataset.modelBound = "1";
    select.addEventListener("change", () => activateModel(select));
  }

  function renderConnectionList(cfg) {
    const box = $("#connectionList");
    if (!box) return;
    const llm = ((cfg || S().config || {}).llm) || {};
    const list = Array.isArray(llm.connections) ? llm.connections : [];
    if (!list.length) {
      box.innerHTML = `<p class="muted connection-empty">尚未保存模型连接。填写服务商、Base URL、模型与 API Key 后保存，即可在聊天框中切换。</p>`;
      return;
    }
    box.innerHTML = list.map((conn) => {
      const active = conn.id === llm.active_connection;
      return `<div class="connection-row ${active ? "active" : ""}">
        <div class="connection-copy">
          <b>${esc(conn.provider_name || conn.provider || "自定义服务")}</b>
          <small>${esc(conn.model || "未选择模型")} · ${esc(conn.base_url || "")}</small>
          <span class="connection-key">${conn.has_key ? `Key ${esc(conn.key_hint || "已配置")}` : "未保存 Key"}</span>
        </div>
        <span class="tag ${active ? "green" : ""}">${active ? "当前使用" : "已保存"}</span>
        <button class="btn tiny ghost" data-connection-activate="${esc(conn.id)}">使用</button>
        <button class="btn tiny ghost danger" data-connection-delete="${esc(conn.id)}">删除</button>
      </div>`;
    }).join("");
  }

  async function activateConnection(id) {
    try {
      const result = await IMP().api("/api/connections/activate", { method: "POST", body: { id } });
      if (result.config) S().config = result.config;
      await IMP().loadConfig();
      await IMP().loadStatus();
      renderConnectionList(S().config);
      toast("已切换连接", result.connection && result.connection.model || "", "ok");
    } catch (error) {
      toast("切换失败", error.message, "err");
    }
  }

  async function deleteConnection(id) {
    if (!window.confirm("删除这条模型连接？只会删除本机保存的 Key 与端点，不会影响服务商账户。")) return;
    try {
      const result = await IMP().api("/api/connections/delete", { method: "POST", body: { id } });
      if (result.config) S().config = result.config;
      await IMP().loadConfig();
      await IMP().loadStatus();
      renderConnectionList(S().config);
      toast("连接已删除", "", "ok");
    } catch (error) {
      toast("删除失败", error.message, "err");
    }
  }

  function bindSettings() {
    const box = $("#connectionList");
    if (box && box.dataset.bound !== "1") {
      box.dataset.bound = "1";
      box.addEventListener("click", (event) => {
        const activate = event.target.closest("[data-connection-activate]");
        if (activate) {
          activateConnection(activate.dataset.connectionActivate);
          return;
        }
        const remove = event.target.closest("[data-connection-delete]");
        if (remove) deleteConnection(remove.dataset.connectionDelete);
      });
    }
    bindModelSelect($("#modelSelect"));
    bindModelSelect($("#qaModelSelect"));
  }

  function connectionHasKey(provider, baseUrl) {
    const llm = (S().config && S().config.llm) || {};
    const target = String(baseUrl || "").replace(/\/+$/, "").toLowerCase();
    const match = connections().find((conn) =>
      String(conn.provider || "") === String(provider || "") &&
      String(conn.base_url || "").replace(/\/+$/, "").toLowerCase() === target);
    if (match && match.has_key) return true;
    return String(llm.provider || "") === String(provider || "") && !!llm.has_key;
  }

  function setShowTools(value) {
    S().showTools = !!value;
    syncDisplayChips();
  }

  /* ------------------------------------------------------------------ */
  /* Rendering                                                          */
  /* ------------------------------------------------------------------ */
  function addUserMessage(container, text, attachments, meta = {}) {
    const wrap = document.createElement("div");
    wrap.className = "msg msg-user";
    if (meta.index != null) wrap.dataset.msgIndex = String(meta.index);
    const files = (attachments || []).map((attachment) =>
      `<span class="attachment-chip">${esc(attachment.name || "附件")} · ${esc(attachment.kind || "")}${attachment.image_count ? ` · ${attachment.image_count} img` : ""}</span>`).join("");
    wrap.innerHTML = `<div class="avatar">我</div>
      <div class="msg-body">
        <div class="bubble">${esc(text).replace(/\n/g, "<br>")}${files ? `<div class="bubble-files">${files}</div>` : ""}</div>
        <div class="msg-actions">
          <button class="msg-action" data-edit-message="${meta.index != null ? meta.index : ""}" title="编辑这条问题并重新发送"><svg><use href="#i-edit"/></svg>编辑</button>
          <button class="msg-action" data-copy-user="${meta.index != null ? meta.index : ""}" title="复制问题"><svg><use href="#i-copy"/></svg>复制</button>
        </div>
      </div>`;
    container.appendChild(wrap);
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
        <div class="tool-activity hidden"><span class="activity-spinner"></span><span class="tool-activity-text">正在调用本地工具…</span></div>
        <div class="md"></div>
        <div class="media-list"></div>
        <div class="typing"><i></i><i></i><i></i></div>
        <details class="sources-block hidden">
          <summary><span>参考来源</span><span class="source-count">0</span></summary>
          <div class="sources-list"></div>
        </details>
      </div>`;
    container.appendChild(wrap);
    return {
      wrap,
      body: $(".msg-body", wrap),
      md: $(".md", wrap),
      media: $(".media-list", wrap),
      typing: $(".typing", wrap),
      thinking: $(".thinking-block", wrap),
      thinkingText: $(".thinking-text", wrap),
      thinkingSize: $(".thinking-size", wrap),
      sources: $(".sources-block", wrap),
      sourcesList: $(".sources-list", wrap),
      sourceCount: $(".source-count", wrap),
      activity: $(".tool-activity", wrap),
      activityText: $(".tool-activity-text", wrap),
      buffer: "",
      reasoning: "",
      raw: "",
      lastRender: 0,
      citations: new Set(),
      citationList: [],
      mediaItems: new Set(),
      toolRunning: 0,
      toolTotal: 0,
      actionsAdded: false,
    };
  }

  function setActivity(assistant) {
    if (!assistant || !assistant.activity) return;
    const visible = assistant.toolRunning > 0 && !S().showTools;
    assistant.activity.classList.toggle("hidden", !visible);
  }

  function pushToken(assistant, text, scroll) {
    assistant.buffer += text;
    const now = performance.now();
    if (now - assistant.lastRender > 55) {
      assistant.md.innerHTML = IMP().renderMarkdown(assistant.buffer);
      assistant.lastRender = now;
      scroll(false);
    }
  }

  function pushReasoning(assistant, text) {
    if (!assistant || !assistant.thinking) return;
    assistant.reasoning += String(text || "");
    if (!assistant.reasoning) return;
    assistant.thinking.classList.remove("hidden");
    assistant.thinkingText.textContent = assistant.reasoning;
    assistant.thinkingSize.textContent = `${assistant.reasoning.length} 字`;
    assistant.thinking.open = !!S().showThinking;
  }

  function citationCard(citation) {
    if (!citation) return "";
    const snippet = esc(String(citation.snippet || "").slice(0, 500))
      .replace(/\[\[([^\]]+)\]\]/g, "<mark>$1</mark>");
    if (citation.kind === "web" && citation.url) {
      const url = /^https?:\/\//i.test(String(citation.url)) ? String(citation.url) : "";
      if (!url) return "";
      return `<a class="citation-card web" href="${esc(url)}" target="_blank" rel="noreferrer">
        <div class="citation-doc-icon"><svg><use href="#i-external"/></svg></div>
        <div class="citation-copy"><b>${esc(citation.title || url)}</b><small>${esc(url)}</small><p>${snippet}</p></div>
        <span class="tag cyan">打开链接</span>
      </a>`;
    }
    if (citation.kind === "textbook") {
      return `<div class="citation-card" data-citation-kind="textbook" data-doc-id="${citation.doc_id}" data-page="${citation.page}" data-rects="${esc(JSON.stringify(citation.rects || []))}">
        <img src="${esc(citation.crop_url || citation.thumb_url || "")}" alt="page">
        <div class="citation-copy"><b>${esc(citation.title || "教材")}</b><small>第 ${citation.page} 页</small><p>${snippet}</p></div>
        <button class="btn tiny" data-open-citation="1">打开</button>
      </div>`;
    }
    return `<div class="citation-card" data-citation-kind="documentation" data-category="${esc(citation.category || "")}" data-block="${esc(citation.block_id || "")}" data-line="${citation.line || 0}">
      <div class="citation-doc-icon"><svg><use href="#i-docs"/></svg></div>
      <div class="citation-copy"><b>${esc(citation.title || "文档")}</b><small>第 ${citation.line || 0} 行</small><p>${snippet}</p></div>
      <button class="btn tiny" data-open-citation="1">打开</button>
    </div>`;
  }

  function finalizeSources(assistant) {
    if (!assistant || !assistant.sources) return;
    if (!assistant.citationList.length) {
      assistant.sources.classList.add("hidden");
      return;
    }
    assistant.sources.classList.remove("hidden");
    assistant.sourceCount.textContent = String(assistant.citationList.length);
    assistant.sourcesList.innerHTML = assistant.citationList.map(citationCard).join("");
    assistant.sources.open = !!S().showCitations;
  }

  function addCitation(assistant, citation) {
    if (!citation || !assistant) return;
    const key = citation.kind === "textbook"
      ? `t:${citation.doc_id}:${citation.page}:${citation.snippet || ""}`
      : citation.kind === "web"
        ? `w:${citation.url}`
        : `d:${citation.category}:${citation.block_id}`;
    if (assistant.citations.has(key)) return;
    assistant.citations.add(key);
    assistant.citationList.push(citation);
    if (assistant.sourceCount) assistant.sourceCount.textContent = String(assistant.citationList.length);
    if (S().showCitations) finalizeSources(assistant);
  }

  function addMedia(assistant, item) {
    if (!assistant || !assistant.media || !item) return;
    const url = safeMediaUrl(item.url);
    if (!url) return;
    const key = String(url).slice(0, 4000);
    if (assistant.mediaItems.has(key)) return;
    assistant.mediaItems.add(key);
    const kind = item.kind || mediaKind(url, item.type);
    const holder = document.createElement("div");
    holder.innerHTML = mediaFigureHtml({
      url, type: item.type || kind, kind,
      name: item.name, title: item.title || item.name,
    });
    const figure = holder.firstElementChild;
    if (figure) assistant.media.appendChild(figure);
  }

  function addAssistantActions(assistant, scroll) {
    if (!assistant || assistant.actionsAdded) return;
    assistant.actionsAdded = true;
    const formulas = Array.from(assistant.md.querySelectorAll("[data-latex]"))
      .map((element) => element.getAttribute("data-latex") || "").filter(Boolean);
    const actions = document.createElement("div");
    actions.className = "msg-actions assistant-actions";
    actions.innerHTML = `<button class="msg-action" data-copy-answer title="复制完整回答（LaTeX 保留为源码）"><svg><use href="#i-copy"/></svg>复制回答</button>` +
      (formulas.length ? `<button class="msg-action" data-copy-formulas title="复制本条回答中的全部公式源码"><svg><use href="#i-copy"/></svg>复制全部公式</button>` : "") +
      `<span class="msg-meta">${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>`;
    actions.querySelector("[data-copy-answer]").addEventListener("click", () => {
      copyText(assistant.raw || assistant.buffer, "已复制回答（公式保留为 LaTeX 源码）");
    });
    const formulaButton = actions.querySelector("[data-copy-formulas]");
    if (formulaButton) {
      formulaButton.addEventListener("click", () => {
        copyText(formulas.join("\n\n"), `已复制 ${formulas.length} 条公式`);
      });
    }
    assistant.body.appendChild(actions);
    scroll(false);
  }

  function finishAssistant(assistant, content, reasoning, media, scroll) {
    if (assistant.typing) { assistant.typing.remove(); assistant.typing = null; }
    assistant.raw = content || assistant.buffer || "";
    assistant.md.innerHTML = IMP().renderMarkdown(assistant.raw || "");
    (media || []).forEach((item) => addMedia(assistant, item));
    assistant.md.querySelectorAll(".md-media").forEach((figure) => {
      if (assistant.mediaItems.has(figure.dataset.mediaUrl || "")) figure.remove();
    });
    IMP().typesetMath(assistant.md);
    if (reasoning) pushReasoning(assistant, reasoning);
    if (assistant.thinking && !assistant.reasoning) assistant.thinking.classList.add("hidden");
    assistant.toolRunning = 0;
    setActivity(assistant);
    finalizeSources(assistant);
    addAssistantActions(assistant, scroll);
  }

  function addToolCard(assistant, event) {
    const card = document.createElement("div");
    card.className = "tool-card";
    card.dataset.callId = event.id;
    card.innerHTML = `
      <div class="tool-card-head">
        <div class="tool-icon"><svg><use href="#i-settings"/></svg></div>
        <div><b>${esc(event.label || event.name)}</b><small>${esc(event.name)}</small></div>
        <span class="spacer"></span><span class="tool-state">运行中</span>
      </div>
      <div class="tool-card-body"><span class="tool-summary">正在调用本地引擎…</span></div>`;
    assistant.body.insertBefore(card, assistant.typing || assistant.sources || null);
    assistant.toolRunning += 1;
    assistant.toolTotal += 1;
    if (assistant.activityText) {
      assistant.activityText.textContent = `正在调用本地工具… ${assistant.toolRunning} 个进行中`;
    }
    setActivity(assistant);
  }

  function updateToolCard(assistant, event) {
    assistant.toolRunning = Math.max(0, assistant.toolRunning - 1);
    if (assistant.activityText) {
      assistant.activityText.textContent = assistant.toolRunning > 0
        ? `正在调用本地工具… ${assistant.toolRunning} 个进行中`
        : `已完成 ${assistant.toolTotal} 个工具调用`;
    }
    setActivity(assistant);
    const card = assistant.body.querySelector(`.tool-card[data-call-id="${CSS.escape(String(event.id))}"]`);
    if (!card) return;
    const state = $(".tool-state", card);
    state.className = `tool-state ${event.ok ? "ok" : "err"}`;
    state.textContent = event.ok ? `完成 · ${event.elapsed_ms || 0}ms` : "失败";
    const body = $(".tool-card-body", card);
    body.innerHTML = `<span class="tool-summary">${esc(event.summary || "无返回摘要")}</span>` +
      (event.data ? `<details><summary>查看工具返回</summary><pre>${esc(JSON.stringify(event.data, null, 2))}</pre></details>` : "");
    if (event.ok && event.data && event.data.components) appendDesignCard(assistant.body, event.data);
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
    else values.push([T("design.topology", "拓扑"), design.topology_name || design.topology || "—"]);
    const card = document.createElement("div");
    card.className = "design-card";
    card.innerHTML = `
      <div class="design-card-head">
        <svg style="width:16px;height:16px;color:var(--cyan)"><use href="#i-check"/></svg>
        <b>${esc(design.topology_name || design.topology || "—")}</b>
        <span class="tag green">节点法已复核</span>
      </div>
      <div class="design-values">${values.map(([key, value]) => `<div class="design-value"><span>${esc(key)}</span><b>${esc(value)}</b></div>`).join("")}</div>
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
    container.insertBefore(card, container.querySelector(".typing, .sources-block"));
  }

  async function copyImageFromUrl(url) {
    if (!/^(?:\/api\/|data:)/i.test(String(url || ""))) {
      copyText(url, "外部图片链接已复制");
      return;
    }
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      if (!navigator.clipboard || !window.ClipboardItem) throw new Error("clipboard unavailable");
      await navigator.clipboard.write([new ClipboardItem({ [blob.type || "image/png"]: blob })]);
      toast("图片已复制", "可直接粘贴到文档或聊天窗口。", "ok");
    } catch (error) {
      copyText(url, "无法复制图片本体，已复制图片链接");
    }
  }

  function handleEvent(eventName, data, assistant, session) {
    const scroll = (force) => session.scrollToBottom(force);
    if (eventName === "status") {
      if (assistant.typing && data.text) assistant.typing.title = data.text;
    } else if (eventName === "tool_call") {
      addToolCard(assistant, data);
    } else if (eventName === "tool_result") {
      updateToolCard(assistant, data);
    } else if (eventName === "design") {
      if (data.design) {
        S().design = data.design;
        if (IMP().updateContext) IMP().updateContext(data.design);
        if (data.design.steps && data.design.steps.length && S().view === "design") {
          IMP().renderDesign && IMP().renderDesign(data.design);
        } else if (IMP().ensureFullDesign) {
          IMP().ensureFullDesign(data.design).catch(() => {});
        }
      }
    } else if (eventName === "token") {
      if (assistant.typing) { assistant.typing.remove(); assistant.typing = null; }
      pushToken(assistant, data.text || "", scroll);
    } else if (eventName === "reasoning") {
      pushReasoning(assistant, data.text || "");
    } else if (eventName === "citation") {
      addCitation(assistant, data);
    } else if (eventName === "media") {
      addMedia(assistant, data);
    } else if (eventName === "usage") {
      IMP().renderChatStats(data, session.options.stats || "#chatStats");
    } else if (eventName === "error") {
      assistant.errored = true;
      if (assistant.typing) { assistant.typing.remove(); assistant.typing = null; }
      const hint = data.hint || "";
      assistant.md.innerHTML = `<div class="error-box"><b>智能体暂时不可用</b><p>${esc(data.message || "未知错误")}</p>${hint ? `<p class="muted">${esc(hint)}</p>` : ""}<button class="btn tiny" onclick="document.getElementById('btnSettings').click()">打开设置</button></div>`;
    } else if (eventName === "done") {
      if (assistant.typing) assistant.typing.remove();
    }
  }

  /* ------------------------------------------------------------------ */
  /* Session                                                            */
  /* ------------------------------------------------------------------ */
  function createSession(options) {
    const session = {
      options,
      messages: [],
      streaming: false,
      controller: null,
      assistant: null,
      autoScroll: true,
    };
    const root = options.root;
    const scroller = options.scroller || root;
    const input = options.input;
    const sendButton = options.sendButton;

    function scrollToBottom(force) {
      if (!scroller) return;
      if (!force && !session.autoScroll) return;
      const apply = () => { scroller.scrollTop = scroller.scrollHeight; };
      if (window.requestAnimationFrame) requestAnimationFrame(apply);
      else apply();
    }
    session.scrollToBottom = scrollToBottom;

    scroller.addEventListener("scroll", () => {
      session.autoScroll = scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight < 90;
    });

    function setBusy(busy) {
      session.streaming = !!busy;
      if (sendButton) {
        sendButton.classList.toggle("stop", !!busy);
        sendButton.disabled = false;
        sendButton.title = busy ? "停止生成" : "发送";
        sendButton.innerHTML = busy
          ? `<span class="send-spinner"></span><svg><use href="#i-stop"/></svg>`
          : `<svg><use href="#i-send"/></svg>`;
      }
      if (input) input.setAttribute("aria-busy", busy ? "true" : "false");
      if (options.toolbar) options.toolbar.classList.toggle("busy", !!busy);
      if (options.onBusy) options.onBusy(!!busy);
    }
    session.setBusy = setBusy;

    function currentTarget() {
      return parseModelValue(options.modelSelect ? options.modelSelect.value : "");
    }

    function ensureModel() {
      const llm = (S().config && S().config.llm) || {};
      const target = currentTarget();
      if (!target.model) {
        toast("请先选择模型", "在输入框下方选择模型，或到设置中添加模型服务。", "amber", 5000);
        IMP().openSettings();
        return false;
      }
      if (target.connectionId) {
        const conn = connections().find((item) => item.id === target.connectionId);
        if (!conn) {
          toast("模型连接不存在", "请重新选择模型或在设置中配置。", "amber", 5000);
          return false;
        }
        if (!conn.has_key) {
          toast("该连接缺少 API Key", "打开设置，为该服务商填写 Key 并保存。", "amber", 5000);
          IMP().openSettings();
          return false;
        }
        return true;
      }
      if (!llm.provider || !llm.has_key || !llm.base_url) {
        toast("请先配置模型服务", "点击设置，选择服务商并填写你自己的 API Key。", "amber", 5000);
        IMP().openSettings();
        return false;
      }
      return true;
    }

    async function send(textOverride) {
      if (session.streaming) return;
      const raw = textOverride != null ? String(textOverride) : (input ? input.value : "");
      const text = raw.trim();
      const pending = (options.getAttachments ? options.getAttachments() : []) || [];
      if (pending.some((item) => item.uploading)) {
        toast("附件仍在上传", "请等待上传百分比到 100% 后再发送。", "amber");
        return;
      }
      const attachments = pending.filter((item) => !item.uploading);
      if (!text && !attachments.length) return;
      if (!ensureModel()) return;

      if (options.welcome) options.welcome.classList.add("hidden");
      const userText = text || "请阅读附件并总结与微波阻抗匹配相关的关键信息。";
      const index = session.messages.length;
      addUserMessage(root, userText, attachments, { index });
      session.messages.push({
        role: "user",
        display: userText,
        content: userText + (attachments.length
          ? `\n[附件: ${attachments.map((item) => item.name).join(", ")}]` : ""),
      });
      if (input) { input.value = ""; input.style.height = "auto"; }
      if (options.clearAttachments) options.clearAttachments();
      session.autoScroll = true;
      scrollToBottom(true);

      const assistant = makeAssistant(root);
      assistant.wrap.dataset.msgIndex = String(session.messages.length);
      assistant.scrollToBottom = scrollToBottom;
      session.assistant = assistant;
      const target = currentTarget();
      const generation = (session.generation || 0) + 1;
      session.generation = generation;
      session.controller = new AbortController();
      setBusy(true);

      const payload = {
        messages: session.messages.filter((message) => !message.error).slice(-18),
        attachments: attachments.map((item) => ({ id: item.id, name: item.name })),
        model: target.model,
        connection_id: target.connectionId,
        context: (options.buildContext || IMP().buildContext)(),
      };
      try {
        const result = await IMP().streamChat(payload, {
          signal: session.controller.signal,
          onEvent: (name, data) => {
            if (generation === session.generation) handleEvent(name, data, assistant, session);
          },
        });
        if (generation !== session.generation) return;
        if (assistant.typing) { assistant.typing.remove(); assistant.typing = null; }
        if (!assistant.errored) {
          const content = result.content || assistant.buffer || "（未收到回答）";
          finishAssistant(assistant, content, result.reasoning || "", result.media || [], scrollToBottom);
          session.messages.push({ role: "assistant", content });
        } else {
          session.messages.push({ role: "assistant", content: "（本次请求失败）", error: true });
        }
        scrollToBottom(true);
      } catch (error) {
        if (generation !== session.generation) return;
        if (assistant.typing) { assistant.typing.remove(); assistant.typing = null; }
        const aborted = error && (error.name === "AbortError" || session.controller.signal.aborted);
        if (aborted) {
          const partial = (assistant.buffer || "").trim();
          const content = (partial ? `${partial}\n\n` : "") + "> ⏹ 已停止生成。";
          finishAssistant(assistant, content, assistant.reasoning || "", [], scrollToBottom);
          session.messages.push({ role: "assistant", content });
          toast("已停止生成", "可以编辑问题后重新发送。", "ok", 2600);
        } else {
          assistant.errored = true;
          const hint = (error.data && error.data.hint) || "";
          assistant.md.innerHTML = `<div class="error-box"><b>智能体暂时不可用</b><p>${esc(error.message)}</p>${hint ? `<p class="muted">${esc(hint)}</p>` : ""}<button class="btn tiny" onclick="document.getElementById('btnSettings').click()">打开设置</button></div>`;
          session.messages.push({ role: "assistant", content: "（本次请求失败）", error: true });
          toast("智能体调用失败", error.message, "err", 7000);
        }
      } finally {
        if (generation !== session.generation) return;
        session.controller = null;
        session.assistant = null;
        setBusy(false);
        if (options.onFinish) options.onFinish();
        scrollToBottom(false);
      }
    }
    session.send = send;

    function stop() {
      if (!session.streaming || !session.controller) return;
      session.controller.abort();
    }
    session.stop = stop;

    function resend(index, text) {
      session.generation = (session.generation || 0) + 1;
      if (session.controller) session.controller.abort();
      session.streaming = false;
      setBusy(false);
      session.messages = session.messages.slice(0, index);
      Array.from(root.querySelectorAll(".msg")).forEach((element) => {
        if (Number(element.dataset.msgIndex) >= index) element.remove();
      });
      session.autoScroll = true;
      send(text);
    }

    function startEdit(index) {
      if (!Number.isInteger(index) || index < 0) return;
      const wrap = root.querySelector(`.msg[data-msg-index="${index}"]`);
      if (!wrap) return;
      const bubble = wrap.querySelector(".bubble");
      const message = session.messages[index];
      if (!bubble || !message) return;
      const original = bubble.innerHTML;
      const editor = document.createElement("div");
      editor.className = "msg-edit";
      editor.innerHTML = `<textarea class="msg-edit-input" rows="3">${esc(message.display || message.content || "")}</textarea>
        <div class="msg-edit-actions">
          <button class="btn tiny primary" data-edit-save>保存并重新发送</button>
          <button class="btn tiny ghost" data-edit-cancel>取消</button>
          <span class="muted">重新发送会从此处截断后续对话。</span>
        </div>`;
      bubble.innerHTML = "";
      bubble.appendChild(editor);
      const textarea = editor.querySelector("textarea");
      textarea.focus();
      textarea.setSelectionRange(textarea.value.length, textarea.value.length);
      editor.querySelector("[data-edit-cancel]").addEventListener("click", () => {
        bubble.innerHTML = original;
      });
      editor.querySelector("[data-edit-save]").addEventListener("click", () => {
        const value = textarea.value.trim();
        if (value) resend(index, value);
      });
      textarea.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
          event.preventDefault();
          const value = textarea.value.trim();
          if (value) resend(index, value);
        }
        if (event.key === "Escape") bubble.innerHTML = original;
      });
    }

    function clear() {
      session.generation = (session.generation || 0) + 1;
      if (session.controller) session.controller.abort();
      session.streaming = false;
      session.controller = null;
      session.messages = [];
      session.assistant = null;
      root.innerHTML = "";
      if (options.welcome) options.welcome.classList.remove("hidden");
      if (options.stats) {
        const stats = typeof options.stats === "string" ? $(options.stats) : options.stats;
        if (stats) stats.innerHTML = "";
      }
      if (options.onClear) options.onClear();
      if (input) { input.value = ""; input.style.height = "auto"; }
      setBusy(false);
      scrollToBottom(true);
    }
    session.clear = clear;

    root.addEventListener("click", (event) => {
      const editButton = event.target.closest("[data-edit-message]");
      if (editButton) {
        startEdit(Number(editButton.dataset.editMessage));
        return;
      }
      const copyUser = event.target.closest("[data-copy-user]");
      if (copyUser) {
        const message = session.messages[Number(copyUser.dataset.copyUser)];
        copyText(message && (message.display || message.content) || "", "已复制问题");
        return;
      }
      const copyImage = event.target.closest("[data-media-copy]");
      if (copyImage) {
        copyImageFromUrl(copyImage.dataset.mediaCopy);
        return;
      }
      const copyLink = event.target.closest("[data-media-copy-link]");
      if (copyLink) {
        copyText(copyLink.dataset.mediaCopyLink, "已复制媒体链接");
        return;
      }
      const external = event.target.closest("a[href^='http']");
      if (external && !external.hasAttribute("download")) {
        event.preventDefault();
        IMP().openExternal(external.getAttribute("href"));
      }
    });

    session.init = function () {
      if (sendButton) {
        sendButton.addEventListener("click", () => {
          if (session.streaming) stop();
          else send();
        });
      }
      if (input) {
        input.addEventListener("input", () => {
          input.style.height = "auto";
          input.style.height = Math.min(options.maxInputHeight || 140, input.scrollHeight) + "px";
        });
        input.addEventListener("keydown", (event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            if (!session.streaming) send();
          }
        });
      }
    };
    return session;
  }

  /* ------------------------------------------------------------------ */
  /* Boot                                                               */
  /* ------------------------------------------------------------------ */
  function initMain() {
    if (mainSession) return mainSession;
    const root = $("#messages");
    if (!root) return null;
    mainSession = createSession({
      name: "main",
      root,
      scroller: $("#chatScroll"),
      input: $("#chatInput"),
      sendButton: $("#btnSend"),
      stats: "#chatStats",
      welcome: $("#chatWelcome"),
      modelSelect: $("#modelSelect"),
      getAttachments: () => S().attachments,
      clearAttachments: () => {
        S().attachments = [];
        if (IMP().renderAttachmentBar) IMP().renderAttachmentBar();
      },
      buildContext: () => IMP().buildContext(),
      maxInputHeight: 200,
    });
    mainSession.init();
    bindModelSelect($("#modelSelect"));
    const newChat = $("#btnNewChat");
    if (newChat) {
      newChat.addEventListener("click", () => {
        if (!mainSession.messages.length) return;
        if (!window.confirm("清空当前对话？已生成的报告与教材索引不会受影响。")) return;
        mainSession.clear();
        toast("已开始新对话", "", "ok", 2000);
      });
    }
    const copyChat = $("#btnCopyChat");
    if (copyChat) {
      copyChat.addEventListener("click", () => {
        if (!mainSession.messages.length) return toast("暂无对话", "先提一个问题。", "amber");
        const text = mainSession.messages.map((message) =>
          `${message.role === "user" ? "用户" : "助手"}：${message.display || message.content}`).join("\n\n");
        copyText(text, "已复制当前对话");
      });
    }
    applyToolVisibility();
    return mainSession;
  }

  function init() {
    initDisplay();
    bindSettings();
    initMain();
  }

  function sendFromPrompt(prompt) {
    const input = $("#chatInput");
    if (input) input.value = prompt || "";
    if (mainSession) return mainSession.send();
  }

  function resetMain() {
    if (mainSession) mainSession.clear();
  }

  window.ChatUI = {
    init,
    initMain,
    createSession,
    populateModelSelects,
    renderConnectionList,
    connectionHasKey,
    bindSettings,
    bindModelSelect,
    syncDisplayChips,
    applyToolVisibility,
    setShowTools,
    sendFromPrompt,
    resetMain,
    get mainSession() { return mainSession; },
  };
})();
