function fallbackCopyText(text) {
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.setAttribute("readonly", "");
  ta.style.position = "fixed";
  ta.style.top = "-1000px";
  ta.style.opacity = "0";
  document.body.appendChild(ta);
  ta.select();
  try {
    return document.execCommand("copy");
  } catch {
    return false;
  } finally {
    document.body.removeChild(ta);
  }
}

export async function copyText(text) {
  if (!text) return { ok: false, method: "none" };
  try {
    await navigator.clipboard.writeText(text);
    return { ok: true, method: "clipboard" };
  } catch {
    const ok = fallbackCopyText(text);
    return { ok, method: "execCommand" };
  }
}

