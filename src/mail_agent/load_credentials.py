"""Load Credentials

Loads the mail-account credentials, so they can be used to log in to the SMTP server.

The credentials are taken from the environment variables ``TUD_MAIL_USERNAME`` and
``TUD_MAIL_PASSWORD``. If they are not set, they are loaded from the first existing env file of:

    1. the file passed as ``credentials_file``
    2. the file named in the environment variable ``MAIL_AGENT_CREDENTIALS``
    3. ``credentials.env`` in the current working directory
    4. ``~/.mail_agent/credentials.env``

The env file is expected to define::

    TUD_MAIL_USERNAME=<your mail account / username>
    TUD_MAIL_PASSWORD=<your password>

Never commit this file (add ``*.env`` to your .gitignore).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from .errors import MailError

CREDENTIALS_PATH_ENV_VARIABLE = "MAIL_AGENT_CREDENTIALS"
DEFAULT_FILE_NAME = "credentials.env"


def _candidate_files(credentials_file: Path | None) -> list[Path]:
    if credentials_file is not None:
        return [Path(credentials_file)]
    candidates = []
    if os.getenv(CREDENTIALS_PATH_ENV_VARIABLE):
        candidates.append(Path(os.environ[CREDENTIALS_PATH_ENV_VARIABLE]))
    candidates.append(Path.cwd() / DEFAULT_FILE_NAME)
    candidates.append(Path.home() / ".mail_agent" / DEFAULT_FILE_NAME)
    return candidates


def get_tud_credentials(
    credentials_file: Path | None = None,
    mail_account_env_variable: str = "TUD_MAIL_USERNAME",
    password_env_variable: str = "TUD_MAIL_PASSWORD",
) -> tuple[str, str]:
    """Return ``(sender_email, password)``.

    Parameters
    ----------
    credentials_file : pathlib.Path, optional
        Env file to load. If given, only this file is used (see module docstring for the search order otherwise).
    mail_account_env_variable : str, optional
        Name of the variable holding the mail account / username.
    password_env_variable : str, optional
        Name of the variable holding the password.

    Raises
    ------
    MailError
        If no env file is found or a variable is missing after loading.

    Examples
    --------
    >>> sender_email, password = get_tud_credentials()
    >>> sender_email, password = get_tud_credentials(Path.home() / "secrets" / "mail.env")
    """

    def from_environment():
        return os.getenv(mail_account_env_variable), os.getenv(password_env_variable)

    sender_email, password = from_environment()
    if credentials_file is None and sender_email and password:
        return sender_email, password

    candidates = _candidate_files(credentials_file)
    env_file = next((c for c in candidates if c.is_file()), None)
    if env_file is None:
        raise MailError("No credentials file found, searched: " + ", ".join(str(c) for c in candidates))

    # Variables that are already set in the process environment are not overwritten
    load_dotenv(env_file)

    sender_email, password = from_environment()
    for name, value in ((mail_account_env_variable, sender_email), (password_env_variable, password)):
        if not value:
            raise MailError(f"Variable {name} is missing in {env_file}")

    return sender_email, password
