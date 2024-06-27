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
        window.location.href = "/oauth/user_config";
      } else {
        alert("Error renaming file. Please try again.");
        window.location.href = "/oauth/user_config";
      }
    })
    .catch(error => {
      console.error("Error sending rename request:", error);
      alert("An error occurred. Please try again.");
      window.location.href = "/oauth/user_config";
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
        alert("File deleted successfully!");
        window.location.href = "/oauth/user_config";
      } else {
        alert("Error deleting file: " + (data.error || "Please try again."));
        window.location.href = "/oauth/user_config";
      }
    })
    .catch(error => {
      console.error("Error sending delete request:", error);
      alert("An error occurred. Please try again.");
      window.location.href = "/oauth/user_config";
    });
  });
});
