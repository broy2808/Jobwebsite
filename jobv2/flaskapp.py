from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, g, request,_app_ctx_stack,Response
import os, sys
import sqlite3
import json
import flask
from flask_bcrypt import Bcrypt
from flask_login import login_user, current_user, logout_user, login_required, UserMixin,LoginManager
from flask import session
from forms import RegistrationForm, LoginForm,ProfileForm,JobPostForm
import process
import forms


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba234'
app.config["DEBUG"] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
response = flask.Response()
response.headers["Access-Control-Allow-Origin"] = "*"
response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
response.headers['Content-Security-Policy'] = "default-src 'self'"


DATABASE='sqlite3:///database.db'
def get_db():
    stacktop = _app_ctx_stack.top
    DATABASE =  os.path.join(app.root_path, 'database.db')
    if not hasattr(stacktop, DATABASE):
        stacktop.DATABASE = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        stacktop.DATABASE.row_factory = sqlite3.Row
    return stacktop.DATABASE


@app.cli.command('initdb')
def init_db():
    """
    register_converter(): convert SQLite types to Python types
    register_adapter(): convert Python types to SQLite types
    """
    db = get_db()
    with app.open_resource('tables.sql', mode='r') as f:
            db.cursor().executescript(f.read())
    process_jobs()
    db.commit()

# @app.teardown_appcontext
# def close_connection(exception):

#     if db is not None:
#         db.close()

def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def Userdet(username,email,password):
     #print(username,email,password)
     db = get_db()
     db.execute('INSERT INTO users(username,email,password) VALUES (?,?,?)',(username,email,password))
     db.commit()

@login_manager.user_loader
def load_user(id):
        db=get_db()
        c = db.execute("SELECT * from users where email = (?)", [id])
        u = c.fetchone()
        return u

def viewprofile(username):
        db=get_db()
        c=db.execute("SELECT * from userprofile where username = ?", [username])
        u = c.fetchone()
        if u:
            li=dict({"Username":u[0],"First name":u[1],"Last name":u[2],"City":u[3],"State":u[4],"Country":u[5],"Zip code":u[6],"Highest Level of Education":u[7],"Field of Study":u[8],"School or University":u[9],"Overall Result(GPA)":u[10],"Total relevant years of Experience":u[11],"Resume Information":u[12],"Skill Set":u[13]})
            return li
        else:
            return ""

class User(UserMixin):
    def __init__(self,name,email,password, active = True):
        self.name = name
        self.email = email
        self.password = password
        self.active = active

    def is_authenticated(self):
        return True
        #return true if user is authenticated, provided credentials

    def is_active(self):
        return True

    def is_annonymous(self):
        return False
        #return true if annon, actual user return false

    def get_id(self):
        db=get_db()
        c = db.execute('SELECT id from users where email = (?)', [g.user])
        id = c.fetchone()
        unicode=str
        return unicode(id)
    def add(self):
        db=get_db()
        c = db.execute('INSERT INTO users(username,email,password)VALUES(?,?,?)',[self.name,self.email,self.password])
        db.commit()
    def addrec(self):
        db=get_db()
        c = db.execute('INSERT INTO recruiters(username,email,password)VALUES(?,?,?)',[self.name,self.email,self.password])
        db.commit()
def skillsetjobs(userid,allrecjobs):
        db=get_db()
        c=db.execute("SELECT skillset from userprofile where username = ?", [userid])
        skills=c.fetchone()
        skilljobsid=set(allrecjobs)

        if skills:
            skills1 = [x.strip() for x in skills[0].split(',')]
            for val in skills1:

                val='%'+val+'%'
                c=db.execute("SELECT id from jobs where summary like ?", [val])
                v=c.fetchall()
                if v:

                    for jobid in v:
                        skilljobsid.add(jobid[0])
            return list(skilljobsid)
        else:
            return []


jobs=process.get_data()
#init_db()
def process_jobs():
    db = get_db()
    for job in jobs:
        db.execute('INSERT INTO jobs(job_title,company_name,summary,location) VALUES (?,?,?,?)',(job['job_title'],job['organization'],job['job_description'],job['location']))
        db.commit()
@app.cli.command('preprocess')
def preprocess():
    db = get_db()
    cursor1 = db.execute('SELECT summary FROM jobs')
    alljobs=cursor1.fetchall()
    process.preprocess_jobs(alljobs)

@app.route("/")
def base():
    #init_db()
    return render_template('base.html')

