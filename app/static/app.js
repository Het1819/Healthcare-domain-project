const fileInput = document.getElementById("fileInput");
const predictBtn = document.getElementById("predictBtn");
const resetBtn = document.getElementById("resetBtn");

const previewImg = document.getElementById("previewImg");
const previewPlaceholder = document.getElementById("previewPlaceholder");
const fileMeta = document.getElementById("fileMeta");

const thresholdSlider = document.getElementById("thresholdSlider");
const thresholdValue = document.getElementById("thresholdValue");

const errorBox = document.getElementById("errorBox");

const predLabel = document.getElementById("predLabel");
const predNote = document.getElementById("predNote");
const probNormal = document.getElementById("probNormal");
const probPneumonia = document.getElementById("probPneumonia");
const barNormal = document.getElementById("barNormal");
const barPneumonia = document.getElementById("barPneumonia");
const thresholdUsed = document.getElementById("thresholdUsed");
const loadingBadge = document.getElementById("loadingBadge");

let selectedFile = null;

function showError(msg) {
  errorBox.textContent = msg;
  errorBox.classList.remove("hidden");
}

function clearError() {
  errorBox.textContent = "";
  errorBox.classList.add("hidden");
}

function setLoading(isLoading) {
  if (isLoading) {
    loadingBadge.classList.remove("hidden");
    predictBtn.disabled = true;
    predictBtn.textContent = "Predicting...";
  } else {
    loadingBadge.classList.add("hidden");
    predictBtn.disabled = !selectedFile;
    predictBtn.textContent = "Predict";
  }
}

function resetUI() {
  selectedFile = null;
  fileInput.value = "";
  predictBtn.disabled = true;

  previewImg.src = "";
  previewImg.classList.add("hidden");
  previewPlaceholder.classList.remove("hidden");
  fileMeta.textContent = "";

  predLabel.textContent = "—";
  predNote.textContent = "Upload an image and click Predict.";
  probNormal.textContent = "—";
  probPneumonia.textContent = "—";
  barNormal.style.width = "0%";
  barPneumonia.style.width = "0%";
  thresholdUsed.textContent = "—";

  clearError();
  setLoading(false);
}

thresholdSlider.addEventListener("input", () => {
  thresholdValue.textContent = Number(thresholdSlider.value).toFixed(2);
});

fileInput.addEventListener("change", () => {
  clearError();

  const files = fileInput.files;
  if (!files || files.length === 0) {
    resetUI();
    return;
  }

  const file = files[0];
  selectedFile = file;
  predictBtn.disabled = false;

  // Preview image
  const url = URL.createObjectURL(file);
  previewImg.src = url;
  previewImg.classList.remove("hidden");
  previewPlaceholder.classList.add("hidden");

  fileMeta.textContent = `${file.name} • ${(file.size / 1024).toFixed(1)} KB • ${file.type || "unknown type"}`;

  // Reset old prediction display (optional, but feels nicer)
  predLabel.textContent = "—";
  predNote.textContent = "Ready. Click Predict.";
  probNormal.textContent = "—";
  probPneumonia.textContent = "—";
  barNormal.style.width = "0%";
  barPneumonia.style.width = "0%";
  thresholdUsed.textContent = "—";
});

predictBtn.addEventListener("click", async () => {
  clearError();

  if (!selectedFile) {
    showError("Please select an image first.");
    return;
  }

  const thr = Number(thresholdSlider.value);

  const formData = new FormData();
  formData.append("file", selectedFile);

  setLoading(true);

  try {
    // Send threshold as query param so your existing endpoint stays the same.
    const resp = await fetch(`/predict?threshold=${encodeURIComponent(thr)}`, {
      method: "POST",
      body: formData,
    });

    const data = await resp.json();

    if (!resp.ok) {
      const detail = data?.detail ? String(data.detail) : "Request failed.";
      throw new Error(detail);
    }

    // Render results
    predLabel.textContent = data.pred_label || "—";
    predNote.textContent = "Prediction completed.";

    const pn = Number(data.prob_normal);
    const pp = Number(data.prob_pneumonia);
    probNormal.textContent = isFinite(pn) ? pn.toFixed(4) : "—";
    probPneumonia.textContent = isFinite(pp) ? pp.toFixed(4) : "—";

    barNormal.style.width = isFinite(pn) ? `${Math.max(0, Math.min(1, pn)) * 100}%` : "0%";
    barPneumonia.style.width = isFinite(pp) ? `${Math.max(0, Math.min(1, pp)) * 100}%` : "0%";

    thresholdUsed.textContent = data.threshold != null ? Number(data.threshold).toFixed(2) : "—";
  } catch (err) {
    showError(err?.message || "Something went wrong.");
  } finally {
    setLoading(false);
  }
});

resetBtn.addEventListener("click", () => resetUI());

// Start clean
resetUI();