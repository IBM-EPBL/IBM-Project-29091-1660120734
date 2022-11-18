from app import db, login_manager
from datetime import date
from flask_login import UserMixin
import ibm_db
@login_manager.user_loader
def load_user(user_id):
    sql="select * from user where id=? limit 1;"
    conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=32286;PROTOCOL=TCPIP;SECURITY=SSL;UID=IBM_ID;PWD=IBM_PWD;","","")
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,user_id)
    ibm_db.execute(stmt)
    users=ibm_db.fetch_both(stmt)
    return User(users[0],users[1],users[2],users[3],users[4])


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    usertype = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    jobs = db.relationship('Jobs', backref='job_applier', lazy=True)
    applications = db.relationship('Application', backref='application_submiter', lazy=True)

    def __init__(self,id,username,usertype,email,password):
        self.id=id
        self.username=username
        self.usertype=usertype
        self.email=email
        self.password=password
    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.usertype}', '{self.email}')"


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(20), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=date.today())
    degree = db.Column(db.String(20), nullable=False)
    industry = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    cv = db.Column(db.String(20), nullable=False)
    cover_letter = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    def __init__(self,id,date_posted,user_id,job_id):
        self.id=id
        self.date_posted=date_posted
        self.user_id=user_id
        self.job_id=job_id
        

    def __repr__(self):
        return f"Application('{self.id}','{self.gender}', '{self.date_posted}', '{self.degree}', '{self.industry}', '{self.experience}', '{self.user_id}', '{self.job_id}')"

class Jobs(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=date.today())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    applications = db.relationship('Application', backref='application_jober', lazy=True)

    def __init__(self,id,title,industry,date_posted,description):
        self.id=id
        self.description=description
        self.title=title
        self.date_posted=date_posted
        self.industry=industry

    def __repr__(self):
        return f"Jobs('{self.id}','{self.title}', '{self.industry}', '{self.date_posted}')"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    review = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Review('{self.username}', '{self.review}')"
# class JOB:
#     def __init__(self,id,title,industry,date_posted,description,user_id):
#         self.id=id
#         self.description=description
#         self.title=title
#         self.date_posted=date_posted
#         self.industry=industry
#         self.user_id=user_id
#     def __repr__(self):
#         return f"job('{self.id}','{self.title}', '{self.industry}', '{self.date_posted}')"
