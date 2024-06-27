import datetime
import json
import os
import time
import urllib
from urllib.parse import unquote

import requests
from flask import request, redirect, render_template, url_for, abort, make_response, send_file, jsonify
from requests import PreparedRequest
from werkzeug.utils import secure_filename
from app_config.app_config import OAUTH_CONFIG_FILE, APP_NAME
from module.logger import rotate_log, logger, read_log
from module.oauth.token_handler import clear_tokens, TOKEN_FILE, TOKEN_DECODED_FILE, get_username, read_decoded_token, \
    decode_token, save_token, save_decoded_token


def register_oauth_endpoints(app):
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

            with open(OAUTH_CONFIG_FILE, "w", encoding="utf-8") as f:
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
            with open(OAUTH_CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.loads(f.read())
        except Exception as e:
            logger.error(f"Файл {OAUTH_CONFIG_FILE} не найден, пуст или неккоретное содержимое файла")
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
    def oauth_callback():
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

            with open(OAUTH_CONFIG_FILE, "r", encoding="utf-8") as f:
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
    def oauth_logout():
        rotate_log(40)

        if request.method == "GET":
            logger.info("Logout calling. Method GET")
            clear_tokens()
            logger.info(f"Files {TOKEN_FILE} and {TOKEN_DECODED_FILE} are cleared")
            time.sleep(1)
            return redirect(url_for("oauth"))

    @app.route("/oauth/clean", methods=["GET"])
    def oauth_clean():
        if request.method == "GET":
            logger.info("Clean calling. Method GET")
            rotate_log(0)
            clear_tokens()
            logger.info(f"Files {TOKEN_FILE} and {TOKEN_DECODED_FILE} are cleared")
            return redirect(url_for("oauth"))

    @app.route("/oauth/config/download/<filename>", methods=["GET"])
    def oauth_download_config(filename):
        try:
            decoded_filename = unquote(filename)  # Декодирование имени файла
            file_path = os.path.join(app.config["USER_OAUTH_CONFIG_FOLDER"], decoded_filename)
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True)
            else:
                logger.warning(f"File {decoded_filename} not found.")
                return jsonify({"success": False, "error": "File not found."}), 404
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/oauth/config/load", methods=["GET", "POST"])
    def oauth_upload_config():
        if request.method == "POST":
            uploaded_file = request.files["USER_OAUTH_CONFIG_FOLDER"]
            if uploaded_file.filename != "":
                filename = secure_filename(uploaded_file.filename)
                file_path = os.path.join(app.config["USER_OAUTH_CONFIG_FOLDER"], filename)
                uploaded_file.save(file_path)
                logger.info(f"File {filename} uploaded successfully!")
            else:
                logger.warning("No file uploaded.")
        return redirect(url_for("oauth_user_config"))

    @app.route("/oauth/config/rename", methods=["POST"])
    def oauth_rename_config():
        if request.method == "POST":
            data = request.get_json()  # Get the JSON data from the request
            original_filename = data.get("original_filename")
            new_filename = data.get("new_filename")
            if not new_filename.endswith(".json"):
                new_filename = new_filename + ".json"

            logger.info("originalFilename:", original_filename)
            logger.info("newFilename:", new_filename)

            if original_filename and new_filename:
                try:
                    old_path = os.path.join(app.config["USER_OAUTH_CONFIG_FOLDER"], original_filename)
                    new_path = os.path.join(app.config["USER_OAUTH_CONFIG_FOLDER"], new_filename)
                    os.rename(old_path, new_path)
                    logger.info(f"File {original_filename} renamed to {new_filename} successfully!")
                    return jsonify({"success": True})
                except Exception as e:
                    logger.error(f"Error renaming file: {e}")
                    return jsonify({"success": False}), 500
            else:
                logger.warning("Missing original or new filename in rename request.")
                return jsonify({"success": False}), 400
        return redirect(url_for("oauth_user_config"))

    @app.route("/oauth/config/delete", methods=["POST"])
    def oauth_delete_config():
        if request.method == "POST":
            data = request.get_json()
            filename = data.get("filename")
            if filename:
                try:
                    file_path = os.path.join(app.config["USER_OAUTH_CONFIG_FOLDER"], filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"File {filename} deleted successfully!")
                        return jsonify({"success": True})
                    else:
                        logger.warning(f"File {filename} not found.")
                        return jsonify({"success": False, "error": "File not found"}), 404
                except Exception as e:
                    logger.error(f"Error deleting file: {e}")
                    return jsonify({"success": False}), 500
            else:
                logger.warning("Missing filename in delete request.")
                return jsonify({"success": False, "error": "Missing filename"}), 400
        return redirect(url_for("oauth_user_config"))

    @app.route("/oauth/user_config")
    def oauth_user_config():
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

        current_oauth_config_files = os.listdir(app.config["APP_OAUTH_CONFIG_FOLDER"])
        current_oauth_config_file_data = []
        for filename in current_oauth_config_files:
            file_path = os.path.join(app.config["APP_OAUTH_CONFIG_FOLDER"], filename)
            file_stats = os.stat(file_path)
            current_oauth_config_file_data.append({
                "current_oauth_config_filename": filename,
                "current_oauth_config_modified_date": datetime.datetime.fromtimestamp(file_stats.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"),
                "current_oauth_config_size": f"{round(file_stats.st_size / 1024, 2)} kb"
            })
        return render_template("/oauth/user_config.html", file_data=file_data,
                               current_oauth_config_file_data=current_oauth_config_file_data)
