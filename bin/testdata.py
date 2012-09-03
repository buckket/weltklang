import os
import rfk

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rfk.init(current_dir)
    
    import rfk.site
    from rfk.site import db

    users = []
    users.append(rfk.User('MrLoom', rfk.User.make_password('wegbuxen'), rfk.User.make_password('wegbuxen')))
    users.append(rfk.User('teddydestodes', rfk.User.make_password('drama'), rfk.User.make_password('queen')))
    users.append(rfk.User('kawaiidesu', rfk.User.make_password('uguuu'), rfk.User.make_password('uguuu')))
    users.append(rfk.User('baffbuff', rfk.User.make_password('baff'), rfk.User.make_password('buff')))
    for user in users:
        db.session.add(user)
        print "[users] Added %s" % user.name
    db.session.commit()
    
    news = []
    news.append(rfk.News(rfk.User.get_user(db.session, 'MrLoom').get_id(), 'Hallo Welt', 'Hallo Loom'))
    news.append(rfk.News(rfk.User.get_user(db.session, 'teddydestodes').get_id(), 'Ich', 'ausversehen'))
    for newz in news:
        db.session.add(newz)
        print "[news] Added news from user %s" % newz.user
    db.session.commit()
        
    key = rfk.ApiKey(rfk.User.get_user(db.session, 'MrLoom').get_id(), 'Testo')
    key.gen_key(db.session)
    db.session.add(key)
    db.session.commit()
    print "[apikeys] Added key %s for user %s" % (key.key, key.user)
    