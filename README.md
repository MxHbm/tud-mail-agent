# Mail Agent

Sends success and error notification mails (e.g. at the end of an experiment) via SMTP with STARTTLS.
The default server is the TU Dresden server (`msx.tu-dresden.de:587`); every send function accepts
`smtp_server` / `smtp_port` for another one.

## Use it in another project

Requires Python >= 3.11. Pin a release tag, so every project stays on a known version:

```bash
pip install "mail-agent @ git+https://github.com/MxHbm/tud-mail-agent.git@v0.2.0"
# or in a poetry project
poetry add "git+https://github.com/MxHbm/tud-mail-agent.git#v0.2.0"
```

In a `requirements.txt`: `mail-agent @ git+https://github.com/MxHbm/tud-mail-agent.git@v0.2.0`

## Credentials

The agent needs two variables, `TUD_MAIL_USERNAME` and `TUD_MAIL_PASSWORD`. Provide them either as
environment variables or in an env file.

### Option A: environment variables (no file)

Set them in the shell that starts your program. They only live in that shell session.

PowerShell:

```powershell
$env:TUD_MAIL_USERNAME = "your.name@tu-dresden.de"
$env:TUD_MAIL_PASSWORD = [System.Net.NetworkCredential]::new("", (Read-Host -AsSecureString "Password")).Password
```

bash / zsh:

```bash
export TUD_MAIL_USERNAME="your.name@tu-dresden.de"
read -rs -p "Password: " TUD_MAIL_PASSWORD && export TUD_MAIL_PASSWORD; echo
```

Windows cmd:

```bat
set TUD_MAIL_USERNAME=your.name@tu-dresden.de
set TUD_MAIL_PASSWORD=your_password
```

The PowerShell and bash password lines prompt for the password, so it doesn't end up in your shell
history. To set the variables permanently for your user (applies to newly opened terminals):

```powershell
# Windows (PowerShell)
[Environment]::SetEnvironmentVariable("TUD_MAIL_USERNAME", "your.name@tu-dresden.de", "User")
[Environment]::SetEnvironmentVariable("TUD_MAIL_PASSWORD", "your_password", "User")
```

```bash
# Linux / macOS: add to ~/.bashrc or ~/.zshrc
export TUD_MAIL_USERNAME="your.name@tu-dresden.de"
export TUD_MAIL_PASSWORD="your_password"
```

Note that permanently stored variables are kept in plain text (Windows registry or your shell profile).

### Option B: env file

```env
TUD_MAIL_USERNAME=your.name@tu-dresden.de
TUD_MAIL_PASSWORD=your_password
```

**Never commit this file** (put `*.env` into your `.gitignore`).

### Lookup order

**Without `credentials_file`** (recommended), the credentials are taken from the first of:

1. the environment variables `TUD_MAIL_USERNAME` / `TUD_MAIL_PASSWORD`, if both are set
2. the file named in the environment variable `MAIL_AGENT_CREDENTIALS`
3. `credentials.env` in the current working directory
4. `~/.mail_agent/credentials.env`

**With `credentials_file=...`**, only that file is used and it **must exist**, even if both environment
variables are set. A relative path is resolved against the current working directory.

In both cases, variables that are already set in the environment take precedence over values in the
file. If a variable is still missing after loading, `MailError` is raised.

## Usage

```python
import traceback
from mail_agent import send_success_message, send_error_message, MailError

try:
    run_experiment()
    send_success_message("your.name@tu-dresden.de", experiment_name="My Experiment")
except Exception:
    send_error_message("your.name@tu-dresden.de", error_text=traceback.format_exc(),
                       experiment_name="My Experiment")
```

Both functions also accept `additional_text` (appended to the body), `individual_subject` (replaces the
default subject) and `credentials_file`. If a mail cannot be sent, `MailError` is raised with the cause
(login, TLS, DNS, connection, ...). Catch it if a failed notification must not stop your program.

Send a test mail from the command line:

```bash
python -m mail_agent your.name@tu-dresden.de --credentials path/to/credentials.env
```

## Development

```bash
git clone https://github.com/MxHbm/tud-mail-agent.git
cd tud-mail-agent
poetry install --extras test      # or: pip install -e ".[test]"
pytest
```

To work on the agent while using it in another project, install your clone editable into that
project's environment (`pip install -e path/to/tud-mail-agent`); changes apply immediately.

## Changes in 0.2.0

- Installable package (`package-mode = false` removed), imports work from anywhere.
- Errors raise `MailError` instead of `SystemExit`, so a failed mail no longer ends the caller's program.
- `get_tud_credentials(credentials_file=...)` replaces the `env_dir` / `credentials_file` pair; credentials are
  also read from environment variables and standard locations (see above).
- SMTP server and port can be passed to every send function.
- `main.py` replaced by `python -m mail_agent <receiver>`.
