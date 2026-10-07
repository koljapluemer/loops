// Crop (drag edges inward) + erase brush on the processed loop image. Applied on save.
(() => {
  const { src, saveUrl } = window.EDITOR;
  const canvas = document.getElementById("canvas");
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  const stage = document.getElementById("stage");
  const cropBox = document.getElementById("cropBox");
  const brushCursor = document.getElementById("brushCursor");
  const sizeInput = document.getElementById("brushSize");
  const sizeLabel = document.getElementById("brushSizeLabel");
  const status = document.getElementById("status");
  const modeButtons = document.querySelectorAll("[data-mode]");

  const UNDO_LIMIT = 20;
  const EDGE_GRAB_PX = 12;

  let mode = "brush";
  let crop = null; // {l, t, r, b} in image px
  let undoStack = [];
  let dirty = false;
  let drag = null; // {kind: "crop", edges} | {kind: "brush", last}

  const scale = () => canvas.width / canvas.getBoundingClientRect().width;
  const brushSize = () => Number(sizeInput.value);

  function setStatus(text) { status.textContent = text; }
  function markDirty() { dirty = true; setStatus("unsaved"); }

  function load() {
    const img = new Image();
    img.onload = () => {
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
      crop = { l: 0, t: 0, r: canvas.width, b: canvas.height };
      undoStack = [];
      dirty = false;
      setStatus(`${canvas.width}×${canvas.height}`);
      renderCrop();
    };
    img.src = `${src}?v=${Date.now()}`;
  }

  function renderCrop() {
    const s = scale();
    Object.assign(cropBox.style, {
      left: `${crop.l / s}px`,
      top: `${crop.t / s}px`,
      width: `${(crop.r - crop.l) / s}px`,
      height: `${(crop.b - crop.t) / s}px`,
    });
  }

  function setMode(m) {
    mode = m;
    modeButtons.forEach((b) => b.classList.toggle("btn-active", b.dataset.mode === m));
    brushCursor.classList.toggle("hidden", m !== "brush");
    stage.style.cursor = m === "brush" ? "none" : "default";
  }

  function setBrushSize(v) {
    sizeInput.value = Math.max(Number(sizeInput.min), Math.min(Number(sizeInput.max), v));
    sizeLabel.textContent = sizeInput.value;
    updateBrushCursor();
  }

  function pushUndo(entry) {
    undoStack.push(entry);
    if (undoStack.length > UNDO_LIMIT) undoStack.shift();
  }

  function undo() {
    const entry = undoStack.pop();
    if (!entry) return;
    if (entry.kind === "pixels") ctx.putImageData(entry.data, 0, 0);
    else crop = entry.crop;
    renderCrop();
    markDirty();
  }

  // pointer position in display px (relative to canvas) and image px
  function pointer(e) {
    const rect = canvas.getBoundingClientRect();
    const dx = e.clientX - rect.left;
    const dy = e.clientY - rect.top;
    const s = scale();
    return { dx, dy, x: dx * s, y: dy * s };
  }

  function edgesAt(p) {
    const s = scale();
    const near = (a, b) => Math.abs(a - b) / s <= EDGE_GRAB_PX;
    const inX = p.x >= crop.l - EDGE_GRAB_PX * s && p.x <= crop.r + EDGE_GRAB_PX * s;
    const inY = p.y >= crop.t - EDGE_GRAB_PX * s && p.y <= crop.b + EDGE_GRAB_PX * s;
    const edges = [];
    if (inY && near(p.x, crop.l)) edges.push("l");
    if (inY && near(p.x, crop.r)) edges.push("r");
    if (inX && near(p.y, crop.t)) edges.push("t");
    if (inX && near(p.y, crop.b)) edges.push("b");
    return edges;
  }

  function cursorFor(edges) {
    const h = edges.includes("l") || edges.includes("r");
    const v = edges.includes("t") || edges.includes("b");
    if (h && v) {
      const nwse = (edges.includes("l") && edges.includes("t")) || (edges.includes("r") && edges.includes("b"));
      return nwse ? "nwse-resize" : "nesw-resize";
    }
    return h ? "ew-resize" : v ? "ns-resize" : "default";
  }

  function moveEdges(edges, p) {
    const x = Math.round(Math.max(0, Math.min(canvas.width, p.x)));
    const y = Math.round(Math.max(0, Math.min(canvas.height, p.y)));
    if (edges.includes("l")) crop.l = Math.min(x, crop.r - 1);
    if (edges.includes("r")) crop.r = Math.max(x, crop.l + 1);
    if (edges.includes("t")) crop.t = Math.min(y, crop.b - 1);
    if (edges.includes("b")) crop.b = Math.max(y, crop.t + 1);
    renderCrop();
  }

  function erase(from, to) {
    ctx.save();
    ctx.globalCompositeOperation = "destination-out";
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.lineWidth = brushSize();
    ctx.beginPath();
    ctx.moveTo(from.x, from.y);
    ctx.lineTo(to.x, to.y);
    ctx.stroke();
    ctx.restore();
  }

  let lastPointer = null;
  function updateBrushCursor() {
    const d = brushSize() / scale();
    brushCursor.style.width = brushCursor.style.height = `${d}px`;
    if (lastPointer) {
      brushCursor.style.left = `${lastPointer.dx}px`;
      brushCursor.style.top = `${lastPointer.dy}px`;
    }
  }

  stage.addEventListener("pointerdown", (e) => {
    if (e.button !== 0) return;
    const p = pointer(e);
    if (mode === "crop") {
      const edges = edgesAt(p);
      if (!edges.length) return;
      pushUndo({ kind: "crop", crop: { ...crop } });
      drag = { kind: "crop", edges };
    } else {
      pushUndo({ kind: "pixels", data: ctx.getImageData(0, 0, canvas.width, canvas.height) });
      drag = { kind: "brush", last: p };
      erase(p, p);
    }
    stage.setPointerCapture(e.pointerId);
    markDirty();
  });

  stage.addEventListener("pointermove", (e) => {
    const p = pointer(e);
    lastPointer = p;
    if (mode === "brush") updateBrushCursor();
    if (!drag) {
      if (mode === "crop") stage.style.cursor = cursorFor(edgesAt(p));
      return;
    }
    if (drag.kind === "crop") moveEdges(drag.edges, p);
    else {
      erase(drag.last, p);
      drag.last = p;
    }
  });

  const endDrag = () => { drag = null; };
  stage.addEventListener("pointerup", endDrag);
  stage.addEventListener("pointercancel", endDrag);
  stage.addEventListener("pointerleave", () => { if (!drag) brushCursor.classList.add("hidden"); });
  stage.addEventListener("pointerenter", () => { if (mode === "brush") brushCursor.classList.remove("hidden"); });

  async function save() {
    const w = crop.r - crop.l;
    const h = crop.b - crop.t;
    const out = document.createElement("canvas");
    out.width = w;
    out.height = h;
    out.getContext("2d").drawImage(canvas, crop.l, crop.t, w, h, 0, 0, w, h);
    const blob = await new Promise((resolve) => out.toBlob(resolve, "image/png"));
    const body = new FormData();
    body.append("image", blob, "image.png");
    setStatus("saving…");
    const res = await fetch(saveUrl, { method: "POST", body });
    if (!res.ok) {
      setStatus(`save failed (${res.status})`);
      return;
    }
    load();
  }

  modeButtons.forEach((b) => b.addEventListener("click", () => setMode(b.dataset.mode)));
  sizeInput.addEventListener("input", () => setBrushSize(Number(sizeInput.value)));
  document.getElementById("undo").addEventListener("click", undo);
  document.getElementById("reset").addEventListener("click", load);
  document.getElementById("save").addEventListener("click", save);
  window.addEventListener("resize", () => { renderCrop(); updateBrushCursor(); });
  window.addEventListener("beforeunload", (e) => { if (dirty) e.preventDefault(); });
  document.querySelector('form[action$="/delete"]').addEventListener("submit", () => { dirty = false; });

  document.addEventListener("keydown", (e) => {
    if (e.target.closest("input, textarea")) return;
    if ((e.ctrlKey || e.metaKey) && e.key === "z") { e.preventDefault(); undo(); return; }
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key === "c") setMode("crop");
    else if (e.key === "b") setMode("brush");
    else if (e.key === "[") setBrushSize(brushSize() - 5);
    else if (e.key === "]") setBrushSize(brushSize() + 5);
  });

  setMode("brush");
  setBrushSize(brushSize());
  load();
})();
