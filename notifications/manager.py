import logging
from logging.handlers import TimedRotatingFileHandler
from typing import Dict, Any
from sentry_sdk import capture_exception, init
from sentry_sdk.integrations.logging import LoggingIntegration
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# Create a TimedRotatingFileHandler to rotate logs at midnight
log_handler = TimedRotatingFileHandler(
    "export-logs.log", when="midnight", interval=1, backupCount=15, encoding="utf-8"
)

# Format logs with timestamp
log_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
))
logging.basicConfig(
    level=logging.INFO,
    handlers=[log_handler],
)

LOGGER = logging.getLogger(__name__)

def export_error(config: Dict[str, Any], e: Exception):
    if "DISABLE_TRY_EXCEPT" not in config:
        catch_exception(config, e)
        body = """
                <p>Dear Client,</p>
                <p>We regret to inform you that the <b>export process</b> has been temporarily halted. Our team is actively working to resolve the issue and resume the process promptly.</p>
                <p>Thank you for your patience.</p>             
                """
        subject = "Export Migration Error"
        send_email(config, body, subject)
    else:
        logging.info(f"method export_error {e}")


def send_email(config, body, subject):
    try:
        to_emails = config['RECIPIENT_EMAILS'].split(",")
        logging.info(to_emails)
        message = Mail(
            from_email=config["SENDER_EMAIL"],
            to_emails=to_emails,  # Split recipient emails into a list
            subject=subject,
            html_content=body,
        )
        sg = SendGridAPIClient(config["SENDGRID_API_KEY"])
        sg.send(message)
    except Exception as e:
        capture_exception(e)
        logging.info(f"method send_email {e}")



# explore it
def catch_exception(config: Dict[str, Any], e: Exception):
    sentry_logging = LoggingIntegration(level=logging.ERROR)
    init(dsn=config["DSN"], integrations=[sentry_logging])
    capture_exception(e)
