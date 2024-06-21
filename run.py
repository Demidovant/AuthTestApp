import time
import urllib.parse
import requests
from flask import render_template, request, redirect, url_for, send_from_directory, abort, make_response, send_file
import json
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from requests.models import PreparedRequest
import os
import jwt
from werkzeug.utils import secure_filename
import datetime

app = Flask(__name__, static_folder="static", static_url_path="", template_folder="templates")

LOG_FILE = "logs/oauth/log.txt"
TOKEN_FILE = "logs/oauth/token.txt"
TOKEN_DECODED_FILE = "logs/oauth/token_decoded.txt"
CONFIG_FILE = "app_config/oauth/oauth_config.json"

for file in [TOKEN_FILE, LOG_FILE, TOKEN_DECODED_FILE]:
    path = os.path.dirname(file)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(file, "w") as f:
        pass

logger = logging.getLogger("AuthTestApp")
logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler = RotatingFileHandler(LOG_FILE)
handler.setFormatter(formatter)
logger.addHandler(handler)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def rotate_log(n):
    lines = []
    with open(LOG_FILE, "r") as f:
        for line in reversed(f.readlines()):
            lines.append(line)
            if len(lines) >= n:
                break
    with open(LOG_FILE, "w") as f:
        f.writelines(lines[::-1])


def read_log():
    with open(LOG_FILE, "r") as f:
        log_content = f.read()
    return log_content


def decode_token(token):
    decoded_data = jwt.decode(jwt=token,
                              algorithms=["HS256"],
                              verify=False,
                              options={"verify_signature": False})
    return decoded_data


def save_token(token):
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(token)
    logger.info(f"Token saved to {TOKEN_FILE}")


def save_decoded_token(decoded_data):
    with open(TOKEN_DECODED_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(decoded_data, indent=4, ensure_ascii=False))
    logger.info(f"Decoded token saved to {TOKEN_DECODED_FILE}")


def read_decoded_token():
    with open(TOKEN_DECODED_FILE, "r", encoding="utf-8") as f:
        token_content = f.read()
    return token_content


def clear_tokens():
    with open(TOKEN_DECODED_FILE, "w", encoding="utf-8") as f:
        pass
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        pass


def get_username():
    username = ""
    attributes = ["sub", "uid", "mail", "email", "phone", "mobile"]
    for attr in attributes:
        if not username:
            try:
                with open(TOKEN_DECODED_FILE, "r", encoding="utf-8") as f:
                    username = json.load(f)[attr]
                    logger.info(f"Username: {username}")
            except:
                pass
    else:
        if not username:
            logger.warning("Can't get any USERNAME from token or no token")
            logger.warning(f"Tried to search {attributes} attributes")
        return username


logger.info("Start")


@app.route("/", methods=["GET", "POST"])
def index():
    return redirect(url_for("oauth"))


@app.route("/oauth", methods=["GET", "POST"])
def oauth():
    rotate_log(40)

    if request.method == "POST":
        logger.info("######################### Login button pressed ##############################")
        config = {
            "authorization_endpoint": request.form["authorization_endpoint"],
            "client_id": request.form["client_id"],
            "redirect_uri": request.form["redirect_uri"],
            "client_secret": request.form["client_secret"],
            "token_endpoint": request.form["token_endpoint"],
            "scope": request.form["scope"],
            "logout_endpoint": request.form["logout_endpoint"],
            "post_logout_redirect_uri": request.form["post_logout_redirect_uri"],
        }

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(json.dumps(config, indent=4, ensure_ascii=False))

        logger.info(config)
        clear_tokens()
        logger.info(f"Files {TOKEN_FILE} and {TOKEN_DECODED_FILE} are cleared")

        url = config["authorization_endpoint"]
        params = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "redirect_uri": config["redirect_uri"],
            "scope": config["scope"],
            "response_type": "code"
        }
        req = PreparedRequest()
        req.prepare_url(url, params)
        logger.info(f"Redirect to: {req.url}")

        return redirect(req.url)

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.loads(f.read())
    except Exception as e:
        logger.error(f"Файл {CONFIG_FILE} не найден, пуст или неккоретное содержимое файла")
        logger.error(e)
        config = {}

    if not config:
        config = {
            "authorization_endpoint": "",
            "client_id": "",
            "redirect_uri": "",
            "client_secret": "",
            "token_endpoint": "",
            "scope": "",
            "logout_endpoint": "",
            "post_logout_redirect_uri": "",
        }

    username = get_username()

    return render_template(
        "oauth/index.html",
        app_name=APP_NAME,
        authorization_endpoint=config["authorization_endpoint"],
        client_id=config["client_id"],
        redirect_uri=config["redirect_uri"],
        client_secret=config["client_secret"],
        token_endpoint=config["token_endpoint"],
        logout_endpoint=config["logout_endpoint"],
        post_logout_redirect_uri=config["post_logout_redirect_uri"],
        scope=config["scope"],
        log_content=read_log(),
        token_content=read_decoded_token(),
        username=username,
    )


