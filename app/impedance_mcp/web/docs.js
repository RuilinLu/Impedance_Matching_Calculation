/* Documentation centre: four domains, full-text search, match navigation, AI search. */
(function () {
  "use strict";

  const IMP = () => window.IMP;
  const esc = (value) => IMP().escapeHtml(value);
  const T = (key, fallback) => IMP().t(key, fallback);
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  const STATE = {
    categories: [],
    category: "features",
    title: "",
    description: "",
    markdown: "",
    query: "",
    matches: [],
    matchIndex: -1,
    results: [],
    resultMap: {},
    pendingFocus: null,
    initialized: false,
    searchTimer: null,
  };

  function init() {
    if (STATE.initialized) return;
    STATE.initialized = true;
    $("#btnDocsSearch").addEventListener("click", () => runSearch(false));
    $("#btnDocsAi").addEventListener("click", () => runSearch(true));
    $("#docsQuery").addEventListener("keydown", (event) => {
      if (event.key === "Enter") runSearch(false);
    });
    $("#docsQuery").addEventListener("input", () => {
      clearTimeout(STATE.searchTimer);
      STATE.searchTimer = setTimeout(() => {
        const query = $("#docsQuery").value.trim();
        if (query.length >= 2) runSearch(false, true);
        else clearLocalHighlights();
      }, 380);
    });
    $("#docsPrev").addEventListener("click", () => moveMatch(-1));
    $("#docsNext").addEventListener("click", () => moveMatch(1));
    $("#docsAsk").addEventListener("click", askDoc);
    document.addEventListener("langchange", async () => {
      await loadCategories();
      await loadDoc(STATE.category, { keepQuery: true });
      if (STATE.query) runSearch(false, true);
    });
  }

  async function onShow() {
    init();
    if (!STATE.categories.length) await loadCategories();
    if (!STATE.markdown) await loadDoc(STATE.category);
  }

  async function loadCategories() {
    try {
      const lang = window.I18N ? window.I18N.lang : "zh";
      const result = await IMP().api(`/api/docs/list?lang=${lang}`);
      STATE.categories = result.categories || [];
      $("#docsCount").textContent = String(STATE.categories.length);
      renderCategories();
    } catch (error) {
      IMP().toast("文档目录加载失败", error.message, "err");
    }
  }

  function renderCategories() {
    const list = $("#docsCategoryList");
    if (!list) return;
    list.innerHTML = STATE.categories.map((category) => `
      <button class="docs-category ${category.id === STATE.category ? "active" : ""}" data-category="${esc(category.id)}">
        <b>${esc(category.title)}</b>
        <small>${esc(category.description)}</small>
        <span>${Math.round(category.chars / 1000)}k chars</span>
      </button>`).join("");
    $$("[data-category]", list).forEach((button) => button.addEventListener("click", () => {
      loadDoc(button.dataset.category);
    }));
  }

  async function loadDoc(category, options = {}) {
    STATE.category = category || STATE.category;
    const lang = window.I18N ? window.I18N.lang : "zh";
    $("#docsContent").innerHTML = `<div class="empty-mini">${esc(T("common.loading", "加载中…"))}</div>`;
    try {
      const result = await IMP().api(`/api/docs/get?category=${encodeURIComponent(STATE.category)}&lang=${lang}`);
      if (!result.ok) throw new Error(result.message || "文档不存在");
      STATE.title = result.title;
      STATE.description = result.description;
      STATE.markdown = result.markdown;
      STATE.matches = [];
      STATE.matchIndex = -1;
      $("#docsTitle").textContent = result.title;
      $("#docsDesc").textContent = result.description;
      $("#docsContent").innerHTML = IMP().renderMarkdown(result.markdown);
      renderCategories();
      updateMatchNav();
      if (STATE.query) {
        highlightQuery(STATE.query);
      } else {
        clearLocalHighlights();
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
      if (options.focusSnippet || options.focusHeading) {
        setTimeout(() => focusSnippet(options.focusSnippet || "", options.focusHeading || ""), 40);
      } else if (!STATE.query) {
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
      setTimeout(() => IMP().typesetMath($("#docsContent")), 90);
    } catch (error) {
      $("#docsContent").innerHTML = `<div class="error-box"><b>无法加载文档</b><p>${esc(error.message)}</p></div>`;
    }
  }

  async function runSearch(ai, quiet) {
    const query = $("#docsQuery").value.trim();
    if (!query) {
      IMP().toast("请输入关键词", "可以搜索功能、代码、AI 接口与 MCP 协议。", "amber");
      return;
    }
    STATE.query = query;
    const meta = $("#docsSearchMeta");
    meta.textContent = T("common.loading", "检索中…");
    try {
      let result;
      if (ai) {
        result = await IMP().api("/api/docs/ai_search", {
          method: "POST",
          body: {
            query,
            lang: window.I18N ? window.I18N.lang : "zh",
            category: null,
            limit: 60,
          },
        });
      } else {
        const params = new URLSearchParams({
          q: query,
          lang: window.I18N ? window.I18N.lang : "zh",
          limit: "60",
        });
        result = await IMP().api(`/api/docs/search?${params.toString()}`);
      }
      STATE.results = result.results || [];
      STATE.resultMap = {};
      STATE.results.forEach((item) => { STATE.resultMap[item.block_id] = item; });
      meta.innerHTML = `${result.count || 0} ${esc(T("docs.hits", "个段落命中"))}` +
        (result.terms && result.terms.length ? ` · ${esc(result.terms.slice(0, 8).join(" / "))}` : "") +
        (result.note ? `<br><span class="muted">${esc(result.note)}</span>` : "");
      renderResults();
      if (!quiet) {
        /* Highlight inside the currently open document as well. */
        highlightQuery(query);
        /* If the current document has no match, open the first result. */
        if (!STATE.matches.length && STATE.results.length) {
          const first = STATE.results[0];
          await loadDoc(first.category, { focusSnippet: first.snippet, focusHeading: first.heading, keepQuery: true });
        }
      } else {
        highlightQuery(query);
      }
    } catch (error) {
      meta.textContent = error.message;
      IMP().toast("文档检索失败", error.message, "err");
    }
  }

  function renderResults() {
    const container = $("#docsResults");
    if (!container) return;
    if (!STATE.results.length) {
      container.innerHTML = `<div class="empty-mini">${esc(T("docs.noHits", "没有命中段落。"))}</div>`;
      return;
    }
    container.innerHTML = STATE.results.map((item, index) => `
      <button class="doc-result" data-doc-result="${index}">
        <div class="doc-result-head"><span class="tag ${item.category === "code" ? "cyan" : ""}">${esc(item.category_title)}</span><small>L${item.line}</small></div>
        <b>${esc(item.heading || item.category_title)}</b>
        <p>${highlightSnippet(item.snippet)}</p>
      </button>`).join("");
    $$("[data-doc-result]", container).forEach((button) => button.addEventListener("click", () => {
      const item = STATE.results[Number(button.dataset.docResult)];
      if (!item) return;
      if (item.category !== STATE.category) {
        loadDoc(item.category, { focusSnippet: item.snippet, focusHeading: item.heading, keepQuery: true });
      } else {
        focusSnippet(item.snippet, item.heading);
      }
    }));
  }

  function highlightSnippet(text) {
    return esc(text || "").replace(/\[\[(.+?)\]\]/g, "<mark>$1</mark>");
  }

  function escapeRegExp(text) {
    return String(text).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function queryTerms(query) {
    const terms = [query];
    for (const part of String(query).split(/[\s,，。;；、/|()（）]+/)) {
      if (part.length >= 2) terms.push(part);
    }
    for (const part of String(query).match(/[\u4e00-\u9fff]{4,}/g) || []) {
      for (let i = 0; i < part.length - 1; i++) terms.push(part.slice(i, i + 2));
    }
    return [...new Set(terms.filter(Boolean))].sort((a, b) => b.length - a.length);
  }

  function highlightQuery(query) {
    clearLocalHighlights();
    if (!query) return;
    const content = $("#docsContent");
    if (!content) return;
    const terms = queryTerms(query);
    const regex = new RegExp(terms.map(escapeRegExp).join("|"), "gi");
    const walker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        if (parent.closest("pre, code, script, style, mark, mjx-container")) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    for (const node of nodes) {
      const text = node.nodeValue;
      let match;
      let last = 0;
      let changed = false;
      const fragment = document.createDocumentFragment();
      regex.lastIndex = 0;
      while ((match = regex.exec(text)) !== null) {
        if (match.index > last) fragment.appendChild(document.createTextNode(text.slice(last, match.index)));
        const mark = document.createElement("mark");
        mark.className = "doc-hit";
        mark.textContent = match[0];
        fragment.appendChild(mark);
        STATE.matches.push(mark);
        last = match.index + match[0].length;
        changed = true;
        if (match[0].length === 0) regex.lastIndex += 1;
      }
      if (changed) {
        fragment.appendChild(document.createTextNode(text.slice(last)));
        node.parentNode.replaceChild(fragment, node);
      }
    }
    STATE.matchIndex = STATE.matches.length ? 0 : -1;
    updateMatchNav();
    if (STATE.matches.length) scrollToMatch(0);
  }

  function clearLocalHighlights() {
    const content = $("#docsContent");
    if (content) {
      $$("mark.doc-hit", content).forEach((mark) => {
        const parent = mark.parentNode;
        parent.replaceChild(document.createTextNode(mark.textContent), mark);
        parent.normalize();
      });
    }
    STATE.matches = [];
    STATE.matchIndex = -1;
    updateMatchNav();
    $("#docsHighlightInfo").textContent = "";
  }

  function updateMatchNav() {
    const count = STATE.matches.length;
    $("#docsMatchCount").textContent = count ? `${STATE.matchIndex + 1} / ${count}` : `0 / 0`;
    STATE.matches.forEach((mark, index) => mark.classList.toggle("active", index === STATE.matchIndex));
    $("#docsHighlightInfo").textContent = count
      ? `${T("docs.match", "匹配")} ${STATE.matchIndex + 1}/${count}`
      : "";
  }

  function moveMatch(direction) {
    if (!STATE.matches.length) return;
    STATE.matchIndex = (STATE.matchIndex + direction + STATE.matches.length) % STATE.matches.length;
    updateMatchNav();
    scrollToMatch(STATE.matchIndex);
  }

  function scrollToMatch(index) {
    const mark = STATE.matches[index];
    if (!mark) return;
    mark.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function focusSnippet(snippet, heading) {
    const content = $("#docsContent");
    if (!content) return;
    const cleanHeading = String(heading || "").replace(/[`#]/g, "").trim();
    if (cleanHeading) {
      const headingNodes = Array.from(content.querySelectorAll("h2, h3, h4, h5, h6"));
      for (const node of headingNodes) {
        const text = node.textContent.replace(/[`#]/g, "").trim();
        if (text && (text.includes(cleanHeading) || cleanHeading.includes(text))) {
          node.scrollIntoView({ behavior: "smooth", block: "center" });
          node.classList.add("doc-focus");
          setTimeout(() => node.classList.remove("doc-focus"), 2400);
          return;
        }
      }
    }
    const plain = String(snippet || "").replace(/\[\[([^\]]+)\]\]/g, "$1").replace(/[#*`|]/g, " ").trim();
    if (!plain) return;
    const candidates = [plain.slice(0, 60), plain.slice(0, 30), plain.split(/\s+/).slice(0, 5).join(" ")];
    for (const candidate of candidates) {
      if (!candidate) continue;
      const walker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        if (node.nodeValue.includes(candidate)) {
          const parent = node.parentElement;
          if (parent) {
            parent.scrollIntoView({ behavior: "smooth", block: "center" });
            parent.classList.add("doc-focus");
            setTimeout(() => parent.classList.remove("doc-focus"), 2400);
            return;
          }
        }
      }
    }
    const line = Number((STATE.pendingFocus && STATE.pendingFocus.line) || 1);
    content.scrollTo({ top: Math.min(content.scrollHeight, line * 18), behavior: "smooth" });
  }

  function openCitation(category, blockId, line, snippet) {
    const item = STATE.resultMap[blockId] || null;
    const focus = snippet || (item && item.snippet) || "";
    const heading = (item && item.heading) || "";
    if (category !== STATE.category) {
      loadDoc(category, { focusSnippet: focus, focusHeading: heading, keepQuery: true });
    } else {
      focusSnippet(focus, heading);
    }
  }

  function askDoc() {
    if (!window.Assistant) return;
    const selection = String(window.getSelection ? window.getSelection().toString() : "").slice(0, 1500);
    const prompt = window.I18N && window.I18N.lang === "en"
      ? `Explain the selected part of "${STATE.title}" and how it applies to this software.`
      : `请解释《${STATE.title}》中我选中的内容，并说明它在本软件中的对应实现。`;
    window.Assistant.openWithPrompt(prompt, {
      docs: {
        category: STATE.category,
        title: STATE.title,
        heading: STATE.matches.length ? "" : "",
        selection,
      },
    });
  }

  function current() {
    if (!STATE.category) return null;
    return {
      category: STATE.category,
      title: STATE.title,
      heading: "",
      line: 0,
    };
  }

  window.Docs = {
    init,
    onShow,
    openCitation,
    current,
    loadDoc,
  };
})();
