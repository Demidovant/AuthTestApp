from flask import redirect, url_for
from flask import Flask
from oauth_endpoints import register_oauth_endpoints
from app_config.app_config import APP_HOST, APP_CERT, APP_KEY, APP_CERT_FOLDER, USER_OAUTH_CONFIG_FOLDER, \
    APP_OAUTH_CONFIG_FOLDER
from module.logger import logger

app = Flask(__name__, static_folder="static", static_url_path="", template_folder="templates")

logger.info("Start")


@app.route("/", methods=["GET", "POST"])
def index():
    return redirect(url_for("oauth"))


register_oauth_endpoints(app)

if __name__ == "__main__":
    app.config["APP_CERT_FOLDER"] = APP_CERT_FOLDER
    app.config["USER_OAUTH_CONFIG_FOLDER"] = USER_OAUTH_CONFIG_FOLDER
    app.config["APP_OAUTH_CONFIG_FOLDER"] = APP_OAUTH_CONFIG_FOLDER

    app.run(host=APP_HOST, debug=True,
            ssl_context=(app.config["APP_CERT_FOLDER"] + "/" + APP_CERT, app.config["APP_CERT_FOLDER"] + "/" + APP_KEY))
