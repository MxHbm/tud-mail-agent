"""Main Script

This script is executable to test the email agent!
"""

from email_agent import send_error_message, send_success_message, send_message

def main(): 

    send_success_message("maximilian.hubmann@mailbox.tu-dresden.de",
                         "Test_Mail",
                         "This mail was created in main and works as automated test")

if __name__ == '__main__':
    main()