@app.route("/home")
def home():
    #return render_template('home2.html', jobs=jobs,keys=request.args.get('username'))
    db = get_db()
    viewprofile1=viewprofile(request.args.get('username'))
    username=request.args.get('username')
    if viewprofile1!="":
        cursor1 = db.execute('SELECT summary FROM jobs')
        alljobs=cursor1.fetchall()
        final=process.compareresumejob(alljobs,viewprofile1['Resume Information'])
        final=skillsetjobs(request.args.get('username'),final)

        c1=[]
        for val in final:
            cjob1 = db.execute('SELECT job_title,company_name,summary,location,status,ID FROM jobs where ID=?',[val])
            cjob=cjob1.fetchone()
            if cjob:
                c1.append(cjob)
        if c1:
            cur1=db.execute('SELECT ID,username,status FROM jobsapplied where username=?',[username])
            job1=cur1.fetchall()
        #sql="SELECT job_title,company_name,summary,location,status,ID FROM jobs where ID in ({seq})".format(seq=','.join(['?']*len(final)))
        #cursor= db.execute(sql,final)
        return render_template('home2.html', jobs=c1,jobs1=job1,keys=request.args.get('username'))
    else:
        cursor = db.execute('SELECT job_title,company_name,summary,location,status,ID FROM jobs')
        job=cursor.fetchall()
        if job:
             cur1=db.execute('SELECT ID,username,status FROM jobsapplied where username=?',[username])
             job1=cur1.fetchall()
        
    return render_template('home2.html', jobs=job,jobs1=job1,keys=request.args.get('username'))

@app.route("/homeall",methods=['GET', 'POST'])
def homeall():
    db = get_db()
    username=request.args.get('username')
    cursor = db.execute('SELECT b.job_title,b.company_name,b.summary,b.location,b.status,b.ID FROM jobs b' )
    job=cursor.fetchall()
    if job:
        cur1=db.execute('SELECT ID,username,status FROM jobsapplied where username=?',[username])
        job1=cur1.fetchall()
        print(job1)
    return render_template('home.html', jobs=job,jobs1=job1,keys=request.args.get('username'))

@app.route("/rechome",methods=['GET', 'POST'])
def rechome():
    form= JobPostForm()
    if request.method == 'POST' and form.validate_on_submit():
        db=get_db()
        username=request.args.get('username')
        db.execute('INSERT INTO jobs (job_title,company_name,location,summary) VALUES (?,?,?,?)',[form.job_title.data,form.company_name.data,form.location.data,form.summary.data])
        db.commit()
        return redirect(url_for('rechome',form=form,username=request.args.get('username')))

    return render_template('rechome.html',form=form,keys=request.args.get('username'))

@app.route("/jobapply",methods=['GET', 'POST'])
def jobapply():
    viewprofile1=viewprofile(request.args.get('username'))
    form = ProfileForm()

    if request.method == 'POST':
        db=get_db()
        username=request.args.get('username')
        jobid=request.args.get('jobid')
        if jobid:
           db.execute('INSERT INTO jobsapplied(ID, username, status) VALUES (?,?,?)',(jobid,username,'Applied'))
           c1 = db.execute('''UPDATE jobs SET status=?  WHERE ID=?''',['Applied',jobid])
           db.commit()
        return redirect(url_for('home',username=request.args.get('username')))

    elif request.method == 'GET' and viewprofile1!="":
        db=get_db()
        jobid=request.args.get('jobid')

        c=db.execute('select * from jobs where ID=?',[jobid])
        u=c.fetchone()
        if u:
            jobexists=dict({"job_title":u[1],"company_name":u[2],"summary":u[3],"location":u[4],"status":u[5],"id":u[0]})
        else:
            jobexists=""
        return render_template('jobapply.html',keys=request.args.get('username'),viewprofile1=viewprofile1,form=form,jobid=request.args.get('jobid'),jobs=jobexists)

    if viewprofile1=="":
        flash('Please add you profile information!')

    return redirect(url_for('home',username=request.args.get('username')))


