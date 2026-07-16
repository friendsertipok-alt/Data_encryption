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

    // Отправка формы Анонимизации
    const formAnon = document.getElementById('anonymize-form');
    const btnAnon = document.getElementById('btn-anon');
    const resultAnon = document.getElementById('anon-result');
    const sessionIdDisplay = document.getElementById('session-id-display');

    formAnon.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!fileAnon.files || fileAnon.files.length === 0) {
            alert('Пожалуйста, выберите файл');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileAnon.files[0]);

        setLoading(btnAnon, true);
        resultAnon.classList.add('hidden');

        try {
            const response = await fetch('/api/anonymize/file', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Ошибка при обработке файла');
            }

            const sessionId = response.headers.get('X-Session-ID');
            if (sessionId) {
                sessionIdDisplay.textContent = sessionId;
                resultAnon.classList.remove('hidden');
                // Предзаполняем поле восстановления для удобства
                document.getElementById('session-id-input').value = sessionId;
            }

            // Скачивание файла
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

        } catch (error) {
            alert(error.message);
        } finally {
            setLoading(btnAnon, false);
        }
    });

    // Отправка формы Деанонимизации
    const formDeanon = document.getElementById('deanonymize-form');
    const btnDeanon = document.getElementById('btn-deanon');

    formDeanon.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const sessionId = document.getElementById('session-id-input').value.trim();
        if (!sessionId) {
            alert('Введите ID сессии');
            return;
        }

        if (!fileDeanon.files || fileDeanon.files.length === 0) {
            alert('Пожалуйста, выберите файл');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileDeanon.files[0]);
        formData.append('session_id', sessionId);

        setLoading(btnDeanon, true);

        try {
            const response = await fetch('/api/deanonymize/file', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Ошибка при восстановлении файла');
            }

            // Скачивание файла
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

        } catch (error) {
            alert(error.message);
        } finally {
            setLoading(btnDeanon, false);
        }
    });

    function setLoading(btn, isLoading) {
        const text = btn.querySelector('.btn-text');
        const spinner = btn.querySelector('.spinner');
        
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
});
