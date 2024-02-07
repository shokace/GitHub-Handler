from flask import Flask, render_template, request, abort
from threading import Thread
import datetime as datetime
import hmac
import hashlib
import subprocess
from dotenv import load_dotenv
import os


app = Flask(__name__)

#Github key comes from the .env file
load_dotenv()

GITHUB_SECRET = os.getenv('GITHUB_SECRET')
GITHUB_SECRET_BYTES = GITHUB_SECRET.encode('utf-8')
#print(GITHUB_SECRET_BYTES)
REPO_PATH = os.getenv('REPO_PATH')


@app.route('/webhook', methods=['POST'])
def webhook():
    # Validate the request
    print("WEBHOOK'D")
    signature = request.headers.get('X-Hub-Signature')
    sha_name, signature = signature.split('=')
    print(sha_name, signature)
    if sha_name != 'sha1':
        abort(501)

    # HMAC requires the key to be bytes, but data is string
    mac = hmac.new(GITHUB_SECRET_BYTES, msg=request.data, digestmod=hashlib.sha1)

    # Verify the signature
    if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
        abort(403)

    # If the signature is valid, run deployment
    try:
        subprocess.call(['/bin/bash', f'{REPO_PATH}/../deploy.sh'])
        print("DONE")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")  

 

    return 'OK', 200

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5210)