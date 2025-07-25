/*
 * Front‑end logic for the AI model tracker.  This script fetches the
 * models.json file from the server (or GitHub Pages) and dynamically
 * constructs the timeline of releases, the SWE‑bench bar chart and the
 * tabular summary.  It uses Chart.js for chart rendering and assumes
 * TailwindCSS is loaded for styling.
 */

async function loadModels() {
  try {
    const response = await fetch('./data/models.json');
    if (!response.ok) {
      throw new Error(`Failed to fetch models.json: ${response.status}`);
    }
    const models = await response.json();
    renderTimeline(models);
    renderChart(models);
    renderTable(models);
  } catch (error) {
    console.error('Error loading models:', error);
  }
}

function renderTimeline(models) {
  // Group models by month and year
  const groups = {};
  models.forEach(model => {
    if (!model.release_date) return;
    const date = new Date(model.release_date);
    if (isNaN(date)) return;
    const key = date.toLocaleString('default', { month: 'long', year: 'numeric' });
    if (!groups[key]) groups[key] = [];
    groups[key].push(model);
  });
  // Sort keys chronologically
  const sortedKeys = Object.keys(groups).sort((a, b) => {
    const da = new Date(a);
    const db = new Date(b);
    return da - db;
  });
  const timelineContainer = document.getElementById('timeline');
  sortedKeys.forEach(key => {
    const section = document.createElement('div');
    section.innerHTML = `\
      <h3 class="text-xl font-semibold mb-2">${key}</h3>\
      <ul class="list-disc list-inside pl-4 space-y-2">\
      </ul>\
    `;
    const ul = section.querySelector('ul');
    // Sort models within the month by release date
    groups[key].sort((a, b) => new Date(a.release_date) - new Date(b.release_date));
    groups[key].forEach(model => {
      const li = document.createElement('li');
      const swe = model.performance && model.performance.swe_bench_verified;
      const sweText = swe ? `${swe}%` : '–';
      li.innerHTML = `<strong>${model.model_name}</strong> (${model.release_date}) – ${model.notes}`;
      ul.appendChild(li);
    });
    timelineContainer.appendChild(section);
  });
}

function renderChart(models) {
  // Filter models with SWE‑bench scores
  const scored = models.filter(m => m.performance && m.performance.swe_bench_verified !== null);
  // Sort descending by score
  scored.sort((a, b) => b.performance.swe_bench_verified - a.performance.swe_bench_verified);
  // Take top 15
  const top = scored.slice(0, 15);
  const labels = top.map(m => m.model_name);
  const data = top.map(m => m.performance.swe_bench_verified);
  const ctx = document.getElementById('sweChart').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'SWE‑bench Verified (%)',
        data,
        backgroundColor: '#3b82f6'
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 100
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: { enabled: true }
      }
    }
  });
}

function renderTable(models) {
  const tbody = document.getElementById('models-table-body');
  // Sort models alphabetically by name for the table
  const sorted = [...models].sort((a, b) => a.model_name.localeCompare(b.model_name));
  sorted.forEach(model => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-gray-50';
    const swe = model.performance && model.performance.swe_bench_verified;
    const sweText = swe ? `${swe}%` : '–';
    const note = model.notes ? model.notes.slice(0, 80) + (model.notes.length > 80 ? '…' : '') : '';
    tr.innerHTML = `\
      <td class="px-4 py-2 whitespace-nowrap">${model.model_name}</td>\
      <td class="px-4 py-2 whitespace-nowrap">${model.provider}</td>\
      <td class="px-4 py-2 whitespace-nowrap">${model.release_date || ''}</td>\
      <td class="px-4 py-2 whitespace-nowrap capitalize">${model.modality || ''}</td>\
      <td class="px-4 py-2 whitespace-nowrap text-center">${sweText}</td>\
      <td class="px-4 py-2">${note}</td>\
    `;
    tbody.appendChild(tr);
  });
}

// Kick off the load when the DOM is ready
document.addEventListener('DOMContentLoaded', loadModels);