document.addEventListener('DOMContentLoaded', () => {
    // Табы
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(btn.dataset.target).classList.add('active');
        });
    });

    // Settings Modal Logic
    const settingsModal = document.getElementById('settings-modal');
    const btnOpenSettings = document.getElementById('open-settings');
    const btnCloseSettings = document.getElementById('close-settings');
    const btnSaveSettings = document.getElementById('save-settings');

    btnOpenSettings.addEventListener('click', () => {
        settingsModal.classList.add('show');
    });

    btnCloseSettings.addEventListener('click', () => {
        settingsModal.classList.remove('show');
    });

    btnSaveSettings.addEventListener('click', () => {
        settingsModal.classList.remove('show');
    });

    // Обработка файлов (Анонимизация)
    const fileAnon = document.getElementById('file-anon');
    const dropAreaAnon = document.getElementById('drop-area-anon');
    const fileNameAnon = document.getElementById('file-name-anon');

    fileAnon.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileNameAnon.textContent = `Выбран файл: ${e.target.files[0].name}`;
        }
    });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropAreaAnon.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropAreaAnon.addEventListener(eventName, () => dropAreaAnon.classList.add('drag-over'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropAreaAnon.addEventListener(eventName, () => dropAreaAnon.classList.remove('drag-over'), false);
    });

    dropAreaAnon.addEventListener('drop', (e) => {
        let dt = e.dataTransfer;
        let files = dt.files;
        fileAnon.files = files;
        if (files.length > 0) {
            fileNameAnon.textContent = `Выбран файл: ${files[0].name}`;
        }
    });

    // Обработка файлов (Деанонимизация)
    const fileDeanon = document.getElementById('file-deanon');
    const dropAreaDeanon = document.getElementById('drop-area-deanon');
    const fileNameDeanon = document.getElementById('file-name-deanon');

    fileDeanon.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileNameDeanon.textContent = `Выбран файл: ${e.target.files[0].name}`;
        }
    });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropAreaDeanon.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropAreaDeanon.addEventListener(eventName, () => dropAreaDeanon.classList.add('drag-over'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropAreaDeanon.addEventListener(eventName, () => dropAreaDeanon.classList.remove('drag-over'), false);
    });

    dropAreaDeanon.addEventListener('drop', (e) => {
        let dt = e.dataTransfer;
        let files = dt.files;
        fileDeanon.files = files;
        if (files.length > 0) {
            fileNameDeanon.textContent = `Выбран файл: ${files[0].name}`;
        }
    });

    // Переключение режимов Файл / Текст
    let anonInputMode = 'file';
    let deanonInputMode = 'file';

    const btnAnonModeFile = document.getElementById('btn-anon-mode-file');
    const btnAnonModeText = document.getElementById('btn-anon-mode-text');
    const anonFileZone = document.getElementById('anon-file-zone');
    const anonTextZone = document.getElementById('anon-text-zone');

    if (btnAnonModeFile && btnAnonModeText) {
        btnAnonModeFile.addEventListener('click', () => {
            anonInputMode = 'file';
            btnAnonModeFile.classList.add('active');
            btnAnonModeFile.style.background = 'rgba(99, 102, 241, 0.2)';
            btnAnonModeFile.style.color = 'white';
            btnAnonModeText.classList.remove('active');
            btnAnonModeText.style.background = 'rgba(255,255,255,0.05)';
            btnAnonModeText.style.color = 'var(--text-muted)';
            anonFileZone.classList.remove('hidden');
            anonTextZone.classList.add('hidden');
        });

        btnAnonModeText.addEventListener('click', () => {
            anonInputMode = 'text';
            btnAnonModeText.classList.add('active');
            btnAnonModeText.style.background = 'rgba(99, 102, 241, 0.2)';
            btnAnonModeText.style.color = 'white';
            btnAnonModeFile.classList.remove('active');
            btnAnonModeFile.style.background = 'rgba(255,255,255,0.05)';
            btnAnonModeFile.style.color = 'var(--text-muted)';
            anonTextZone.classList.remove('hidden');
            anonFileZone.classList.add('hidden');
        });
    }

    const btnDeanonModeFile = document.getElementById('btn-deanon-mode-file');
    const btnDeanonModeText = document.getElementById('btn-deanon-mode-text');
    const deanonFileZone = document.getElementById('deanon-file-zone');
    const deanonTextZone = document.getElementById('deanon-text-zone');

    if (btnDeanonModeFile && btnDeanonModeText) {
        btnDeanonModeFile.addEventListener('click', () => {
            deanonInputMode = 'file';
            btnDeanonModeFile.classList.add('active');
            btnDeanonModeFile.style.background = 'rgba(99, 102, 241, 0.2)';
            btnDeanonModeFile.style.color = 'white';
            btnDeanonModeText.classList.remove('active');
            btnDeanonModeText.style.background = 'rgba(255,255,255,0.05)';
            btnDeanonModeText.style.color = 'var(--text-muted)';
            deanonFileZone.classList.remove('hidden');
            deanonTextZone.classList.add('hidden');
        });

        btnDeanonModeText.addEventListener('click', () => {
            deanonInputMode = 'text';
            btnDeanonModeText.classList.add('active');
            btnDeanonModeText.style.background = 'rgba(99, 102, 241, 0.2)';
            btnDeanonModeText.style.color = 'white';
            btnDeanonModeFile.classList.remove('active');
            btnDeanonModeFile.style.background = 'rgba(255,255,255,0.05)';
            btnDeanonModeFile.style.color = 'var(--text-muted)';
            deanonTextZone.classList.remove('hidden');
            deanonFileZone.classList.add('hidden');
        });
    }

    // Кнопки копирования
    const btnCopyAnon = document.getElementById('btn-copy-anon-text');
    if (btnCopyAnon) {
        btnCopyAnon.addEventListener('click', () => {
            const txt = document.getElementById('anon-text-output').value;
            navigator.clipboard.writeText(txt);
            btnCopyAnon.textContent = '✅ Скопировано!';
            setTimeout(() => btnCopyAnon.textContent = '📋 Скопировать', 2000);
        });
    }

    const btnCopyDeanon = document.getElementById('btn-copy-deanon-text');
    if (btnCopyDeanon) {
        btnCopyDeanon.addEventListener('click', () => {
            const txt = document.getElementById('deanon-text-output').value;
            navigator.clipboard.writeText(txt);
            btnCopyDeanon.textContent = '✅ Скопировано!';
            setTimeout(() => btnCopyDeanon.textContent = '📋 Скопировать', 2000);
        });
    }

    // Отправка формы Анонимизации
    const formAnon = document.getElementById('anonymize-form');
    const btnAnon = document.getElementById('btn-anon');
    const resultAnon = document.getElementById('anon-result');
    const sessionIdDisplay = document.getElementById('session-id-display');
    const anonTextOutputContainer = document.getElementById('anon-text-output-container');
    const anonTextOutput = document.getElementById('anon-text-output');

    formAnon.addEventListener('submit', async (e) => {
        e.preventDefault();

        const apiKey = document.getElementById('api-key-input').value.trim();
        if (!apiKey) {
            alert('Введите API Ключ');
            return;
        }

        const modeValue = document.querySelector('input[name="mode"]:checked').value;
        const groupIdInput = document.getElementById('group-id-input');
        const groupIdVal = groupIdInput ? groupIdInput.value.trim() : null;

        setLoading(btnAnon, true);
        resultAnon.classList.add('hidden');
        if (anonTextOutputContainer) anonTextOutputContainer.classList.add('hidden');

        try {
            if (anonInputMode === 'text') {
                const textVal = document.getElementById('text-anon-input').value.trim();
                if (!textVal) {
                    alert('Пожалуйста, введите текст');
                    setLoading(btnAnon, false);
                    return;
                }

                const res = await fetch('/api/anonymize/text', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': apiKey
                    },
                    body: JSON.stringify({
                        text: textVal,
                        mode: modeValue,
                        group_id: groupIdVal
                    })
                });

                if (!res.ok) {
                    const error = await res.json();
                    throw new Error(error.detail || error.error || 'Ошибка при обработке текста');
                }

                const data = await res.json();
                const displayCode = data.group_id || data.session_id;
                sessionIdDisplay.textContent = displayCode;
                document.getElementById('session-id-input').value = displayCode;
                
                if (anonTextOutput && anonTextOutputContainer) {
                    anonTextOutput.value = data.anonymized_text;
                    anonTextOutputContainer.classList.remove('hidden');
                }
                resultAnon.classList.remove('hidden');
            } else {
                if (!fileAnon.files || fileAnon.files.length === 0) {
                    alert('Пожалуйста, выберите файл');
                    setLoading(btnAnon, false);
                    return;
                }

                const formData = new FormData();
                formData.append('file', fileAnon.files[0]);
                formData.append('mode', modeValue);
                if (groupIdVal) formData.append('group_id', groupIdVal);

                const response = await fetch('/api/anonymize/file', {
                    method: 'POST',
                    headers: { 'X-API-Key': apiKey },
                    body: formData
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Ошибка при обработке файла');
                }

                const sessionId = response.headers.get('X-Session-ID');
                const groupIdHeader = response.headers.get('X-Group-ID');
                const displayCode = groupIdHeader || sessionId;

                if (displayCode) {
                    sessionIdDisplay.textContent = displayCode;
                    resultAnon.classList.remove('hidden');
                    document.getElementById('session-id-input').value = displayCode;
                }

                let filename = 'safe_file';
                const disposition = response.headers.get('Content-Disposition');
                if (disposition && disposition.indexOf('filename*=utf-8\'\'') !== -1) {
                    filename = decodeURIComponent(disposition.split("filename*=utf-8''")[1]);
                }

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            }
        } catch (error) {
            alert(error.message);
        } finally {
            setLoading(btnAnon, false);
        }
    });

    // Отправка формы Деанонимизации
    const formDeanon = document.getElementById('deanonymize-form');
    const btnDeanon = document.getElementById('btn-deanon');
    const deanonResultText = document.getElementById('deanon-result-text');
    const deanonTextOutput = document.getElementById('deanon-text-output');

    formDeanon.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const sessionId = document.getElementById('session-id-input').value.trim();
        if (!sessionId) {
            alert('Введите ID сессии');
            return;
        }

        const apiKey = document.getElementById('api-key-input').value.trim();
        if (!apiKey) {
            alert('Введите API Ключ');
            return;
        }

        setLoading(btnDeanon, true);
        if (deanonResultText) deanonResultText.classList.add('hidden');

        try {
            if (deanonInputMode === 'text') {
                const textVal = document.getElementById('text-deanon-input').value.trim();
                if (!textVal) {
                    alert('Пожалуйста, введите текст');
                    setLoading(btnDeanon, false);
                    return;
                }

                const res = await fetch('/api/deanonymize/text', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': apiKey
                    },
                    body: JSON.stringify({
                        text: textVal,
                        session_id: sessionId
                    })
                });

                if (!res.ok) {
                    const error = await res.json();
                    throw new Error(error.detail || error.error || 'Ошибка при восстановлении текста');
                }

                const data = await res.json();
                if (deanonTextOutput && deanonResultText) {
                    deanonTextOutput.value = data.restored_text;
                    deanonResultText.classList.remove('hidden');
                }
            } else {
                if (!fileDeanon.files || fileDeanon.files.length === 0) {
                    alert('Пожалуйста, выберите файл');
                    setLoading(btnDeanon, false);
                    return;
                }

                const formData = new FormData();
                formData.append('file', fileDeanon.files[0]);
                formData.append('session_id', sessionId);

                const response = await fetch('/api/deanonymize/file', {
                    method: 'POST',
                    headers: { 'X-API-Key': apiKey },
                    body: formData
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Ошибка при восстановлении файла');
                }

                let filename = 'restored_file';
                const disposition = response.headers.get('Content-Disposition');
                if (disposition && disposition.indexOf('filename*=utf-8\'\'') !== -1) {
                    filename = decodeURIComponent(disposition.split("filename*=utf-8''")[1]);
                }

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            }
        } catch (error) {
            alert(error.message);
        } finally {
            setLoading(btnDeanon, false);
        }
    });

    function setLoading(btn, isLoading) {
        const text = btn.querySelector('.btn-text');
        const spinner = btn.querySelector('.loader');
        
        if (isLoading) {
            text.classList.add('hidden');
            spinner.classList.remove('hidden');
            btn.disabled = true;
        } else {
            text.classList.remove('hidden');
            spinner.classList.add('hidden');
            btn.disabled = false;
        }
    }

    // History & Projects Management Logic
    const btnRefreshHistory = document.getElementById('btn-refresh-history');
    const historyTableBody = document.getElementById('history-table-body');
    const selectAllCheckbox = document.getElementById('select-all-sessions');
    const selectedCountSpan = document.getElementById('selected-count');
    const btnUseSelected = document.getElementById('btn-use-selected-sessions');

    if (btnRefreshHistory) {
        btnRefreshHistory.addEventListener('click', loadHistory);
    }

    async function loadHistory() {
        const apiKey = document.getElementById('api-key-input').value.trim();
        try {
            const res = await fetch('/api/sessions', {
                headers: { 'X-API-Key': apiKey }
            });
            if (!res.ok) return;
            const data = await res.json();
            renderHistory(data.sessions || []);
        } catch (e) {
            console.error('Failed to load history:', e);
        }
    }

    function renderHistory(sessions) {
        if (!sessions || sessions.length === 0) {
            historyTableBody.innerHTML = '<tr><td colspan="6" style="padding: 20px; text-align: center; color: var(--text-muted);">История сессий пуста.</td></tr>';
            return;
        }

        historyTableBody.innerHTML = sessions.map(s => {
            const dateStr = s.created_at ? new Date(s.created_at).toLocaleString('ru-RU') : '—';
            const groupBadge = s.group_id ? `<span style="background: rgba(99, 102, 241, 0.2); color: #818cf8; padding: 2px 8px; border-radius: 6px; font-weight: 600;">${s.group_id}</span>` : '<span style="color: var(--text-muted);">—</span>';
            return `
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="padding: 10px 12px;"><input type="checkbox" class="session-checkbox" value="${s.group_id || s.session_id}"></td>
                    <td style="padding: 10px 12px; font-weight: 500;">${s.filename}</td>
                    <td style="padding: 10px 12px;">${groupBadge}</td>
                    <td style="padding: 10px 12px;">${s.entities_count}</td>
                    <td style="padding: 10px 12px; color: var(--text-muted); font-size: 12px;">${dateStr}</td>
                    <td style="padding: 10px 12px; font-family: monospace; font-size: 11px; color: var(--text-muted);">${s.session_id.substring(0, 8)}...</td>
                </tr>
            `;
        }).join('');

        updateCheckboxes();
    }

    function updateCheckboxes() {
        const checkboxes = document.querySelectorAll('.session-checkbox');
        checkboxes.forEach(cb => {
            cb.addEventListener('change', updateSelectedCount);
        });
    }

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', (e) => {
            const checkboxes = document.querySelectorAll('.session-checkbox');
            checkboxes.forEach(cb => cb.checked = e.target.checked);
            updateSelectedCount();
        });
    }

    function updateSelectedCount() {
        const checked = document.querySelectorAll('.session-checkbox:checked');
        if (selectedCountSpan) selectedCountSpan.textContent = checked.length;
    }

    if (btnUseSelected) {
        btnUseSelected.addEventListener('click', () => {
            const checked = document.querySelectorAll('.session-checkbox:checked');
            if (checked.length === 0) {
                alert('Пожалуйста, выберите хотя бы одну сессию из списка');
                return;
            }
            const selectedValues = Array.from(checked).map(cb => cb.value);
            const uniqueValues = [...new Set(selectedValues)];
            document.getElementById('session-id-input').value = uniqueValues.join(', ');
            
            // Переключаемся на вкладку Восстановление
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.querySelector('.tab-btn[data-target="deanonymize-tab"]').classList.add('active');
            document.getElementById('deanonymize-tab').classList.add('active');
        });
    }
});
