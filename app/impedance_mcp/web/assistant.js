/* Floating AI assistant available on every view. */
(function () {
  "use strict";

  const IMP = () => window.IMP;
  const T = (key, fallback) => IMP().t(key, fallback);
  const $ = (selector, root = document) => root.querySelector(selector);

  const STATE = {
    open: false,
    attachments: [],
    pendingContext: null,
    unread: false,
    initialized: false,
    session: null,
  };

  function init() {
    if (STATE.initialized) return;
    STATE.initialized = true;
    $("#qaToggle").addEventListener("click", () => setOpen(true));
    $("#qaCollapse").addEventListener("click", () => setOpen(false));
    $("#qaAttach").addEventListener("click", () => $("#qaFileInput").click());
    $("#qaFileInput").addEventListener("change", (event) => {
      uploadFiles(event.target.files);
      event.target.value = "";
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

    STATE.session = window.ChatUI.createSession({
      name: "quick",
      root: $("#qaMessages"),
      scroller: $("#qaMessages"),
      input: $("#qaInput"),
      sendButton: $("#qaSend"),
      stats: "#qaStats",
      modelSelect: $("#qaModelSelect"),
      getAttachments: () => STATE.attachments,
      clearAttachments: () => {
        STATE.attachments = [];
        renderAttachments();
      },
      buildContext: () => {
        const base = IMP().buildContext() || {};
        return Object.assign({}, base, STATE.pendingContext || {});
      },
      maxInputHeight: 130,
      onFinish: () => {
        if (!STATE.open) {
          STATE.unread = true;
          $("#qaToggle").classList.add("unread");
        }
      },
      onClear: () => {
        STATE.attachments = [];
        renderAttachments();
        STATE.pendingContext = null;
      },
    });
    STATE.session.init();
    window.ChatUI.bindModelSelect($("#qaModelSelect"));
    const newChat = $("#qaNewChat");
    if (newChat) {
      newChat.addEventListener("click", () => {
        if (!STATE.session.messages.length) return;
        if (!window.confirm("清空右侧助手的当前对话？")) return;
        STATE.session.clear();
        IMP().toast("已清空对话", "", "ok", 1800);
      });
    }
    window.ChatUI.applyToolVisibility();
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
      if (STATE.session) STATE.session.scrollToBottom(true);
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
    const room = Math.max(0, 4 - STATE.attachments.length);
    for (const file of list.slice(0, room)) {
      if (file.size > 60 * 1024 * 1024) {
        IMP().toast("文件过大", `${file.name} 超过 60 MB。`, "err");
        continue;
      }
      const name = file.name || (file.type && file.type.startsWith("image/")
        ? `粘贴图片_${Date.now()}.png` : "粘贴附件");
      const placeholder = {
        id: null, name, kind: "上传中", chars: 0, uploading: true,
        progress: 0, size: file.size,
      };
      STATE.attachments.push(placeholder);
      renderAttachments();
      try {
        const info = await IMP().uploadBlobWithProgress(file, (progress) => {
          placeholder.progress = progress;
          placeholder.kind = `上传中 ${Math.round(progress * 100)}%`;
          renderAttachments();
        });
        const index = STATE.attachments.indexOf(placeholder);
        if (index >= 0) STATE.attachments[index] = info;
        renderAttachments();
        IMP().toast("附件已解析", `${info.name} · ${info.kind} · ${info.chars || 0} 字符`, "ok", 3000);
      } catch (error) {
        const index = STATE.attachments.indexOf(placeholder);
        if (index >= 0) STATE.attachments.splice(index, 1);
        renderAttachments();
        IMP().toast("附件失败", `${name}：${error.message}`, "err");
      }
    }
  }

  function renderAttachments() {
    const bar = $("#qaAttachmentBar");
    if (!bar) return;
    bar.innerHTML = STATE.attachments.map((item, index) => {
      if (item.uploading) {
        const percent = Math.round((item.progress || 0) * 100);
        return `<span class="attachment-chip uploading"><span class="attach-spinner"></span>${IMP().escapeHtml(item.name)}<small>${percent}% · ${IMP().formatBytes(item.size)}</small><span class="attach-progress"><i style="width:${percent}%"></i></span><button data-qa-remove="${index}"><svg><use href="#i-close"/></svg></button></span>`;
      }
      return `<span class="attachment-chip">${IMP().escapeHtml(item.name)} <small>${IMP().escapeHtml(item.kind || "")} · ${Number(item.chars || 0)} 字${item.image_count ? ` · ${item.image_count} 图` : ""}</small><button data-qa-remove="${index}"><svg><use href="#i-close"/></svg></button></span>`;
    }).join("");
    bar.querySelectorAll("[data-qa-remove]").forEach((button) => button.addEventListener("click", () => {
      STATE.attachments.splice(Number(button.dataset.qaRemove), 1);
      renderAttachments();
    }));
  }

  function openWithPrompt(prompt, context) {
    init();
    setOpen(true);
    STATE.pendingContext = context || null;
    $("#qaInput").value = prompt || "";
    setTimeout(() => STATE.session.send(), 80);
  }

  window.Assistant = {
    init,
    setOpen,
    openWithPrompt,
    updateContextLabel,
  };
})();
