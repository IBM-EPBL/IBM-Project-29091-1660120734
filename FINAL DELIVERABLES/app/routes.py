from flask import render_template, url_for, flash, redirect, request, send_file
from app import  app, bcrypt
from PIL import Image
import os
import secrets
from app.form import RegistrationForm, LoginForm, ReviewForm, JobForm, ApplicationForm,ProfileUpdateForm
from app.models import User, Jobs, Review, Application
from flask_login import login_user, current_user, logout_user, login_required
import random
import ibm_db
import datetime
from app.sendmail import sendMail

rev = [
    {
        'username': 'Micheal Scott',
        'review': 'I hired multiple people using this website. Thank you'
    },
    {
        'username': 'Dwight Schrute',
        'review': 'It could be better'
    },
    {
        'username': 'Andy Bernard',
        'review': 'Best website ever'
    }
]


# Review_Obj = Review.query.all()
# if len(Review_Obj) < 3:
#     Random_Review = rev
# else:
#     Random_Review = random.sample(Review_Obj, 3)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.usertype == 'Job Seeker':
            return redirect(url_for('show_jobs'))
        elif current_user.usertype == 'Company':
            return redirect(url_for('posted_jobs'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        sql="insert into user(username,usertype,email,password) values(?,?,?,?);"
        conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=32286;PROTOCOL=TCPIP;SECURITY=SSL;UID=fbc81880;PWD=v4TioNbfWbm9MZP7;","","")
        print("insert into user(username,usertype,email,password) values("+form.username.data+","+form.usertype.data+","+form.email.data+","+hashed_password+");")
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,form.username.data)
        ibm_db.bind_param(stmt,2,form.usertype.data)
        ibm_db.bind_param(stmt,3,form.email.data)
        ibm_db.bind_param(stmt,4,hashed_password)
        ibm_db.execute(stmt)
        # user = ibm_db.fetch_both(stmt)
        # users=[]
        # while user!=False:
        #     users.append(User(user["id"],user["username"],user["usertype"],user["email"]))
        #     user = ibm_db.fetch_both(stmt)
        # user = User(username=form.username.data, usertype=form.usertype.data, email=form.email.data, password=hashed_password)
        # db.session.append(user)
        # db.session.commit()
        flash('You account has been created! You are now able to log in', 'success')
        return redirect(url_for('updateprofile'))
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.usertype == 'Job Seeker':
            return redirect(url_for('show_jobs'))
        elif current_user.usertype == 'Company':
            return redirect(url_for('posted_jobs'))
    form = LoginForm()
    if form.validate_on_submit():
        sql="select * from user where email=? limit 1;"
        conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=32286;PROTOCOL=TCPIP;SECURITY=SSL;UID=IBM_ID;PWD=IBM_PWD;","","")
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,form.email.data)
        ibm_db.execute(stmt)
        users=ibm_db.fetch_both(stmt)
        user=None
        if users!=False:
            print(users)
            user=User(users[0],users[1],users[2],users[3],users[4])
            print(user.password)
        else:
            flash('Login Unsuccessful. Please check email, password and usertype', 'danger')
            return render_template('login.html', form=form)
        # user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            print('password clear')
            if form.usertype.data == user.usertype and form.usertype.data == 'Company':
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('posted_jobs'))
            elif form.usertype.data == user.usertype and form.usertype.data == 'Job Seeker':
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('show_jobs'))
            else:
                flash('Login Unsuccessful. Please check email, password and usertype', 'danger')
        else:
            flash('Login Unsuccessful. Please check email, password and usertype', 'danger')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('show_jobs'))

