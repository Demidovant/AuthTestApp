const downloadButtons = document.querySelectorAll('.download_button[data-filename]');

downloadButtons.forEach(button => {
    button.addEventListener('click', () => {
        const filename = button.dataset.filename;
        const encodedFilename = encodeURIComponent(filename); // Кодирование имени файла
        const downloadUrl = `/oauth/config/download/${encodedFilename}`;
        fetch(downloadUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.blob();
            })
            .then(blob => {
                const downloadLink = document.createElement('a');
                downloadLink.href = URL.createObjectURL(blob);
                downloadLink.download = filename;
                downloadLink.style.display = 'none';

                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
            })
            .catch(error => {
                console.error('Download failed:', error);
            });
    });
});


const manageConfigsButton = document.getElementById('home_button');
manageConfigsButton.addEventListener('click', () => {
    window.location.href = '/oauth';
});


const renameButtons = document.querySelectorAll('.rename_button[data-original-filename]');

renameButtons.forEach(button => {
    button.addEventListener('click', () => {
        const originalFilename = button.dataset.originalFilename;
        const newFilenameInput = button.closest('tr').querySelector('.new_filename');
        const newFilename = newFilenameInput.value;
        if (!newFilename) {
            alert("Please enter a new filename");
            return;
        }

        console.log("originalFilename: ", originalFilename);
        console.log("newFilename: ", newFilename);

        fetch("/oauth/config/rename", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                original_filename: originalFilename,
                new_filename: newFilename
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("File renamed successfully!");
                    window.location.reload();
                } else {
                    alert("Error renaming file. Please try again.");
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error("Error sending rename request:", error);
                alert("An error occurred. Please try again.");
                window.location.reload();
            });
    });
});


const deleteButtons = document.querySelectorAll('.delete_button[data-filename]');

deleteButtons.forEach(button => {
    button.addEventListener('click', () => {
        const filename = button.dataset.filename;

        const confirmDelete = confirm(`Are you sure you want to delete the file: ${filename}?`);
        if (!confirmDelete) {
            return;
        }

        console.log("filename: ", filename);

        fetch("/oauth/config/delete", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                filename: filename
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    //alert("File deleted successfully!");
                    window.location.reload();
                } else {
                    alert("Error deleting file: " + (data.error || "Please try again."));
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error("Error sending delete request:", error);
                alert("An error occurred. Please try again.");
                window.location.reload();
            });
    });
});


document.getElementById('current_config_save_button').addEventListener('click', () => {
    const newFilenameInput = document.querySelector('.current_config_save_input');
    const newFilename = newFilenameInput.value;

    if (!newFilename) {
        alert("Please enter a filename");
        return;
    }

    fetch("/oauth/config/save_user_config", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            filename: newFilename
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                //alert("Configuration saved successfully!");
                window.location.reload();
            } else {
                alert("Error saving configuration. Please try again.");
            }
        })
        .catch(error => {
            console.error("Error saving configuration:", error);
            alert("An error occurred. Please try again.");
            window.location.reload();
        });
});


const useButtons = document.querySelectorAll('.use_button[data-filename]');
useButtons.forEach(button => {
    button.addEventListener('click', () => {
        const filename = button.dataset.filename;

        const confirmUse = confirm(`Are you sure you want to use the config file: ${filename}?`);
        if (!confirmUse) {
            return;
        }

        console.log("filename: ", filename);

        fetch("/oauth/config/use", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                filename: filename
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Configuration used successfully!");
                    window.location.reload();
                } else {
                    alert("Error using configuration: " + (data.error || "Please try again."));
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error("Error sending use request:", error);
                alert("An error occurred. Please try again.");
                indow.location.reload();
            });
    });
});


document.addEventListener('DOMContentLoaded', () => {
    const viewButtons = document.querySelectorAll('.view_button[data-filename]');
    const modal = document.getElementById('modal');
    const closeModal = document.querySelector('.close');
    const configContent = document.getElementById('config-content');

    viewButtons.forEach(button => {
        button.addEventListener('click', () => {
            const filename = button.dataset.filename;

            fetch(`/oauth/config/view/${filename}`)
                .then(response => response.text())
                .then(data => {
//                    console.log(data)
                    configContent.textContent = data;
                    modal.style.display = 'block';
                })
                .catch(error => {
                    console.error('Error fetching config:', error);
                });
        });
    });

    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            modal.style.display = 'none';
        }
    });

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});