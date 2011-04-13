from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from email.parser import FeedParser
from os.path import abspath, join
from uuid import uuid4


# POST http://host.com/upload
# with newer versions of django, if you do not put CSRF exempt on this, 
# you will get a HTTP 403: Forbidden, since MailGun doesn't send CSRF Token.
@csrf_exempt
def upload(request):
    """
    This callback receives parsed email message via HTTP POST

    All text values are guaranteed to be in UTF-8 regardless of the original encoding
    the message was sent in. This is nice.

    POST parameters are:
        sender 
        recipient 
        subject
        body-plain   [optional]
        body-html    [optional]
        
    Also available: (Not sure if they are always there)
        X-Mailgun-Sid
        Received
        Message-Id
        from
        Subject (Yes both subject and Subject)
        To
        Dkim-Signature
        Date
        From
        DomainKey-Signature
    
    There may be variable number of attachments. They will be posted as uploaded
    files under "attachment-1", "attachment-2"..."attachment-N"
    """
    if request.method == 'POST':
        sender    = request.POST.get('sender')
        recipient = request.POST.get('recipient')
        subject   = request.POST.get('subject', '')
        
        body_html  = request.POST.get('body-html', '')
        body_plain = request.POST.get('body-plain', '')

        for key in request.FILES:
            file = request.FILES[key]
            # do_something_cool_with(file)

    # Returned text is ignored but HTTP status code matters: 
    # Mailgun wants to see 200, otherwise it will make another attempt
    return HttpResponse('OK')


# POST http://host.com/upload_mime
# with newer versions of django, if you do not put CSRF exempt on this, 
# you will get a HTTP 403: Forbidden, since MailGun doesn't send CSRF Token.
@csrf_exempt
def upload_mime(request):
    """
    This callback receives raw MIME messages. 
    Why? Because the URL ends with 'mime'

    POST parameters are:
        'sender'    
        'recipient'
        'body-mime'

    MIME is a raw message which can be saved into an .msg or .eml file, parsed
    with Python's MIME parser, etc

    Use callbacks like this when you want to have full control over messages,
    for example when you need access to all original MIME headers, etc
    """
    if request.method == 'POST':
        sender    = request.POST.get('sender', None)
        recipient = request.POST.get('recipient', None)
        body_mime = request.POST.get('body-mime', None)

        # Simplistic MIME parsing:
        parser = FeedParser()
        parser.feed(body_mime)
        message = parser.close()

    # Returned text is ignored but HTTP status code matters: 
    # Mailgun wants to see 200, otherwise it will make another attempt
    return HttpResponse('OK')
