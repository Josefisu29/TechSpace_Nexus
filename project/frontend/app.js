const API_BASE = 'http://127.0.0.1:8000';

const form = document.getElementById('upscaleForm');
const fileInput = document.getElementById('videoFile');
const resolutionInput = document.getElementById('resolution');
const submitBtn = document.getElementById('submitBtn');
const statusText = document.getElementById('statusText');
const deviceText = document.getElementById('deviceText');
const progressText = document.getElementById('progressText');
const progressBar = document.getElementById('progressBar');

let pollTimer = null;

function setProgress(value) {
  const clamped = Math.max(0, Math.min(100, Number(value) || 0));
  progressBar.style.width = `${clamped}%`;
  progressText.textContent = `${clamped}%`;
}

async function pollStatus(jobId) {
  const res = await fetch(`${API_BASE}/status/${jobId}`);
  if (!res.ok) throw new Error(`Status check failed: ${res.status}`);

  const data = await res.json();
  statusText.textContent = data.status;
  deviceText.textContent = data.device;
  setProgress(data.progress);

  if (data.status === 'completed') {
    clearInterval(pollTimer);
    submitBtn.disabled = false;
    window.location.href = `${API_BASE}/download/${jobId}`;
  } else if (data.status === 'failed') {
    clearInterval(pollTimer);
    submitBtn.disabled = false;
    alert(data.error || 'Job failed. Check backend logs.');
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const file = fileInput.files[0];
  if (!file) {
    alert('Please choose a video file.');
    return;
  }

  const payload = new FormData();
  payload.append('file', file);
  payload.append('resolution', resolutionInput.value);

  submitBtn.disabled = true;
  statusText.textContent = 'queued';
  deviceText.textContent = '-';
  setProgress(0);

  try {
    const res = await fetch(`${API_BASE}/submit`, {
      method: 'POST',
      body: payload,
    });

    if (!res.ok) {
      throw new Error(`Submit failed (${res.status})`);
    }

    const data = await res.json();
    statusText.textContent = data.status;
    deviceText.textContent = data.device;

    clearInterval(pollTimer);
    pollTimer = setInterval(() => {
      pollStatus(data.job_id).catch((err) => {
        clearInterval(pollTimer);
        submitBtn.disabled = false;
        statusText.textContent = 'failed';
        alert(err.message);
      });
    }, 1500);
  } catch (err) {
    submitBtn.disabled = false;
    statusText.textContent = 'failed';
    alert(err.message);
  }
});

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('service-worker.js').catch(console.error);
}
