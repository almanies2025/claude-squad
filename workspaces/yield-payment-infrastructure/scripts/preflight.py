#!/usr/bin/env python3
"""
FloatYield — Preflight Check
Verifies backend health, database, and feature flags before Sprint 1.
"""

import sys
import urllib.request
import json
from pathlib import Path


def check_backend_health() -> bool:
    try:
        req = urllib.request.urlopen("http://localhost:8000/health", timeout=5)
        data = json.loads(req.read())
        print(f"  [OK] Backend health: {data}")
        assert data.get("status") == "ok", f"status != ok: {data}"
        assert data.get("feature_store") is True, "feature_store not True"
        return True
    except Exception as e:
        print(f"  [FAIL] Backend health: {e}")
        return False


def check_frontend_serves() -> bool:
    try:
        req = urllib.request.urlopen("http://localhost:3000", timeout=5)
        print(f"  [OK] Frontend serves on :3000 (status {req.status})")
        return True
    except Exception as e:
        print(f"  [FAIL] Frontend not serving: {e}")
        return False


def check_accounts_seed() -> bool:
    try:
        req = urllib.request.urlopen("http://localhost:8000/accounts", timeout=5)
        accounts = json.loads(req.read())
        print(f"  [OK] Accounts endpoint: {len(accounts)} account(s) seeded")
        assert len(accounts) >= 3, f"Expected 3+ accounts, got {len(accounts)}"
        return True
    except Exception as e:
        print(f"  [FAIL] Accounts endpoint: {e}")
        return False


def main():
    print("=== FloatYield Preflight ===")

    backend_ok = check_backend_health()
    accounts_ok = check_accounts_seed() if backend_ok else False
    frontend_ok = check_frontend_serves()

    print()
    if backend_ok and accounts_ok and frontend_ok:
        print("ALL CHECKS PASSED — environment is green")
        sys.exit(0)
    else:
        print("SOME CHECKS FAILED — fix before proceeding")
        sys.exit(1)


if __name__ == "__main__":
    main()
