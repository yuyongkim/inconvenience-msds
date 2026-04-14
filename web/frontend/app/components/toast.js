export function createToast(toastEl) {
  let timer = null;

  function show(message, { durationMs = 2000 } = {}) {
    toastEl.textContent = message;
    toastEl.classList.add("visible");
    if (timer) window.clearTimeout(timer);
    timer = window.setTimeout(() => toastEl.classList.remove("visible"), durationMs);
  }

  return { show };
}

