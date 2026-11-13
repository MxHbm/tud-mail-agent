"""Send Notification Mails

Sends success and error notification mails (e.g. at the end of an
experiment) through the TUD SMTP server, using STARTTLS and the
credentials loaded by `load_credentials.get_tud_credentials`.

This file can be imported as a module and contains the following
functions:

    * send_success_message - sends a mail reporting a successful run
    * send_error_message - sends a mail reporting an error
    * send_message - sends any prepared `EmailMessage`
"""

import smtplib
import socket
import ssl
import truststore

from load_credentials import get_tud_credentials
from smtp_server_globals import SMTP_PORT, SMTP_SERVER
from message_creator import create_error_message, create_success_message, EmailMessage


def send_success_message(receiver_email: str,
                         experiment_name: str = "Test",
                         additional_text: str = "",
                         individual_subject: str = ""
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
    """
    sender_email, password = get_tud_credentials()

    success_message = create_success_message(sender_email, receiver_email, experiment_name, individual_subject, additional_text)

    send_message(success_message)


def send_error_message(receiver_email: str,
                       error_text: str,
                       experiment_name: str = "Test",
                       additional_text: str = "",
                       individual_subject: str = ""
                       ) -> None:
    """Send an error notification.

    Parameters
    ----------
    receiver_email : str
        Address the mail is sent to.
    experiment_name : str, optional
        Name of the experiment shown in the mail. Defaults to ``"Test"``.
    error_text : str
        Description of the error (e.g. the traceback).
    additional_text : str, optional
        Extra text appended to the mail body.
    individual_subject : str, optional
        Custom subject; if empty, the default subject is used.
    """
    sender_email, password = get_tud_credentials()

    error_message = create_error_message(sender_email, receiver_email, experiment_name, error_text, individual_subject, additional_text)

    send_message(error_message)


def send_message(messsage: EmailMessage) -> None:
    """Send a prepared mail via the TUD SMTP server.

    Connects to ``SMTP_SERVER:SMTP_PORT``, upgrades the connection with
    STARTTLS, logs in and sends the message.

    Parameters
    ----------
    messsage : EmailMessage
        The fully built message (recipient, subject and body set).

    Raises
    ------
    SystemExit
        If login, TLS, the connection or sending fails; the exit message
        describes the cause.
    """
    sender_email, password = get_tud_credentials()

    #Fetch missing roots automatically!
    context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.starttls(context=context)
            server.login(sender_email, password)
            server.send_message(messsage)

    except smtplib.SMTPAuthenticationError as e:
        # Wrong username/password, or the account needs an app password
        raise SystemExit(f"Login failed ({e.smtp_code}): {e.smtp_error!r}") from e

    except smtplib.SMTPNotSupportedError as e:
        # Server doesn't offer STARTTLS on this port
        raise SystemExit(f"STARTTLS not supported on {SMTP_SERVER}:{SMTP_PORT}") from e

    except smtplib.SMTPRecipientsRefused as e:
        # All recipients rejected
        raise SystemExit(f"All recipients refused: {e.recipients}") from e

    except smtplib.SMTPSenderRefused as e:
        # Server won't accept mail from this sender address
        raise SystemExit(f"Sender {e.sender} refused: {e.smtp_error!r}") from e

    except smtplib.SMTPException as e:
        # Any other SMTP-level problem (disconnects, data errors, ...)
        raise SystemExit(f"SMTP error: {e}") from e

    except ssl.SSLError as e:
        # TLS handshake failed, e.g. WRONG_VERSION_NUMBER (port/protocol mismatch) or certificate problems
        raise SystemExit(f"TLS error, check port/protocol: {e}") from e

    except socket.gaierror as e:
        # DNS: hostname can't be resolved (typo, no network)
        raise SystemExit(f"Cannot resolve host {SMTP_SERVER}") from e

    except (TimeoutError, ConnectionRefusedError) as e:
        # Firewall, VPN, wrong port, server down
        raise SystemExit(f"Cannot connect to {SMTP_SERVER}:{SMTP_PORT}: {e}") from e