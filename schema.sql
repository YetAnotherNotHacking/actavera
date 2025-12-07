CREATE TABLE IF NOT EXISTS pastes (
    id TEXT PRIMARY KEY,
    nonce TEXT,
    ciphertext TEXT,
    created_at TEXT,
    ttl INTEGER,
    destroy_on_read INTEGER
);
ALTER TABLE pastes ADD COLUMN salt TEXT; -- needed for new encryption method