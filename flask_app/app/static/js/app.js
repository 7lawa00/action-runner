document.addEventListener('DOMContentLoaded', () => {
  const tabs = document.querySelectorAll('.tab');
  const panels = {
    requests: document.getElementById('panel-requests'),
    actions: document.getElementById('panel-actions'),
    scenarios: document.getElementById('panel-scenarios'),
    environments: document.getElementById('panel-environments'),
    snippets: document.getElementById('panel-snippets'),
  };

  function setActive(tabName) {
    tabs.forEach(t => t.classList.remove('tab-active'));
    Object.values(panels).forEach(p => p.classList.add('hidden'));
    document.querySelector(`.tab[data-tab="${tabName}"]`).classList.add('tab-active');
    panels[tabName].classList.remove('hidden');
    loadPanel(tabName);
  }

  tabs.forEach(btn => btn.addEventListener('click', () => setActive(btn.dataset.tab)));
  setActive('requests');

  async function loadPanel(tabName) {
    if (tabName === 'requests') {
      const res = await fetch('/api/requests');
      const data = await res.json();
      const list = document.getElementById('requests-list');
      list.innerHTML = data.map(r => `
        <div class="flex items-center justify-between border border-slate-700/80 rounded-lg p-3 mb-2">
          <div>
            <div class="font-medium">${r.name}</div>
            <div class="text-xs text-slate-400">${r.method} • ${r.url}</div>
          </div>
          <button class="btn-primary" data-send="${r.id}">Send</button>
        </div>
      `).join('');
      list.querySelectorAll('[data-send]').forEach(btn => {
        btn.addEventListener('click', async () => {
          btn.disabled = true; btn.textContent = 'Sending…';
          const res = await fetch(`/api/requests/${btn.dataset.send}/send`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({})});
          const out = await res.json();
          alert('Response: ' + JSON.stringify(out, null, 2));
          btn.disabled = false; btn.textContent = 'Send';
        });
      });
    }
    if (tabName === 'scenarios') {
      const res = await fetch('/api/scenarios');
      const data = await res.json();
      const list = document.getElementById('scenarios-list');
      list.innerHTML = data.map(s => `
        <div class="border border-slate-700/80 rounded-lg p-3 mb-2">
          <div class="font-medium">${s.name}</div>
          <div class="text-xs text-slate-400">${s.description}</div>
          <button class="btn-primary mt-2" data-run="${s.id}">Run Scenario</button>
        </div>
      `).join('');
      list.querySelectorAll('[data-run]').forEach(btn => {
        btn.addEventListener('click', async () => {
          btn.disabled = true; btn.textContent = 'Running…';
          const res = await fetch(`/api/scenarios/${btn.dataset.run}/run`, {method:'POST'});
          const out = await res.json();
          alert('Results: ' + JSON.stringify(out, null, 2));
          btn.disabled = false; btn.textContent = 'Run Scenario';
        });
      });
    }
    if (tabName === 'actions') {
      const btn = document.getElementById('run-demo-action');
      btn.onclick = async () => {
        btn.disabled = true; btn.textContent = 'Running…';
        const res = await fetch('/api/actions/1/run', {method:'POST'});
        const out = await res.json();
        document.getElementById('action-output').textContent = JSON.stringify(out, null, 2);
        btn.disabled = false; btn.textContent = 'Run Selenium Demo';
      };
    }
    if (tabName === 'environments') {
      const res = await fetch('/api/environments');
      const data = await res.json();
      const list = document.getElementById('envs-list');
      list.innerHTML = data.map(e => `
        <div class="border border-slate-700/80 rounded-lg p-3 mb-2">
          <div class="font-medium">${e.name}</div>
          <div class="text-xs text-slate-400">${e.description}</div>
          <div class="mt-2 text-xs">${e.variables.map(v => `${v.key}=${v.is_secret ? '***' : v.value}`).join(', ')}</div>
        </div>
      `).join('');
    }
  }
});
