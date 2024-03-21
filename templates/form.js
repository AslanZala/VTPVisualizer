function submitForm() {
    const folderInput = document.getElementById("folderInput");
    const files = folderInput.files;
    const fileArray = Array.from(files);
    const filePaths = [];

    for (let i = 0; i < fileArray.length; i++) {
        const file = fileArray[i];
        // Only .vtp files
        if (file.name.endsWith('.vtp')) {
            const relativePath = file.webkitRelativePath || file.mozRelativePath || file.relativePath;
            if (relativePath) {
                filePaths.push('F:/vtp/' + relativePath);
            }
        }
    }

    // Send AJAX request to backend Python code
    const formData = new FormData();
    formData.append('filePaths', JSON.stringify(filePaths));
    // Add other parameters
    formData.append('particle_id', parseFloat(document.getElementById('particle_id').value));
    formData.append('x_threshold', JSON.stringify([parseFloat(document.getElementById('x_min').value), parseFloat(document.getElementById('x_max').value)]));
    formData.append('y_threshold', JSON.stringify([parseFloat(document.getElementById('y_min').value), parseFloat(document.getElementById('y_max').value)]));
    formData.append('z_threshold', JSON.stringify([parseFloat(document.getElementById('z_min').value), parseFloat(document.getElementById('z_max').value)]));

    async function fetchData() {
        try {
            const response = await fetch('http://localhost:2887/getPositions', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (data) {
                let img = new Image();
                img.src = 'data:image/png;base64,' + data.imgBase64;
                // document.body.appendChild(img);
                let container = document.createElement('div');
                container.style.display = 'flex';
                container.style.flexDirection = 'column';
                container.style.alignItems = 'center';
                container.appendChild(img);
                let name = document.createElement('p');
                name.textContent = data.fileName;
                container.appendChild(name);
                document.body.appendChild(container);
            } else {
                console.error('Error:', data.error);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    fetchData();
}
