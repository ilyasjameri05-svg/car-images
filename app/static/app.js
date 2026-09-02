document.addEventListener('DOMContentLoaded', () => {
    // --- State ---
    let appState = {
        puzzleTypes: [],
        difficulties: [],
        project: null,
        puzzles: [],
        currentPreviewIndex: 0
    };

    // --- Navigation ---
    const navButtons = document.querySelectorAll('.nav-btn');
    const pages = document.querySelectorAll('.page');

    function navigateTo(targetId) {
        pages.forEach(p => p.classList.add('hidden'));
        navButtons.forEach(btn => btn.classList.remove('active'));
        
        document.getElementById(targetId).classList.remove('hidden');
        document.querySelector(`.nav-btn[data-target="${targetId}"]`).classList.add('active');
        
        if (targetId === 'preview') {
            renderPreview();
        }
    }

    navButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            navigateTo(e.target.dataset.target);
        });
    });

    // --- API Fetchers ---
    async function fetchInfo() {
        try {
            const res = await fetch('/api/info');
            const data = await res.json();
            appState.puzzleTypes = data.puzzle_types;
            appState.difficulties = data.difficulties;
            populateUI();
        } catch (e) {
            console.error("Failed to fetch info", e);
        }
    }

    // --- Populators ---
    function populateUI() {
        const diffSelect = document.getElementById('set-difficulty');
        if (diffSelect) {
            diffSelect.innerHTML = '';
            appState.difficulties.forEach(d => {
                const opt = document.createElement('option');
                opt.value = d;
                opt.textContent = d.charAt(0).toUpperCase() + d.slice(1);
                if (d === 'medium') opt.selected = true;
                diffSelect.appendChild(opt);
            });
        }

        const tbody = document.getElementById('puzzle-config-body');
        if (tbody) {
            tbody.innerHTML = '';
            appState.puzzleTypes.forEach(pt => {
                const tr = document.createElement('tr');
                
                // Name
                const tdName = document.createElement('td');
                tdName.textContent = pt.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                
                // Quantity
                const tdQty = document.createElement('td');
                const qtyInput = document.createElement('input');
                qtyInput.type = 'number';
                qtyInput.min = '0';
                qtyInput.value = '0';
                qtyInput.dataset.type = pt;
                qtyInput.className = 'puzzle-qty';
                qtyInput.addEventListener('input', updateTotalPuzzles);
                tdQty.appendChild(qtyInput);
                
                // Difficulty
                const tdDiff = document.createElement('td');
                const diffInput = document.createElement('select');
                diffInput.dataset.type = pt;
                diffInput.className = 'puzzle-diff';
                appState.difficulties.forEach(d => {
                    const opt = document.createElement('option');
                    opt.value = d;
                    opt.textContent = d.charAt(0).toUpperCase() + d.slice(1);
                    if (d === 'medium') opt.selected = true;
                    diffInput.appendChild(opt);
                });
                tdDiff.appendChild(diffInput);
                
                tr.appendChild(tdName);
                tr.appendChild(tdQty);
                tr.appendChild(tdDiff);
                tbody.appendChild(tr);
            });
        }
    }

    function updateTotalPuzzles() {
        let total = 0;
        document.querySelectorAll('.puzzle-qty').forEach(input => {
            const val = parseInt(input.value, 10);
            if (!isNaN(val) && val >= 0) {
                total += val;
            }
        });
        document.getElementById('total-puzzles').textContent = total;
    }

    // --- Actions ---
    document.getElementById('btn-new-project').addEventListener('click', () => {
        navigateTo('settings');
    });

    document.getElementById('btn-save-settings').addEventListener('click', async () => {
        const settings = {
            title: document.getElementById('set-title').value,
            subtitle: document.getElementById('set-subtitle').value || null,
            author: document.getElementById('set-author').value,
            difficulty: 'medium', // Default stub for old API
            include_cover: document.getElementById('set-cover').checked,
            include_title_page: document.getElementById('set-titlepage').checked,
            include_introduction: document.getElementById('set-intro').checked,
            include_answer_key: document.getElementById('set-answers').checked,
            puzzle_configs: {} // We build this in btn-start-generation
        };

        try {
            await fetch('/api/project/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });
            navigateTo('selection');
        } catch (e) {
            alert('Failed to save settings.');
        }
    });

    document.getElementById('btn-start-generation').addEventListener('click', async () => {
        const puzzleConfig = {};
        let totalCount = 0;
        
        document.querySelectorAll('.puzzle-qty').forEach(input => {
            const pt = input.dataset.type;
            const quantity = parseInt(input.value, 10);
            
            if (!isNaN(quantity) && quantity > 0) {
                const diffSelect = document.querySelector(`.puzzle-diff[data-type="${pt}"]`);
                puzzleConfig[pt] = {
                    quantity: quantity,
                    difficulty: diffSelect ? diffSelect.value : 'medium'
                };
                totalCount += quantity;
            }
        });
        
        if (totalCount === 0) {
            alert('Please select at least one puzzle to generate.');
            return;
        }
        
        navigateTo('generation');
        document.getElementById('gen-status-text').textContent = 'Generating puzzles... please wait.';
        document.getElementById('gen-progress-bar').style.width = '50%';
        document.getElementById('btn-go-preview').classList.add('hidden');
        document.getElementById('gen-stats-list').innerHTML = '';

        try {
            const res = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ puzzle_config: puzzleConfig })
            });
            const data = await res.json();
            
            if (data.status === 'success') {
                appState.project = data.state;
                appState.puzzles = data.state.puzzles;
                appState.currentPreviewIndex = 0;
                
                document.getElementById('gen-progress-bar').style.width = '100%';
                document.getElementById('gen-status-text').textContent = 'Generation complete!';
                
                const stats = document.getElementById('gen-stats-list');
                
                // Group puzzles by type
                const typeCounts = {};
                let validTotal = 0;
                appState.puzzles.forEach(p => {
                    const pt = p.puzzle_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                    if (!typeCounts[pt]) typeCounts[pt] = { total: 0, valid: 0 };
                    typeCounts[pt].total++;
                    if (p.validation_status === 'valid') {
                        typeCounts[pt].valid++;
                        validTotal++;
                    }
                });
                
                let statsHtml = '';
                for (const [pt, counts] of Object.entries(typeCounts)) {
                    statsHtml += `<li>${pt}: ${counts.valid} / ${counts.total}</li>`;
                }
                statsHtml += `<hr style="margin: 10px 0;">`;
                statsHtml += `<li><strong>Total: ${validTotal} / ${appState.puzzles.length} valid</strong></li>`;
                
                stats.innerHTML = statsHtml;
                
                document.getElementById('btn-go-preview').classList.remove('hidden');
            } else {
                document.getElementById('gen-status-text').textContent = 'Error during generation.';
            }
        } catch (e) {
            document.getElementById('gen-status-text').textContent = 'Failed to generate puzzles.';
        }
    });

    document.getElementById('btn-go-preview').addEventListener('click', () => {
        navigateTo('preview');
    });

    // --- Preview ---
    function renderPreview() {
        if (!appState.puzzles || appState.puzzles.length === 0) {
            document.getElementById('page-indicator').textContent = 'No puzzles generated';
            document.getElementById('puzzle-json-data').textContent = '';
            document.getElementById('puzzle-visuals').innerHTML = '<p>No data</p>';
            return;
        }

        const idx = appState.currentPreviewIndex;
        const puzzle = appState.puzzles[idx];
        
        document.getElementById('page-indicator').textContent = `Puzzle ${idx + 1} of ${appState.puzzles.length}`;
        
        // Show raw data
        document.getElementById('puzzle-json-data').textContent = JSON.stringify(puzzle, null, 2);
        
        // Very basic visual render based on type
        const vis = document.getElementById('puzzle-visuals');
        vis.innerHTML = `<h2>${puzzle.title}</h2><p><strong>Type:</strong> ${puzzle.puzzle_type}</p><p><strong>Status:</strong> ${puzzle.validation_status}</p>`;
        
        if (puzzle.puzzle_type === 'sudoku') {
            let table = '<table border="1" style="border-collapse: collapse; text-align: center;">';
            for (let r of puzzle.puzzle_data.givens) {
                table += '<tr>';
                for (let c of r) {
                    table += `<td style="width: 30px; height: 30px;">${c || ''}</td>`;
                }
                table += '</tr>';
            }
            table += '</table>';
            vis.innerHTML += table;
        } else if (puzzle.puzzle_type === 'word_search') {
            let gridStr = puzzle.puzzle_data.grid.map(row => row.join(' ')).join('<br>');
            vis.innerHTML += `<div style="font-family: monospace; letter-spacing: 5px;">${gridStr}</div>`;
        }
    }

    document.getElementById('prev-page').addEventListener('click', () => {
        if (appState.currentPreviewIndex > 0) {
            appState.currentPreviewIndex--;
            renderPreview();
        }
    });

    document.getElementById('next-page').addEventListener('click', () => {
        if (appState.currentPreviewIndex < appState.puzzles.length - 1) {
            appState.currentPreviewIndex++;
            renderPreview();
        }
    });

    document.getElementById('btn-regenerate-single').addEventListener('click', async () => {
        if (!appState.puzzles || appState.puzzles.length === 0) return;
        
        const puzzle = appState.puzzles[appState.currentPreviewIndex];
        const btn = document.getElementById('btn-regenerate-single');
        btn.disabled = true;
        btn.textContent = 'Regenerating...';
        
        try {
            const res = await fetch(`/api/puzzle/${puzzle.puzzle_id}/regenerate`, { method: 'POST' });
            const data = await res.json();
            if (data.status === 'success') {
                appState.puzzles[appState.currentPreviewIndex] = data.puzzle;
                renderPreview();
            }
        } catch (e) {
            alert('Failed to regenerate');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Regenerate This Puzzle';
        }
    });

    // --- Preflight & Export ---
    document.getElementById('btn-run-preflight').addEventListener('click', async () => {
        const resultsDiv = document.getElementById('preflight-results');
        resultsDiv.innerHTML = 'Running...';
        
        try {
            const res = await fetch('/api/preflight');
            const data = await res.json();
            
            let html = `<div class="alert ${data.status.toLowerCase()}">Status: ${data.status}</div>`;
            
            if (data.errors.length) {
                html += '<h4>Errors</h4><ul>' + data.errors.map(e => `<li>${e}</li>`).join('') + '</ul>';
            }
            
            resultsDiv.innerHTML = html;
            
            if (data.status === 'PASS' || data.status === 'WARNING') {
                document.getElementById('btn-export-pdf').disabled = false;
            } else {
                document.getElementById('btn-export-pdf').disabled = true;
            }
            
        } catch (e) {
            resultsDiv.innerHTML = '<div class="alert error">Failed to run preflight</div>';
        }
    });

    document.getElementById('btn-export-pdf').addEventListener('click', async () => {
        const btn = document.getElementById('btn-export-pdf');
        const filename = document.getElementById('export-filename').value;
        const resultsDiv = document.getElementById('export-results');
        
        btn.disabled = true;
        btn.textContent = 'Exporting...';
        resultsDiv.innerHTML = '';
        
        try {
            const res = await fetch('/api/export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename })
            });
            const data = await res.json();
            
            if (res.ok && data.status === 'success') {
                resultsDiv.innerHTML = `<div class="alert success">PDF successfully created at:<br><strong>${data.path}</strong></div>`;
            } else {
                resultsDiv.innerHTML = `<div class="alert error">Export failed: ${data.detail || 'Unknown error'}</div>`;
            }
        } catch (e) {
            resultsDiv.innerHTML = '<div class="alert error">Failed to export PDF</div>';
        } finally {
            btn.disabled = false;
            btn.textContent = 'Export PDF';
        }
    });

    // --- Init ---
    fetchInfo();
});
