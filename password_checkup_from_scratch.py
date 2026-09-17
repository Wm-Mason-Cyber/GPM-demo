#!/usr/bin/env python3
"""
Password Checkup, by hand.

Google Password Manager's "compromised password" warning (and Have I Been
Pwned's API, which uses the same trick) needs to answer a touchy question:
"is this password on a public breach list?" -- without ever sending your
actual password, or even its full hash, to a server.

The trick is k-anonymity:
  1. Hash the password (SHA-1, for compatibility with existing breach corpora).
  2. Only send the first 5 hex characters of that hash to the server.
  3. The server sends back every known breached hash that starts with those
     5 characters -- could be hundreds of them -- with no idea which one (if
     any) is actually yours.
  4. You check locally whether your *full* hash is anywhere in that list.

This script plays both roles (client and "server") locally against a tiny
demo breach list, so you can watch every step with nothing hidden.
"""

import hashlib
import time

# A handful of infamous throwaway passwords, pre-hashed, standing in for the
# hundreds of millions of real entries in an actual breach corpus. In real
# life this list lives on Google's / HIBP's servers, not on your machine.
DEMO_BREACH_CORPUS = [
    hashlib.sha1(pw.encode()).hexdigest().upper()
    for pw in [
        "password", "password123", "123456", "123456789", "qwerty",
        "letmein", "admin", "welcome", "monkey", "dragon",
        "iloveyou", "football", "starwars", "trustno1", "sunshine",
    ]
]


def sha1_hex(password: str) -> str:
    return hashlib.sha1(password.encode()).hexdigest().upper()


def server_lookup_by_prefix(prefix: str) -> list[str]:
    """Stands in for a real k-anonymity API call (e.g. HIBP's /range/ endpoint).

    Crucially: the "server" only ever sees `prefix` (5 characters), never the
    full hash and never the password itself.
    """
    return [h for h in DEMO_BREACH_CORPUS if h.startswith(prefix)]


def check_password(password: str) -> bool:
    print(f"\n1. Password entered: {password!r}")

    full_hash = sha1_hex(password)
    print(f"2. SHA-1 hash (computed locally, never leaves this machine):\n   {full_hash}")

    prefix, suffix = full_hash[:5], full_hash[5:]
    print(f"3. Split into prefix / suffix:\n   prefix = {prefix}  (this is ALL that gets sent over the network)\n   suffix = {suffix}")

    time.sleep(0.3)  # pretend that's a network round trip
    candidates = server_lookup_by_prefix(prefix)
    print(f"4. \"Server\" responds with {len(candidates)} hash(es) sharing that prefix:")
    for c in candidates:
        print(f"     {c}")

    breached = full_hash in candidates
    print(f"5. Local check: is our full hash in that list? -> {breached}")
    return breached


def main():
    print(__doc__)
    print("Demo breach corpus (would normally be hundreds of millions of hashes,")
    print("and would normally live on a server, not printed on your screen):")
    for h in DEMO_BREACH_CORPUS:
        print(f"  {h}")

    print("\n" + "=" * 60)
    print("Trying a password that's on a well-known breach list:")
    check_password("dragon")

    print("\n" + "=" * 60)
    print("Trying a password that (probably) isn't:")
    check_password("Tr0mb0ne-Kayak-47!")

    print("\n" + "=" * 60)
    while True:
        try:
            pw = input("\nType a password to check (Ctrl+C to quit): ")
        except (EOFError, KeyboardInterrupt):
            print("\nbye!")
            break
        result = check_password(pw)
        print("\n>>> COMPROMISED -- appears in the demo breach list! <<<" if result
              else "\n>>> Not found in the demo breach list. <<<")


if __name__ == "__main__":
    main()
