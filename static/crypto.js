// hash func
async function sha256(msg) {
    const enc = new TextEncoder().encode(msg)
    const h = await crypto.subtle.digest("SHA-256", enc)
    return h
}

// derive key from passphrase
async function deriveKey(password, salt) {
    const keyMaterial = await crypto.subtle.importKey("raw", await sha256(password), {name:"PBKDF2"}, false, ["deriveBits","deriveKey"])
    return crypto.subtle.deriveKey(
        {name:"PBKDF2", salt:salt, iterations:200000, hash:"SHA-256"},
        keyMaterial,
        {name:"AES-GCM", length:256},
        false,
        ["encrypt","decrypt"]
    )
}

// main enc func
async function encryptAES(pwd, text) {
    const salt = crypto.getRandomValues(new Uint8Array(16))
    const key = await deriveKey(pwd, salt)
    const iv = crypto.getRandomValues(new Uint8Array(12))
    const enc = new TextEncoder().encode(text)
    const ct = await crypto.subtle.encrypt({name:"AES-GCM", iv:iv}, key, enc)
    return {salt: btoa(String.fromCharCode(...salt)), iv: btoa(String.fromCharCode(...iv)), ct: btoa(String.fromCharCode(...new Uint8Array(ct)))}
}

// main de-enc func
async function decryptAES(pwd, salt_b64, iv_b64, ct_b64) {
    const salt = Uint8Array.from(atob(salt_b64), c => c.charCodeAt(0))
    const iv = Uint8Array.from(atob(iv_b64), c => c.charCodeAt(0))
    const ct = Uint8Array.from(atob(ct_b64), c => c.charCodeAt(0))
    const key = await deriveKey(pwd, salt)
    const pt = await crypto.subtle.decrypt({name:"AES-GCM", iv:iv}, key, ct)
    return new TextDecoder().decode(pt)
}

// page functionality
document.addEventListener("DOMContentLoaded", () => {
    const send = document.getElementById("send")
    if (send) {
        send.onclick = async () => {
            const text = document.getElementById("text").value
            const pub = document.getElementById("public").checked
            const ttl = document.getElementById("ttl").value
            const destroy = document.getElementById("destroy").checked

            let payload

            if (pub) {
                payload = {
                    public: true,
                    plaintext: text,
                    ttl: ttl,
                    destroy_on_read: destroy
                }
            } else {
                const pwd = document.getElementById("password").value
                const r = await encryptAES(pwd, text)
                payload = {
                    nonce: r.iv,
                    ciphertext: r.ct,
                    ttl: ttl,
                    destroy_on_read: destroy,
                    salt: r.salt,
                    public: false
                }
            }

            const resp = await fetch("/upload", {
                method:"POST",
                headers:{"Content-Type":"application/json"},
                body: JSON.stringify(payload)
            })

            const j = await resp.json()
            const base = location.origin

            if (pub) {
                const link = base + "/paste/" + j.id
                const res = document.getElementById("result")
                res.innerText = "Link: " + link
                const copy = document.getElementById("copy")
                copy.style.display = "inline-block"
                copy.onclick = () => navigator.clipboard.writeText(link)
            } else {
                const pwd = document.getElementById("password").value
                const link = base + "/paste/" + j.id + "#" + payload.salt
                const res = document.getElementById("result")
                res.innerText = "Link: " + link + "\nPassword: " + pwd
                const copy = document.getElementById("copy")
                copy.style.display = "inline-block"
                copy.onclick = () => navigator.clipboard.writeText(link)
            }
        }
    }

    if (typeof pid !== "undefined") {
        const box = document.getElementById("decrypt-box")
        const btn = document.getElementById("decrypt-btn")
        const pw = document.getElementById("pwinput")
        const out = document.getElementById("output")

        ;(async () => {
            const req = await fetch("/api/paste/" + pid)
            const data = await req.json()

            if (data.public) {
                box.style.display = "none"
                out.textContent = data.ciphertext
                return
            }

            btn.onclick = async () => {
                const hash = location.hash.slice(1)
                if (!hash) {
                    out.textContent = "missing key"
                    return
                }
                try {
                    const dec = await decryptAES(pw.value, data.salt, data.nonce, data.ciphertext)
                    out.textContent = dec
                } catch (_) {
                    out.textContent = "failed decryption"
                }
            }
        })()
    }
})