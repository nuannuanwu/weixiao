"""SMTP email backend class."""
import smtplib
import socket
import threading

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.utils import DNS_NAME
from django.core.mail.message import sanitize_address


class EmailBackend(BaseEmailBackend):
    """
    A wrapper that manages the SMTP network connection.
    """
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, **kwargs):
        super(EmailBackend, self).__init__(fail_silently=fail_silently)
        self.host = host or settings.EMAIL_HOST
        self.port = port or settings.EMAIL_PORT
        if username is None:
            self.username = settings.EMAIL_HOST_USER
        else:
            self.username = username
        if password is None:
            self.password = settings.EMAIL_HOST_PASSWORD
        else:
            self.password = password
        if use_tls is None:
            self.use_tls = settings.EMAIL_USE_TLS
        else:
            self.use_tls = use_tls
        self.connection = None
        self._lock = threading.RLock()



    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        if not email_messages:
            return
        self._lock.acquire()
        try:
            num_sent = 0
            for message in email_messages:
                sent = self._send(message)
                if sent:
                    num_sent += 1
        finally:
            self._lock.release()
        return num_sent

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False
        from_email = sanitize_address(email_message.from_email, email_message.encoding)
        recipients = [sanitize_address(addr, email_message.encoding)
                      for addr in email_message.recipients()]
        #print from_email,recipients,"================"
        #print email_message.message().as_string(),"dddddd"
        try:
            #from sae.mail import send_mail
            #send_mail(recipients, "invite", "to tonight's party"
            #          (self.host, self.port, self.username, self.password, self.use_tls))

            from sae.mail import EmailMessage

            m = EmailMessage()
            m.to = recipients
            m.subject = email_message.subject
            m.html = email_message.body
            m.smtp = (self.host, self.port, self.username, self.password, self.use_tls)
            m.send()

            #self.connection.sendmail(from_email, recipients,email_message.message().as_string())
        except:
            if not self.fail_silently:
                raise
            return False
        return True
