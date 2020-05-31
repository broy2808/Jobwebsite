from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,SelectField, BooleanField,IntegerField,DecimalField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    profiletype = SelectField(u'Type of Profile', choices=[('Job Seeker','Job Seeker'),('Recruiter','Recruiter')])


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    profiletype = SelectField(u'Type of Profile', choices=[('Job Seeker','Job Seeker'),('Recruiter','Recruiter')])

class ProfileForm(FlaskForm):
    firstname = StringField('First Name',
                           validators=[DataRequired()])
    lastname = StringField('Last Name',
                        validators=[DataRequired(), Length(min=2, max=30)])
    city = StringField('City',
                           validators=[DataRequired(), Length(min=2, max=20)])
    state = StringField('State',
                           validators=[DataRequired(), Length(min=2, max=20)])  
    country = StringField('Country',
                           validators=[DataRequired(), Length(min=2, max=20)])   
    zipcode = IntegerField('Zipcode',
                           validators=[DataRequired()])
    degreename = StringField('Highest Level of Education',
                           validators=[DataRequired(), Length(min=2, max=40)])
    studyfield = StringField('Field of Study',
                           validators=[DataRequired(), Length(min=2, max=40)])      
    school = StringField('School or University',
                           validators=[DataRequired(), Length(min=2, max=40)])  
    gpa = DecimalField('Overall Result(GPA)',
                           validators=[DataRequired()])     
    exp = IntegerField('Total relevant years of Experience',
                           validators=[DataRequired()]) 
    resume=TextAreaField('Profile Resume Update',
                           validators=[DataRequired()])
    skillset=TextAreaField('SkillSet or Preferred Job Descriptions')                                                                                                                                                                        
    submit = SubmitField('Submit')    

class JobPostForm(FlaskForm): 
    job_title = StringField('Job Title',
                           validators=[DataRequired(), Length(min=5, max=255)]) 
    company_name = StringField('Company Name',
                           validators=[DataRequired(), Length(min=5, max=255)]) 
    location = StringField('Location',
                           validators=[DataRequired(), Length(min=2, max=30)]) 
    summary=TextAreaField('Job Summary Update',
                           validators=[DataRequired()])
    submit = SubmitField('Submit')                          