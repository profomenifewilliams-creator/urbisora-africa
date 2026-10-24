(() => {
  "use strict";
  const root = document.getElementById("urbi-ai-root");
  if (!root) return;
  const toggle = root.querySelector("[data-ai-toggle]");
  const panel = root.querySelector("[data-ai-panel]");
  const close = root.querySelector("[data-ai-close]");
  const form = root.querySelector("[data-ai-form]");
  const input = root.querySelector("[data-ai-input]");
  const transcript = root.querySelector("[data-ai-transcript]");
  const sendButton = root.querySelector("[data-ai-send]");
  const status = root.querySelector("[data-ai-status]");
  const starter = root.querySelector("[data-ai-starters]");
  const history = [];
  let busy = false;
  const chatUrl = root.dataset.chatUrl;
  const actionUrl = root.dataset.actionUrl;
  const csrfInput = document.querySelector("#urbi-ai-csrf input[name='csrfmiddlewaretoken']");

  const internalUrl = value => typeof value === "string" && value.startsWith("/") && !value.startsWith("//");
  const openPanel = () => {
    panel.hidden = false;
    toggle.setAttribute("aria-expanded", "true");
    panel.setAttribute("aria-hidden", "false");
    setTimeout(() => input.focus(), 20);
  };
  const closePanel = () => {
    panel.hidden = true;
    toggle.setAttribute("aria-expanded", "false");
    panel.setAttribute("aria-hidden", "true");
    toggle.focus();
  };
  toggle.addEventListener("click", () => panel.hidden ? openPanel() : closePanel());
  close.addEventListener("click", closePanel);
  document.addEventListener("keydown", event => { if (event.key === "Escape" && !panel.hidden) closePanel(); });

  function addMessage(role, text, mode) {
    const article = document.createElement("article");
    article.className = "urbi-ai-message urbi-ai-" + role;
    const label = document.createElement("span");
    label.className = "urbi-ai-message-label";
    label.textContent = role === "assistant" ? "URBISORA AI" : "YOU";
    article.appendChild(label);
    const body = document.createElement("div");
    body.className = "urbi-ai-message-body";
    // Plain text only. We intentionally never render model output as HTML.
    body.textContent = text;
    article.appendChild(body);
    if (role === "assistant" && mode) {
      const modeLabel = document.createElement("span");
      modeLabel.className = "urbi-ai-mode";
      modeLabel.textContent = mode === "reasoning" ? "AI reasoning" : "Platform tools";
      article.appendChild(modeLabel);
    }
    transcript.appendChild(article);
    transcript.scrollTop = transcript.scrollHeight;
  }

  function addLinks(items) {
    if (!Array.isArray(items) || !items.length) return;
    const row = document.createElement("div");
    row.className = "urbi-ai-links";
    items.forEach(item => {
      if (!item || !internalUrl(item.url)) return;
      const anchor = document.createElement("a");
      anchor.href = item.url;
      anchor.className = "urbi-ai-link";
      anchor.textContent = item.label || "Open section";
      row.appendChild(anchor);
    });
    if (row.childElementCount) transcript.appendChild(row);
  }

  function addCards(cards) {
    if (!Array.isArray(cards) || !cards.length) return;
    const wrap = document.createElement("div");
    wrap.className = "urbi-ai-results";
    cards.forEach(card => {
      if (!card || typeof card.title !== "string") return;
      const el = document.createElement(card.url && internalUrl(card.url) ? "a" : "div");
      el.className = "urbi-ai-result-card";
      if (el.tagName === "A") el.href = card.url;
      if (card.image && /^https:\/\//i.test(card.image)) {
        const img = document.createElement("img");
        img.src = card.image;
        img.alt = "";
        img.loading = "lazy";
        img.referrerPolicy = "no-referrer";
        el.appendChild(img);
      }
      const content = document.createElement("span");
      content.className = "urbi-ai-result-content";
      const title = document.createElement("strong");
      title.textContent = card.title;
      content.appendChild(title);
      if (card.details) {
        const detail = document.createElement("span");
        detail.textContent = card.details;
        content.appendChild(detail);
      }
      if (card.description) {
        const description = document.createElement("small");
        description.textContent = card.description;
        content.appendChild(description);
      }
      if (card.status) {
        const badge = document.createElement("em");
        badge.textContent = card.status;
        content.appendChild(badge);
      }
      el.appendChild(content);
      wrap.appendChild(el);
    });
    if (wrap.childElementCount) transcript.appendChild(wrap);
  }

  function addPendingAction(action) {
    if (!action || !action.type || !Number.isInteger(Number(action.object_id))) return;
    const box = document.createElement("div");
    box.className = "urbi-ai-confirm";
    const title = document.createElement("strong");
    title.textContent = action.label || "Confirm action";
    const summary = document.createElement("p");
    summary.textContent = action.description || "Review this action before it is applied.";
    const buttons = document.createElement("div");
    buttons.className = "urbi-ai-confirm-buttons";
    const yes = document.createElement("button");
    yes.type = "button";
    yes.className = "urbi-ai-confirm-yes";
    yes.textContent = "Confirm";
    const no = document.createElement("button");
    no.type = "button";
    no.className = "urbi-ai-confirm-no";
    no.textContent = "Cancel";
    no.addEventListener("click", () => {
      box.remove();
      addMessage("assistant", "Cancelled. Nothing was changed.");
    });
    yes.addEventListener("click", async () => {
      if (busy) return;
      busy = true;
      yes.disabled = true;
      yes.textContent = "Working…";
      try {
        const response = await fetch(actionUrl, {
          method: "POST",
          credentials: "same-origin",
          headers: {"Content-Type": "application/json", "X-CSRFToken": csrfInput ? csrfInput.value : ""},
          body: JSON.stringify({type: action.type, object_id: Number(action.object_id), status: action.status, confirmed: true})
        });
        const data = await response.json();
        addMessage("assistant", data.reply || "The action returned no message.");
        if (!response.ok) addLinks([{label: "Open dashboard", url: "/dashboard/"}]);
        box.remove();
      } catch (_) {
        addMessage("assistant", "I couldn't contact the server, so I can't confirm that any change happened. Please try again from your dashboard.");
      } finally {
        busy = false;
        yes.disabled = false;
      }
    });
    buttons.append(yes, no);
    box.append(title, summary, buttons);
    transcript.appendChild(box);
    transcript.scrollTop = transcript.scrollHeight;
  }

  function renderResponse(data) {
    addMessage("assistant", data.reply || "I couldn't produce a response. Please try again.", data.mode);
    addCards(data.cards);
    addLinks(data.links);
    addPendingAction(data.pending_action);
    transcript.scrollTop = transcript.scrollHeight;
  }

  async function ask(message) {
    const clean = String(message || "").trim();
    if (!clean || busy) return;
    busy = true;
    sendButton.disabled = true;
    input.disabled = true;
    addMessage("user", clean);
    history.push({role: "user", content: clean});
    const pending = document.createElement("article");
    pending.className = "urbi-ai-message urbi-ai-pending";
    pending.textContent = "Checking Urbisora…";
    transcript.appendChild(pending);
    transcript.scrollTop = transcript.scrollHeight;
    try {
      const response = await fetch(chatUrl, {
        method: "POST",
        credentials: "same-origin",
        headers: {"Content-Type": "application/json", "X-CSRFToken": csrfInput ? csrfInput.value : ""},
        body: JSON.stringify({message: clean, history: history.slice(-8), page: window.location.pathname})
      });
      const data = await response.json();
      pending.remove();
      if (!response.ok && !data.reply) throw new Error(data.error || "Request failed");
      renderResponse(data);
      history.push({role: "assistant", content: String(data.reply || "")});
      if (history.length > 12) history.splice(0, history.length - 12);
      status.textContent = data.mode === "reasoning" ? "AI reasoning enabled" : "Live platform tools";
    } catch (_) {
      pending.remove();
      addMessage("assistant", "I couldn't connect to the assistant service. You can still use the website navigation, search and dashboard. Please try again shortly.");
    } finally {
      busy = false;
      sendButton.disabled = false;
      input.disabled = false;
      input.focus();
    }
  }
  form.addEventListener("submit", event => {
    event.preventDefault();
    const message = input.value.trim();
    input.value = "";
    ask(message);
  });
  starter.querySelectorAll("button[data-prompt]").forEach(button => {
    button.addEventListener("click", () => ask(button.dataset.prompt || ""));
  });
  status.textContent = "Live platform tools";
})();
