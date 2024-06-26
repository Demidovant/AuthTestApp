document.getElementById('logout_button').onclick = function () {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
        const [name, value] = cookie.split('=');
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=${window.location.host}`;
    }
    const postLogoutRedirectUri = document.getElementById('post_logout_redirect_uri').value;
    const clientID = document.getElementById('client_id').value;
    console.log(postLogoutRedirectUri);
    console.log(clientID);
    let logoutURL = document.getElementById('logout_endpoint').dataset.href;
    logoutURL += "?post_logout_redirect_uri=" + postLogoutRedirectUri + "&client_id=" + clientID;
    window.location.href = logoutURL;
};

document.getElementById('clean_button').onclick = function () {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
        const [name, value] = cookie.split('=');
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=${window.location.host}`;
    }
    const baseUrl = window.location.origin;
    const cleanEndpoint = '/oauth/clean';
    const cleanURL = baseUrl + cleanEndpoint;
    window.location.href = cleanURL;
};

const manageConfigsButton = document.getElementById('manage_configs_button');
manageConfigsButton.addEventListener('click', () => {
  window.location.href = 'oauth/user_config';
});