@app.route("/about", methods=['GET', 'POST'])
def about():
    viewprofile1=viewprofile(request.args.get('username'))
    form = ProfileForm()
    if request.method == 'POST' and form.validate_on_submit():
        db=get_db()
        username=request.args.get('username')
        c=db.execute('select * from userprofile where username=?',(username,))
        userexists=c.fetchone()
        if userexists:
           print("I'AM HERE",username,form.firstname.data,form.lastname.data,form.city.data,form.state.data,form.country.data,form.zipcode.data,form.degreename.data,form.studyfield.data,form.school.data,type(form.gpa.data))
           c1 = db.execute('''UPDATE userprofile SET firstname=? , lastname=? , city=? , state=? , country=? , zipcode=? , degreename=? , studyfield=? , school=? , gpa=? , exp1=?,resume1=?,skillset=? WHERE username=?''',[form.firstname.data,form.lastname.data,form.city.data,form.state.data,form.country.data,form.zipcode.data,form.degreename.data,form.studyfield.data,form.school.data,float(form.gpa.data),form.exp.data,form.resume.data,form.skillset.data,username])
           db.commit()
        else:
           c1 = db.execute('INSERT INTO userprofile(username,firstname,lastname,city,state,country,zipcode,degreename,studyfield,school,gpa,exp1,resume1,skillset) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',[username,form.firstname.data,form.lastname.data,form.city.data,form.state.data,form.country.data,form.zipcode.data,form.degreename.data,form.studyfield.data,form.school.data,float(form.gpa.data),form.exp.data,form.resume.data,form.skillset.data])
           db.commit()
        return redirect(url_for('about',username=request.args.get('username')))
    elif request.method == 'GET' and viewprofile1!="":

        form.firstname.data=str(viewprofile1['First name'])
        form.lastname.data=str(viewprofile1['Last name'])
        form.city.data=str(viewprofile1['City'])
        form.state.data=str(viewprofile1['State'])
        form.country.data=str(viewprofile1['Country'])
        form.zipcode.data=int(viewprofile1['Zip code'])
        form.degreename.data=str(viewprofile1['Highest Level of Education'])
        form.studyfield.data=str(viewprofile1['Field of Study'])
        form.school.data=str(viewprofile1['School or University'])
        form.gpa.data=float(viewprofile1['Overall Result(GPA)'])
        form.exp.data=int(viewprofile1['Total relevant years of Experience'])
        form.resume.data=str(viewprofile1['Resume Information'])
        form.skillset.data=str(viewprofile1['Skill Set'])
    return render_template('about.html', title='About',viewprofile1=viewprofile1,keys=request.args.get('username'), form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.profiletype.data=="Job Seeker":
             hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
             db=get_db()
             c=db.execute('select * from users where email=? or username=?',(form.email.data,form.username.data,))
             userexists=c.fetchone()
             #print(userexists)
             if userexists:
                  flash('Username or email already exists!', 'danger')
             else:
                  user = User(name=form.username.data, email=form.email.data, password=hashed_password)
                  user.add()
                  flash('Your account has been created! You are now able to log in', 'success')
             return redirect(url_for('login'))
        else:
             hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
             db=get_db()
             c=db.execute('select * from recruiters where email=? or username=?',(form.email.data,form.username.data,))
             userexists=c.fetchone()
             #print(userexists)
             if userexists:
                  flash('Username or email already exists!', 'danger')
             else:
                  user = User(name=form.username.data, email=form.email.data, password=hashed_password)
                  user.addrec()
                  flash('Your account has been created! You are now able to log in', 'success')
             return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        if form.profiletype.data=="Job Seeker":
            g.user=form.email.data
            g.passw=form.password.data
            db=get_db()
            c=db.execute('select * from users where email=?',(form.email.data,))
            userexists=c.fetchone()
            #print(userexists)
            if userexists and bcrypt.check_password_hash(userexists['password'], form.password.data):
                 user = User(userexists['username'], g.user, g.passw)
                 login_user(user, remember=True)
                 #login_user(user['username'], remember=form.remember.data)
                 next_page = request.args.get('next')
                 return redirect(next_page) if next_page else redirect(url_for('home',username=userexists['username']))
                 #return redirect(url_for('home',username=userexists['username']))
            else:
                 flash('Login Unsuccessful. Please check email and password', 'danger')
        else:
            g.user=form.email.data
            g.passw=form.password.data
            db=get_db()
            c=db.execute('select * from recruiters where email=?',(form.email.data,))
            userexists=c.fetchone()
            #print(userexists)
            if userexists and bcrypt.check_password_hash(userexists['password'], form.password.data):
                 user = User(userexists['username'], g.user, g.passw)
                 login_user(user, remember=True)
                 next_page = request.args.get('next')
                 return redirect(next_page) if next_page else redirect(url_for('rechome',username=userexists['username']))
            else:
                 flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return render_template('base.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1',port='5001',debug = True)
