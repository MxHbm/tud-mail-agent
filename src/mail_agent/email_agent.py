"""Send Notification Mails

Sends success and error notification mails (e.g. at the end of an
experiment) through an SMTP server (default: TU Dresden), using STARTTLS and the
credentials loaded by `load_credentials.get_tud_credentials`.

This file can be imported as a module and contains the following
functions:

    * send_success_message - sends a mail reporting a successful run
    * send_error_message - sends a mail reporting an error
    * send_message - sends any prepared `EmailMessage`

All functions raise `MailError` if the mail cannot be sent.
"""

from pathlib import Path
import smtplib
import socket
import ssl

import truststore

from .errors import MailError
from .load_credentials import get_tud_credentials
from .message_creator import EmailMessage, create_error_message, create_success_message
from .smtp_server_globals import SMTP_PORT, SMTP_SERVER


def send_success_message(receiver_email: str,
                         experiment_name: str = "Test",
                         additional_text: str = "",
                         individual_subject: str = "",
                         credentials_file: Path | None = None,
                         smtp_server: str = SMTP_SERVER,
                         smtp_port: int = SMTP_PORT,
                         ) -> None:
    """Send a success notification for an experiment.

    Parameters
    ----------
    receiver_email : str
        Address the mail is sent to.
    experiment_name : str, optional
        Name of the experiment shown in the mail. Defaults to ``"Test"``.
    additional_text : str, optional
        Extra text appended to the mail body.
    individual_subject : str, optional
        Custom subject; if empty, the default subject is used.
    credentials_file : pathlib.Path, optional
        Env file with the credentials, see `get_tud_credentials`.
    smtp_server, smtp_port : optional
        SMTP server to use, defaults to the TU Dresden server.
    """
    sender_email, password = get_tud_credentials(credentials_file)
    message = create_success_message(sender_email, receiver_email, experiment_name, individual_subject, additional_text)
    _send(message, sender_email, password, smtp_server, smtp_port)


def send_error_message(receiver_email: str,
                       error_text: str,
                       experiment_name: str = "Test",
                       additional_text: str = "",
                       individual_subject: str = "",
                       credentials_file: Path | None = None,
                       smtp_server: str = SMTP_SERVER,
                       smtp_port: int = SMTP_PORT,
                       ) -> None:
    """Send an error notification.

    Parameters
    ----------
    receiver_email : str
        Address the mail is sent to.
    error_text : str
        Description of the error (e.g. the traceback).
    experiment_name : str, optional
        Name of the experiment shown in the mail. Defaults to ``"Test"``.
    additional_text : str, optional
        Extra text appended to the mail body.
    individual_subject : str, optional
        Custom subject; if empty, the default subject is used.
    credentials_file : pathlib.Path, optional
        Env file with the credentials, see `get_tud_credentials`.
    smtp_server, smtp_port : optional
        SMTP server to use, defaults to the TU Dresden server.
    """
    sender_email, password = get_tud_credentials(credentials_file)
    message = create_error_message(sender_email, receiver_email, experiment_name, error_text, individual_subject, additional_text)
    _send(message, sender_email, password, smtp_server, smtp_port)


def send_message(message: EmailMessage,
                 credentials_file: Path | None = None,
                 smtp_server: str = SMTP_SERVER,
                 smtp_port: int = SMTP_PORT) -> None:
    """Send a prepared mail (recipient, subject and body set) via the SMTP server."""
    sender_email, password = get_tud_credentials(credentials_file)
    _send(message, sender_email, password, smtp_server, smtp_port)


def _send(message: EmailMessage, sender_email: str, password: str, smtp_server: str, smtp_port: int) -> None:
    """Connects to ``smtp_server:smtp_port``, upgrades the connection with STARTTLS, logs in and sends."""

    # Uses the certificate store of the operating system, so missing root certificates are fetched automatically
    context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            server.starttls(context=context)
            server.login(sender_email, password)
            server.send_message(message)

    except smtplib.SMTPAuthenticationError as e:
        # Wrong username/password, or the account needs an app password
        raise MailError(f"Login failed ({e.smtp_code}): {e.smtp_error!r}") from e

    except smtplib.SMTPNotSupportedError as e:
        # Server doesn't offer STARTTLS on this port
        raise MailError(f"STARTTLS not supported on {smtp_server}:{smtp_port}") from e

    except smtplib.SMTPRecipientsRefused as e:
        # All recipients rejected
        raise MailError(f"All recipients refused: {e.recipients}") from e

    except smtplib.SMTPSenderRefused as e:
        # Server won't accept mail from this sender address
        raise MailError(f"Sender {e.sender} refused: {e.smtp_error!r}") from e

    except smtplib.SMTPException as e:
        # Any other SMTP-level problem (disconnects, data errors, ...)
        raise MailError(f"SMTP error: {e}") from e

    except ssl.SSLError as e:
        # TLS handshake failed, e.g. WRONG_VERSION_NUMBER (port/protocol mismatch) or certificate problems
        raise MailError(f"TLS error, check port/protocol: {e}") from e

    except socket.gaierror as e:
        # DNS: hostname can't be resolved (typo, no network)
        raise MailError(f"Cannot resolve host {smtp_server}") from e

    except (TimeoutError, ConnectionRefusedError) as e:
        # Firewall, VPN, wrong port, server down
        raise MailError(f"Cannot connect to {smtp_server}:{smtp_port}: {e}") from e
