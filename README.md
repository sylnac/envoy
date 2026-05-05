# envoy

> Lightweight .env file manager with per-project profiles and secret diffing

---

## Installation

```bash
pip install envoy-env
```

Or with [pipx](https://pypa.github.io/pipx/) for isolated installs:

```bash
pipx install envoy-env
```

---

## Usage

```bash
# Initialize envoy in your project
envoy init

# Create a new profile
envoy profile create staging

# Set a secret in the staging profile
envoy set DATABASE_URL postgres://user:pass@host/db --profile staging

# Switch to the staging profile
envoy use staging

# Diff secrets between two profiles
envoy diff staging production

# Run a command with a profile's secrets injected
envoy run --profile staging -- python app.py
```

Profiles are stored locally in `.envoy/` and can be gitignored to keep secrets safe.

---

## Features

- 📁 Per-project environment profiles
- 🔍 Secret diffing between profiles
- 🔒 Simple, file-based secret storage
- ⚡ Zero-dependency core

---

## License

MIT © [envoy contributors](LICENSE)