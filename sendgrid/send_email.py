# Using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
import argparse
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Email configuration
class EmailConfig:
    def __init__(self, api_key: str):
        self.api_key = api_key

# Email sender using SendGrid
class SendGridEmailSender:
    def __init__(self, config: EmailConfig):
        self.config = config
        self.client = SendGridAPIClient(self.config.api_key)

    def send_email(self, from_email: str, to_emails: list, subject: str, content: str):
        """Sends an email using the SendGrid API"""
        # Create the email object
        message = Mail(
            from_email=from_email,
            to_emails=to_emails,
            subject=subject,
            html_content=content
        )
        
        try:
            # Send the email
            response = self.client.send(message)
            print(f"Email sent! Status code: {response.status_code}")
            return response
        except Exception as e:
            print(f"Failed to send email: {e}")
            return None

# Usage example
if __name__ == "__main__":
    # Configure API key from environment variable
    api_key = os.getenv('SENDGRID_API_KEY')
    email_config = EmailConfig(api_key)

    # Initialize email sender
    email_sender = SendGridEmailSender(email_config)

    # Send an email
    # Get the from and to email addresses from the arguments introduced by the user when running the script
    parser = argparse.ArgumentParser(description="Send an email to a recipient using SendGrid.")
    parser.add_argument('from_email', type=str, help="The email address of the sender.")
    parser.add_argument('to_email', type=str, help="The email address of the recipient.")
    args = parser.parse_args()

    subject = "Hello from rettX"
    content = "<p>This is a test email sent using SendGrid API.</p>"

    email_sender.send_email(args.from_email, [args.to_email], subject, content)
