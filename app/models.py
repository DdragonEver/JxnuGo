# -*- coding: UTF-8 -*-from flask import url_forfrom . import dbfrom flask.ext.login import UserMixin, AnonymousUserMixinfrom werkzeug.security import generate_password_hash, check_password_hashfrom . import login_managerimport randomfrom flask import current_appfrom itsdangerous import TimedJSONWebSignatureSerializer as Serializerfrom dateutil import tzfrom datetime import datetimeclass Permission:    FOLLOW = 0x01    COMMENT = 0x02    WRITE_ARTICLES = 0x04    MODERATE_COMMENTS = 0x08    ADMINISTER = 0x80class Role(db.Model):    __tablename__ = 'roles'    id = db.Column(db.Integer, primary_key=True)   # 角色id    name = db.Column(db.String(64), unique=True)   # 角色名    default = db.Column(db.Boolean, default=False, index=True)   # 默认角色    permissions = db.Column(db.Integer)                    # 角色权限    users = db.relationship('User', backref='role', lazy='dynamic')    # 外键    home = db.Column(db.String(64), unique=True)    @staticmethod    def insert_roles():        roles = {            'User': (Permission.FOLLOW |                     Permission.COMMENT |                     Permission.WRITE_ARTICLES, True),            'Moderator': (Permission.FOLLOW |                          Permission.COMMENT |                          Permission.WRITE_ARTICLES |                          Permission.MODERATE_COMMENTS, False),            'Administrator': (0xff, False)        }        for r in roles:            role = Role.query.filter_by(name=r).first()            if role is None:                role = Role(name=r)            role.permissions = roles[r][0]            role.default = roles[r][1]            db.session.add(role)        db.session.commit()    def __repr__(self):        return '<Role %r>' % self.nameclass Follow(db.Model):        # 关注用户    __tablename__ = 'follows'    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),   # 粉丝id                            primary_key=True)    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),   # 被关注者id                            primary_key=True)    timestamp = db.Column(db.DateTime, default=datetime.now)    def followers_to_json(self):        json_follow={            "userName": User.idChangeToUserName(self.follower_id),            "urlLinkUser": url_for('api.get_user', id=self.follower_id, _external=True),            "userId": self.follower_id,            "userAvatar": User.idChangeToUserAvatar(self.follower_id),            "aboutMe": User.idChangeToUserAbout_me(self.follower_id)        }        return json_follow    def followed_to_json(self):        json_follow={            "userName": User.idChangeToUserName(self.followed_id),            "urlLinkUser": url_for('api.get_user', id=self.followed_id, _external=True),            "userId": self.followed_id,            "userAvatar": User.idChangeToUserAvatar(self.followed_id),            "aboutMe": User.idChangeToUserAbout_me(self.followed_id)        }        return json_follow# 收藏帖子collectionPosts = db.Table('collectionPosts',    db.Column('userId', db.Integer, db.ForeignKey('users.id')),    db.Column('postId', db.Integer, db.ForeignKey('posts.id')),    db.Column('timestamp', db.DateTime, default=datetime.utcnow))class User(UserMixin, db.Model):    __tablename__='users'    id = db.Column(db.Integer, primary_key=True, unique=True)  # 用户id    userName = db.Column(db.String(20), index=True)     # 用户名    userEmail = db.Column(db.String(30))               # 用户邮箱    userPasswordHash = db.Column(db.String(128))      # 用户密码hash值    confirmed = db.Column(db.Boolean, default=False)   # 确认用户是否激活,默认未激活    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # 用户角色,默认为普通用户    name = db.Column(db.String(15))                # 昵称    location = db.Column(db.String(32))           # 位置    sex = db.Column(db.String(10))                # 性别    about_me = db.Column(db.String(64))               # 关于我    contactMe = db.Column(db.String(30))          # 联系方式    avatar = db.Column(db.String(128), default='http://7xrkww.com1.z0.glb.clouddn.com/logo.png')             #用户头像    menber_since = db.Column(db.DateTime(), default=datetime.utcnow)   # 注册时间    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)      # 最后登录时间    posts = db.relationship('Post', backref='author', lazy='dynamic')    # 关键用户发布的帖子    bbsPosts = db.relationship('bbsPost', backref='author', lazy='dynamic')   # 关联用户发布的bbs板块帖子    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id], backref=db.backref('follower', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')  #用户关注的人    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], backref=db.backref('followed', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')  #粉丝id    collectionPost=db.relationship('Post', secondary=collectionPosts, backref=db.backref('users',lazy='dynamic'),                                   lazy='dynamic')  # 收藏的帖子    comments=db.relationship('Comment', backref='author', lazy='dynamic')    def __repr__(self):        return '<User %r>' % self.userName    def to_json(self):        json_user={            'userId': self.id,            'userName': self.userName,            'name': self.name,            'location': judge_empty(self.location, 'location'),            'sex': judge_empty(self.sex, 'sex'),            'about_me': judge_empty(self.about_me, 'about_me'),            'contactMe': judge_empty(self.contactMe, 'contactMe'),            'member_since': utcChangeCst(self.menber_since),            'last_seen': utcChangeCst(self.menber_since),            'followed': self.followed.count(),            'followers': self.followers.count(),            'avatar': self.avatar+'?imageMogr2/thumbnail/800x800',            'postCollectionCount': self.collectionPost.count(),            'postCount': self.posts.count()        }        return json_user    def from_json(json_user):        id = User.query.count()+1        userName = json_post.get('userName')        userEmail = json_post.get('userEmail')        passWord = json_post.get('passWord')        return User(id=id, userName=userName, userEmail=userEmail, passWord=passWord)    def edifInfo_from_json(json_info_post):        name = json_info_post.get('name')        location = json_info_post.get('location')        sex = json_info_post.get('sex')        about_me = json_info_post.get('about_me')        avator = json_info_post.get('avatar')        return User(name=name, sex=sex, about_me=about_me, location=location, avator=avator)    @staticmethod    def idChangeToUserName(id):        user=User.query.get_or_404(id)        return user.name    def followers_to_json(self,user):        json_followers = {            "followers": self.followers.filter_by(followed_id=user.id).all()        }        return json_followers    @staticmethod    def idChangeToUserAvatar(id):        user = User.query.get_or_404(id)        return user.avatar    @staticmethod    def idChangeToUserAbout_me(id):        user = User.query.get_or_404(id)        return user.about_me    # check password by passWordHash    @property    def passWord(self):        raise AttributeError("passWord was not a  readable arrribute")    @passWord.setter    def passWord(self,passWord):        self.userPasswordHash = generate_password_hash(passWord)    def verify_passWord(self, passWord):        return check_password_hash(self.userPasswordHash,passWord)    # confirm account when user register    def generate_confirmation_token(self, expiration=3600):        s = Serializer(current_app.config['SECRET_KEY'], expiration)        return s.dumps({'confirm':self.id})    def confirm(self,token):        s = Serializer(current_app.config['SECRET_KEY'])        try:            data = s.loads(token)        except:            return False        if data.get('confirm') !=self.id:            return False        self.confirmed = True        db.session.add(self)        db.session.commit()        return True    # api generate_token    def generate_auth_token(self, expiration):        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)        return s.dumps({'id':self.id})    @staticmethod    def verify_auth_token(token):        s = Serializer(current_app.config['SECRET_KEY'])        try:            data = s.loads(token)        except:            return None        return User.query.get(data['id'])    # role and user_permissions    def __init__(self,**kwargs):        super(User, self).__init__(**kwargs)        if self.role is None:            if self.userEmail == current_app.config['JXNUGO_ADMIN']:                self.role = Role.query.filter_by(permissions=0xff).first()            if self.role is None:                self.role = Role.query.filter_by(default=True).first()    def can(self, permissions):        return self.role is not None and (self.role.permissions & permissions)==permissions    def is_administrator(self):        return self.can(Permission.ADMINISTER)    # user information about register time    def ping(self):        self.last_seen = datetime.utcnow()        db.session.add(self)        db.session.commit()    @staticmethod    def generate_fake(count=100):        from sqlalchemy.exc import IntegrityError        import forgery_py        random.seed()        for i in range(count):            u = User(id=getPrimaryKeyId('isUser'), name='jxnugo_'+str(getPrimaryKeyId('isUser')), userName=forgery_py.internet.user_name(True),                   userEmail=forgery_py.internet.email_address(),confirmed=True,                   passWord='123', sex=u'男', location=forgery_py.address.city(), about_me=forgery_py.lorem_ipsum.sentence(),                   menber_since=forgery_py.date.date(True), contactMe=randomId())            db.session.add(u)            try:                db.session.commit()            except IntegrityError:                db.session.rollback()    # follow and unfollow    def follow(self, user):        if not self.is_following(user):            f=Follow(follower=self, followed=user)            db.session.add(f)            db.session.commit()    def unfollow(self, user):        f=self.followed.filter_by(followed_id=user.id).first()        if f:            db.session.delete(f)            db.session.commit()    def is_following(self, user):        return self.followed.filter_by(followed_id=user.id).first() is not None    def is_followed_by(self, user):        return self.followers.filter_by(follower_id=user.id).first() is not None    def collect(self, post):        if not self.is_collecting(post):            self.collectionPost.append(post)            db.session.commit()    def uncollect(self, post):        if self.is_collecting(post):            self.collectionPost.remove(post)            db.session.commit()    def is_collecting(self, post):         if post in self.collectionPost.all():             return True         else:             return Falseclass AnonymousUser(AnonymousUserMixin):    def can(self, perimissions):        return False    def is_administrator(self):        return Falseclass Post(db.Model):    __tablename__ = 'posts'    id = db.Column(db.Integer,primary_key=True)   # 帖子id,主键    body = db.Column(db.Text())                   # 帖子主题内容    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)  # 帖子发布时间    goodName = db.Column(db.String(128))     # 物品名    goodPrice = db.Column(db.String(20), default='0')  # 物品价格    goodNum = db.Column(db.String(20), default='1')  # 物品数量    goodLocation = db.Column(db.String(64))    # 发布人位置如一栋N204    goodQuality = db.Column(db.String(64))     # 物品成色    goodBuyTime = db.Column(db.String(64))     # 物品购买时间    goodTag = db.Column(db.Integer, default=4)  # 物品标签,用来确定物品的类型,0生活用品1数码科技2服饰箱包3图书音像4其它,默认其它    contact = db.Column(db.String(64))         # 发帖人联系方式    photos = db.Column(db.String(512), default="FsEAykjBT4VlaqS934nGjd7GbmLu:Fn5e3ZfrHJ4GbfPmlaAjhfYAxiFn")         # 图片的key    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 外键  关联发布帖子的人    comments = db.relationship('Comment', backref='post', lazy='dynamic')    @staticmethod    def generate_fake(count=50):        import forgery_py        random.seed()        user_count=User.query.count()        random.seed()        for i in range(count):            u = User.query.offset(random.randint(0, user_count-1)).first()            p = Post(body=forgery_py.lorem_ipsum.sentences(random.randint(1,  3)), timestamp=forgery_py.date.date(True),                   id=getPrimaryKeyId('isPost'), goodName=forgery_py.name.industry(), goodPrice=1239.12, goodNum=1, goodLocation=forgery_py.address.street_address(),                   goodQuality=u'9成新', goodBuyTime=forgery_py.date.date(True), goodTag=4, contact=randomId(),                   author=u)            db.session.add(p)            db.session.commit()    @staticmethod    def idChangeToPostName(id):         post=Post.query.get_or_404(id)         return post.goodName    def to_json(self):        json_post={            'postId':self.id,            'postNickName':User.idChangeToUserName(self.author_id),            'postUserAvatar':User.idChangeToUserAvatar(self.author_id),            'url':url_for('api.get_post',id=self.id,_external=True),            # 'url':'http://www.jxnugo.com/api/posts/%d' % self.id,            'body':self.body,            'timestamp':utcChangeCst(self.timestamp),            'goodsName':self.goodName,            'goodsPrice':self.goodPrice,            'goodsLocation':judge_empty(self.goodLocation, 'goodsLocation'),            'goodsQuality':judge_empty(self.goodQuality, 'goodsQuality'),            'goodsBuyTime':judge_empty(self.goodBuyTime, 'goodsBuyTime'),            'goodsTag':self.goodTag,            'author_id':self.author_id,            'contact':self.contact,            "photos":[{"key":key} for key in self.photos.split(":")],            'author': url_for('api.get_user', id=self.author_id, _external=True),            # 'author':'http://www.jxnugo.com/api/user/%d' %self.id,            'commentsCount':self.comments.count()        }        return json_post    def from_json(json_post):        id=Post.query.count()+1        body=json_post.get('body')        goodName=json_post.get('goodName')        goodPrice=json_post.get('goodPrice')        goodLocation=json_post.get('goodLocation')        goodQuality=json_post.get('goodQuality')        goodBuyTime=json_post.get('goodBuyTime')        goodTag=json_post.get('goodTag')        contact=json_post.get('contact')        photos=json_post.get('photos')        return Post(id=id, body=body,goodName=goodName,goodPrice=goodPrice,goodLocation=goodLocation,goodQuality=goodQuality,goodBuyTime=goodBuyTime,goodTag=goodTag,                    contact=contact,photos=photos)class Comment(db.Model):    __tablename__ = 'comments'    id = db.Column(db.Integer,primary_key=True)    body = db.Column(db.Text)    timestamp = db.Column(db.DateTime,index=True,default=datetime.now)    disabled = db.Column(db.Boolean)    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))    def to_json(self):        json_comment = {            "body":self.body,            "timestamp":self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),            "author":User.idChangeToUserName(self.author_id),            "authorId":self.author_id,            "authorAvatar":User.idChangeToUserAvatar(self.author_id)        }        return json_comment    def userComment_to_json(self):        json_comment = {            "body":self.body,            "timestamp":self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),            "postName":Post.idChangeToPostName(self.post_id),            "url":url_for('api.get_post',id=self.post_id,_external=True)        }        return json_commentclass bbsPost(db.Model):    __tablename__ = 'bbsposts'    id = db.Column(db.Integer, primary_key=True)    title = db.Column(db.String(128))    body = db.Column(db.Text)    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))class JxnuTour(db.Model):    __tablename__ = 'jxnutour'    id = db.Column(db.Integer, primary_key=True)    car_id = db.Column(db.Integer)    car_x = db.Column(db.String(64))    car_y = db.Column(db.String(64))    car_angle = db.Column(db.String(64))    timestamp = db.String(db.DateTime)    if_use = db.String(db.String(64))    def __repr__(self):        return '<Car %d>' % self.car_id@login_manager.user_loaderdef load_user(user_id):    return User.query.get(user_id)login_manager.anonymous_user = AnonymousUserlogin_manager.login_message = u'请登陆账户后再尝试访问此页面'def randomId():    l = '1'    for x in range(0,9):        a = int(random.uniform(0,9))        z = str(a)        l = l+z    return ldef judge_about_me(pid):    user = User.query.get_or_404(pid)    if user.about_me is not Nont:        return user.about_me    else:        return u'用户未设置签名'def judge_empty(type, info):    if type is not None:        return type    else:        if info is 'about_me':            return u'用户未设置签名'        elif info is 'location':            return u'用户未设置位置'        elif info is 'sex':            return u'用户未设置性别'        elif info is 'contactMe':            return u'用户未设置联系方式'        elif info is 'goodsLocation':            return u'未填写位置信息'        elif info is 'goodsQuality':            return u'未填写物品成色信息'        elif info is 'goodsBuyTime':            return u'未填写物品购买时间'        else:            passdef utcChangeCst(utcTime):    from_zone = tz.gettz('UTC')    to_zone = tz.gettz('CST')    utc = utcTime    utc = utc.replace(tzinfo=from_zone)    local = utc.astimezone(to_zone)    return datetime.strftime(local, "%Y-%m-%d %H:%M:%S")def getPrimaryKeyId(cate):    if cate is 'isUser':        count = User.query.count()        if count == 0:            return 1        else:            result = User.query.all()            firstUser = result[::-1]            return firstUser[0].id+1    elif cate is 'isPost':        count = Post.query.count()        if count == 0:            return 1        else:            result = Post.query.all()            firstPost = result[::-1]            return firstPost[0].id+1    elif cate is 'isComment':        count_comment=Comment.query.count()        if count_comment == 0:            return 1        else:            result = Comment.query.all()            firstComment = result[::-1]            return firstComment[0].id+1    else:        pass