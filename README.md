# Mail Agent

Sends success and error notification mails (e.g. at the end of an experiment) via the TU Dresden SMTP server (`msx.tu-dresden.de:587`, STARTTLS).

## Installation

Requires Python >= 3.11 and [Poetry](https://python-poetry.org/).

```bash
cd mail-agent
poetry env use 3.11
poetry install
source .venv/bin/activate
```

## Sending a mail

**First create the file `src/mail_agent/credentials.env`** with your TUD mail credentials:

```env
TUD_MAIL_USERNAME=your.name@tu-dresden.de
TUD_MAIL_PASSWORD=your_password
```

This file is ignored by git (`*.env`), so it stays out of the repo. If you want to use a different file or location, pass it to `get_tud_credentials(env_dir=..., credentials_file=...)` in `load_credentials.py`.

Then send a test mail (set the recipient in `main.py` first):

```bash
cd src/mail_agent
python main.py
```

## Usage in your own project

1. Copy `email_agent.py`, `message_creator.py`, `load_credentials.py`, `smtp_server_globals.py` and your `credentials.env` together into **one folder** of your project.
2. Install the dependency there: `poetry add python-dotenv`.
3. Import the functions and start notifying yourself:

```python
from email_agent import send_success_message, send_error_message

try:
    run_experiment()
    send_success_message("your.name@tu-dresden.de", experiment_name="My Experiment")
except Exception:
    import traceback
    send_error_message("your.name@tu-dresden.de", error_text=traceback.format_exc(),
                       experiment_name="My Experiment")
```

Both functions also accept `additional_text` (appended to the body) and `individual_subject` (replaces the default subject).
