import base64
import hashlib
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def canonical_bytes(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def deterministic_test_key(name):
    """Synthetic reproducibility key only. Never use in production."""
    seed = hashlib.sha256(("exp2-seed-42|" + name).encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def sign(signer_name, payload):
    sk = deterministic_test_key(signer_name)
    sig = sk.sign(canonical_bytes(payload))
    return {
        "signer": signer_name,
        "payload": payload,
        "signature_b64": base64.b64encode(sig).decode(),
    }


def verify(attestation, trusted_names):
    signer = attestation.get("signer")
    if signer not in trusted_names:
        return False
    pk = deterministic_test_key(signer).public_key()
    try:
        pk.verify(
            base64.b64decode(attestation["signature_b64"]),
            canonical_bytes(attestation["payload"]),
        )
        return True
    except Exception:
        return False
