from mailgun import *

def main():
    Mailgun.init("my-api-key")

    m = Mailbox.make_new(user = "new1", domain = "myhost.com", password = "123123")
    m.upsert()
    
    m.password = "123456"
    m.upsert()

    Mailbox.upsert_from_csv("up1@{domain}, abc123\nup2@{domain}, 321bca".format(domain = "myhost.com"))
    print "Mailboxes:"
    print ",\n".join(["{0}@{1} {2}".format(m.user, m.domain, m.size) for m in Mailbox.find()])

if __name__ == "__main__":    
    main()
