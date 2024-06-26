const downloadButtons = document.querySelectorAll('.download_button[data-filename]');

downloadButtons.forEach(button => {
  button.addEventListener('click', () => {
    const filename = button.dataset.filename;
    const downloadUrl = `/oauth/config/download/${filename}`;
    fetch(downloadUrl)
      .then(response => response.blob())
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


/*
const renameButtons = document.querySelectorAll('.rename_button[data-filename]');
renameButtons.forEach(button => {
  button.addEventListener('click', () => {
    const baseUrl = window.location.origin;
    const saveConfigEndpoint = 'oauth/config/load/';
    const filename = document.getElementById('new_filename').value;
    const saveConfigURL = baseUrl + saveConfigEndpoint + filename + ".json";
    console.log("saveConfigURL: ", saveConfigURL)
    window.location.href = saveConfigURL;
      });
    });
*/

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
      }
    })
    .catch(error => {
      console.error("Error sending rename request:", error);
      alert("An error occurred. Please try again.");
    });
  });
});