const downloadButtons = document.querySelectorAll('button[data-filename]');

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
document.getElementById('rename_config_button').onclick = function () {
    const baseUrl = window.location.origin;
    const saveConfigEndpoint = 'oauth/config/load/';
    const filename = document.getElementById('filename').value;
    const saveConfigURL = baseUrl + saveConfigEndpoint + filename + ".json";
    console.log("saveConfigURL: ", saveConfigURL)
    window.location.href = saveConfigURL;
};
*/