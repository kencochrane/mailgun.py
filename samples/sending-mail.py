#coding: utf-8
"""
Example of how to send email messages over HTTP using Mailgun API
"""        
from mailgun import *
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from os.path import join


def send_text_message():
    "Sending a simple text message"
    MailgunMessage.send_txt("me@samples.mailgun.org", 
                            "you@mailgun.info, him@mailgun.info",
                            "Hello text Python API!",
                            "Hi!\nI am sending you a text message through HTTP gateway!")

    #tag the message
    MailgunMessage.send_txt("me@samples.mailgun.org", 
                            "you@mailgun.info, him@mailgun.info",
                            "Hello text Python API + tag!",
                            "Hi!\nI am sending you a text message through HTTP gateway!",
                            "",
                            {"headers": {MailgunMessage.MAILGUN_TAG: "sample_text_python"}})


def send_mime_message_with_attachments():
    """
    Sending using Python's MIME libraries to construct a 
    message with attachments:
    """
    msg = MIMEMultipart()
    msg['Subject'] = 'See info attached'
    msg['From'] = "me@samples.mailgun.org"
    msg['To'] = "you@mailgun.info"
    msg[MailgunMessage.MAILGUN_TAG] = 'sample_raw_python'

    #some cool images from
    #Adam Hickmott / FreeDigitalPhotos.net
    #Christian Meyn / FreeDigitalPhotos.net
    for file in ['attachment-1.jpg', 'attachment-2.jpg']:
        attach = MIMEBase("application", "octet-stream")
        fp = open(join('samples', 'files', file), 'rb')
        attach.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attach)
        attach.add_header('Content-Disposition', 'attachment', filename=file)
        msg.attach(attach)

    raw_mime = msg.as_string()
    MailgunMessage.send_raw(msg['From'], msg['To'], raw_mime)


def main():
    # Initialize Mailgun API before making calls:
    Mailgun.init("key-afy6amxoo2fnj$u@mc")
    send_text_message()
    send_mime_message_with_attachments()
    print "Messages were successfully sent"


if __name__ == "__main__":
    main()
