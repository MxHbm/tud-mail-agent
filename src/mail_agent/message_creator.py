"""Message Creator

Builds the success and error notification mails sent by `email_agent`.

This file can be imported as a module and contains the following
functions:

    * create_success_message - builds a mail reporting a successful run
    * create_error_message - builds a mail reporting an error
"""

from email.message import EmailMessage


def _build_message(sender_email: str, receiver_email: str, subject: str, body: str) -> EmailMessage:
    """Create an `EmailMessage` with recipient, subject and plain-text body."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(body)
    return msg


def create_success_message(sender_email: str,
                           receiver_email: str,
                           experiment_name: str,
                           individual_subject: str = "",
                           additional_text: str = "") -> EmailMessage:
    """Build a success notification.

    Parameters
    ----------
    sender_email : str
        Address the mail was sent from.
    receiver_email : str
        Address the mail is sent to.
    experiment_name : str
        Name of the experiment, used in the default subject.
    individual_subject : str, optional
        Custom subject; if empty, a default subject is used.
    additional_text : str, optional
        Extra text appended to the mail body.
    """
    subject = individual_subject or f"Successful run of experiment {experiment_name}"
    body = f"All experiments of {experiment_name} ran successfully!"
    if additional_text:
        body += f"\n\n{additional_text}"

    return _build_message(sender_email, receiver_email, subject, body)


def create_error_message(sender_email: str,
                         receiver_email: str,
                         experiment_name: str,
                         error_text: str,
                         individual_subject: str = "",
                         additional_text: str = "") -> EmailMessage:
    """Build an error notification.

    Parameters
    ----------
    sender_email : str
        Address the mail was sent from.   
    receiver_email : str
        Address the mail is sent to.
    experiment_name : str
        Name of the experiment, used in subject and body.
    error_text : str
        Description of the error (e.g. the traceback).
    individual_subject : str, optional
        Custom subject; if empty, a default subject is used.
    additional_text : str, optional
        Extra text appended to the mail body.
    """
    subject = individual_subject or f"Error occurred during experiment {experiment_name}"
    body = f"An error occurred during experiment {experiment_name}:\n\n{error_text}"
    if additional_text:
        body += f"\n\n{additional_text}"

    return _build_message(sender_email, receiver_email, subject, body)