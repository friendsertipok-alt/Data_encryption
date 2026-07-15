document.addEventListener('DOMContentLoaded', () => {
    // --- Tabs Logic ---
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(btn.dataset.tab + '-tab').classList.add('active');
        });
    });

    // --- Drag & Drop Logic Helper ---
    function setupDropZone(dropZoneId, fileInputId, infoId, btnId) {
        const dropZone = document.getElementById(dropZoneId);
        const fileInput = document.getElementById(fileInputId);
        const info = document.getElementById(infoId);
        const btn = document.getElementById(btnId);
        let currentFile = null;

        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                handleFileSelect();
            }
        });

        fileInput.addEventListener('change', handleFileSelect);

        function handleFileSelect() {
            if (fileInput.files.length > 0) {
                currentFile = fileInput.files[0];
                info.textContent = `Выбран файл: ${currentFile.name}`;
                btn.disabled = false;
            } else {
                currentFile = null;
                info.textContent = '';
                btn.disabled = true;
            }
        }

        return () => currentFile;
    }

    const getAnonymizeFile = setupDropZone('drop-anonymize', 'file-anonymize', 'info-anonymize', 'btn-anonymize');
    const getDeanonymizeFile = setupDropZone('drop-deanonymize', 'file-deanonymize', 'info-deanonymize', 'btn-deanonymize');

    // --- Управление Сессиями ---
    async function loadSessions() {
        const select = document.getElementById('session-select');
        try {
            const res = await fetch('/api/sessions');
            const data = await res.json();
            
            select.innerHTML = ''; // Очистка
            
            if (!data.sessions || data.sessions.length === 0) {
                select.innerHTML = '<option value="">Нет сохраненных сессий</option>';
                return;
            }
            
            // Добавляем пустую опцию (placeholder)
            const defaultOpt = document.createElement('option');
            defaultOpt.value = "";
            defaultOpt.textContent = "-- Выберите файл --";
            select.appendChild(defaultOpt);

            data.sessions.forEach(session => {
                const opt = document.createElement('option');
                opt.value = session.session_id;
                const date = new Date(session.created_at).toLocaleString('ru-RU', {
                    day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
                });
                opt.textContent = `${session.filename} (${date})`;
                select.appendChild(opt);
            });
        } catch (e) {
            console.error("Ошибка загрузки сессий", e);
            select.innerHTML = '<option value="">Ошибка загрузки</option>';
        }
    }

    // Обработчик выбора в селекте
    document.getElementById('session-select').addEventListener('change', (e) => {
        document.getElementById('session-id').value = e.target.value;
    });

    // Загружаем сессии при старте и при переключении на вкладку
    loadSessions();
    document.querySelector('[data-tab="deanonymize"]').addEventListener('click', loadSessions);

    // --- API Calls ---
    
    // 1. Анонимизация
    document.getElementById('btn-anonymize').addEventListener('click', async () => {
        const file = getAnonymizeFile();
        if (!file) return;

        const btn = document.getElementById('btn-anonymize');
        const loader = document.getElementById('loader-anonymize');
        
        btn.style.display = 'none';
        loader.style.display = 'block';

        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_token', 'default_user'); // Можно брать из авторизации, если она есть

        try {
            const response = await fetch('/api/anonymize/file', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.error || 'Ошибка сервера');
            }

            // Получаем Session ID из заголовков
            const sessionId = response.headers.get('X-Session-ID');
            if(sessionId) {
                // Скачиваем файл
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = `anonymized_${file.name}`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                
                // Переключаем юзера на вкладку деанонимизации и обновляем список
                document.querySelector('[data-tab="deanonymize"]').click();
                
                setTimeout(() => {
                    document.getElementById('session-select').value = sessionId;
                    document.getElementById('session-id').value = sessionId;
                }, 500); // Небольшая задержка, чтобы список успел загрузиться
            }
            
        } catch (error) {
            alert('Ошибка: ' + error.message);
        } finally {
            btn.style.display = 'block';
            loader.style.display = 'none';
        }
    });

    // 2. Деанонимизация
    document.getElementById('btn-deanonymize').addEventListener('click', async () => {
        const file = getDeanonymizeFile();
        const sessionId = document.getElementById('session-id').value.trim();

        if (!file) return;
        if (!sessionId) {
            alert('Пожалуйста, введите ID сессии');
            return;
        }

        const btn = document.getElementById('btn-deanonymize');
        const loader = document.getElementById('loader-deanonymize');
        
        btn.style.display = 'none';
        loader.style.display = 'block';

        const formData = new FormData();
        formData.append('file', file);
        formData.append('session_id', sessionId);

        try {
            const response = await fetch('/api/deanonymize/file', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.error || 'Ошибка сервера');
            }

            // Скачиваем восстановленный файл
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = `restored_${file.name}`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            
        } catch (error) {
            alert('Ошибка: ' + error.message);
        } finally {
            btn.style.display = 'block';
            loader.style.display = 'none';
        }
    });
});
