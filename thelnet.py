import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, PasswordField
from wtforms.validators import DataRequired, Length

#App initialization ######################################
app = Flask(__name__)
app.config.from_object(__name__)
#app.run(host='0.0.0.0')

app.config.update(dict(DATABASE=os.path.join(app.root_path, "thelnet.db"),
    SECRET_KEY='hushhush',
    USERNAME='admin',
    PASSWORD='PASS',
))

# for futureproofing, if we ever need to set up a separate configuration file. 
# As of now the above suffices.
app.config.from_envvar('THELNET_SETTINGS', silent=True)

#########################################################

#Form functions ##########################################

class RegisterForm(FlaskForm):
    name = StringField('Name', 
                        validators=[DataRequired(message='This is a mandatory field.')])
    gender = RadioField('Gender', 
                        validators=[DataRequired(message='This is a mandatory field.')],
                        choices = [('m', 'Male'), ('f', 'Female')])
    uname = StringField('Username', 
                        validators=[DataRequired(message='This is a mandatory field.'),
                        Length(max=10, message='Username cannot have a length of more than 10.')])
    password = PasswordField('Password', 
                        validators=[DataRequired(message='This is a mandatory field.'), 
                        Length(min=6, message='Password must be a minimum of 6 characters.')])

class LoginForm(FlaskForm):
    uname = StringField('Username', 
                        validators=[DataRequired(message='Enter your username.')])
    password = PasswordField('Password', 
                        validators=[DataRequired(message='Enter your password.')])

#Helper functions ########################################
def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row    #so that a cursor on rv returns a dictionary object
    return rv

def init_db():
    db = get_db()
    with app.open_resource('login_db_init.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print("Database created.")

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(exception):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

#########################################################

#Webpage configs ########################################

@app.route('/')
def index():
    if session.get('logged_in') == None:
        session['logged_in'] = False
    return render_template('index.html')

# @app.route('/register_action/', methods = ['POST'])
# def register_action():
#     if not session.logged_in:
#         db = get_db()
#         db.execute('insert into users values(?, ?, ?, ?)', 
#         (request.form['uname'], request.form['realName'], request.form['gender'], request.form['userPass']))
#         db.commit()
#         flash('You have been registered successfully!')
#         session.logged_in = True
#         session.username = request.form['uname']
#         return render_template('index.html')
#     else:
#         flash("You are already logged in!")
#         return render_template('index.html') 

@app.route('/register/', methods=['GET', 'POST']) 
def register():
    details = RegisterForm()
    error = None
    if not session['logged_in']:
        if details.validate_on_submit():
            db = get_db()
            cur = db.cursor()
            cur.execute("select uName from users where uName=?", (details.uname.data,))
            r = cur.fetchone()
            if not r:
                db.execute('insert into users values(?, ?, ?, ?)',
                        (details.uname.data, details.name.data, details.gender.data, details.password.data))
                db.commit()
                flash('You have been registered successfully!')
                session['logged_in'] = True
                session['username'] = details.uname.data
                return redirect('/')
            else:
                error = 'An account with the username already exists.'
    else:
        error = 'You are already logged in!'
    return render_template('register.html', form=details, error=error)

@app.route('/login/', methods=['GET', 'POST']) # also handle the flash thingy
def login():
    details = LoginForm()
    error = None
    if details.validate_on_submit():
        db = get_db()
        cur = db.cursor()
        cur.execute("select uName, userPass from users where uName=?", (details.uname.data,))
        r = cur.fetchone()
        if not r:
            error = "Username doesn't exist."
        else:
            if details.password.data == r['userPass']:
                flash("You have logged in!")
                session['logged_in'] = True
                session['username'] = details.uname.data
                return redirect('/')
            else:
                error = "Password is incorrect."
    return render_template('login.html', form=details, error=error)

@app.route('/logout/')
def logout():
    session['logged_in'] = False
    return render_template('logout.html')

###########################################################
