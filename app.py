from flask import Flask, url_for, render_template, flash, redirect, request
from forms import RegisterForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

app = Flask(__name__)

app.config["SECRET_KEY"] = '5ac7163b41e01ecfb54668399e3b6ad7'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///app.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'primary'

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

# User Model
class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	full_name = db.Column(db.String(40), nullable = False)
	email = db.Column(db.String(50), unique = True, nullable = False)
	age = db.Column(db.Integer, nullable = False)
	profile_picture = db.Column(db.String(30), nullable = False, default = 'default.jpg')
	password = db.Column(db.String(60), nullable = False)

	def __repr__(self):
		return f"User({self.full_name}, {self.email}, {self.age})"


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
	form = RegisterForm()
	if (form.validate_on_submit()):
		user = User.query.filter_by(email = form.email.data).first()
		if (user):
			flash('An account already exists for the entered email!', 'danger')
		else:
			hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
			user = User(full_name = form.full_name.data, email = form.email.data, age = form.age.data, password = hashed_password)
			db.session.add(user)
			db.session.commit()
			flash('Your account has been created successfully!', 'success')
			return redirect(url_for('login'))

	return render_template('register.html', title = 'Register', form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if (form.validate_on_submit()):
		user = User.query.filter_by(email = form.email.data).first()
		if (user and bcrypt.check_password_hash(user.password, form.password.data)):
			login_user(user, remember = form.remember_me.data)
			page = request.args.get('next')
			if page:
				return redirect(page)
			else:
				return redirect(url_for('home'))
		flash('Invalid Credentials! Please make sure that you have entered correct email and password', 'danger')
	return render_template('login.html', title = 'Login', form = form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))

@app.route('/account')
@login_required
def account():
	return render_template('account.html', title = 'My Profile')

if (__name__ == '__main__'):
	app.run(debug = True)