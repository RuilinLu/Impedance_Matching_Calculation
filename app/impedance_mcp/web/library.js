/* Textbook library UI: search, page rendering, OCR, translation, citations. */
(function () {
  "use strict";

  const IMP = () => window.IMP;
  const esc = (value) => IMP().escapeHtml(value);
  const T = (key, fallback) => IMP().t(key, fallback);

  const STATE = {
    docs: [],
    currentDoc: null,
    currentPage: 1,
    zoom: 1.2,
    rects: [],
    text: "",
    title: "",
    translation: null,
    results: [],
    filter: "",
    loadingPage: false,
    statusTimer: null,
    initialized: false,
  };

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  function markSnippet(text) {
    return esc(text || "").replace(/\[\[(.+?)\]\]/g, "<mark>$1</mark>");
  }

  function init() {
    if (STATE.initialized) return;
    STATE.initialized = true;
    $("#btnAddBook").addEventListener("click", () => $("#bookInput").click());
    $("#bookInput").addEventListener("change", handleBookUpload);
    $("#btnReindex").addEventListener("click", reindex);
    $("#btnLibrarySearch").addEventListener("click", runSearch);
    $("#btnLibraryAi").addEventListener("click", runAiSearch);
    $("#libraryQuery").addEventListener("keydown", (event) => {
      if (event.key === "Enter") runSearch();
    });
    $("#libraryBookFilter").addEventListener("input", (event) => {
      STATE.filter = event.target.value.trim().toLowerCase();
      renderDocList();
    });
    $("#libPrev").addEventListener("click", () => goPage(STATE.currentPage - 1));
    $("#libNext").addEventListener("click", () => goPage(STATE.currentPage + 1));
    $("#libPageInput").addEventListener("change", (event) => goPage(Number(event.target.value)));
    $("#libZoomIn").addEventListener("click", () => setZoom(STATE.zoom + 0.2));
    $("#libZoomOut").addEventListener("click", () => setZoom(STATE.zoom - 0.2));
    $("#libOcr").addEventListener("click", runOcr);
    $("#libOcrBook").addEventListener("click", runOcrBook);
    $("#libTranslate").addEventListener("click", runTranslate);
    $("#libAsk").addEventListener("click", askPage);
    $("#libraryPage").addEventListener("load", () => {
      $("#libraryLoading").classList.add("hidden");
      drawHighlights();
    });
    $("#libraryPage").addEventListener("error", () => {
      $("#libraryLoading").classList.add("hidden");
      $("#libraryPage").classList.add("hidden");
    });
    window.addEventListener("resize", drawHighlights);
    document.addEventListener("langchange", () => {
      renderDocList();
      renderResults();
      updateStatusText(window.__libraryStatus || null);
    });
  }

  async function onShow() {
    init();
    try {
      const status = await IMP().api("/api/library/status");
      window.__libraryStatus = status;
      updateStatusText(status);
      if (!STATE.docs.length) await loadDocs();
      if (status.running) startPolling();
    } catch (error) {
      updateStatusText(null, error.message);
    }
  }

  async function loadDocs() {
    try {
      const result = await IMP().api("/api/library/docs");
      STATE.docs = result.documents || [];
      $("#libraryCount").textContent = String(STATE.docs.length);
      renderDocList();
    } catch (error) {
      IMP().toast("教材列表加载失败", error.message, "err");
    }
  }

  function renderDocList() {
    const list = $("#libraryDocList");
    if (!list) return;
    const docs = STATE.docs.filter((doc) =>
      !STATE.filter || `${doc.title} ${doc.filename}`.toLowerCase().includes(STATE.filter));
    if (!docs.length) {
      list.innerHTML = `<div class="empty-mini">${esc(T("library.noDocs", "还没有可检索的教材。"))}</div>`;
      return;
    }
    list.innerHTML = docs.map((doc) => {
      const active = STATE.currentDoc && STATE.currentDoc.id === doc.id;
      const lang = doc.lang === "zh" ? "中文" : doc.lang === "en" ? "EN" : "";
      let ocr = "";
      if (doc.needs_ocr > Math.max(8, doc.pages * 0.18)) {
        ocr = `<span class="badge amber" title="待 OCR">OCR</span>`;
      } else if (doc.ocr_pages) {
        ocr = `<span class="badge" title="已 OCR 页数">OCR ${doc.ocr_pages}</span>`;
      }
      return `<button class="library-doc ${active ? "active" : ""}" data-doc="${doc.id}">
        <div class="library-doc-title">${esc(doc.title)}</div>
        <div class="library-doc-meta"><span>${doc.pages} p</span><span>${lang}</span>${ocr}</div>
      </button>`;
    }).join("");
    $$("[data-doc]", list).forEach((button) => button.addEventListener("click", () => {
      const doc = STATE.docs.find((item) => item.id === Number(button.dataset.doc));
      if (doc) openPage(doc.id, 1, []);
    }));
  }

  async function refreshStatus() {
    try {
      const status = await IMP().api("/api/library/status");
      window.__libraryStatus = status;
      updateStatusText(status);
      if (!status.running) {
        stopPolling();
        await loadDocs();
      }
    } catch (error) { /* keep polling */ }
  }

  function updateStatusText(status, error) {
    const element = $("#libraryIndexStatus");
    if (!element) return;
    if (error) {
      element.innerHTML = `<span class="bad">${esc(error)}</span>`;
      return;
    }
    if (!status) {
      element.textContent = "—";
      return;
    }
    if (status.running) {
      const percent = status.total ? Math.round(100 * status.done / status.total) : 0;
      element.innerHTML = `<div class="index-progress"><i style="width:${percent}%"></i></div>
        <span>${esc(T("library.indexing", "索引中…"))} ${status.done}/${status.total} · ${esc(status.current || "")}</span>`;
      return;
    }
    element.innerHTML = `<span><b>${status.docs || 0}</b> ${T("library.books", "本")} · <b>${status.indexed_pages || 0}</b> ${T("library.pages", "页")} · <b>${status.ocr_pages || 0}</b> OCR · <b>${status.needs_ocr || 0}</b> ${T("library.pendingOcr", "待 OCR")}</span>`;
  }

  function startPolling() {
    if (STATE.statusTimer) return;
    STATE.statusTimer = setInterval(refreshStatus, 1800);
  }

  function stopPolling() {
    if (STATE.statusTimer) {
      clearInterval(STATE.statusTimer);
      STATE.statusTimer = null;
    }
  }

  async function reindex() {
    try {
      await IMP().api("/api/library/index", { method: "POST", body: { force: true } });
      IMP().toast("已开始重建索引", "后台扫描教材文件。", "ok");
      startPolling();
      refreshStatus();
    } catch (error) { IMP().toast("重建失败", error.message, "err"); }
  }

  async function handleBookUpload(event) {
    const files = Array.from(event.target.files || []);
    event.target.value = "";
    for (const file of files) {
      if (file.size > 120 * 1024 * 1024) {
        IMP().toast("文件过大", `${file.name} 超过 120 MB。`, "err");
        continue;
      }
      try {
        IMP().toast("正在读取教材", file.name, "ok", 2000);
        const base64 = await readBase64(file);
        const result = await IMP().api("/api/library/upload", {
          method: "POST",
          body: { name: file.name, content_base64: base64 },
        });
        IMP().toast("教材已加入", result.message || file.name, "ok");
      } catch (error) {
        IMP().toast("教材添加失败", `${file.name}：${error.message}`, "err", 7000);
      }
    }
    await loadDocs();
    await refreshStatus();
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

  async function runSearch(ai) {
    const query = $("#libraryQuery").value.trim();
    if (!query) {
      IMP().toast("请输入关键词", "可以输入中文、英文、公式片段或代码。", "amber");
      return;
    }
    const fuzzy = $("#libraryFuzzy").checked;
    const meta = $("#librarySearchMeta");
    meta.textContent = T("library.searching", "检索中…");
    try {
      let result;
      if (ai) {
        result = await IMP().api("/api/library/ai_search", {
          method: "POST",
          body: { query, fuzzy, limit: 30 },
        });
      } else {
        const params = new URLSearchParams({ q: query, fuzzy: fuzzy ? "1" : "0", limit: "30" });
        result = await IMP().api(`/api/library/search?${params.toString()}`);
      }
      STATE.results = result.results || [];
      meta.innerHTML = `${result.count || 0} ${esc(T("library.hits", "个命中页"))}` +
        (result.terms && result.terms.length ? ` · ${esc(result.terms.slice(0, 8).join(" / "))}` : "") +
        (result.note ? `<br><span class="muted">${esc(result.note)}</span>` : "") +
        (result.message ? `<br><span class="muted">${esc(result.message)}</span>` : "");
      renderResults();
    } catch (error) {
      meta.textContent = error.message;
      IMP().toast("检索失败", error.message, "err");
    }
  }

  function runAiSearch() { runSearch(true); }

  function renderResults() {
    const container = $("#libraryResults");
    if (!container) return;
    if (!STATE.results.length) {
      container.innerHTML = `<div class="empty-mini">${esc(T("library.resultsEmpty", "输入关键词开始检索；结果会显示书名、页码与命中片段。"))}</div>`;
      return;
    }
    container.innerHTML = STATE.results.map((item, index) => `
      <button class="library-result ${index === 0 ? "best" : ""}" data-result="${index}">
        <div class="library-result-head"><b>${esc(item.title)}</b><span class="tag ${item.source === "ocr" ? "amber" : "cyan"}">${item.source === "ocr" ? "OCR" : "TEXT"}</span></div>
        <div class="library-result-page">p.${item.page} · score ${item.score}</div>
        <p>${markSnippet(item.snippet)}</p>
      </button>`).join("");
    $$("[data-result]", container).forEach((button) => button.addEventListener("click", () => {
      const item = STATE.results[Number(button.dataset.result)];
      if (item) openPage(item.doc_id, item.page, item.rects || []);
    }));
  }

  async function openPage(docId, page, rects) {
    if (!docId) return;
    init();
    STATE.rects = rects || [];
    STATE.currentPage = Math.max(1, Number(page) || 1);
    STATE.translation = null;
    try {
      const doc = await IMP().api(`/api/library/doc?id=${docId}`);
      if (!doc.ok) throw new Error(doc.message || "文档不存在");
      STATE.currentDoc = doc;
      STATE.title = doc.title;
      const isPdf = String(doc.filename || "").toLowerCase().endsWith(".pdf");
      $("#libraryDocTitle").textContent = doc.title;
      $("#libraryDocMeta").textContent = `${doc.pages} p · ${doc.lang} · ${isPdf ? "PDF" : doc.filename}`;
      $("#libPageInput").max = doc.pages;
      $("#libPageInput").value = STATE.currentPage;
      $("#libPageTotal").textContent = `/ ${doc.pages}`;
      $("#pdfEmpty").classList.add("hidden");
      $("#libraryLoading").classList.remove("hidden");
      if (isPdf) {
        $("#libraryPage").classList.remove("hidden");
        loadPageImage();
      } else {
        $("#libraryPage").classList.add("hidden");
        $("#libraryLoading").classList.add("hidden");
      }
      await loadPageInfo();
      renderDocList();
    } catch (error) {
      IMP().toast("无法打开教材页", error.message, "err", 6000);
      $("#libraryLoading").classList.add("hidden");
    }
  }

  function loadPageImage() {
    if (!STATE.currentDoc) return;
    $("#libraryLoading").classList.remove("hidden");
    const url = `/api/library/page?doc=${STATE.currentDoc.id}&page=${STATE.currentPage}&zoom=${STATE.zoom.toFixed(2)}`;
    const image = $("#libraryPage");
    image.onload = () => {
      $("#libraryLoading").classList.add("hidden");
      drawHighlights();
    };
    image.onerror = () => {
      $("#libraryLoading").classList.add("hidden");
      image.classList.add("hidden");
    };
    image.src = url;
    const wrap = $("#pdfCanvasWrap");
    if (wrap) wrap.style.width = `${Math.max(20, STATE.zoom * 100)}%`;
    $("#libZoomLabel").textContent = `${Math.round(STATE.zoom * 100)}%`;
  }

  async function loadPageInfo() {
    if (!STATE.currentDoc) return;
    try {
      const info = await IMP().api(`/api/library/page_info?doc=${STATE.currentDoc.id}&page=${STATE.currentPage}&lang=${window.I18N ? window.I18N.lang : "zh"}`);
      if (!info.ok) throw new Error(info.message);
      STATE.text = info.text || "";
      if (info.translation) STATE.translation = info.translation;
      $("#libraryText").textContent = STATE.text || T("library.needText", "当前页没有文字层。可以点击「OCR 本页」，或使用视觉模型读图。");
      $("#libraryTranslation").textContent = STATE.translation ? STATE.translation.text : T("library.noTranslation", "尚未翻译。点击「翻译」生成学术译文（需要配置模型）。");
      $("#libOcr").classList.toggle("needs", !!info.needs_ocr);
      drawHighlights();
    } catch (error) {
      $("#libraryText").textContent = error.message;
    }
  }

  function drawHighlights() {
    const overlay = $("#libraryHighlights");
    if (!overlay) return;
    const image = $("#libraryPage");
    const rects = STATE.rects || [];
    if (!rects.length || image.classList.contains("hidden")) {
      overlay.innerHTML = "";
      return;
    }
    overlay.innerHTML = rects.map((rect) =>
      `<i class="pdf-highlight" style="left:${rect[0] * 100}%;top:${rect[1] * 100}%;width:${Math.max(0.4, (rect[2] - rect[0]) * 100)}%;height:${Math.max(0.4, (rect[3] - rect[1]) * 100)}%"></i>`
    ).join("");
  }

  function goPage(page) {
    if (!STATE.currentDoc) return;
    const target = Math.max(1, Math.min(STATE.currentDoc.pages, Number(page) || 1));
    if (target === STATE.currentPage) {
      $("#libPageInput").value = target;
      return;
    }
    STATE.currentPage = target;
    STATE.rects = [];
    STATE.translation = null;
    $("#libPageInput").value = target;
    if (String(STATE.currentDoc.filename || "").toLowerCase().endsWith(".pdf")) loadPageImage();
    loadPageInfo();
  }

  function setZoom(value) {
    STATE.zoom = Math.max(0.4, Math.min(3.0, value));
    if (STATE.currentDoc && String(STATE.currentDoc.filename || "").toLowerCase().endsWith(".pdf")) {
      loadPageImage();
    }
  }

  async function runOcr() {
    if (!STATE.currentDoc) return IMP().toast("请先打开一页", "", "amber");
    const button = $("#libOcr");
    button.disabled = true;
    const old = button.innerHTML;
    button.innerHTML = `<span>${esc(T("library.ocrRunning", "OCR 中…"))}</span>`;
    try {
      const result = await IMP().api("/api/library/ocr", {
        method: "POST",
        body: { doc_id: STATE.currentDoc.id, page: STATE.currentPage, force: true },
      });
      if (!result.ok) throw new Error(result.message || "OCR 失败");
      IMP().toast("OCR 完成", `${(result.text || "").length} 字符`, "ok");
      await loadPageInfo();
      await refreshStatus();
    } catch (error) {
      IMP().toast("OCR 失败", error.message + (error.data && error.data.hint ? ` ${error.data.hint}` : ""), "err", 7000);
    } finally {
      button.disabled = false;
      button.innerHTML = old;
    }
  }

  async function runOcrBook() {
    if (!STATE.currentDoc) return IMP().toast("请先打开一页", "", "amber");
    const en = window.I18N && window.I18N.lang === "en";
    const startText = window.prompt(
      en ? "First page to OCR" : "从第几页开始 OCR", "1");
    if (startText === null) return;
    const endText = window.prompt(
      en ? "Last page to OCR (max 40 pages per batch)" : "OCR 到第几页（每批最多 40 页）",
      String(Math.min(STATE.currentDoc.pages, Number(startText || 1) + 39)));
    if (endText === null) return;
    const start = Math.max(1, Number(startText) || 1);
    const end = Math.max(start, Number(endText) || start);
    const button = $("#libOcrBook");
    button.disabled = true;
    const old = button.innerHTML;
    button.innerHTML = `<span>${esc(T("library.ocrRunning", "OCR 中…"))}</span>`;
    try {
      const result = await IMP().api("/api/library/ocr_book", {
        method: "POST",
        body: {
          doc_id: STATE.currentDoc.id,
          start,
          end,
          max_pages: Math.min(40, Math.max(1, end - start + 1)),
        },
      });
      if (!result.ok) throw new Error(result.message || "OCR 失败");
      IMP().toast(
        en ? "OCR queued" : "OCR 已排队",
        result.message || `${start}–${end}`,
        "ok", 5000);
      startPolling();
      await refreshStatus();
    } catch (error) {
      IMP().toast("OCR 失败", error.message + (error.data && error.data.hint ? ` ${error.data.hint}` : ""), "err", 7000);
    } finally {
      button.disabled = false;
      button.innerHTML = old;
    }
  }

  async function runTranslate() {
    if (!STATE.currentDoc) return IMP().toast("请先打开一页", "", "amber");
    const button = $("#libTranslate");
    button.disabled = true;
    const old = button.innerHTML;
    button.innerHTML = `<span>${esc(T("library.translating", "翻译中…"))}</span>`;
    try {
      const result = await IMP().api("/api/library/translate", {
        method: "POST",
        body: { doc_id: STATE.currentDoc.id, page: STATE.currentPage },
      });
      if (!result.ok) throw new Error(result.message || "翻译失败");
      STATE.translation = result;
      $("#libraryTranslation").textContent = result.text || "";
      IMP().toast("翻译完成", `${result.lang} · ${result.cached ? "缓存" : "新译"}`, "ok");
    } catch (error) {
      IMP().toast("翻译失败", error.message + (error.data && error.data.hint ? ` ${error.data.hint}` : ""), "err", 8000);
    } finally {
      button.disabled = false;
      button.innerHTML = old;
    }
  }

  function askPage() {
    if (!STATE.currentDoc) return IMP().toast("请先打开一页", "", "amber");
    if (!window.Assistant) return;
    const prompt = window.I18N && window.I18N.lang === "en"
      ? `Explain page ${STATE.currentPage} of "${STATE.title}" in the context of microwave engineering. Cite the book and page.`
      : `请结合微波工程解释《${STATE.title}》第 ${STATE.currentPage} 页的内容，并引用书名与页码。`;
    window.Assistant.openWithPrompt(prompt, {
      library: {
        doc_id: STATE.currentDoc.id,
        page: STATE.currentPage,
        title: STATE.title,
        selection: String(window.getSelection ? window.getSelection().toString() : "").slice(0, 1200),
      },
    });
  }

  function current() {
    if (!STATE.currentDoc) return null;
    return {
      docId: STATE.currentDoc.id,
      page: STATE.currentPage,
      title: STATE.title,
      text: STATE.text,
    };
  }

  window.Library = {
    init,
    onShow,
    openPage,
    current,
    refreshStatus,
  };
})();
