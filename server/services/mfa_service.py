"""
TOTP Multi-Factor Authentication Service — RiskGuard Pro
Implements RFC 6238 Time-Based One-Time Password algorithm.
Uses only Python standard library (hmac, hashlib, base64, struct, time, secrets).
Compatible with Google Authenticator, Microsoft Authenticator, 1Password, etc.
"""

import hmac
import hashlib
import time
import base64
import struct
import secrets
from urllib.parse import quote


def generate_totp_secret() -> str:
    """Generate a high-entropy 160-bit Base32 secret for TOTP MFA."""
    raw = secrets.token_bytes(20)
    return base64.b32encode(raw).decode('utf-8').rstrip('=')


def get_totp_provisioning_uri(secret: str, account_email: str, issuer_name: str = "RiskGuard Pro") -> str:
    """
    Generate standard otpauth:// URI for QR code generators and authenticator apps.
    Format: otpauth://totp/Issuer:account?secret=...&issuer=Issuer&digits=6&period=30
    """
    label = quote(f"{issuer_name}:{account_email}")
    issuer = quote(issuer_name)
    return f"otpauth://totp/{label}?secret={secret}&issuer={issuer}&digits=6&period=30"


def generate_totp_code(secret: str, time_step: int = 30) -> str:
    """Calculate the current 6-digit TOTP code for a given Base32 secret."""
    clean_secret = secret.strip().replace(' ', '').upper()
    padding = '=' * ((8 - len(clean_secret) % 8) % 8)
    key = base64.b32decode(clean_secret + padding)

    counter = int(time.time() // time_step)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()

    offset = digest[19] & 15
    binary_code = struct.unpack(">I", digest[offset:offset+4])[0] & 0x7fffffff
    totp = binary_code % 1000000
    return f"{totp:06d}"


def verify_totp_code(secret: str, code: str, window: int = 1, time_step: int = 30) -> bool:
    """
    Validate a user-submitted 6-digit TOTP token against their secret.
    Allows +/- window intervals (default: +/- 1 step of 30 seconds for clock drift).
    """
    if not secret or not code:
        return False

    clean_code = str(code).strip().replace(" ", "").replace("-", "")
    if len(clean_code) != 6 or not clean_code.isdigit():
        return False

    clean_secret = secret.strip().replace(' ', '').upper()
    padding = '=' * ((8 - len(clean_secret) % 8) % 8)
    try:
        key = base64.b32decode(clean_secret + padding)
    except Exception:
        return False

    current_counter = int(time.time() // time_step)

    for offset in range(-window, window + 1):
        msg = struct.pack(">Q", current_counter + offset)
        digest = hmac.new(key, msg, hashlib.sha1).digest()
        idx = digest[19] & 15
        binary_code = struct.unpack(">I", digest[idx:idx+4])[0] & 0x7fffffff
        expected = binary_code % 1000000
        if f"{expected:06d}" == clean_code:
            return True

    return False
