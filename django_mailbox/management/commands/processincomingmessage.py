import email
import logging
import sys
try:
    from email import utils
except ImportError:
    import rfc822 as utils

from django.core.management.base import BaseCommand

from django_mailbox.models import Mailbox


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '-mbox', '--mailbox',
            type=str,
            help='Mailbox name to which Messages will be added to',
        )

    def handle(self, *args, **options):
        message = email.message_from_string(sys.stdin.read())
        mbox = options.get('mailbox')
        if message:
            if mbox:
                mailbox = self.get_mailbox_by_name(mbox)
            else:
                mailbox = self.get_mailbox_for_message(message)
            logger.info(
                "Processing message for %s",
                mailbox.name
            )
            mailbox.process_incoming_message(message)
            logger.info(
                "Message received from %s",
                message['from']
            )
        else:
            logger.warning("Message not processable.")

    def get_mailbox_by_name(self, name):
        mailbox, created = Mailbox.objects.get_or_create(
            name__iexact=name,
        )
        return mailbox

    def get_mailbox_for_message(self, message):
        email_address = utils.parseaddr(message['to'])[1][0:255]
        return self.get_mailbox_by_name(email_address)
