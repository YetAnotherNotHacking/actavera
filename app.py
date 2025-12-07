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
    if not nonce or not ciphertext or ttl <=0:
        abort(400) # malformed data
    pid = db.new_id()
    print(f"Registered new paste: {pid}")
    db.insert_paste(pid, nonce, ciphertext, ttl, destroy)
    return jsonify({"id": pid})

@app.route("/paste/<pid>")
def view(pid):
    return render_template('view.html', pid=pid)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9001)