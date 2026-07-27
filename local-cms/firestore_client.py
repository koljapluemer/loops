"""Firebase Admin SDK init. Admin credentials bypass firestore.rules, which
is why this only ever runs locally, never in the deployed static site."""

from __future__ import annotations

import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

_HERE = Path(__file__).resolve().parent


def _key_path() -> Path:
    env = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    return Path(env) if env else _HERE / "service-account.json"


def get_db():
    if not firebase_admin._apps:
        key_path = _key_path()
        if not key_path.exists():
            raise FileNotFoundError(
                f"Missing Firebase service account key at {key_path}.\n"
                "See FIREBASE_SETUP.md for how to generate one, or set "
                "FIREBASE_SERVICE_ACCOUNT to point at your key file."
            )
        cred = credentials.Certificate(str(key_path))
        firebase_admin.initialize_app(cred)
    return firestore.client()
