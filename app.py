from flask import Flask, request, jsonify, render_template, abort
import time
import db

app = Flask(__name__)
db.init_db()

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
        abort(400) # no data
    nonce = data.get("nonce")
    ciphertext = data.get("ciphertext")
    ttl = int(data.get('ttl', 0))
    destroy = bool(data.get('destroy_on_read', False))
    salt = data.get("salt")
    if not nonce or not ciphertext or ttl <=0:
        abort(400) # malformed data
    # submission safety, very important!!!
    if not isinstance(nonce, str) or len(nonce) > 400:
        abort(400)
    if not isinstance(ciphertext, str) or len(ciphertext) > 5_000_000:
        abort(400)
    if not isinstance(salt, str) or len(salt) > 200:
        abort(400)
    if ttl < 1 or ttl > 2419200:
        abort(400)
    pid = db.new_id()
    print(f"Registered new paste: {pid}")
    db.insert_paste(pid, nonce, ciphertext, ttl, destroy, salt)
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
    now = int(time.time())

    if now > created_at + ttl:
        db.delete_paste(pid)
        abort(404)  # expired according to the user's ttl

    response = {
        "nonce": row[1],
        "ciphertext": row[2],
        "salt": row[3]
    }

    if destroy_on_read:
        db.delete_paste(pid) # once read, delete

    return jsonify(response)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9001)