from flask import Flask, request, abort
import datetime as datetime
import hmac
import hashlib
import subprocess
from dotenv import load_dotenv
import os
import logging


app = Flask(__name__)

#Github key comes from the .env file
load_dotenv()

GITHUB_SECRET = os.getenv('GITHUB_SECRET')
GITHUB_SECRET_BYTES = GITHUB_SECRET.encode('utf-8')
#print(GITHUB_SECRET_BYTES)
REPO_PATH = os.getenv('REPO_PATH')


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Validate the request
        app.logger.info("WEBHOOK'D")
        signature = request.headers.get('X-Hub-Signature')
        sha_name, signature = signature.split('=')
        app.logger.info(f"Signature details: {sha_name}, {signature}")
        if sha_name != 'sha1':
            app.logger.error("Unsupported hash algorithm")
            abort(501)

        # HMAC requires the key to be bytes, but data is string
        mac = hmac.new(GITHUB_SECRET_BYTES, msg=request.data, digestmod=hashlib.sha1)

        # Verify the signature
        if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
            app.logger.error("Signature verification failed")
            abort(403)

        # If the signature is valid, run deployment
        subprocess.Popen(['/bin/bash', f'{REPO_PATH}/../deploy.sh'])
        
    except Exception as e:
        app.logger.exception(f"Error during webhook processing: {e}")
        abort(500)  # Or handle the error as appropriate  

    app.logger.info("Subprocess completed, attempting to return 200...")

    return 'OK', 200

if __name__ == "__main__":
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.run(debug=False, host="127.0.0.1", port=5210)