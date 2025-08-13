document.addEventListener('DOMContentLoaded', () => {
  const tabs = document.querySelectorAll('.tab');
  const panels = {
    requests: document.getElementById('panel-requests'),
    actions: document.getElementById('panel-actions'),
    scenarios: document.getElementById('panel-scenarios'),
    environments: document.getElementById('panel-environments'),
    snippets: document.getElementById('panel-snippets'),
  };

  let currentRequest = null;
  let allRequests = [];

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
      await loadRequests();
      setupRequestHandlers();
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

  async function loadRequests() {
    try {
      const res = await fetch('/api/requests');
      allRequests = await res.json();
      renderRequestsList();
    } catch (error) {
      console.error('Failed to load requests:', error);
    }
  }

  function renderRequestsList() {
    const list = document.getElementById('requests-list');
    if (allRequests.length === 0) {
      list.innerHTML = '<div class="text-slate-400">No requests found. Create your first request!</div>';
      return;
    }
    
    list.innerHTML = allRequests.map(r => `
      <div class="request-item border border-slate-700/80 rounded-lg p-3 cursor-pointer hover:border-blue-500/50 ${currentRequest?.id === r.id ? 'border-blue-500 bg-blue-500/10' : ''}" data-request-id="${r.id}">
        <div class="font-medium">${r.name}</div>
        <div class="text-xs text-slate-400">${r.method} • ${r.url}</div>
      </div>
    `).join('');

    // Add click handlers for request selection
    list.querySelectorAll('.request-item').forEach(item => {
      item.addEventListener('click', () => {
        const requestId = parseInt(item.dataset.requestId);
        selectRequest(requestId);
      });
    });
  }

  function selectRequest(requestId) {
    currentRequest = allRequests.find(r => r.id === requestId);
    if (currentRequest) {
      populateEditor(currentRequest);
      document.getElementById('request-editor').style.display = 'block';
      document.getElementById('no-request-selected').style.display = 'none';
      renderRequestsList(); // Re-render to update selection
    }
  }

  function populateEditor(request) {
    document.getElementById('req-name').value = request.name || '';
    document.getElementById('req-method').value = request.method || 'GET';
    document.getElementById('req-url').value = request.url || '';
    document.getElementById('req-headers').value = JSON.stringify(request.headers || {}, null, 2);
    document.getElementById('req-body').value = request.body || '';
    document.getElementById('response-section').style.display = 'none';
  }

  function getEditorData() {
    let headers = {};
    try {
      headers = JSON.parse(document.getElementById('req-headers').value || '{}');
    } catch (e) {
      headers = {};
    }

    return {
      name: document.getElementById('req-name').value,
      method: document.getElementById('req-method').value,
      url: document.getElementById('req-url').value,
      headers: headers,
      body: document.getElementById('req-body').value,
      payload_type: 'json'
    };
  }

  function setupRequestHandlers() {
    // New request button
    document.getElementById('new-request-btn').onclick = async () => {
      const newRequestData = {
        name: 'New Request',
        method: 'GET',
        url: '',
        headers: {'Content-Type': 'application/json'},
        body: '',
        payload_type: 'json'
      };

      try {
        const res = await fetch('/api/requests', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(newRequestData)
        });
        const result = await res.json();
        await loadRequests();
        selectRequest(result.id);
      } catch (error) {
        alert('Failed to create request: ' + error.message);
      }
    };

    // Send request button
    document.getElementById('send-request-btn').onclick = async () => {
      if (!currentRequest) return;
      
      const btn = document.getElementById('send-request-btn');
      btn.disabled = true;
      btn.textContent = 'Sending...';

      try {
        // First save current changes
        const requestData = getEditorData();
        await fetch(`/api/requests/${currentRequest.id}`, {
          method: 'PUT',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(requestData)
        });

        // Then send the request
        const res = await fetch(`/api/requests/${currentRequest.id}/send`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({})
        });
        const response = await res.json();
        
        // Show response
        showResponse(response);
        
      } catch (error) {
        alert('Request failed: ' + error.message);
      } finally {
        btn.disabled = false;
        btn.textContent = 'Send Request';
      }
    };

    // Save request button
    document.getElementById('save-request-btn').onclick = async () => {
      if (!currentRequest) return;

      const requestData = getEditorData();
      try {
        await fetch(`/api/requests/${currentRequest.id}`, {
          method: 'PUT',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(requestData)
        });
        await loadRequests();
        currentRequest = allRequests.find(r => r.id === currentRequest.id);
        alert('Request saved successfully!');
      } catch (error) {
        alert('Failed to save request: ' + error.message);
      }
    };

    // Delete request button
    document.getElementById('delete-request-btn').onclick = async () => {
      if (!currentRequest) return;
      
      if (confirm('Are you sure you want to delete this request?')) {
        try {
          await fetch(`/api/requests/${currentRequest.id}`, { method: 'DELETE' });
          await loadRequests();
          currentRequest = null;
          document.getElementById('request-editor').style.display = 'none';
          document.getElementById('no-request-selected').style.display = 'block';
        } catch (error) {
          alert('Failed to delete request: ' + error.message);
        }
      }
    };
  }

  function showResponse(response) {
    const responseSection = document.getElementById('response-section');
    const statusDiv = document.getElementById('response-status');
    const bodyPre = document.getElementById('response-body');

    if (response.ok) {
      statusDiv.innerHTML = `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
        ${response.status} Success
      </span>`;
      bodyPre.textContent = JSON.stringify(response.data, null, 2);
    } else {
      statusDiv.innerHTML = `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
        Error: ${response.error}
      </span>`;
      bodyPre.textContent = response.error;
    }
    
    responseSection.style.display = 'block';
  }
});