def save_picture(form_picture):
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = f_name + f_ext
    picture_path = os.path.join(app.root_path, 'static', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@app.route("/post_cvs/<jobid>", methods=['GET', 'POST'])
@login_required
def post_cvs(jobid):
    form = ApplicationForm()
    # sql="select * from job where id=? limit 1"
    conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=32286;PROTOCOL=TCPIP;SECURITY=SSL;UID=IBM_ID;PWD=IBM_PWD;","","")
    # stmt = ibm_db.prepare(conn, sql)
    # ibm_db.bind_param(stmt,1,jobid)
    # ibm_db.execute(stmt)
    # job=ibm_db.fetch_both(stmt)
    # jobs=[]
    # while job!=False:
    #     jobs.append(Jobs(job["ID"],job["TITLE"],job["INDUSTRY"],job["DATE_POSTED"],job["DESCRIPTION"]))
    #     job = ibm_db.fetch_both(stmt)
    if form.validate_on_submit():
        sql1="insert into application(user_id,job_id,cover_letter,cv) values(?,?,?,?)"
        stmt=ibm_db.prepare(conn,sql1)
        ibm_db.bind_param(stmt,1,current_user.id)
        ibm_db.bind_param(stmt,2,jobid)
        ibm_db.bind_param(stmt,4,form.cv.data.filename)
        ibm_db.bind_param(stmt,3,form.cover_letter.data)
        
        ibm_db.execute(stmt)
        # application = Application(gender=form.gender.data,
        #                       degree=form.degree.data,
        #                       industry=form.industry.data,
        #                       experience=form.experience.data,
        #                       cover_letter=form.cover_letter.data,
        #                       application_submiter=current_user,
        #                       application_jober=job,
        #                       cv=form.cv.data.filename)
        # print(form.cv.data)
        save_picture(form.cv.data)
        print("hii")
        flash('Resume uploaded successfully.', 'danger')
        # db.session.append(application)
        # db.session.commit()
        return redirect(url_for('show_jobs'))
    return render_template('post_cvs.html', form=form)

@app.route("/post_jobs", methods=['GET', 'POST'])
@login_required
def post_jobs():
    form = JobForm()
    print("before entered")
    if form.validate_on_submit():
        print("after entered")
        sql="insert into job(title,industry,description,user_id,required_skill) values(?,?,?,?,?)"
        conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=32286;PROTOCOL=TCPIP;SECURITY=SSL;UID=IBM_ID;PWD=IBM_PWD;","","")
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,form.title.data)
        ibm_db.bind_param(stmt,2,form.industry.data)
        ibm_db.bind_param(stmt,3,form.description.data)
        ibm_db.bind_param(stmt,4,current_user.id)
        ibm_db.bind_param(stmt,5,form.required_skill.data)
        # d=datetime.datetime.now()
        # ibm_db.bind_param(stmt,5,d)
        print(form.industry.data,form.description.data,form.title.data)
        ibm_db.execute(stmt)
        print("hello vishwa")
        integrateMail(form.title.data,form.description.data,form.required_skill.data)
        # job = Jobs(title=form.title.data,
        #            industry=form.industry.data,
        #            description=form.description.data,
        #            job_applier=current_user)
        # db.session.append(job)
        # db.session.commit()
        return redirect(url_for('posted_jobs'))
    return render_template('post_jobs.html', form=form)


@app.route("/review", methods=['GET', 'POST'])
@login_required
def review():
    form = ReviewForm()
    if form.validate_on_submit():
        sql="insert into review(username,review) values(?,?)"
        conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=32286;PROTOCOL=TCPIP;SECURITY=SSL;UID=IBM_ID;PWD=IBM_PWD;","","")
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,form.username.data)
        ibm_db.bind_param(stmt,2,form.review.data)
        ibm_db.execute(stmt)
        # review = Review(username=form.username.data,
        #                     review=form.review.data)
        # db.session.append(review)
        # db.session.commit()
        flash('Thank you for providing the review!', 'success')
        return redirect(url_for('show_jobs'))
    return  render_template('review.html', form=form)

@app.route("/posted_jobs")
@login_required
def posted_jobs():
    sql="select * from job where user_id=?"
    conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=32286;PROTOCOL=TCPIP;SECURITY=SSL;UID=IBM_ID;PWD=IBM_PWD;","","")
    stmt=ibm_db.prepare(conn,sql)
    print(current_user)
    ibm_db.bind_param(stmt,1,current_user.id)
    ibm_db.execute(stmt)
    job=ibm_db.fetch_both(stmt)
    jobs=[]
    while job!=False:
        jobs.append(Jobs(job["ID"],job["TITLE"],job["INDUSTRY"],job["DATE_POSTED"],job["DESCRIPTION"]))
        job = ibm_db.fetch_both(stmt)
    # jobs = Jobs.query.filter_by(job_applier=current_user)
    return render_template('show_jobs.html', jobs=jobs)


