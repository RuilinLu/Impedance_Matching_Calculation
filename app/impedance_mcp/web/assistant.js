/* Floating AI assistant available on every view. */
(function () {
  "use strict";

  const IMP = () => window.IMP;
  const T = (key, fallback) => IMP().t(key, fallback);
  const $ = (selector, root = document) => root.querySelector(selector);

  const STATE = {
    open: false,
    streaming: false,
    messages: [],
    attachments: [],
    pendingContext: null,
    unread: false,
    initialized: false,
  };

  function init() {
    if (STATE.initialized) return;
    STATE.initialized = true;
    $("#qaToggle").addEventListener("click", () => setOpen(true));
    $("#qaCollapse").addEventListener("click", () => setOpen(false));
    $("#qaSend").addEventListener("click", send);
    $("#qaAttach").addEventListener("click", () => $("#qaFileInput").click());
    $("#qaFileInput").addEventListener("change", (event) => {
      uploadFiles(event.target.files);
      event.target.value = "";
    });
    $("#qaInput").addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        send();
      }
    });
    $("#qaInput").addEventListener("input", () => {
      const input = $("#qaInput");
      input.style.height = "auto";
      input.style.height = Math.min(140, input.scrollHeight) + "px";
    });
    $("#qaInput").addEventListener("paste", handlePaste);
    const composer = $(".qa-composer");
    if (composer) {
      composer.addEventListener("dragover", (event) => {
        event.preventDefault();
        composer.classList.add("dragging");
      });
      composer.addEventListener("dragleave", () => composer.classList.remove("dragging"));
      composer.addEventListener("drop", (event) => {
        event.preventDefault();
        composer.classList.remove("dragging");
        uploadFiles(event.dataTransfer.files);
      });
    }
    const bar = document.createElement("div");
    bar.id = "qaAttachmentBar";
    bar.className = "attachment-bar qa-attachment-bar";
    composer.insertBefore(bar, composer.firstChild);
    updateContextLabel();
    document.addEventListener("langchange", updateContextLabel);
    document.addEventListener("selectionchange", () => {
      if (!STATE.open) return;
      const selection = String(window.getSelection ? window.getSelection().toString() : "").trim();
      if (selection.length > 4) {
        $("#qaContext").textContent = `${T("qa.selection", "选中")} ${selection.slice(0, 42)}…`;
      } else {
        updateContextLabel();
      }
    });
  }

  function setOpen(open) {
    STATE.open = !!open;
    const root = $("#quickAssistant");
    root.classList.toggle("collapsed", !STATE.open);
    if (STATE.open) {
      STATE.unread = false;
      $("#qaToggle").classList.remove("unread");
      setTimeout(() => $("#qaInput").focus(), 120);
      updateContextLabel();
    }
  }

  function updateContextLabel() {
    const view = IMP().state.view;
    const names = {
      agent: T("qa.viewAgent", "AI 智能体"),
      design: T("qa.viewDesign", "匹配设计"),
      analysis: T("qa.viewAnalysis", "圆图分析"),
      stress: T("qa.viewStress", "耐压分析"),
      library: T("qa.viewLibrary", "教材库"),
      docs: T("qa.viewDocs", "文档中心"),
      about: T("qa.viewAbout", "关于"),
    };
    let label = names[view] || T("qa.title", "AI 助手");
    if (view === "library" && window.Library && window.Library.current()) {
      const current = window.Library.current();
      label = `${current.title} · p.${current.page}`;
    }
    if (view === "docs" && window.Docs && window.Docs.current()) {
      const current = window.Docs.current();
      label = current.title || label;
    }
    const element = $("#qaContext");
    if (element) element.textContent = label;
  }

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
      uploadFiles(files);
    }
  }

  async function uploadFiles(files) {
    const list = Array.from(files || []);
    for (const file of list.slice(0, Math.max(0, 4 - STATE.attachments.length))) {
      if (file.size > 60 * 1024 * 1024) {
        IMP().toast("文件过大", `${file.name} 超过 60 MB。`, "err");
        continue;
      }
      try {
        const base64 = await readBase64(file);
        const info = await IMP().api("/api/upload", {
          method: "POST",
          body: { name: file.name, content_base64: base64 },
        });
        STATE.attachments.push(info);
        renderAttachments();
        IMP().toast("附件已解析", `${info.name} · ${info.kind} · ${info.chars || 0} 字符`, "ok", 3000);
      } catch (error) {
        IMP().toast("附件失败", error.message, "err");
      }
    }
  }

  function readBase64(file) {
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

  function renderAttachments() {
    const bar = $("#qaAttachmentBar");
    if (!bar) return;
    bar.innerHTML = STATE.attachments.map((item, index) =>
      `<span class="attachment-chip">${IMP().escapeHtml(item.name)} <small>${IMP().escapeHtml(item.kind || "")} · ${Number(item.chars || 0)} 字${item.image_count ? ` · ${item.image_count} 图` : ""}</small><button data-qa-remove="${index}"><svg><use href="#i-close"/></svg></button></span>`).join("");
    bar.querySelectorAll("[data-qa-remove]").forEach((button) => button.addEventListener("click", () => {
      STATE.attachments.splice(Number(button.dataset.qaRemove), 1);
      renderAttachments();
    }));
  }

  function addUser(text, attachments) {
    IMP().addUserMessage($("#qaMessages"), text, attachments);
    scroll();
  }

  function makeAssistant() {
    return IMP().makeAssistant($("#qaMessages"));
  }

  function scroll() {
    const element = $("#qaMessages");
    if (element) element.scrollTop = element.scrollHeight;
  }

  function buildPayload() {
    const text = $("#qaInput").value.trim();
    if (!text && !STATE.attachments.length) return null;
    const base = IMP().buildContext() || {};
    const context = Object.assign({}, base, STATE.pendingContext || {});
    if (STATE.attachments.length) {
      context.attachments = STATE.attachments.map((item) => ({
        name: item.name, kind: item.kind, chars: item.chars,
      }));
    }
    const userText = text || "请阅读附件并总结与当前界面相关的关键信息。";
    addUser(userText, STATE.attachments);
    STATE.messages.push({
      role: "user",
      content: userText + (STATE.attachments.length ? `\n[附件: ${STATE.attachments.map((item) => item.name).join(", ")}]` : ""),
    });
    const payload = {
      messages: STATE.messages.slice(-14),
      attachments: STATE.attachments.map((item) => ({ id: item.id, name: item.name })),
      model: $("#modelSelect") ? $("#modelSelect").value : "",
      context,
    };
    $("#qaInput").value = "";
    $("#qaInput").style.height = "auto";
    STATE.attachments = [];
    renderAttachments();
    STATE.pendingContext = null;
    return { payload, userText };
  }

  async function send() {
    if (STATE.streaming) return;
    const built = buildPayload();
    if (!built) return;
    const llm = (IMP().state.config && IMP().state.config.llm) || {};
    if (!llm.provider || !llm.has_key || !llm.base_url || !llm.model) {
      IMP().toast("请先配置模型服务", "点击设置，选择服务商并填写 API Key。", "amber", 5000);
      IMP().openSettings();
      return;
    }
    STATE.streaming = true;
    $("#qaSend").disabled = true;
    const assistant = makeAssistant();
    try {
      const result = await IMP().streamChat(built.payload, {
        onEvent: (eventName, data) => IMP().handleChatEvent(eventName, data, assistant, { statsTarget: "#qaStats" }),
      });
      if (assistant.typing) { assistant.typing.remove(); assistant.typing = null; }
      if (!assistant.errored) {
        assistant.md.innerHTML = IMP().renderMarkdown(result.content || assistant.buffer || "（未收到回答）");
        IMP().typesetMath(assistant.md);
        STATE.messages.push({ role: "assistant", content: result.content || assistant.buffer || "" });
        if (STATE.messages.length > 20) STATE.messages = STATE.messages.slice(-20);
      }
      scroll();
    } catch (error) {
      if (assistant.typing) { assistant.typing.remove(); assistant.typing = null; }
      assistant.md.innerHTML = `<div class="error-box"><b>智能体暂时不可用</b><p>${IMP().escapeHtml(error.message)}</p></div>`;
      IMP().toast("助手调用失败", error.message, "err", 6000);
    } finally {
      STATE.streaming = false;
      $("#qaSend").disabled = false;
      if (!STATE.open) {
        STATE.unread = true;
        $("#qaToggle").classList.add("unread");
      }
      scroll();
    }
  }

  function openWithPrompt(prompt, context) {
    init();
    setOpen(true);
    STATE.pendingContext = context || null;
    $("#qaInput").value = prompt || "";
    setTimeout(send, 80);
  }

  window.Assistant = {
    init,
    setOpen,
    openWithPrompt,
    updateContextLabel,
  };
})();
