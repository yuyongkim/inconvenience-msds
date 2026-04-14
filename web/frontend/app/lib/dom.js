export function qs(root, sel) {
  const el = root.querySelector(sel);
  if (!el) throw new Error(`Missing element: ${sel}`);
  return el;
}

export function qsa(root, sel) {
  return Array.from(root.querySelectorAll(sel));
}

export function clear(el) {
  while (el.firstChild) el.removeChild(el.firstChild);
}

export function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text ?? "";
  return div.innerHTML;
}

export function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === undefined || v === null) continue;
    if (k === "class") node.className = String(v);
    else if (k === "text") node.textContent = String(v);
    else if (k === "html") node.innerHTML = String(v);
    else if (k.startsWith("data-")) node.setAttribute(k, String(v));
    else node.setAttribute(k, String(v));
  }
  for (const child of children) {
    if (child === null || child === undefined) continue;
    node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
  }
  return node;
}

