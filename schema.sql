CREATE TABLE pastes (
    id TEXT PRIMARY KEY,
    nonce TEXT,
    ciphertext TEXT,
    salt TEXT,
    created_at INTEGER,
    ttl INTEGER,
    destroy_on_read INTEGER
);
