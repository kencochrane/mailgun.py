import urllib, urllib2
from pyactiveresource.activeresource import ActiveResource
from pyactiveresource.connection import BadRequest, UnauthorizedAccess, ForbiddenAccess, ResourceNotFound, \
                                        MethodNotAllowed, ResourceConflict, ResourceInvalid, ClientError, ServerError,\
                                        Request as _Request, Response as _Response

class Mailgun:
    '''
    Adding a route:
    
    >>> Mailgun.init("api-key-secret")
    >>> route = Route.make_new(pattern = 'me@myhost.com', destination = 'http://myhost/accept_mail')
    >>> route.upsert()

    Sending a simple text message:
    >>> MailgunMessage.send_text("sender@myhost.com", 'recipient@otherhost.com", "Subject", "Body")    

    '''
    @staticmethod
    def init(api_key, api_url = "http://mailgun.net/api/"):
        MailgunResource._set_server_info(api_key, api_url)
    
    @staticmethod
    def _handle_http_error(err):
        # This is a patch of private ActiveResource method.
        # It takes HTTPResponse and raise AR-like error if response code is not 2xx
        """
        Handle an HTTP error.

        Args:
            err: A urllib2.HTTPError object.
        Returns:
            An HTTP response object if the error is recoverable.
        Raises:
            Redirection: if HTTP error code 301,302 returned.
            BadRequest: if HTTP error code 400 returned.
            UnauthorizedAccess: if HTTP error code 401 returned.
            ForbiddenAccess: if HTTP error code 403 returned.
            ResourceNotFound: if HTTP error code 404 is returned.
            MethodNotAllowed: if HTTP error code 405 is returned.
            ResourceConflict: if HTTP error code 409 is returned.
            ResourceInvalid: if HTTP error code 422 is returned.
            ClientError: if HTTP error code falls in 401 - 499.
            ServerError: if HTTP error code falls in 500 - 599.
            ConnectionError: if unknown HTTP error code returned.
        """
        if err.code in (301, 302):
            raise Redirection(err)
        elif 200 <= err.code < 400:
            return err
        elif err.code == 400:
            raise BadRequest(err)
        elif err.code == 401:
            raise UnauthorizedAccess(err)
        elif err.code == 403:
            raise ForbiddenAccess(err)
        elif err.code == 404:
            raise ResourceNotFound(err)
        elif err.code == 405:
            raise MethodNotAllowed(err)
        elif err.code == 409:
            raise ResourceConflict(err)
        elif err.code == 422:
            raise ResourceInvalid(err)
        elif 401 <= err.code < 500:
            raise ClientError(err)
        elif 500 <= err.code < 600:
            raise ServerError(err)
        else:
            raise ConnectionError(err)

        

class MailgunResource(ActiveResource):
    '''
    Base class for Mailgun Resources, subclass of ActiveResource
    Provides additional upsert() method.  
    '''
    _site = "you forgot to call Mailgun.init()"
    
    @classmethod
    def _set_server_info(cls, api_key, api_url):
        cls._user = 'api_key'
        cls._password = api_key
        cls._site = api_url.strip().rstrip('/')
        # HACK: Force resource to recreate connection object with updated site.
        # String below is based on the fact that activeresource.ResourceMeta.connection property
        # caches some object in "_connection" class variable. 
        cls._connection = None

    def upsert(self):
        '''
        Create new resource or update it if resource already exist.
        There are 2 differences between upsert() and save().
        * Upsert does not throw exception if object already exist.
        * Upsert does not load id of the object.
        
        It ensures that resource exists on the server and does not syncronize client object instance.
        In order to modify "upserted" object, you need to find() it first.
        
            route = Route()
            route.pattern = '*@myhost.com'
            route.destination = 'http://myhost.com/addcomment'
            route.upsert()        
        '''
        type(self).post("upsert", self.to_xml())


class Route(MailgunResource):
    '''
    Route represents the basic rule:
    Message for particular recipient R is forwarded to destination D.
    
    A route has 2 properties: 
        * pattern     (applies to recipient address)
        * destination
        
    The pair (pattern, destination) must be unique.
    There are 4 types of patterns:

        * '*' - match all
        * exact string match, case-sensitive. (foo@bar.com)
        * pattern starts with *@ (*@example.com - matches all emails going to example.com)
        * any regular expression
    
    A destination can be:

        * email address. Message, as it is, will be forwarded to the address
        * http URL
    '''
    @classmethod
    def make_new(cls, pattern=None, destination=None):
        return cls(dict(pattern=pattern, destination=destination))


def _post(request):
    request.set_method("POST")
    try:
        response = _Response.from_httpresponse(urllib2.urlopen(request))
    except urllib2.HTTPError, err:
        response = _Response.from_httpresponse(Mailgun._handle_http_error(err))
    return response


class Mailbox(MailgunResource):
    '''
    All mail arriving to email addresses that have mailboxes associated
    will be stored on the server and can be later accessed via IMAP or POP3
    protocols.
    
    Mailbox has several properties:

    alex@gmail.com
     ^      ^
     |      |
    user    domain

    and a password

    user and domain can not be changed for an existing mailbox.

    '''
    @classmethod
    def make_new(cls, user, domain, password):
        return cls(dict(user=user, domain=domain, password=password))

    @classmethod
    def upsert_from_csv(cls, mailboxes):
        '''
        Upsert mailboxes contained in a csv string,
        
        john@domain.com, password
        doe@domain.com, password2         
        '''
        request = _Request("{0}/mailboxes.txt?api_key={1}".format(MailgunResource._site, MailgunResource._password))
        request.add_data(mailboxes)
        request.add_header("Content-Type", "text/plain")
        _post(request)

    
class MailgunMessage:
    '''
    Send messages through Mailgun HTTP gateway, applying routing.
    SMTP sender/recipient specification are in the format most email programs utilize:
        'Foo Bar' <foo@bar.com>  
        "Foo Bar" <foo@bar.com>  
        Foo Bar <foo@bar.com>    
        <foo@bar.com>            
        foo@bar.com          
        
    Recipient list is comma- or semicolon- delimited string of recipients        
    '''
    @classmethod
    def send_raw(cls, sender, recipients, mime_body, servername=''):
        '''
        Sends a raw MIME message
        
        >>> Mailgun.init("api-key-dirty-secret")
        >>> raw_mime = "X-Priority: 1 (Highest)\n"\
                "Content-Type: text/plain;charset=utf-8\n"\
                "Subject: Hello!\n"\
                "\n"\
                "I construct MIME message and send it!"
        >>> MailgunMessage.send_raw("me@myhost.com", "you@yourhost.com", raw_mime)        
        '''
        request = _Request(cls._messages_url('eml', servername))
        request.add_data("{0}\n{1}\n\n{2}".format(sender, recipients, mime_body))
        request.add_header("Content-Type", "text/plain")
        _post(request)
   

    @classmethod
    def send_txt(cls, sender, recipients, subject, text, servername=''):
        '''
        Sends a plain-text message
        
        >>> MailgunMessage.send_text("me@myhost.com",
            "you@yourhost.com",
            "Hello",
            "Hi!\nI am sending the message using Mailgun")          
        '''        
        params = dict(sender=sender, recipients=recipients, subject=subject, body=text)
        request = _Request(cls._messages_url('txt', servername))
        request.add_data(urllib.urlencode(params))
        _post(request)


         
    @staticmethod
    def _messages_url(format, servername=''):
        return "{0}/messages.{2}?api_key={1}&servername={3}".format(
            MailgunResource._site, MailgunResource._password, format, servername)

