from flask import Flask, request, jsonify, render_template, abort
import time
import db
import subprocess
import os

tor_bin = os.path.join(os.path.dirname(__file__), "tor", "tor")
tor_data = os.path.join(os.path.dirname(__file__), "tor_data")
hs_dir = os.path.join(tor_data, "hs")
os.makedirs(hs_dir, exist_ok=True)

subprocess.Popen([
    tor_bin,
    "--DataDirectory", tor_data,
    "--HiddenServiceDir", hs_dir,
    "--HiddenServicePort", "80 127.0.0.1:9001"
])

hostname_file = os.path.join(hs_dir, "hostname")
onion = None
while not onion:
    try:
        with open(hostname_file, "r") as f:
            onion = f.read().strip()
    except:
        time.sleep(0.2)

print(f"Onion adress is: {onion}")

app = Flask(__name__)
db.init_db()

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 # limit 2mb of text per submission via flask

# routes:
# /
# main index, a simple client to make a new paste
# /upload
# simple json post to add a new paste, needs harderning
# /paste/<pid>
# get paste by paste id, return simple decryptor client and ciphertext


# main page, full client
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    data = request.get_json()
    if not data:
        abort(400)
    ttl = int(data.get("ttl", 0))
    destroy = bool(data.get("destroy_on_read", False))
    public = bool(data.get("public", False))
    if ttl < 1 or ttl > 2419200:
        abort(400)
    if public:
        plaintext = data.get("plaintext")
        if not isinstance(plaintext, str) or len(plaintext) == 0:
            abort(400)
        nonce = ""
        ciphertext = plaintext
        salt = ""
    else:
        nonce = data.get("nonce")
        ciphertext = data.get("ciphertext")
        salt = data.get("salt")
        if not nonce or not ciphertext or not salt:
            abort(400)
        if not isinstance(nonce, str) or len(nonce) > 400:
            abort(400)
        if not isinstance(ciphertext, str) or len(ciphertext) > 5_000_000:
            abort(400)
        if not isinstance(salt, str) or len(salt) > 200:
            abort(400)
    pid = db.new_id()
    db.insert_paste(pid, nonce, ciphertext, ttl, destroy, salt, public)
    return jsonify({"id": pid})


@app.route("/paste/<pid>")
def view(pid):
    return render_template('view.html', pid=pid)

@app.route("/api/paste/<pid>")
def api_paste(pid):
    row = db.get_paste(pid)
    if not row: 
        abort(404)

    created_at = row[4]
    ttl = row[5]
    destroy_on_read = bool(row[6])
    public = bool(row[7])
    now = int(time.time())

    if now > created_at + ttl:
        db.delete_paste(pid)
        abort(404)  # expired according to the user's ttl

    response = {
        "nonce": row[1],
        "ciphertext": row[2],
        "salt": row[3],
        "public": public
    }

    if destroy_on_read:
        db.delete_paste(pid) # once read, delete

    return jsonify(response)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9001)
