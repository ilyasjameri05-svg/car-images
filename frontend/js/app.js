/* ══════════════════════════════════════════════════════════════════════
   Color-by-Number Mosaic Book Generator — Main Application
   Single-file SPA: Router, State, API Client, Pages, Components
   ══════════════════════════════════════════════════════════════════════ */

// ── API Client ────────────────────────────────────────────────────────
const API = {
    base: '',
    async get(url) {
        const res = await fetch(this.base + url);
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },
    async post(url, body, isForm = false) {
        const opts = { method: 'POST' };
        if (isForm) {
            opts.body = body;
        } else {
            opts.headers = { 'Content-Type': 'application/json' };
            opts.body = JSON.stringify(body);
        }
        const res = await fetch(this.base + url, opts);
        if (!res.ok) {
            let errText;
            try { errText = JSON.stringify(await res.json()); } catch { errText = await res.text(); }
            throw new Error(errText);
        }
        const ct = res.headers.get('content-type');
        if (ct && ct.includes('application/json')) return res.json();
        if (ct && ct.includes('application/pdf')) return res.blob();
        return res;
    },
    async postForm(url, formData) {
        const res = await fetch(this.base + url, { method: 'POST', body: formData });
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },
    async put(url, body) {
        const res = await fetch(this.base + url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },
    async delete(url) {
        const res = await fetch(this.base + url, { method: 'DELETE' });
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },
};

// ── State ─────────────────────────────────────────────────────────────
const State = {
    currentPage: 'dashboard',
    theme: localStorage.getItem('theme') || 'dark',
    config: null,
    projects: [],
    currentProject: null,
    wizardStep: 1,
    wizardData: {
        name: '', subtitle: '', author: '', theme: 'animals',
        difficulty: 'medium', grid_size: 30, color_count: 'auto',
        page_size: 'kdp_8_5x11', orientation: 'portrait',
        answer_key_position: 'at_end', decoration_mode: 'off',
        decoration_theme: '', seed: null, images: [],
    },
    tempImages: [],
    currentPuzzle: null,
    recommendedColorCount: null,
};

// ── Toast Notifications ───────────────────────────────────────────────
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
    toast.innerHTML = `
        <span style="font-size:1.1em">${icons[type] || 'ℹ'}</span>
        <span class="toast-message">${message}</span>
        <span class="toast-close" onclick="this.parentElement.remove()">×</span>
    `;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

// ── Router ────────────────────────────────────────────────────────────
function navigate(page) {
    State.currentPage = page;
    window.location.hash = page;
    render();
}

window.addEventListener('hashchange', () => {
    const hash = window.location.hash.slice(1) || 'dashboard';
    State.currentPage = hash;
    render();
});

// ── Theme ─────────────────────────────────────────────────────────────
function toggleTheme() {
    State.theme = State.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', State.theme);
    localStorage.setItem('theme', State.theme);
    render();
}

// ── Main Render ───────────────────────────────────────────────────────
function render() {
    document.documentElement.setAttribute('data-theme', State.theme);
    const app = document.getElementById('app');
    app.className = 'app-layout';
    app.innerHTML = `
        ${renderSidebar()}
        <div class="main-area">
            ${renderTopbar()}
            <div class="content-area" id="content">
                ${renderPage()}
            </div>
        </div>
    `;
    attachEventListeners();
}

// ── Sidebar ───────────────────────────────────────────────────────────
function renderSidebar() {
    const items = [
        { id: 'dashboard', icon: '📊', label: 'Dashboard' },
        { id: 'projects', icon: '📁', label: 'Projects' },
        { id: 'create-book', icon: '✨', label: 'Create New Book' },
        { id: 'image-generator', icon: '🎨', label: 'Image Generator' },
        { id: 'puzzle-generator', icon: '🧩', label: 'Puzzle Generator' },
        { id: 'book-builder', icon: '📖', label: 'Book Builder' },
        { id: 'export-center', icon: '📤', label: 'Export Center' },
        { id: 'settings', icon: '⚙️', label: 'Settings' },
    ];

    return `
    <nav class="sidebar">
        <div class="sidebar-header">
            <div class="sidebar-logo">M</div>
            <div>
                <div class="sidebar-title">Mosaic Studio</div>
                <div class="sidebar-subtitle">Book Generator</div>
            </div>
        </div>
        <div class="sidebar-nav">
            <div class="sidebar-section-label">Main</div>
            ${items.slice(0, 3).map(i => `
                <div class="nav-item ${State.currentPage === i.id ? 'active' : ''}"
                     onclick="navigate('${i.id}')" id="nav-${i.id}">
                    <span class="nav-icon">${i.icon}</span>
                    <span>${i.label}</span>
                </div>
            `).join('')}
            <div class="sidebar-section-label">Tools</div>
            ${items.slice(3, 7).map(i => `
                <div class="nav-item ${State.currentPage === i.id ? 'active' : ''}"
                     onclick="navigate('${i.id}')" id="nav-${i.id}">
                    <span class="nav-icon">${i.icon}</span>
                    <span>${i.label}</span>
                </div>
            `).join('')}
            <div class="sidebar-section-label">System</div>
            ${items.slice(7).map(i => `
                <div class="nav-item ${State.currentPage === i.id ? 'active' : ''}"
                     onclick="navigate('${i.id}')" id="nav-${i.id}">
                    <span class="nav-icon">${i.icon}</span>
                    <span>${i.label}</span>
                </div>
            `).join('')}
        </div>
    </nav>`;
}

// ── Topbar ────────────────────────────────────────────────────────────
function renderTopbar() {
    const titles = {
        'dashboard': 'Dashboard',
        'projects': 'Projects',
        'create-book': 'Create New Book',
        'image-generator': 'Image Generator',
        'puzzle-generator': 'Puzzle Generator',
        'book-builder': 'Book Builder',
        'export-center': 'Export Center',
        'settings': 'Settings',
    };
    return `
    <div class="topbar">
        <div class="topbar-left">
            <span class="topbar-title">${titles[State.currentPage] || 'Dashboard'}</span>
        </div>
        <div class="topbar-right">
            <span class="text-sm text-tertiary" id="provider-status"></span>
            <button class="btn btn-ghost btn-icon" onclick="toggleTheme()"
                    title="Toggle Theme">
                ${State.theme === 'dark' ? '☀️' : '🌙'}
            </button>
        </div>
    </div>`;
}

// ── Page Router ───────────────────────────────────────────────────────
function renderPage() {
    switch (State.currentPage) {
        case 'dashboard': return renderDashboard();
        case 'projects': return renderProjects();
        case 'create-book': return renderCreateBook();
        case 'image-generator': return renderImageGenerator();
        case 'puzzle-generator': return renderPuzzleGenerator();
        case 'book-builder': return renderBookBuilder();
        case 'export-center': return renderExportCenter();
        case 'settings': return renderSettings();
        default: return renderDashboard();
    }
}

// ══════════════════════════════════════════════════════════════════════
//  PAGES
// ══════════════════════════════════════════════════════════════════════

// ── Dashboard ─────────────────────────────────────────────────────────
function renderDashboard() {
    return `
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">Total Projects</div>
            <div class="stat-value" id="stat-projects">—</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Puzzles Created</div>
            <div class="stat-value" id="stat-puzzles">—</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">AI Provider</div>
            <div class="stat-value" id="stat-provider" style="font-size:var(--fs-md)">—</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Quick Action</div>
            <div style="margin-top:var(--sp-2)">
                <button class="btn btn-primary" onclick="navigate('create-book')">
                    ✨ Create New Book
                </button>
            </div>
        </div>
    </div>
    <div class="card">
        <div class="card-header">
            <span class="card-title">Recent Projects</span>
            <button class="btn btn-secondary btn-sm" onclick="navigate('projects')">View All</button>
        </div>
        <div class="card-body" id="recent-projects">
            <div class="empty-state">
                <div class="empty-state-icon">📁</div>
                <div class="empty-state-title">No projects yet</div>
                <div class="empty-state-text">Create your first Color-by-Number book to get started.</div>
                <button class="btn btn-primary" onclick="navigate('create-book')">✨ Create New Book</button>
            </div>
        </div>
    </div>`;
}

// ── Projects ──────────────────────────────────────────────────────────
function renderProjects() {
    return `
    <div class="flex justify-between items-center mb-6">
        <div>
            <h2 style="font-size:var(--fs-xl);font-weight:var(--fw-bold)">Your Projects</h2>
            <p class="text-secondary text-sm mt-2">Manage your Color-by-Number book projects</p>
        </div>
        <button class="btn btn-primary" onclick="navigate('create-book')">✨ New Project</button>
    </div>
    <div id="projects-list">
        <div class="spinner"></div>
    </div>`;
}

// ── Create Book (7-Step Wizard) ───────────────────────────────────────
function renderCreateBook() {
    const steps = [
        { num: 1, label: 'Book Setup' },
        { num: 2, label: 'Images' },
        { num: 3, label: 'Mosaic Settings' },
        { num: 4, label: 'Preview' },
        { num: 5, label: 'Pages' },
        { num: 6, label: 'Answer Keys' },
        { num: 7, label: 'Export' },
    ];
    const s = State.wizardStep;

    return `
    <div class="stepper">
        ${steps.map((step, i) => `
            <div class="step ${s === step.num ? 'active' : s > step.num ? 'completed' : ''}"
                 onclick="setWizardStep(${step.num})">
                <div class="step-number">${s > step.num ? '✓' : step.num}</div>
                <span class="step-label">${step.label}</span>
            </div>
            ${i < steps.length - 1 ? `<div class="step-connector ${s > step.num ? 'completed' : ''}"></div>` : ''}
        `).join('')}
    </div>
    <div style="padding:var(--sp-6)">
        ${renderWizardStep()}
    </div>
    <div class="flex justify-between" style="padding:0 var(--sp-6) var(--sp-6)">
        <button class="btn btn-secondary" ${s === 1 ? 'disabled' : ''} onclick="setWizardStep(${s - 1})">
            ← Previous
        </button>
        ${s < 7 ? `
            <button class="btn btn-primary" onclick="handleWizardNext()">
                Next →
            </button>
        ` : `
            <button class="btn btn-success btn-lg" onclick="handleFinalExport()">
                📤 Export Book
            </button>
        `}
    </div>`;
}

function setWizardStep(n) {
    State.wizardStep = Math.max(1, Math.min(7, n));
    render();
}

function renderWizardStep() {
    switch (State.wizardStep) {
        case 1: return renderWizardBookSetup();
        case 2: return renderWizardImages();
        case 3: return renderWizardMosaicSettings();
        case 4: return renderWizardPreview();
        case 5: return renderWizardPages();
        case 6: return renderWizardAnswerKeys();
        case 7: return renderWizardExport();
    }
}

function renderWizardBookSetup() {
    const d = State.wizardData;
    const themes = State.config?.themes || ['animals','christmas','halloween','space','dinosaur',
        'ocean','farm','jungle','fantasy','winter','summer'];
    return `
    <div class="card">
        <div class="card-header"><span class="card-title">📖 Book Setup</span></div>
        <div class="card-body">
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Book Name *</label>
                    <input class="form-input" id="wiz-name" value="${d.name}" placeholder="My Color-by-Number Book">
                </div>
                <div class="form-group">
                    <label class="form-label">Subtitle</label>
                    <input class="form-input" id="wiz-subtitle" value="${d.subtitle}" placeholder="Optional subtitle">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Author Name</label>
                    <input class="form-input" id="wiz-author" value="${d.author}" placeholder="Your name">
                </div>
                <div class="form-group">
                    <label class="form-label">Theme</label>
                    <select class="form-select" id="wiz-theme">
                        ${themes.map(t => `<option value="${t}" ${d.theme === t ? 'selected' : ''}>${t.charAt(0).toUpperCase() + t.slice(1)}</option>`).join('')}
                    </select>
                </div>
            </div>
            <div class="form-row-3">
                <div class="form-group">
                    <label class="form-label">Difficulty</label>
                    <select class="form-select" id="wiz-difficulty">
                        <option value="easy" ${d.difficulty==='easy'?'selected':''}>Easy</option>
                        <option value="medium" ${d.difficulty==='medium'?'selected':''}>Medium</option>
                        <option value="hard" ${d.difficulty==='hard'?'selected':''}>Hard</option>
                        <option value="expert" ${d.difficulty==='expert'?'selected':''}>Expert</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Page Size</label>
                    <select class="form-select" id="wiz-pagesize">
                        <option value="kdp_8_5x11" ${d.page_size==='kdp_8_5x11'?'selected':''}>KDP 8.5×11</option>
                        <option value="kdp_8x10" ${d.page_size==='kdp_8x10'?'selected':''}>KDP 8×10</option>
                        <option value="us_letter" ${d.page_size==='us_letter'?'selected':''}>US Letter</option>
                        <option value="a4" ${d.page_size==='a4'?'selected':''}>A4</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Orientation</label>
                    <select class="form-select" id="wiz-orientation">
                        <option value="portrait" ${d.orientation==='portrait'?'selected':''}>Portrait</option>
                        <option value="landscape" ${d.orientation==='landscape'?'selected':''}>Landscape</option>
                    </select>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Seed (optional — for deterministic generation)</label>
                <input class="form-input" id="wiz-seed" type="number" value="${d.seed || ''}" placeholder="Leave empty for random">
            </div>
        </div>
    </div>`;
}

function renderWizardImages() {
    return `
    <div class="split-panel">
        <div class="card">
            <div class="card-header"><span class="card-title">📷 Upload Images</span></div>
            <div class="card-body">
                <div class="upload-zone" id="upload-zone"
                     ondragover="event.preventDefault(); this.classList.add('dragover')"
                     ondragleave="this.classList.remove('dragover')"
                     ondrop="handleDrop(event)"
                     onclick="document.getElementById('file-input').click()">
                    <div class="upload-zone-icon">📁</div>
                    <div class="upload-zone-text">Drag & drop images here</div>
                    <div class="upload-zone-hint">or click to browse • PNG, JPG, WEBP</div>
                </div>
                <input type="file" id="file-input" multiple accept="image/*"
                       style="display:none" onchange="handleFileSelect(event)">
                <p class="form-hint mt-4">Uploaded images are temporary — they won't be saved to any permanent library.</p>
            </div>
        </div>
        <div class="card">
            <div class="card-header">
                <span class="card-title">🎨 AI Generate</span>
                <span class="badge badge-info" id="ai-badge">—</span>
            </div>
            <div class="card-body">
                <div class="form-group">
                    <label class="form-label">Theme</label>
                    <select class="form-select" id="gen-theme">
                        ${(State.config?.themes || ['animals']).map(t =>
                            `<option value="${t}">${t.charAt(0).toUpperCase() + t.slice(1)}</option>`
                        ).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Custom Prompt (optional)</label>
                    <textarea class="form-textarea" id="gen-prompt"
                              placeholder="e.g. Cute cartoon lion sitting in a jungle"></textarea>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Number of Images</label>
                        <select class="form-select" id="gen-count">
                            <option value="1">1</option>
                            <option value="5">5</option>
                            <option value="10" selected>10</option>
                            <option value="20">20</option>
                            <option value="50">50</option>
                        </select>
                    </div>
                    <div class="form-group" style="display:flex;align-items:flex-end">
                        <button class="btn btn-primary w-full" onclick="handleAIGenerate()" id="btn-generate">
                            🎨 Generate
                        </button>
                    </div>
                </div>
                <div id="gen-progress" class="hidden">
                    <div class="progress-bar mt-4"><div class="progress-fill" id="gen-progress-fill" style="width:0%"></div></div>
                    <p class="text-sm text-secondary mt-2" id="gen-progress-text">Generating...</p>
                </div>
            </div>
        </div>
    </div>
    <div class="card mt-6">
        <div class="card-header">
            <span class="card-title">Selected Images (${State.tempImages.length})</span>
            ${State.tempImages.length ? '<button class="btn btn-ghost btn-sm" onclick="State.tempImages=[];render()">Clear All</button>' : ''}
        </div>
        <div class="card-body">
            ${State.tempImages.length === 0 ? `
                <div class="empty-state">
                    <div class="empty-state-icon">🖼️</div>
                    <div class="empty-state-text">No images selected yet. Upload or generate images above.</div>
                </div>
            ` : `
                <div class="thumbnail-grid">
                    ${State.tempImages.map((img, i) => `
                        <div class="thumbnail-card">
                            <img class="thumbnail-image" src="/api/images/temp/${img.filename || img.temp_name}" alt="Image ${i+1}">
                            <div class="thumbnail-info flex justify-between items-center">
                                <span class="thumbnail-title">${img.filename || img.temp_name}</span>
                                <button class="btn btn-ghost btn-sm" onclick="removeImage(${i})" title="Remove">✕</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `}
        </div>
    </div>`;
}

function renderWizardMosaicSettings() {
    const d = State.wizardData;
    const gridSizes = State.config?.grid_sizes || [20,30,40,50,60];
    const colorCounts = State.config?.color_counts || [6,8,10,12,15,20];
    return `
    <div class="card">
        <div class="card-header"><span class="card-title">🧩 Mosaic Settings</span></div>
        <div class="card-body">
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Grid Size</label>
                    <select class="form-select" id="wiz-gridsize" onchange="State.wizardData.grid_size = parseInt(this.value); render();">
                        ${gridSizes.map(g => `<option value="${g}" ${d.grid_size===g?'selected':''}>${g}×${g}</option>`).join('')}
                    </select>
                    <p class="form-hint">Higher = more detail, smaller cells</p>
                    ${d.grid_size >= 50 ? '<p class="text-sm mt-1" style="color:#f59e0b;font-weight:500;">⚠️ High grid density: numbers may be difficult to read in print.</p>' : ''}
                </div>
                <div class="form-group">
                    <label class="form-label">Number of Colors</label>
                    <select class="form-select" id="wiz-colorcount" onchange="State.wizardData.color_count = (this.value === 'auto' ? 'auto' : parseInt(this.value)); render();">
                        <option value="auto" ${d.color_count==='auto'||d.color_count===0?'selected':''}>Auto (Smart Optimal Detection)</option>
                        ${[6,8,10,12,15,20].map(c => `<option value="${c}" ${String(d.color_count)===String(c)?'selected':''}>${c} colors</option>`).join('')}
                    </select>
                    <p class="form-hint" style="${d.color_count==='auto' ? 'color:#3b82f6;font-weight:500;' : ''}">
                        ${d.color_count === 'auto'
                            ? (State.recommendedColorCount ? `Colors: Auto (Recommended: ${State.recommendedColorCount} colors)` : 'Colors: Auto (Intelligently detects optimal palette)')
                            : 'Manual palette size'}
                    </p>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Decoration Mode</label>
                    <select class="form-select" id="wiz-decomode">
                        <option value="off" ${d.decoration_mode==='off'?'selected':''}>Off</option>
                        <option value="library" ${d.decoration_mode==='library'?'selected':''}>Library</option>
                        <option value="custom" ${d.decoration_mode==='custom'?'selected':''}>Custom</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Decoration Theme</label>
                    <select class="form-select" id="wiz-decotheme">
                        <option value="">Same as book theme</option>
                        ${(State.config?.themes || []).map(t => `<option value="${t}" ${d.decoration_theme===t?'selected':''}>${t.charAt(0).toUpperCase() + t.slice(1)}</option>`).join('')}
                    </select>
                </div>
            </div>
            <div class="mt-4 p-4" style="background:var(--bg-tertiary);border-radius:var(--radius-md)">
                <h4 style="font-weight:var(--fw-semibold);margin-bottom:var(--sp-3)">Difficulty Presets</h4>
                <div class="flex gap-3">
                    <button class="btn ${d.difficulty==='easy'?'btn-primary':'btn-secondary'} btn-sm" onclick="applyDifficulty('easy')">Easy</button>
                    <button class="btn ${d.difficulty==='medium'?'btn-primary':'btn-secondary'} btn-sm" onclick="applyDifficulty('medium')">Medium</button>
                    <button class="btn ${d.difficulty==='hard'?'btn-primary':'btn-secondary'} btn-sm" onclick="applyDifficulty('hard')">Hard</button>
                    <button class="btn ${d.difficulty==='expert'?'btn-primary':'btn-secondary'} btn-sm" onclick="applyDifficulty('expert')">Expert</button>
                </div>
                <p class="form-hint mt-2">Presets adjust grid size and color count. You can manually override after.</p>
            </div>
        </div>
    </div>`;
}

function renderWizardPreview() {
    return `
    <div class="split-panel">
        <div class="card">
            <div class="card-header"><span class="card-title">🔍 Live Preview</span></div>
            <div class="card-body">
                <div class="tabs" id="preview-tabs">
                    <div class="tab active" onclick="switchPreview('source')">Source Image</div>
                    <div class="tab" onclick="switchPreview('puzzle')">Puzzle</div>
                    <div class="tab" onclick="switchPreview('answer')">Answer Key</div>
                </div>
                <div class="preview-container mt-4" id="preview-container" style="min-height:400px;display:flex;align-items:center;justify-content:center">
                    ${State.tempImages.length > 0 ? `
                        <img class="preview-image" id="preview-image"
                             src="/api/images/temp/${State.tempImages[0].filename || State.tempImages[0].temp_name}"
                             alt="Preview">
                    ` : `
                        <div class="empty-state">
                            <div class="empty-state-icon">🖼️</div>
                            <div class="empty-state-text">Add images in Step 2 to see a preview</div>
                        </div>
                    `}
                </div>
            </div>
        </div>
        <div class="card">
            <div class="card-header"><span class="card-title">📊 Image Analysis</span></div>
            <div class="card-body" id="analysis-panel">
                ${State.tempImages.length > 0 ? `
                    <button class="btn btn-primary w-full mb-4" onclick="analyzeCurrentImage()">Analyze Image</button>
                    <div id="analysis-results"></div>
                ` : `
                    <div class="empty-state">
                        <div class="empty-state-text">Select an image to analyze</div>
                    </div>
                `}
            </div>
        </div>
    </div>
    ${State.tempImages.length > 1 ? `
    <div class="card mt-6">
        <div class="card-header"><span class="card-title">All Images</span></div>
        <div class="card-body">
            <div class="thumbnail-grid">
                ${State.tempImages.map((img, i) => `
                    <div class="thumbnail-card ${i === 0 ? 'selected' : ''}" onclick="selectPreviewImage(${i})">
                        <img class="thumbnail-image" src="/api/images/temp/${img.filename || img.temp_name}" alt="Image ${i+1}">
                        <div class="thumbnail-info">
                            <span class="thumbnail-title">Image ${i + 1}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    </div>` : ''}`;
}

function renderWizardPages() {
    return `
    <div class="card">
        <div class="card-header">
            <span class="card-title">📑 Book Pages</span>
            <span class="badge badge-primary">${State.tempImages.length} puzzle pages</span>
        </div>
        <div class="card-body">
            ${State.tempImages.length === 0 ? `
                <div class="empty-state">
                    <div class="empty-state-icon">📄</div>
                    <div class="empty-state-text">No pages yet. Add images in Step 2.</div>
                </div>
            ` : `
                <div class="thumbnail-grid">
                    ${State.tempImages.map((img, i) => `
                        <div class="thumbnail-card" draggable="true"
                             ondragstart="dragStart(event, ${i})"
                             ondragover="event.preventDefault()"
                             ondrop="dropPage(event, ${i})">
                            <img class="thumbnail-image" src="/api/images/temp/${img.filename || img.temp_name}" alt="Page ${i+1}">
                            <div class="thumbnail-info flex justify-between items-center">
                                <div>
                                    <span class="thumbnail-title">Page ${i + 1}</span>
                                    <span class="thumbnail-meta">Puzzle</span>
                                </div>
                                <div class="flex gap-2">
                                    <button class="btn btn-ghost btn-sm" onclick="duplicateImage(${i})" title="Duplicate">📋</button>
                                    <button class="btn btn-ghost btn-sm" onclick="removeImage(${i})" title="Remove">✕</button>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <p class="form-hint mt-4">Drag and drop to reorder pages.</p>
            `}
        </div>
    </div>`;
}

function renderWizardAnswerKeys() {
    const d = State.wizardData;
    return `
    <div class="card">
        <div class="card-header"><span class="card-title">🔑 Answer Key Position</span></div>
        <div class="card-body">
            <div class="form-group">
                <label class="form-label">Where should answer keys appear?</label>
                <div class="flex gap-4 mt-4">
                    <div class="card ${d.answer_key_position === 'after_each' ? 'selected' : ''}"
                         style="flex:1;cursor:pointer;padding:var(--sp-5);text-align:center;
                                ${d.answer_key_position === 'after_each' ? 'border-color:var(--brand-primary);box-shadow:0 0 0 2px var(--brand-primary-bg)' : ''}"
                         onclick="State.wizardData.answer_key_position='after_each';render()">
                        <div style="font-size:2rem;margin-bottom:var(--sp-3)">📄↔️📄</div>
                        <h4 style="font-weight:var(--fw-semibold)">After Each Puzzle</h4>
                        <p class="text-sm text-secondary mt-2">Puzzle 1 → Answer 1 → Puzzle 2 → Answer 2 ...</p>
                    </div>
                    <div class="card ${d.answer_key_position === 'at_end' ? 'selected' : ''}"
                         style="flex:1;cursor:pointer;padding:var(--sp-5);text-align:center;
                                ${d.answer_key_position === 'at_end' ? 'border-color:var(--brand-primary);box-shadow:0 0 0 2px var(--brand-primary-bg)' : ''}"
                         onclick="State.wizardData.answer_key_position='at_end';render()">
                        <div style="font-size:2rem;margin-bottom:var(--sp-3)">📄📄📄➡️🔑</div>
                        <h4 style="font-weight:var(--fw-semibold)">All at End</h4>
                        <p class="text-sm text-secondary mt-2">All puzzles first, then all answer keys at the end</p>
                    </div>
                </div>
            </div>
            <div class="mt-6 p-4" style="background:var(--bg-tertiary);border-radius:var(--radius-md)">
                <h4 style="font-weight:var(--fw-semibold)">Book Summary</h4>
                <p class="text-sm text-secondary mt-2">
                    ${State.tempImages.length} puzzle pages + ${State.tempImages.length} answer key pages
                    = <strong>${State.tempImages.length * 2} total pages</strong>
                </p>
            </div>
        </div>
    </div>`;
}

function renderWizardExport() {
    return `
    <div class="card">
        <div class="card-header"><span class="card-title">📤 Export Book</span></div>
        <div class="card-body">
            <div class="stats-grid mb-6">
                <div class="stat-card">
                    <div class="stat-label">Book Name</div>
                    <div class="stat-value" style="font-size:var(--fs-lg)">${State.wizardData.name || '—'}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Pages</div>
                    <div class="stat-value">${State.tempImages.length * 2}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Grid Size</div>
                    <div class="stat-value">${State.wizardData.grid_size}×${State.wizardData.grid_size}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Colors</div>
                    <div class="stat-value">${State.wizardData.color_count === 'auto' ? (State.recommendedColorCount ? `Auto (${State.recommendedColorCount})` : 'Auto') : State.wizardData.color_count}</div>
                </div>
            </div>
            <div class="flex gap-4">
                <button class="btn btn-primary btn-lg" onclick="handleFinalExport()" id="btn-export">
                    📥 Export Complete Book (PDF)
                </button>
                <button class="btn btn-secondary btn-lg" onclick="handleValidate()">
                    ✅ Validate First
                </button>
            </div>
            <div id="export-progress" class="hidden mt-6">
                <div class="progress-bar"><div class="progress-fill" id="export-progress-fill" style="width:0%"></div></div>
                <p class="text-sm text-secondary mt-2" id="export-progress-text">Processing...</p>
            </div>
            <div id="export-result" class="mt-6"></div>
        </div>
    </div>`;
}

// ── Image Generator Page ──────────────────────────────────────────────
function renderImageGenerator() {
    return `
    <div class="split-panel">
        <div class="card">
            <div class="card-header"><span class="card-title">🎨 AI Image Generator</span></div>
            <div class="card-body">
                <div class="form-group">
                    <label class="form-label">Theme</label>
                    <select class="form-select" id="ig-theme">
                        ${(State.config?.themes || ['animals']).map(t =>
                            `<option value="${t}">${t.charAt(0).toUpperCase() + t.slice(1)}</option>`
                        ).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Subject (optional)</label>
                    <input class="form-input" id="ig-subject" placeholder="e.g. cat, dragon, rocket">
                </div>
                <div class="form-group">
                    <label class="form-label">Custom Prompt (optional)</label>
                    <textarea class="form-textarea" id="ig-prompt"
                              placeholder="Cute cartoon lion sitting in a jungle"></textarea>
                </div>
                <button class="btn btn-primary w-full" onclick="handleStandaloneGenerate()">🎨 Generate Image</button>
                <div id="ig-result" class="mt-4"></div>
            </div>
        </div>
        <div class="card">
            <div class="card-header"><span class="card-title">📷 Upload Image</span></div>
            <div class="card-body">
                <div class="upload-zone" id="ig-upload-zone"
                     ondragover="event.preventDefault(); this.classList.add('dragover')"
                     ondragleave="this.classList.remove('dragover')"
                     ondrop="handleStandaloneDrop(event)"
                     onclick="document.getElementById('ig-file-input').click()">
                    <div class="upload-zone-icon">📁</div>
                    <div class="upload-zone-text">Drag & drop an image</div>
                    <div class="upload-zone-hint">or click to browse</div>
                </div>
                <input type="file" id="ig-file-input" accept="image/*"
                       style="display:none" onchange="handleStandaloneUpload(event)">
            </div>
        </div>
    </div>`;
}

// ── Puzzle Generator Page ─────────────────────────────────────────────
function renderPuzzleGenerator() {
    return `
    <div class="split-panel-wide">
        <div class="card">
            <div class="card-header"><span class="card-title">🧩 Puzzle Generator</span></div>
            <div class="card-body">
                <div class="upload-zone" id="pg-upload-zone"
                     ondragover="event.preventDefault(); this.classList.add('dragover')"
                     ondragleave="this.classList.remove('dragover')"
                     ondrop="handlePuzzleDrop(event)"
                     onclick="document.getElementById('pg-file-input').click()">
                    <div class="upload-zone-icon">🖼️</div>
                    <div class="upload-zone-text">Drop source image here</div>
                    <div class="upload-zone-hint">or click to browse</div>
                </div>
                <input type="file" id="pg-file-input" accept="image/*"
                       style="display:none" onchange="handlePuzzleUpload(event)">
                <div id="pg-source" class="mt-4"></div>
                <div class="form-row mt-4">
                    <div class="form-group">
                        <label class="form-label">Grid Size</label>
                        <select class="form-select" id="pg-grid">
                            ${(State.config?.grid_sizes || [20,30,40,50,60]).map(g =>
                                `<option value="${g}" ${g===30?'selected':''}>${g}×${g}</option>`
                            ).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Colors</label>
                        <select class="form-select" id="pg-colors">
                            <option value="auto" selected>Auto (Smart Optimal)</option>
                            ${[6,8,10,12,15,20].map(c => `<option value="${c}">${c} colors</option>`).join('')}
                        </select>
                    </div>
                </div>
                <button class="btn btn-primary w-full mt-2" onclick="handleGeneratePuzzle()" id="btn-gen-puzzle">
                    🧩 Generate Puzzle
                </button>
            </div>
        </div>
        <div class="card">
            <div class="card-header"><span class="card-title">Preview</span></div>
            <div class="card-body" id="pg-preview">
                <div class="empty-state">
                    <div class="empty-state-icon">🧩</div>
                    <div class="empty-state-text">Upload an image and generate a puzzle to see the preview</div>
                </div>
            </div>
        </div>
    </div>`;
}

// ── Book Builder Page ─────────────────────────────────────────────────
function renderBookBuilder() {
    return `
    <div class="flex justify-between items-center mb-6">
        <div>
            <h2 style="font-size:var(--fs-xl);font-weight:var(--fw-bold)">Book Builder</h2>
            <p class="text-secondary text-sm mt-2">Arrange and manage your book pages</p>
        </div>
        <button class="btn btn-primary" onclick="navigate('create-book')">✨ Create New Book</button>
    </div>
    <div class="card">
        <div class="card-body">
            ${State.currentProject ? `
                <div class="thumbnail-grid" id="book-pages">
                    <!-- Pages would be loaded dynamically -->
                </div>
            ` : `
                <div class="empty-state">
                    <div class="empty-state-icon">📖</div>
                    <div class="empty-state-title">No active book project</div>
                    <div class="empty-state-text">Create a new book project to start building.</div>
                    <button class="btn btn-primary" onclick="navigate('create-book')">✨ Create New Book</button>
                </div>
            `}
        </div>
    </div>`;
}

// ── Export Center Page ────────────────────────────────────────────────
function renderExportCenter() {
    return `
    <div class="flex justify-between items-center mb-6">
        <div>
            <h2 style="font-size:var(--fs-xl);font-weight:var(--fw-bold)">Export Center</h2>
            <p class="text-secondary text-sm mt-2">Export your books as PDF, PNG, or SVG</p>
        </div>
    </div>
    <div class="stats-grid mb-6">
        <div class="stat-card">
            <div class="stat-label">Export Format</div>
            <div class="flex gap-3 mt-2">
                <button class="btn btn-primary btn-sm">PDF</button>
                <button class="btn btn-secondary btn-sm">PNG</button>
                <button class="btn btn-secondary btn-sm">SVG</button>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Export Type</div>
            <div class="flex gap-3 mt-2">
                <button class="btn btn-primary btn-sm">Complete Book</button>
                <button class="btn btn-secondary btn-sm">Puzzles Only</button>
                <button class="btn btn-secondary btn-sm">Answers Only</button>
            </div>
        </div>
    </div>
    <div class="card">
        <div class="card-body">
            <div class="empty-state">
                <div class="empty-state-icon">📤</div>
                <div class="empty-state-title">Ready to Export</div>
                <div class="empty-state-text">Use the Create New Book wizard (Step 7) to generate and export a complete book, or select a project to export.</div>
                <button class="btn btn-primary" onclick="navigate('create-book')">✨ Create New Book</button>
            </div>
        </div>
    </div>`;
}

// ── Settings Page ─────────────────────────────────────────────────────
function renderSettings() {
    return `
    <div class="card mb-6">
        <div class="card-header"><span class="card-title">🎨 Appearance</span></div>
        <div class="card-body">
            <div class="flex justify-between items-center">
                <div>
                    <h4 style="font-weight:var(--fw-semibold)">Dark Mode</h4>
                    <p class="text-sm text-secondary">Toggle between dark and light themes</p>
                </div>
                <div class="toggle ${State.theme === 'dark' ? 'active' : ''}" onclick="toggleTheme()">
                    <div class="toggle-knob"></div>
                </div>
            </div>
        </div>
    </div>
    <div class="card mb-6">
        <div class="card-header"><span class="card-title">🤖 AI Provider</span></div>
        <div class="card-body">
            <div id="provider-details">
                <div class="spinner"></div>
            </div>
        </div>
    </div>
    <div class="card">
        <div class="card-header"><span class="card-title">ℹ️ About</span></div>
        <div class="card-body">
            <p><strong>Color-by-Number Mosaic Book Generator</strong></p>
            <p class="text-secondary mt-2">Version 1.0.0</p>
            <p class="text-secondary mt-1">Create professional KDP-ready Color-by-Number books from AI-generated or uploaded images.</p>
        </div>
    </div>`;
}

// ══════════════════════════════════════════════════════════════════════
//  EVENT HANDLERS
// ══════════════════════════════════════════════════════════════════════

function attachEventListeners() {
    // Load dashboard data
    if (State.currentPage === 'dashboard') loadDashboardData();
    if (State.currentPage === 'projects') loadProjects();
    if (State.currentPage === 'settings') loadProviderInfo();
    if (State.currentPage === 'image-generator') loadProviderBadge();
    if (State.currentPage === 'create-book' && State.wizardStep === 2) loadProviderBadge();
}

async function loadDashboardData() {
    try {
        const projects = await API.get('/api/projects');
        const el = document.getElementById('stat-projects');
        if (el) el.textContent = projects.length;

        const info = await API.get('/api/images/provider-info');
        const provEl = document.getElementById('stat-provider');
        if (provEl) provEl.textContent = info.name;

        if (projects.length > 0) {
            const recentEl = document.getElementById('recent-projects');
            if (recentEl) {
                recentEl.innerHTML = projects.slice(0, 5).map(p => `
                    <div class="flex justify-between items-center p-4" style="border-bottom:1px solid var(--border-primary)">
                        <div>
                            <strong>${p.name}</strong>
                            <span class="badge badge-primary" style="margin-left:8px">${p.theme}</span>
                            <div class="text-sm text-tertiary mt-1">${p.page_count} pages · ${p.grid_size}×${p.grid_size} · ${p.color_count} colors</div>
                        </div>
                        <span class="text-sm text-tertiary">${new Date(p.created_at).toLocaleDateString()}</span>
                    </div>
                `).join('');
            }
        }
    } catch (e) { /* silent on dashboard */ }
}

async function loadProjects() {
    try {
        const projects = await API.get('/api/projects');
        State.projects = projects;
        const el = document.getElementById('projects-list');
        if (!el) return;

        if (projects.length === 0) {
            el.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📁</div>
                    <div class="empty-state-title">No projects yet</div>
                    <div class="empty-state-text">Create your first book to get started.</div>
                    <button class="btn btn-primary" onclick="navigate('create-book')">✨ Create New Book</button>
                </div>`;
            return;
        }

        el.innerHTML = `<div class="thumbnail-grid">${projects.map(p => `
            <div class="thumbnail-card" onclick="openProject(${p.id})">
                <div class="thumbnail-image" style="display:flex;align-items:center;justify-content:center;background:var(--bg-tertiary);font-size:2rem">
                    📖
                </div>
                <div class="thumbnail-info">
                    <span class="thumbnail-title">${p.name}</span>
                    <div class="thumbnail-meta">${p.theme} · ${p.page_count} pages · ${new Date(p.created_at).toLocaleDateString()}</div>
                </div>
            </div>
        `).join('')}</div>`;
    } catch (e) {
        showToast('Failed to load projects: ' + e.message, 'error');
    }
}

async function loadProviderInfo() {
    try {
        const info = await API.get('/api/images/provider-info');
        const el = document.getElementById('provider-details');
        if (!el) return;
        el.innerHTML = `
            <div class="flex justify-between items-center mb-4">
                <div>
                    <h4 style="font-weight:var(--fw-semibold)">${info.name}</h4>
                    <p class="text-sm text-secondary mt-1">Provider Type: ${info.provider_type}</p>
                </div>
                <span class="badge ${info.has_api_key ? 'badge-success' : 'badge-warning'}">
                    ${info.has_api_key ? 'API Key Set' : 'No API Key'}
                </span>
            </div>
            ${!info.has_api_key ? `
                <div class="p-4" style="background:var(--color-warning-bg);border-radius:var(--radius-md)">
                    <p class="text-sm"><strong>No AI provider configured.</strong></p>
                    <p class="text-sm text-secondary mt-1">Set <code>IMAGE_PROVIDER=openai</code> and <code>OPENAI_API_KEY=sk-...</code> in your environment to enable AI image generation.</p>
                    <p class="text-sm text-secondary mt-1">Upload and drag-drop workflows work fully without an API key.</p>
                </div>
            ` : ''}`;
    } catch (e) { /* silent */ }
}

async function loadProviderBadge() {
    try {
        const info = await API.get('/api/images/provider-info');
        const el = document.getElementById('ai-badge');
        if (el) {
            el.textContent = info.name;
            el.className = `badge ${info.has_api_key ? 'badge-success' : 'badge-warning'}`;
        }
    } catch (e) { /* silent */ }
}

// ── File Upload Handlers ──────────────────────────────────────────────

async function handleFileSelect(event) {
    const files = event.target.files;
    if (!files.length) return;
    await uploadFiles(files);
}

async function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    const files = event.dataTransfer.files;
    if (files.length) await uploadFiles(files);
}

async function uploadFiles(files) {
    const formData = new FormData();
    for (const file of files) formData.append('files', file);

    try {
        const result = await API.postForm('/api/images/upload', formData);
        const uploaded = result.uploaded.filter(r => r.success);
        State.tempImages.push(...uploaded);
        showToast(`${uploaded.length} image(s) uploaded`, 'success');
        render();
    } catch (e) {
        showToast('Upload failed: ' + e.message, 'error');
    }
}

function removeImage(index) {
    State.tempImages.splice(index, 1);
    render();
}

function duplicateImage(index) {
    State.tempImages.splice(index + 1, 0, { ...State.tempImages[index] });
    render();
}

// ── Drag & Drop Reorder ───────────────────────────────────────────────
let dragIndex = null;
function dragStart(event, index) {
    dragIndex = index;
    event.dataTransfer.effectAllowed = 'move';
}

function dropPage(event, targetIndex) {
    event.preventDefault();
    if (dragIndex === null || dragIndex === targetIndex) return;
    const [item] = State.tempImages.splice(dragIndex, 1);
    State.tempImages.splice(targetIndex, 0, item);
    dragIndex = null;
    render();
}

// ── AI Generation ─────────────────────────────────────────────────────

async function handleAIGenerate() {
    const theme = document.getElementById('gen-theme')?.value || 'animals';
    const prompt = document.getElementById('gen-prompt')?.value || '';
    const count = parseInt(document.getElementById('gen-count')?.value || '1');

    const btn = document.getElementById('btn-generate');
    const progress = document.getElementById('gen-progress');
    if (btn) btn.disabled = true;
    if (progress) progress.classList.remove('hidden');

    try {
        if (prompt) {
            const result = await API.post('/api/images/generate', { prompt, theme, count });
            State.tempImages.push(...result.images.map(img => ({
                filename: img.filename, path: img.path, temp_name: img.filename
            })));
            showToast(`${result.count} image(s) generated`, 'success');
        } else {
            const formData = new FormData();
            formData.append('theme', theme);
            formData.append('count', count);
            const result = await API.postForm('/api/images/generate-bulk', formData);
            State.tempImages.push(...result.results.map(r => ({
                filename: r.filename, path: r.path, temp_name: r.filename
            })));
            showToast(`${result.successful} image(s) generated`, 'success');
            if (result.failed > 0) showToast(`${result.failed} failed`, 'warning');
        }
    } catch (e) {
        showToast('Generation failed: ' + e.message, 'error');
    }

    if (btn) btn.disabled = false;
    if (progress) progress.classList.add('hidden');
    render();
}

// ── Wizard Navigation ─────────────────────────────────────────────────

function handleWizardNext() {
    // Save current step data
    saveWizardData();

    if (State.wizardStep === 1 && !State.wizardData.name) {
        showToast('Please enter a book name', 'warning');
        return;
    }
    if (State.wizardStep === 2 && State.tempImages.length === 0) {
        showToast('Please add at least one image', 'warning');
        return;
    }

    State.wizardStep++;
    render();
}

function saveWizardData() {
    const d = State.wizardData;
    const getVal = id => document.getElementById(id)?.value;

    if (State.wizardStep === 1) {
        d.name = getVal('wiz-name') || d.name;
        d.subtitle = getVal('wiz-subtitle') || '';
        d.author = getVal('wiz-author') || '';
        d.theme = getVal('wiz-theme') || d.theme;
        d.difficulty = getVal('wiz-difficulty') || d.difficulty;
        d.page_size = getVal('wiz-pagesize') || d.page_size;
        d.orientation = getVal('wiz-orientation') || d.orientation;
        const seed = getVal('wiz-seed');
        d.seed = seed ? parseInt(seed) : null;
    }
    if (State.wizardStep === 3) {
        d.grid_size = parseInt(getVal('wiz-gridsize') || d.grid_size);
        const cc = getVal('wiz-colorcount');
        d.color_count = (cc === 'auto' ? 'auto' : parseInt(cc || d.color_count));
        d.decoration_mode = getVal('wiz-decomode') || d.decoration_mode;
        d.decoration_theme = getVal('wiz-decotheme') || d.decoration_theme;
    }
}

function applyDifficulty(level) {
    const defaults = State.config?.difficulty_defaults?.[level] ||
        { easy: {grid_size:20,color_count:8}, medium: {grid_size:30,color_count:10},
          hard: {grid_size:40,color_count:12}, expert: {grid_size:50,color_count:15} }[level];

    State.wizardData.difficulty = level;
    State.wizardData.grid_size = defaults.grid_size;
    // Keep 'auto' if already auto, or update to default
    if (State.wizardData.color_count !== 'auto') {
        State.wizardData.color_count = defaults.color_count;
    }
    render();
}

// ── Preview ───────────────────────────────────────────────────────────

async function switchPreview(type) {
    if (State.tempImages.length === 0) return;

    // Update tab states
    document.querySelectorAll('#preview-tabs .tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');

    const img = State.tempImages[0];
    const container = document.getElementById('preview-container');
    if (!container) return;

    if (type === 'source') {
        container.innerHTML = `<img class="preview-image" src="/api/images/temp/${img.filename || img.temp_name}" alt="Source">`;
        return;
    }

    container.innerHTML = '<div class="loading-overlay"><div class="spinner"></div><span class="text-secondary">Generating preview...</span></div>';

    try {
        const result = await API.post('/api/puzzles/preview', {
            source_image_path: img.path,
            grid_width: State.wizardData.grid_size,
            grid_height: State.wizardData.grid_size,
            color_count: State.wizardData.color_count,
            seed: State.wizardData.seed,
            preview_type: type,
        });
        if (result.recommended_color_count) {
            State.recommendedColorCount = result.recommended_color_count;
        }
        container.innerHTML = `<img class="preview-image" src="${result.image}" alt="${type} preview">`;
    } catch (e) {
        container.innerHTML = `<div class="empty-state"><div class="empty-state-text">Preview failed: ${e.message}</div></div>`;
    }
}

function selectPreviewImage(index) {
    // Move selected image to front for preview
    const [img] = State.tempImages.splice(index, 1);
    State.tempImages.unshift(img);
    render();
}

async function analyzeCurrentImage() {
    if (State.tempImages.length === 0) return;
    const img = State.tempImages[0];
    const resultsEl = document.getElementById('analysis-results');
    if (!resultsEl) return;

    resultsEl.innerHTML = '<div class="spinner"></div>';

    try {
        const formData = new FormData();
        formData.append('image_path', img.path);
        const result = await API.postForm('/api/images/analyze', formData);

        if (result.recommended_color_count) {
            State.recommendedColorCount = result.recommended_color_count;
        }

        const meterHtml = (label, value) => {
            const cls = value >= 70 ? 'good' : value >= 40 ? 'moderate' : 'poor';
            return `
            <div class="quality-meter">
                <div class="quality-meter-label">
                    <span>${label}</span>
                    <span class="quality-meter-value">${value}%</span>
                </div>
                <div class="quality-meter-bar">
                    <div class="quality-meter-fill ${cls}" style="width:${value}%"></div>
                </div>
            </div>`;
        };

        resultsEl.innerHTML = `
            <div class="badge ${result.is_suitable ? 'badge-success' : 'badge-warning'} mb-3" style="font-size:var(--fs-sm);padding:var(--sp-2) var(--sp-4)">
                ${result.recommendation}
            </div>
            <div class="mb-4 p-3 flex items-center justify-between" style="background:var(--bg-tertiary);border-radius:var(--radius-md)">
                <div>
                    <div style="font-weight:var(--fw-semibold);font-size:var(--fs-sm)">Optimal Palette Recommendation</div>
                    <div class="text-xs text-secondary">Colors: Auto &rarr; Recommended: <strong>${result.recommended_color_count} colors</strong></div>
                </div>
                <span class="badge badge-primary" style="font-size:var(--fs-sm);padding:var(--sp-1) var(--sp-3)">${result.recommended_color_count} Colors</span>
            </div>
            <div class="quality-meters">
                ${meterHtml('Image Quality', result.image_quality)}
                ${meterHtml('Color Separation', result.color_separation)}
                ${meterHtml('Contrast', result.contrast)}
                ${meterHtml('Subject Clarity', result.subject_clarity)}
                ${meterHtml('Mosaic Suitability', result.mosaic_suitability)}
            </div>
            ${result.issues.length > 0 ? `
                <div class="mt-4 p-4" style="background:var(--color-warning-bg);border-radius:var(--radius-md)">
                    <h4 style="font-weight:var(--fw-semibold);font-size:var(--fs-sm)">Suggestions</h4>
                    <ul style="margin-top:var(--sp-2);padding-left:var(--sp-5);font-size:var(--fs-sm);color:var(--text-secondary)">
                        ${result.issues.map(i => `<li>${i}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}`;
    } catch (e) {
        resultsEl.innerHTML = `<p class="text-sm" style="color:var(--color-error)">Analysis failed: ${e.message}</p>`;
    }
}

// ── Standalone image gen/upload (Image Generator page) ────────────────

async function handleStandaloneGenerate() {
    const theme = document.getElementById('ig-theme')?.value || 'animals';
    const subject = document.getElementById('ig-subject')?.value || '';
    const prompt = document.getElementById('ig-prompt')?.value || '';
    const resultEl = document.getElementById('ig-result');

    try {
        resultEl.innerHTML = '<div class="spinner"></div>';
        const result = await API.post('/api/images/generate', { prompt: prompt || undefined, subject: subject || undefined, theme });
        if (result.images.length > 0) {
            resultEl.innerHTML = `
                <div class="preview-container">
                    <img class="preview-image" src="/api/images/temp/${result.images[0].filename}" alt="Generated">
                </div>
                <p class="text-sm text-secondary mt-2">Generated by ${result.provider}</p>`;
        }
    } catch (e) {
        resultEl.innerHTML = `<p style="color:var(--color-error)">${e.message}</p>`;
    }
}

async function handleStandaloneDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    const files = event.dataTransfer.files;
    if (files.length) await uploadFiles(files);
}

async function handleStandaloneUpload(event) {
    const files = event.target.files;
    if (files.length) await uploadFiles(files);
}

// ── Puzzle Generator page handlers ────────────────────────────────────
let pgSourcePath = null;

async function handlePuzzleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    const files = event.dataTransfer.files;
    if (files.length) {
        const formData = new FormData();
        formData.append('files', files[0]);
        const result = await API.postForm('/api/images/upload', formData);
        if (result.uploaded[0]?.success) {
            pgSourcePath = result.uploaded[0].path;
            const el = document.getElementById('pg-source');
            if (el) {
                el.innerHTML = `<div class="preview-container"><img class="preview-image" src="/api/images/temp/${result.uploaded[0].temp_name}" alt="Source"></div>`;
            }
            showToast('Image uploaded', 'success');
        }
    }
}

async function handlePuzzleUpload(event) {
    const files = event.target.files;
    if (files.length) {
        const formData = new FormData();
        formData.append('files', files[0]);
        const result = await API.postForm('/api/images/upload', formData);
        if (result.uploaded[0]?.success) {
            pgSourcePath = result.uploaded[0].path;
            const el = document.getElementById('pg-source');
            if (el) {
                el.innerHTML = `<div class="preview-container"><img class="preview-image" src="/api/images/temp/${result.uploaded[0].temp_name}" alt="Source"></div>`;
            }
            showToast('Image uploaded', 'success');
        }
    }
}

async function handleGeneratePuzzle() {
    if (!pgSourcePath) { showToast('Upload an image first', 'warning'); return; }

    const grid = parseInt(document.getElementById('pg-grid')?.value || '30');
    const colorsVal = document.getElementById('pg-colors')?.value || 'auto';
    const colors = colorsVal === 'auto' ? 'auto' : parseInt(colorsVal);
    const btn = document.getElementById('btn-gen-puzzle');
    const previewEl = document.getElementById('pg-preview');

    if (btn) btn.disabled = true;
    if (previewEl) previewEl.innerHTML = '<div style="text-align:center;padding:40px"><div class="spinner spinner-lg" style="margin:0 auto"></div><p class="text-secondary mt-4">Generating puzzle...</p></div>';

    try {
        // Generate puzzle
        const puzzle = await API.post('/api/puzzles/generate', {
            source_image_path: pgSourcePath,
            grid_width: grid, grid_height: grid,
            color_count: colors,
        });

        // Get previews
        const puzzlePreview = await API.post('/api/puzzles/preview', {
            source_image_path: pgSourcePath,
            grid_width: grid, grid_height: grid,
            color_count: colors,
            preview_type: 'puzzle',
        });
        const answerPreview = await API.post('/api/puzzles/preview', {
            source_image_path: pgSourcePath,
            grid_width: grid, grid_height: grid,
            color_count: colors,
            preview_type: 'answer',
        });

        previewEl.innerHTML = `
            <div class="tabs mb-4">
                <div class="tab active" onclick="showPgTab(this, 'pg-puzzle-img')">Puzzle</div>
                <div class="tab" onclick="showPgTab(this, 'pg-answer-img')">Answer Key</div>
            </div>
            <div id="pg-puzzle-img"><img class="preview-image" src="${puzzlePreview.image}" alt="Puzzle"></div>
            <div id="pg-answer-img" class="hidden"><img class="preview-image" src="${answerPreview.image}" alt="Answer"></div>
            <div class="color-palette mt-4">
                ${puzzle.palette.map(p => `
                    <div class="color-swatch">
                        <div class="color-swatch-dot" style="background:${p.color_hex}"></div>
                        <span>${p.color_id} ${p.color_name}</span>
                    </div>
                `).join('')}
            </div>
            <div class="mt-4 flex gap-3">
                <button class="btn btn-primary btn-sm" onclick="exportSinglePuzzle(${puzzle.id}, 'pdf', 'puzzle')">📥 PDF Puzzle</button>
                <button class="btn btn-primary btn-sm" onclick="exportSinglePuzzle(${puzzle.id}, 'pdf', 'answer')">📥 PDF Answer</button>
                <button class="btn btn-secondary btn-sm" onclick="exportSinglePuzzle(${puzzle.id}, 'png', 'puzzle')">PNG</button>
                <button class="btn btn-secondary btn-sm" onclick="exportSinglePuzzle(${puzzle.id}, 'svg', 'puzzle')">SVG</button>
            </div>`;

        showToast('Puzzle generated successfully!', 'success');
    } catch (e) {
        previewEl.innerHTML = `<div class="empty-state"><p style="color:var(--color-error)">Generation failed: ${e.message}</p></div>`;
        showToast('Puzzle generation failed', 'error');
    }
    if (btn) btn.disabled = false;
}

function showPgTab(tabEl, showId) {
    tabEl.parentElement.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tabEl.classList.add('active');
    document.getElementById('pg-puzzle-img')?.classList.add('hidden');
    document.getElementById('pg-answer-img')?.classList.add('hidden');
    document.getElementById(showId)?.classList.remove('hidden');
}

async function exportSinglePuzzle(puzzleId, format, type) {
    try {
        const endpoint = `/api/export/${format}`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ puzzle_id: puzzleId, format, export_type: type }),
        });

        if (!response.ok) throw new Error(await response.text());

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `puzzle_${puzzleId}_${type}.${format}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
        showToast(`${format.toUpperCase()} exported!`, 'success');
    } catch (e) {
        showToast('Export failed: ' + e.message, 'error');
    }
}

// ── Final Export (Wizard Step 7) ──────────────────────────────────────

async function handleFinalExport() {
    saveWizardData();
    const d = State.wizardData;

    if (!d.name) { showToast('Please enter a book name in Step 1', 'warning'); return; }
    if (State.tempImages.length === 0) { showToast('Please add images in Step 2', 'warning'); return; }

    const progressEl = document.getElementById('export-progress');
    const progressFill = document.getElementById('export-progress-fill');
    const progressText = document.getElementById('export-progress-text');
    const resultEl = document.getElementById('export-result');
    const btn = document.getElementById('btn-export');

    if (progressEl) progressEl.classList.remove('hidden');
    if (btn) btn.disabled = true;
    if (resultEl) resultEl.innerHTML = '';

    try {
        // Step 1: Create project
        if (progressText) progressText.textContent = 'Creating project...';
        if (progressFill) progressFill.style.width = '10%';

        const project = await API.post('/api/projects', d);
        State.currentProject = project;

        // Step 2: Generate puzzles for each image
        const total = State.tempImages.length;
        const puzzleIds = [];

        for (let i = 0; i < total; i++) {
            const img = State.tempImages[i];
            const pct = 10 + (i / total) * 60;
            if (progressFill) progressFill.style.width = `${pct}%`;
            if (progressText) progressText.textContent = `Generating puzzle ${i + 1} / ${total}...`;

            const puzzle = await API.post('/api/puzzles/generate', {
                source_image_path: img.path,
                grid_width: d.grid_size,
                grid_height: d.grid_size,
                color_count: d.color_count,
                difficulty: d.difficulty,
                title: `Puzzle ${i + 1}`,
                seed: d.seed ? d.seed + i : null,
                project_id: project.id,
            });
            puzzleIds.push(puzzle.id);

            // Add page to project
            await API.post(`/api/projects/${project.id}/pages`, {
                page_number: i + 1,
                page_type: 'puzzle',
                title: `Puzzle ${i + 1}`,
                puzzle_id: puzzle.id,
                source_image_path: img.path,
            });
        }

        // Step 3: Validate
        if (progressFill) progressFill.style.width = '75%';
        if (progressText) progressText.textContent = 'Validating book...';

        const validation = await API.post('/api/export/validate', {
            project_id: project.id,
            format: 'pdf',
            export_type: 'complete',
            page_size: d.page_size,
            orientation: d.orientation,
        });

        if (!validation.is_valid) {
            if (resultEl) {
                resultEl.innerHTML = `
                    <div class="p-4" style="background:var(--color-error-bg);border-radius:var(--radius-md)">
                        <h4 style="font-weight:var(--fw-semibold);color:var(--color-error)">Validation Failed</h4>
                        <ul style="margin-top:var(--sp-2);padding-left:var(--sp-5);font-size:var(--fs-sm)">
                            ${validation.errors.map(e => `<li>${e}</li>`).join('')}
                        </ul>
                    </div>`;
            }
            showToast('Validation failed — cannot export', 'error');
            if (btn) btn.disabled = false;
            return;
        }

        // Step 4: Export PDF
        if (progressFill) progressFill.style.width = '85%';
        if (progressText) progressText.textContent = 'Generating PDF...';

        const response = await fetch('/api/export/pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                project_id: project.id,
                format: 'pdf',
                export_type: 'complete',
                page_size: d.page_size,
                orientation: d.orientation,
            }),
        });

        if (!response.ok) throw new Error(await response.text());

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        if (progressFill) progressFill.style.width = '100%';
        if (progressText) progressText.textContent = 'Complete!';

        // Download
        const a = document.createElement('a');
        a.href = url;
        a.download = `${d.name.replace(/\s+/g, '_')}_complete.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();

        if (resultEl) {
            resultEl.innerHTML = `
                <div class="p-4" style="background:var(--color-success-bg);border-radius:var(--radius-md)">
                    <h4 style="font-weight:var(--fw-semibold);color:var(--color-success)">✅ Book Exported Successfully!</h4>
                    <p class="text-sm text-secondary mt-2">${total} puzzles + ${total} answer keys = ${total * 2} pages</p>
                    <p class="text-sm text-secondary mt-1">File: ${d.name.replace(/\s+/g, '_')}_complete.pdf</p>
                </div>`;
        }

        showToast('Book exported successfully!', 'success');

    } catch (e) {
        showToast('Export failed: ' + e.message, 'error');
        if (resultEl) {
            resultEl.innerHTML = `<div class="p-4" style="background:var(--color-error-bg);border-radius:var(--radius-md)"><p style="color:var(--color-error)">${e.message}</p></div>`;
        }
    }

    if (btn) btn.disabled = false;
}

async function handleValidate() {
    if (!State.currentProject) {
        showToast('Generate the book first (export will create the project)', 'info');
        return;
    }
    try {
        const d = State.wizardData;
        const result = await API.post('/api/export/validate', {
            project_id: State.currentProject.id,
            format: 'pdf', export_type: 'complete',
            page_size: d.page_size, orientation: d.orientation,
        });
        if (result.is_valid) {
            showToast('✅ Validation passed! Ready to export.', 'success');
        } else {
            showToast('Validation failed: ' + result.errors.join('; '), 'error');
        }
    } catch (e) {
        showToast('Validation error: ' + e.message, 'error');
    }
}

function openProject(id) {
    // TODO: Load project and navigate to book builder
    showToast('Project loading coming soon', 'info');
}

// ══════════════════════════════════════════════════════════════════════
//  INITIALIZATION
// ══════════════════════════════════════════════════════════════════════

async function init() {
    document.documentElement.setAttribute('data-theme', State.theme);

    // Load config
    try {
        State.config = await API.get('/api/config');
    } catch (e) {
        console.error('Failed to load config:', e);
    }

    // Route from hash
    State.currentPage = window.location.hash.slice(1) || 'dashboard';

    render();
}

// Start the app
init();
