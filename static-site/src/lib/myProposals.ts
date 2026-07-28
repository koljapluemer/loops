import {
  subscribeMyProposals,
  deleteProposal,
  updateObjectProposal,
  updateRelationshipProposal,
  type Proposal,
} from "./firebase";

function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className: string,
  text?: string,
): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function relationshipTargetLabel(p: Proposal): string {
  if (p.newTarget) {
    const nt = p.newTarget as { name: string; top: string };
    return `new: ${nt.name} (${nt.top})`;
  }
  return String(p.targetName ?? p.targetId ?? "");
}

function renderRelationshipCard(p: Proposal): HTMLElement {
  const card = el("li", "border border-primary/40 bg-primary/5 rounded px-2 py-1.5 text-sm flex flex-col gap-1");
  const row = el("div", "flex items-center justify-between gap-2");
  const info = el(
    "span",
    "",
    `${String(p.context)}: ${String(p.label)} → ${relationshipTargetLabel(p)}`,
  );
  const badge = el("span", "badge badge-xs badge-primary shrink-0", "pending · yours");
  row.append(info, badge);

  const actions = el("div", "flex gap-2");
  const editBtn = el("button", "link link-primary text-xs", "edit");
  editBtn.type = "button";
  const delBtn = el("button", "link link-error text-xs", "delete");
  delBtn.type = "button";
  actions.append(editBtn, delBtn);

  card.append(row, actions);

  delBtn.addEventListener("click", async () => {
    if (!confirm("Withdraw this proposal?")) return;
    await deleteProposal(p.id);
  });

  editBtn.addEventListener("click", () => {
    if (card.querySelector(".edit-form")) return;
    const form = el("div", "edit-form flex flex-col gap-1 mt-1");
    const contextInput = el("input", "input input-bordered input-xs w-full") as HTMLInputElement;
    contextInput.value = String(p.context ?? "");
    const labelInput = el("input", "input input-bordered input-xs w-full") as HTMLInputElement;
    labelInput.value = String(p.label ?? "");
    const saveRow = el("div", "flex gap-2");
    const saveBtn = el("button", "btn btn-xs btn-primary", "save");
    saveBtn.type = "button";
    const cancelBtn = el("button", "btn btn-xs btn-ghost", "cancel");
    cancelBtn.type = "button";
    saveRow.append(saveBtn, cancelBtn);
    form.append(contextInput, labelInput, saveRow);
    card.append(form);

    cancelBtn.addEventListener("click", () => form.remove());
    saveBtn.addEventListener("click", async () => {
      await updateRelationshipProposal(p.id, {
        context: contextInput.value.trim(),
        label: labelInput.value.trim(),
      });
    });
  });

  return card;
}

function renderObjectCard(p: Proposal): HTMLElement {
  const card = el(
    "li",
    "flex items-center gap-1.5 rounded border border-primary/40 bg-primary/5 px-2 py-1 text-sm",
  );
  if (p.sub) card.append(el("span", "badge badge-sm badge-primary", String(p.sub)));
  const nameInput = el("input", "input input-ghost input-xs flex-1 min-w-0") as HTMLInputElement;
  nameInput.value = String(p.name ?? "");
  nameInput.addEventListener("change", () => {
    updateObjectProposal(p.id, { name: nameInput.value.trim() });
  });
  const delBtn = el("button", "link link-error text-xs shrink-0", "delete");
  delBtn.type = "button";
  delBtn.addEventListener("click", async () => {
    if (!confirm("Withdraw this proposal?")) return;
    await deleteProposal(p.id);
  });
  card.append(el("span", "badge badge-xs badge-primary", "pending"), nameInput, delBtn);
  return card;
}

// Mounts a live view of the current user's own pending relationship
// proposals for one node (`sourceId`), routing each into the container for
// its context name (one per context block already on the page) and
// falling back to `fallback` for proposals whose context doesn't match any
// of those (i.e. a newly proposed context).
export function mountMyRelationshipProposalsGrouped(
  sourceId: string,
  containersByContext: Map<string, HTMLElement>,
  fallback: HTMLElement,
): void {
  subscribeMyProposals((proposals) => {
    const mine = proposals.filter((p) => p.type === "relationship" && p.sourceId === sourceId);
    containersByContext.forEach((el) => el.replaceChildren());
    fallback.replaceChildren();
    for (const p of mine) {
      const target = containersByContext.get(String(p.context)) ?? fallback;
      target.append(renderRelationshipCard(p));
    }
  });
}

// Mounts a live view of the current user's own pending object (new node)
// proposals scoped to one `top`, appended alongside the real entries list.
export function mountMyObjectProposals(container: HTMLElement, top: string): void {
  subscribeMyProposals((proposals) => {
    const mine = proposals.filter((p) => p.type === "object" && p.top === top);
    container.replaceChildren();
    for (const p of mine) container.append(renderObjectCard(p));
  });
}