@app.route("/show_applications/<jobid>", methods=['GET'])
@login_required
def show_applications(jobid):
    sql="select * from application where job_id=? order by degree,experience desc"
    conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=32286;PROTOCOL=TCPIP;SECURITY=SSL;UID=IBM_ID;PWD=IBM_PWD;","","")
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,jobid)
    ibm_db.execute(stmt)
    application=ibm_db.fetch_both(stmt)
    applications=[]
    while application!=False:
        applications.append(Application(application["ID"],application["GENDER"],application["DATE_POSTED"],application["DEGREE"],application["INDUSTRY"],application["EXPERIENCE"],application["USER_ID"],application["JOB_ID"]))
        application = ibm_db.fetch_both(stmt)
    # applications = Application.query.filter_by(job_id=jobid).order_by(Application.degree, Application.experience.desc()).all()
    return render_template('show_applications.html', applications=applications)

@app.route("/meeting/<application_id>")
@login_required
def meeting(application_id):
    # applicant_id = Application.query.get(int(application_id)).user_id
    # applicant = User.query.get(applicant_id)
    return render_template('meeting.html')

@app.route("/")
@app.route("/show_jobs")
def show_jobs():
    sql="select * from job"
    conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=32286;PROTOCOL=TCPIP;SECURITY=SSL;UID=IBM_ID;PWD=IBM_PWD;","","")
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.execute(stmt)
    job=ibm_db.fetch_both(stmt)
    jobs=list()
    while job!=False:
        jobs.append(Jobs(job["ID"],job["TITLE"],job["INDUSTRY"],job["DATE_POSTED"],job["DESCRIPTION"]))
        job = ibm_db.fetch_both(stmt)
    print(jobs)
    # jobs = Jobs.query.all()
    return render_template('show_jobs.html', jobs=jobs)

@app.route("/resume/<id>", methods=['GET'])
def resume(id):
    sql="select cv from application where id=?"
    conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=32286;PROTOCOL=TCPIP;SECURITY=SSL;UID=IBM_ID;PWD=IBM_PWD;","","")
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,id)
    ibm_db.execute(stmt)
    c=ibm_db.fetch_both(stmt)
    cv=""
    while c!=False:
        cv=c[0]
        c = ibm_db.fetch_both(stmt)
    # cv = Application.query.get(int(id)).cv
    return render_template('resume.html', cv=cv, id=id)

@app.route("/updateprofile" , methods=['GET',"POST"])
@login_required
def updateprofile():
    if current_user.usertype=="Job Seeker":
        form=ProfileUpdateForm()
        if form.validate_on_submit():
            sql="insert into jobseeker values(?,?,?,?,?,?,?)"
            conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=32286;PROTOCOL=TCPIP;SECURITY=SSL;UID=IBM_ID;PWD=IBM_PWD;","","")
            stmt=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,current_user.id)
            ibm_db.bind_param(stmt,2,form.gender.data)
            ibm_db.bind_param(stmt,3,form.degree.data)
            ibm_db.bind_param(stmt,4,form.experience.data)
            ibm_db.bind_param(stmt,5,form.skill1.data)
            ibm_db.bind_param(stmt,6,form.skill2.data)
            ibm_db.bind_param(stmt,7,form.skill3.data)
            ibm_db.execute(stmt)
            return redirect(url_for('login'))
        return render_template("profile_update.html",form=form)


@app.route("/show_application", methods=['GET'])
@login_required
def show_application():
    sql="select * from application inner join job on job.id=application.job_id where application.user_id=? order by date_applied desc"
    conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=32286;PROTOCOL=TCPIP;SECURITY=SSL;UID=IBM_ID;PWD=IBM_PWD;","","")
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,current_user.id)
    ibm_db.execute(stmt)
    application=ibm_db.fetch_both(stmt)
    print(application)
    applications=[]
    while application!=False:
        applications.append(Application(application["ID"],application["DATE_POSTED"],application["USER_ID"],application["JOB_ID"]))
        application = ibm_db.fetch_both(stmt)
    # applications = Application.query.filter_by(job_id=jobid).order_by(Application.degree, Application.experience.desc()).all()
    return render_template('show_applications.html', applications=applications)


def integrateMail(title,description,skill):
    sql="select distinct(u.email) from jobseeker as j inner join user as u on j.id=u.id  where j.skill1=? or j.skill2=? or j.skill3=?;"
    conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=32286;PROTOCOL=TCPIP;SECURITY=SSL;UID=IBM_ID;PWD=IBM_PWD;","","")
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,skill)
    ibm_db.bind_param(stmt,2,skill)
    ibm_db.bind_param(stmt,3,skill)
    ibm_db.execute(stmt)
    emails=[]
    email=ibm_db.fetch_both(stmt)
    while email:
        emails.append(email[0])
        email=ibm_db.fetch_both(stmt)
    print(emails)
    sendMail(emails,title+"\n"+description)



