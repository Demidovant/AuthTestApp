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