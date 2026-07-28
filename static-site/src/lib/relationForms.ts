import { submitRelationshipProposal, type NewNodeTarget } from "./firebase";

function showMessage(form: HTMLFormElement, selector: string, text?: string) {
  const el = form.querySelector<HTMLElement>(selector);
  if (!el) return;
  if (text !== undefined) el.textContent = text;
  el.hidden = false;
}

function hideMessage(form: HTMLFormElement, selector: string) {
  const el = form.querySelector<HTMLElement>(selector);
  if (el) el.hidden = true;
}

function wireTabs(dialog: HTMLDialogElement) {
  const tabs = dialog.querySelectorAll<HTMLElement>(".rel-tab");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.tab;
      tabs.forEach((t) => t.classList.toggle("tab-active", t === tab));
      dialog.querySelectorAll<HTMLElement>(".rel-panel").forEach((panel) => {
        panel.hidden = panel.dataset.panel !== target;
      });
    });
  });
}

function wireSecondaryTypes(form: HTMLFormElement) {
  const primarySelect = form.querySelector<HTMLSelectElement>(".rel-primary-select");
  const secondarySelect = form.querySelector<HTMLSelectElement>(".rel-secondary-select");
  if (!primarySelect || !secondarySelect) return;
  const primary = primarySelect;
  const secondary = secondarySelect;
  const secondaryTypes: Record<string, string[]> = JSON.parse(
    form.dataset.secondaryTypes ?? "{}",
  );
  function refresh() {
    const options = secondaryTypes[primary.value] ?? [];
    secondary.innerHTML = options.map((o) => `<option value="${o}">${o}</option>`).join("");
    secondary.disabled = options.length === 0;
  }
  primary.addEventListener("change", refresh);
  refresh();
}

function wireForm(form: HTMLFormElement, dialog: HTMLDialogElement) {
  const sourceId = form.dataset.sourceId!;
  const sourceName = form.dataset.sourceName!;
  const fixedContext = form.dataset.context || undefined;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideMessage(form, ".rel-error");
    hideMessage(form, ".rel-success");

    const contextInput = form.querySelector<HTMLInputElement>(".rel-context-input");
    const context = fixedContext ?? contextInput?.value.trim() ?? "";
    const labelInput = form.querySelector<HTMLInputElement>(".rel-label-input")!;
    const label = labelInput.value.trim();

    const activeTab =
      form.querySelector<HTMLElement>(".rel-tab.tab-active")?.dataset.tab ?? "existing";

    if (!context) {
      showMessage(form, ".rel-error", "please choose a context");
      return;
    }

    try {
      if (activeTab === "existing") {
        const targetSelect = form.querySelector<HTMLSelectElement>(".rel-target-select")!;
        const opt = targetSelect.selectedOptions[0];
        if (!opt || !opt.value) {
          showMessage(form, ".rel-error", "choose a related object");
          return;
        }
        await submitRelationshipProposal({
          sourceId,
          sourceName,
          context,
          label,
          targetId: opt.value,
          targetName: opt.dataset.name ?? opt.value,
        });
      } else {
        const primary = form.querySelector<HTMLSelectElement>(".rel-primary-select")!.value;
        const secondary = form.querySelector<HTMLSelectElement>(".rel-secondary-select")!.value;
        const name = form.querySelector<HTMLInputElement>(".rel-name-input")!.value.trim();
        const description = form
          .querySelector<HTMLTextAreaElement>(".rel-description-input")!
          .value.trim();
        const topics = form
          .querySelector<HTMLInputElement>(".rel-topics-input")!
          .value.split(",")
          .map((t) => t.trim())
          .filter(Boolean);
        const url = form.querySelector<HTMLInputElement>(".rel-url-input")!.value.trim();
        const urlLabel = form
          .querySelector<HTMLInputElement>(".rel-url-label-input")!
          .value.trim();

        if (!name) {
          showMessage(form, ".rel-error", "please name the new node");
          return;
        }
        if (url && !urlLabel) {
          showMessage(form, ".rel-error", "url label is required when a url is given");
          return;
        }

        const newTarget: NewNodeTarget = {
          top: primary,
          sub: secondary || undefined,
          name,
          description: description || undefined,
          topics: topics.length > 0 ? topics : undefined,
          url: url || undefined,
          urlLabel: url ? urlLabel : undefined,
        };
        await submitRelationshipProposal({ sourceId, sourceName, context, label, newTarget });
      }

      form.reset();
      wireSecondaryTypes(form);
      showMessage(form, ".rel-success");
      setTimeout(() => dialog.close(), 900);
    } catch (err) {
      showMessage(
        form,
        ".rel-error",
        err instanceof Error ? err.message.replace(/^Firebase:\s*/, "") : String(err),
      );
    }
  });
}

export function initRelationForms(): void {
  document.querySelectorAll<HTMLElement>("[data-open-dialog]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const dialog = document.getElementById(btn.dataset.openDialog!) as HTMLDialogElement | null;
      dialog?.showModal();
    });
  });

  document.querySelectorAll<HTMLDialogElement>("dialog.relation-modal").forEach((dialog) => {
    wireTabs(dialog);
    const form = dialog.querySelector<HTMLFormElement>("form[data-relation-form]");
    if (!form) return;
    wireSecondaryTypes(form);
    wireForm(form, dialog);
  });
}
