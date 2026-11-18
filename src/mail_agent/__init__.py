"""Send success and error notification mails, e.g. at the end of an experiment."""

from .email_agent import send_error_message, send_message, send_success_message, send_start_message
from .errors import MailError
from .load_credentials import get_tud_credentials
from .message_creator import create_error_message, create_success_message, create_start_message

__version__ = "0.2.0"

__all__ = [
    "MailError", "create_error_message", "create_success_message", "create_start_message", "get_tud_credentials",
    "send_error_message", "send_message", "send_success_message","send_start_message"
]