@app.route("/oauth/callback", methods=["GET", "POST"])
def callback():
    rotate_log(40)

    if request.method == "GET":
        logger.info("Callback calling. Method GET")
        logger.info(request.args.to_dict())
        code = request.args.get("code")
        if code:
            logger.info(f"Get CODE: {code}")
            logger.info(f"Ready for get token")
        else:
            logger.error(f"No CODE from identity provider")
            return redirect(url_for("oauth"))

        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

        url = config["token_endpoint"]
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        params = {
            "code": code,
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "redirect_uri": config["redirect_uri"],
            "scope": config["scope"],
            "grant_type": "authorization_code",
        }

        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}"
        logger.info(f"POST to: {full_url}")

        # time.sleep(27)
        try:
            # response = requests.post(full_url, headers=headers, data=params, verify=IDP_CA_CERT)
            response = requests.post(url, headers=headers, data=params, verify=False)
            try:
                encoded_token = response.json()["access_token"]
                decoded_token = decode_token(encoded_token)
                logger.info("Token decoded successfully")
                save_token(encoded_token)
                save_decoded_token(decoded_token)
            except Exception as e:
                logger.info("Can't decode token or token not presented")
                logger.error(e)
            return redirect(url_for("oauth"))
        except Exception as e:
            logger.error(e)
            return redirect(url_for("oauth"))

    if request.method == "POST":
        logger.info("Callback calling. Method POST")
        return redirect(url_for("oauth"))


@app.route("/oauth/logout", methods=["GET"])
def logout():
    rotate_log(40)

    if request.method == "GET":
        logger.info("Logout calling. Method GET")
        clear_tokens()
        logger.info(f"Files {TOKEN_FILE} and {TOKEN_DECODED_FILE} are cleared")
        time.sleep(1)
        return redirect(url_for("oauth"))


@app.route("/oauth/clean", methods=["GET"])
def clean():
    if request.method == "GET":
        logger.info("Clean calling. Method GET")
        rotate_log(0)
        clear_tokens()
        logger.info(f"Files {TOKEN_FILE} and {TOKEN_DECODED_FILE} are cleared")
        return redirect(url_for("oauth"))


@app.route("/oauth/config/download/<filename>", methods=["GET", "POST"])
def download_config(filename):
    file_path = os.path.join(app.config["USER_OAUTH_CONFIG_FOLDER"], filename)
    if not os.path.exists(file_path):
        return abort(404)
    response = make_response(send_file(file_path, as_attachment=True))
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@app.route("/oauth/config/load", methods=["GET", "POST"])
def upload_config():
    if request.method == "POST":
        uploaded_file = request.files["config_file"]
        if uploaded_file.filename != "":
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            uploaded_file.save(file_path)
            logger.info(f"File {filename} uploaded successfully!")
        else:
            logger.warning("No file uploaded.")
    return redirect(url_for("oauth"))

@app.route("/oauth/user_config")
def user_config():
    files = os.listdir(app.config["USER_OAUTH_CONFIG_FOLDER"])
    file_data = []
    for filename in files:
        file_path = os.path.join(app.config["USER_OAUTH_CONFIG_FOLDER"], filename)
        file_stats = os.stat(file_path)
        file_data.append({
            "filename": filename,
            "modified_date": datetime.datetime.fromtimestamp(file_stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "size": f"{round(file_stats.st_size / 1024, 2)} kb"
        })

    current_config_files = os.listdir(app.config["APP_OAUTH_CONFIG_FOLDER"])
    current_config_file_data = []
    for filename in current_config_files:
        file_path = os.path.join(app.config["APP_OAUTH_CONFIG_FOLDER"], filename)
        file_stats = os.stat(file_path)
        current_config_file_data.append({
            "current_config_filename": filename,
            "current_config_modified_date": datetime.datetime.fromtimestamp(file_stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "current_config_size": f"{round(file_stats.st_size / 1024, 2)} kb"
        })
    return render_template("/oauth/user_config.html", file_data=file_data, current_config_file_data=current_config_file_data)


if __name__ == "__main__":
    app.config["APP_CERT_FOLDER"] = "app_cert"
    app.config["USER_OAUTH_CONFIG_FOLDER"] = "user_config/oauth"
    app.config["APP_OAUTH_CONFIG_FOLDER"] = "app_config/oauth"

    APP_CERT = "AuthTestApp.crt"
    APP_KEY = "AuthTestApp.key"
    #IDP_CA_CERT = "./certs/eurosib_ca.crt"
    APP_HOST = "localhost"
    APP_NAME = "AuthTestApp"

    app.run(host=APP_HOST, debug=True, ssl_context=(app.config["APP_CERT_FOLDER"] + "/" + APP_CERT, app.config["APP_CERT_FOLDER"] + "/" + APP_KEY))
