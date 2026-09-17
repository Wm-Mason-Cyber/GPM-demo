# Google Password Manager 101

A companion to [totp-demo](https://github.com/Wm-Mason-Cyber/totp-demo):
built for classroom demos, this time about what happens when Chrome offers
to save, generate, or autofill a password. Two parts, use whichever fits
the lesson:

1. **`password_checkup_from_scratch.py`** -- a single file, zero
   dependencies, that implements the k-anonymity trick behind Google
   Password Manager's "this password has appeared in a data breach"
   warning (the same technique Have I Been Pwned uses) and prints every
   intermediate value. Best for explaining *how a service can check your
   password against a breach list without ever learning your password*.
2. **`webapp/`** -- two tiny, independent Flask sites ("Nimbus Bank" and
   "Pixel Outfitters") that behave like real websites as far as your
   browser is concerned. Best for actually *practicing* with Google
   Password Manager in a real Chrome browser: saving a password, using
   the generated-password suggestion, autofill, and updating a saved
   entry.

## Quick start: the algorithm

```bash
python3 password_checkup_from_scratch.py
```

Prints a small demo "breach corpus," walks through checking one known-bad
password and one probably-fine password step by step, then lets you type
in your own passwords to check interactively.

## Quick start: the web app

You'll want a real desktop Chrome browser, signed into a Google account,
with Google Password Manager enabled (Settings -> Autofill and passwords).

```bash
cd webapp
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run_both.py
```

This starts **two separate sites at once**:

- Nimbus Bank -- http://localhost:5000
- Pixel Outfitters -- http://localhost:5001

Try this flow:

1. Go to Nimbus Bank, click **Sign up**, and click into the password field
   -- Chrome should offer a **suggested strong password** (key icon).
   Use it, submit the form, and accept the **"Save password?"** prompt.
2. Log out, then log back in -- Chrome should **autofill** the form.
3. Visit Pixel Outfitters and try to log in. Nothing autofills, and
   Password Manager won't offer your Nimbus Bank credentials here either
   -- saved passwords are scoped to the exact site they came from.
4. Sign up on Pixel Outfitters using a weak password like `password123`.
   The dashboard will flag it as a demo "breached password," and Password
   Manager itself may separately flag it in
   `chrome://settings/passwords` under Password Checkup.
5. Go to **Change password** on either site and set a new one -- Chrome
   should offer to **update** the saved entry instead of creating a new
   one.

### Or with Docker

```bash
cd webapp
docker compose up --build
```

Same two sites, one container each.

### Running one site at a time

```bash
cd webapp
python app.py bank   # http://localhost:5000
python app.py shop   # http://localhost:5001
```

## What to point out in class

- **Saved passwords are scoped to the origin** (scheme + host + port), not
  just the domain name. That's *why* the two demo sites don't share
  autofill even though they're both on `localhost` -- and it's also why a
  phishing site at a look-alike domain can never trigger autofill of your
  real credentials. Autofill silence is a phishing tell.
- **The generated password Chrome suggests is random and long on
  purpose.** It's meant to be used once, saved, and never memorized --
  that's the whole model Password Manager is optimizing for, versus
  reusing a password you can remember.
- **Encryption and sync happen after the fact, tied to your Google
  account.** This demo has no such thing -- passwords are hashed
  (`werkzeug.security.generate_password_hash`, not reversible) but live
  in a plain Python dict in memory and vanish when the process stops.
  Real Password Manager entries are encrypted and synced across your
  signed-in devices.
- **Password Checkup never learns your actual password**, even though it
  can tell you it's been breached. `password_checkup_from_scratch.py`
  shows exactly why: only a 5-character hash prefix ever leaves your
  device, and the "server" replies with every hash sharing that prefix,
  not just yours.
- **Passwords are being phased toward passkeys.** Google Password Manager
  also stores passkeys now, which use public-key cryptography instead of
  a shared secret -- there's nothing to breach on the server side because
  the server never had a secret to leak in the first place. This demo
  doesn't implement passkeys/WebAuthn, but it's a good discussion prompt:
  *why can't a passkey be phished the way a password can?*
- **This demo is intentionally simplified**: no HTTPS, no rate limiting,
  no real persistence, and a toy 10-password "breach list" instead of a
  real corpus. Good discussion prompt: *what's missing before a signup
  page like this could go live?*
