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

const manageCertsButton = document.getElementById('manage_certs_button');
manageCertsButton.addEventListener('click', () => {
  window.location.href = 'oauth/user_cert';
});


document.getElementById('save_current_config_button').addEventListener('click', () => {
  const authorizationEndpoint = document.getElementById('authorization_endpoint').value;
  const tokenEndpoint = document.getElementById('token_endpoint').value;
  const logoutEndpoint = document.getElementById('logout_endpoint').value;
  const clientId = document.getElementById('client_id').value;
  const clientSecret = document.getElementById('client_secret').value;
  const redirectUri = document.getElementById('redirect_uri').value;
  const postLogoutRedirectUri = document.getElementById('post_logout_redirect_uri').value;
  const scope = document.getElementById('scope').value;

  const configData = {
    authorization_endpoint: authorizationEndpoint,
    token_endpoint: tokenEndpoint,
    logout_endpoint: logoutEndpoint,
    client_id: clientId,
    client_secret: clientSecret,
    redirect_uri: redirectUri,
    post_logout_redirect_uri: postLogoutRedirectUri,
    scope: scope
  };

  fetch("/oauth/config/save_current_config", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(configData)
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      //alert("Configuration saved successfully!");
      window.location.reload();
    } else {
      alert("Error saving configuration: " + (data.error || "Please try again."));
      window.location.reload();
    }
  })
  .catch(error => {
    console.error("Error sending save request:", error);
    alert("An error occurred. Please try again.");
    window.location.reload();
  });
});