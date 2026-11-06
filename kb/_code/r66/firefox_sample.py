"""复做 FireFox Forensics：python firefox_sample.py 原题.zip。需要 pycryptodome。"""

import argparse
import hmac
import json
import re
import sqlite3
from base64 import b64decode
from hashlib import pbkdf2_hmac, sha1
from pathlib import Path
from zipfile import ZipFile

from Crypto.Cipher import AES, DES3
from Crypto.Util.asn1 import DerObjectId, DerOctetString, DerSequence
from Crypto.Util.Padding import unpad


def seq(b):
    return DerSequence().decode(b)


def octets(b):
    return DerOctetString().decode(b).payload


def oid(b):
    return DerObjectId().decode(b).value


def unlock_blob(blob, salt, password):
    alg, cipher = seq(blob)
    scheme, args = seq(alg)
    scheme = oid(scheme)
    if scheme == "1.2.840.113549.1.12.5.1.3":
        entry, _ = seq(args)
        entry = octets(entry)
        hp = sha1(salt + password).digest()
        chp = sha1(hp + entry).digest()
        padded = entry.ljust(20, b"\0")
        k1 = hmac.digest(chp, padded + entry, "sha1")
        tk = hmac.digest(chp, padded, "sha1")
        k2 = hmac.digest(chp, tk + entry, "sha1")
        stream = k1 + k2
        key, iv = stream[:24], stream[-8:]
        return unpad(
            DES3.new(key, DES3.MODE_CBC, iv).decrypt(octets(cipher)), 8
        ), scheme
    assert scheme == "1.2.840.113549.1.5.13", scheme
    kdf, enc = seq(args)
    kind, params = seq(kdf)
    assert oid(kind) == "1.2.840.113549.1.5.12"
    salt2, count, keysize, prf = seq(params)
    assert keysize == 32 and oid(seq(prf)[0]) == "1.2.840.113549.2.9"
    enc_kind, iv = seq(enc)
    assert oid(enc_kind) == "2.16.840.1.101.3.4.1.42"
    hp = sha1(salt + password).digest()
    key = pbkdf2_hmac("sha256", hp, octets(salt2), count, keysize)
    iv = octets(iv) if len(octets(iv)) == 16 else iv
    assert len(iv) == 16
    return unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(octets(cipher)), 16), scheme


def verify(path):
    with ZipFile(path) as z:
        db_blob = z.read("key4.db")
        login = json.loads(z.read("logins.json"))["logins"][0]
    keyid, alg, cipher = seq(b64decode(login["encryptedPassword"], validate=True))
    kind, iv = seq(alg)
    assert oid(kind) == "1.2.840.113549.3.7"
    with sqlite3.connect(":memory:") as db:
        db.deserialize(db_blob)
        salt, check = db.execute(
            "SELECT item1,item2 FROM metaData WHERE id='password'"
        ).fetchone()
        clear, scheme = unlock_blob(check, salt, b"")
        assert clear == b"password-check"
        (wrapped,) = db.execute(
            "SELECT a11 FROM nssPrivate WHERE a102 = ?", (octets(keyid),)
        ).fetchone()
    key, key_scheme = unlock_blob(wrapped, salt, b"")
    assert len(key) == 24
    answer = unpad(DES3.new(key, DES3.MODE_CBC, octets(iv)).decrypt(octets(cipher)), 8)
    assert re.fullmatch(rb"[A-Za-z0-9_]+\{[^{}\r\n]+\}", answer)
    return {
        "main_password_empty_checked": True,
        "storage_scheme": scheme,
        "key_scheme": key_scheme,
        "key_id_matched": True,
        "login_cipher": "3DES-CBC",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="赛题原 ZIP")
    args = parser.parse_args()
    print(json.dumps(verify(args.file), ensure_ascii=False))
