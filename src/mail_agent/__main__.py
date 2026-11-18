"""Send a test mail: python -m mail_agent <receiver address> [--credentials path/to/credentials.env]"""

import argparse
from pathlib import Path

from .email_agent import send_success_message


def main():
    parser = argparse.ArgumentParser(prog="python -m mail_agent", description="Send a test mail.")
    parser.add_argument("receiver", help="address the test mail is sent to")
    parser.add_argument("--credentials", type=Path, default=None, help="env file with the credentials")
    args = parser.parse_args()

    send_success_message(args.receiver, "Test_Mail",
                         "This mail was sent by 'python -m mail_agent' as a test.",
                         credentials_file=args.credentials)
    print(f"Test mail sent to {args.receiver}")


if __name__ == "__main__":
    main()
