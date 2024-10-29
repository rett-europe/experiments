# How to send emails using SendGrid

1. Install SendGrid Python package

```bash
pip install sendgrid
```

2. Get a API key from SendGrid, and setup an env constant with the API key

```bash
setx SENDGRID_API_KEY "<your API key>"
```

3. Execute the script specifying the from and to emails:

```bash
Python send_email.py <from email> <to email>
```