import { clear, el } from "../lib/dom.js";
import { t } from "../lib/i18n.js";

function formatStatusText(job) {
  if (!job) return t("bulk.idle");
  if (job.status === "queued")
    return t("bulk.queued", { done: job.completed_items, total: job.total_items });
  if (job.status === "running")
    return t("bulk.running", { done: job.completed_items, total: job.total_items });
  if (job.status === "done")
    return t("bulk.done", { done: job.completed_items, failed: job.failed_items });
  return job.error || t("bulk.failed");
}

export function renderBulkToolbar({ mountEl, state }) {
  clear(mountEl);

  const jobBusy = state.bulkJob && (state.bulkJob.status === "queued" || state.bulkJob.status === "running");
  const canCreate = state.selectedChemIds.length > 0 && state.bulkFormats.length > 0 && !jobBusy;
  const downloadReady = state.bulkJob?.status === "done" && state.bulkJob?.download_url;

  const toolbar = el("div", { class: "bulk-toolbar-main" }, [
    el("div", { class: "bulk-count", text: t("bulk.count", { n: state.selectedChemIds.length }) }),
    el("div", { class: "bulk-label", text: t("bulk.format") }),
    el("label", { class: "format-chip" }, [
      el("input", {
        type: "checkbox",
        "data-format": "txt",
        checked: state.bulkFormats.includes("txt") ? "checked" : null,
      }),
      "Unicode TXT",
    ]),
    el("label", { class: "format-chip" }, [
      el("input", {
        type: "checkbox",
        "data-format": "brf",
        checked: state.bulkFormats.includes("brf") ? "checked" : null,
      }),
      "BRF",
    ]),
  ]);

  const actions = el("div", { class: "bulk-toolbar-actions" }, [
    el("button", { class: "btn btn-secondary", type: "button", "data-action": "select-visible" }, [t("bulk.selectVisible")]),
    el("button", { class: "btn btn-secondary", type: "button", "data-action": "clear-selected" }, [t("bulk.clearSelected")]),
    el(
      "button",
      {
        class: "btn btn-primary",
        type: "button",
        "data-action": "create-bulk-job",
        disabled: canCreate ? null : "disabled",
      },
      [t("bulk.create")],
    ),
    downloadReady
      ? el(
          "a",
          {
            class: "btn btn-ghost",
            href: state.bulkJob.download_url,
            download: "",
          },
          [t("bulk.download")],
        )
      : null,
  ]);

  const status = el("div", { class: "bulk-toolbar-status" }, [
    el(
      "div",
      {
        class: `bulk-status-text${state.bulkJob?.status === "failed" ? " error" : ""}`,
        text: formatStatusText(state.bulkJob),
      },
    ),
  ]);

  mountEl.appendChild(el("div", { class: "bulk-toolbar" }, [toolbar, actions, status]));
}
