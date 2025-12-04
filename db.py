import time
import sqlite3
import secrets
import base64

# easy connect function
def connect():
    return sqlite.connect('pastes.db') # probably would be remote in a real production, TODO: make this configurable by the host

# init db, just reading and running the schema.sql
def init_db():
    with connect() as c:
        with open("schema.sql") as f:
            c.executescript(f.read())

# get a new id for the post
def new_id():
    return base64.urlsafe_base64encode(secrets.token_bytes(16)).decode().rstrip("=")

# very very simple insert paste function, automatically inserting the current time into the time value
def insert_paste(id, nonce, ciphertext, ttl, destroy):
    with connect() as c:
        c.execute(
            'INSERT INTO pastes (id, nonce, ciphertext, created_at, ttl, destroy_on_read) VALUES (?, ?, ?, ?, ?, ?)',
            (id, nonce, ciphertext, int(time.time()), ttl, 1 if destroy else 0)
        )

# very simple get paste by id
def get_paste(id):
    with connect() as c:
        row = c.execute('SELECT id, nonce, ciphertext, created_at, ttl, destroy_on_read FROM pastes WHERE id=?', (id,)).fetchone()
        return row

# very simple delete paste
def delete_paste(id):
    with connect() as c:
        c.execute('DELETE FROM pastes WHERE id=?', (id,))