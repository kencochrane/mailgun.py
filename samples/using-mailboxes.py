from mailgun import *

def main():
    Mailgun.init("key-afy6amxoo2fnj$u@mc")

    m = Mailbox.make_new(user = "new1", domain = "samples.mailgun.org", password = "123123")
    m.upsert()
    
    m.password = "123456"
    m.upsert()

    Mailbox.upsert_from_csv("up1@%s, abc123\nup2@%s, 321bca"%("samples.mailgun.org","samples.mailgun.org"))
    print "Mailboxes:"
    print ",\n".join(["%s@%s %s" % (m.user, m.domain, m.size) for m in Mailbox.find()])

if __name__ == "__main__":    
    main()
