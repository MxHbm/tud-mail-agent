"""Load Credentials Script

This script loads mail-account credentials from an environment file so
they can be used to log in to the TUD mail server.

The credentials are read from a ``credentials.env`` file (by default
located in the same directory as this script) that is expected to define
the following variables::

    TUD_MAIL_USERNAME=<your mail account / username>
    TUD_MAIL_PASSWORD=<your password>

This script requires that `python-dotenv` (which provides
``load_dotenv``) be installed within the Python environment you are
running this script in.

This file can also be imported as a module and contains the following
functions:

    * get_tud_credentials - returns the mail account and password loaded
      from the environment file
"""

import os
from pathlib import Path

from dotenv import load_dotenv


def get_tud_credentials(
    env_dir: Path = Path(__file__).parents[0],
    credentials_file: str = "credentials.env",
    mail_account_env_variable: str = "TUD_MAIL_USERNAME",
    password_env_variable: str = "TUD_MAIL_PASSWORD",
) -> tuple[str, str]:
    """Load the TUD mail credentials from an environment file.

    Reads ``env_dir / credentials_file`` with ``load_dotenv`` and returns
    the values of the mail-account and password variables. Variables that
    are already set in the process environment are not overwritten
    (default ``load_dotenv`` behaviour).

    Parameters
    ----------
    env_dir : pathlib.Path, optional
        Directory containing the environment file. Defaults to the
        directory this script is located in.
    credentials_file : str, optional
        File name of the environment file inside ``env_dir``.
        Defaults to ``"credentials.env"``.
    mail_account_env_variable : str, optional
        Name of the variable holding the mail account / username.
        Defaults to ``"TUD_MAIL_USERNAME"``.
    password_env_variable : str, optional
        Name of the variable holding the password.
        Defaults to ``"TUD_MAIL_PASSWORD"``.

    Returns
    -------
    tuple[str, str]
        ``(sender_email, password)`` as read from the environment.

    Raises
    ------
    OSError
        If ``env_dir`` does not exist, if the environment file could not
        be loaded, or if either variable is missing after loading.
    FileExistsError
        If ``credentials_file`` is not a file inside ``env_dir``.

    Examples
    --------
    >>> sender_email, password = get_tud_credentials()
    >>> sender_email, password = get_tud_credentials(
    ...     env_dir=Path.home() / "secrets",
    ...     credentials_file="mail.env",
    ... )
    """
    credentials_env_path = env_dir / credentials_file

    if not env_dir.exists():
        raise OSError(f"Directory {env_dir} does not exist!")

    if not credentials_env_path.is_file():
        raise FileExistsError(
            f"Credentials file {credentials_file} does not exist in directory {env_dir}!"
        )

    # Load environment variables from the .env file into os.environ
    if not load_dotenv(credentials_env_path):
        raise OSError("Could not load needed environment file!")

    sender_email = os.getenv(mail_account_env_variable)
    if sender_email is None:
        raise OSError(
            f"Environment variable {mail_account_env_variable} was not loaded correctly from .env file"
        )

    password = os.getenv(password_env_variable)
    if password is None:
        raise OSError(
            f"Environment variable {password_env_variable} was not loaded correctly from .env file"
        )

    return sender_email, password