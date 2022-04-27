import os
import time
import datetime
from PIL import Image
from flask import Flask, url_for, render_template, flash, redirect, request
from forms import RegisterForm, LoginForm, AddJobForm, UpdateProfileForm
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from numpy import dot
from numpy.linalg import norm
import preprocess
import vectorizer

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

# Association table
user_job = db.Table('user_job',
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('job_id', db.Integer, db.ForeignKey('job.id')),
	db.Column('match', db.Integer, default = 0),
	db.Column('status', db.String(20), default = 'Pending')
)

# User Model
class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	full_name = db.Column(db.String(40), nullable = False)
	age = db.Column(db.Integer, nullable = False)
	email = db.Column(db.String(50), unique = True, nullable = False)
	phone = db.Column(db.String(15), nullable = False)
	profile_picture = db.Column(db.String(30), nullable = False, default = 'default.png')
	resume = db.Column(db.String(30), nullable = False, default = '')
	password = db.Column(db.String(60), nullable = False)
	is_admin = db.Column(db.Boolean, nullable = False, default = False)
	applied_at = db.relationship('Job', secondary = user_job, backref = 'applicants')

	def __repr__(self):
		return f"User({self.full_name}, {self.email}, {self.age})"


# Job Model
class Job(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	role = db.Column(db.String(60), nullable = False)
	job_desc = db.Column(db.Text, nullable = False)
	skills_required = db.Column(db.Text, nullable = False)
	work_location = db.Column(db.String(60), nullable = False)
	salary = db.Column(db.String(30), nullable = False)
	deadline = db.Column(db.DateTime, nullable = False)
	posted_on = db.Column(db.DateTime, nullable = False, default = datetime.datetime.now())

	def __repr__(self):
		return f"Job({self.role})"


# ROUTES

@app.route('/')
@app.route('/explore')
def explore():
	jobs = Job.query.all()
	return render_template('explore.html', title='Explore', jobs=jobs)


@app.route('/register', methods = ['GET', 'POST'])
def register():
	if (current_user.is_authenticated):
		return redirect(url_for('explore')) 
	form = RegisterForm()
	if (form.validate_on_submit()):
		user = User.query.filter_by(email = form.email.data).first()
		if (user):
			flash('An account already exists for the entered email!', 'danger')
		else:
			hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
			user = User(full_name = form.full_name.data, email = form.email.data, phone = form.phone.data, age = form.age.data, password = hashed_password)
			db.session.add(user)
			db.session.commit()
			flash('Your account has been created successfully!', 'success')
			return redirect(url_for('login'))

	return render_template('register.html', title = 'Register', form = form)


@app.route('/login', methods = ['GET', 'POST'])
def login():
	if (current_user.is_authenticated):
		return redirect(url_for('explore')) 
	form = LoginForm()
	if (form.validate_on_submit()):
		user = User.query.filter_by(email = form.email.data).first()
		if (user and bcrypt.check_password_hash(user.password, form.password.data)):
			login_user(user, remember = form.remember_me.data)
			page = request.args.get('next')
			if page:
				return redirect(page)
			else:
				return redirect(url_for('explore'))
		flash('Invalid Credentials! Please make sure that you have entered correct email and password', 'danger')
	return render_template('login.html', title = 'Login', form = form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))


def save_profile_pic(picture):
	file_name = str(int(time.time()))
	_, file_ext = os.path.splitext(picture.filename)
	file_name = file_name + file_ext
	path = os.path.join(app.root_path, 'static/profile_pictures', file_name)
	
	compressed = Image.open(picture)
	compressed.thumbnail((200, 200))
	compressed.save(path)

	return file_name

def save_resume(resume):
	file_name = str(int(time.time()))
	_, file_ext = os.path.splitext(resume.filename)
	name = file_name + file_ext
	path = os.path.join(app.root_path, 'static/resumes', name)
	
	resume.save(path)

	return file_name

@app.route('/account', methods = ['GET', 'POST'])
@login_required
def account():
	form = UpdateProfileForm()
	if form.validate_on_submit():
		email_unique = True
		if form.email.data != current_user.email:
			user = User.query.filter_by(email = form.email.data).first()
			if (user):
				email_unique = False
				flash('An account already exists for the entered email!', 'danger')
			else:
				current_user.email = form.email.data
		if (email_unique):
			if form.phone.data != current_user.phone:
				current_user.phone = form.phone.data
			if form.profile_picture.data:
				file_name = save_profile_pic(form.profile_picture.data)
				current_user.profile_picture = file_name
			if form.resume.data:
				file_name = save_resume(form.resume.data)

				preprocessed = preprocess.preprocess_file(file_name + '.pdf')
				txtfile = open(f"./static/resume_preprocessed/{file_name}.txt", "w")
				txtfile.write(preprocessed)
				txtfile.close()

				current_user.resume = file_name + '.pdf'
			db.session.commit()
			flash('Your profile was updated successfully', 'success')
			return redirect(url_for('account'))

	if request.method == 'GET':
		form.email.data = current_user.email
		form.age.data = current_user.age
		form.phone.data = current_user.phone
		applied_count = len(current_user.applied_at)
	image_path = url_for('static', filename = 'profile_pictures/' + current_user.profile_picture)
	return render_template('account.html', title = 'My Profile', image_path = image_path, form = form, applied_count = applied_count)

@app.route('/applications/<int:user_id>')
@login_required
def applications(user_id):
	jobs = current_user.applied_at
	return render_template('explore.html', title='My Applications', jobs=jobs)

@app.route('/position/<int:job_id>')
def position(job_id):
	job = Job.query.get(job_id)
	num_applicants = len(job.applicants)
	if current_user.is_authenticated and job in current_user.applied_at:
		status = db.session.query(user_job).filter_by(user_id = current_user.id, job_id = job_id).first().status
	else:
		status = None
	return render_template('job-details.html', title = job.role, job = job, num_applicants = num_applicants, status = status)


def cosine_similarity(x, y):
	return dot(x,y) / (norm(x) * norm(y))

@app.route('/applicants/<int:job_id>')
@login_required
def applicants(job_id):
	job = Job.query.get(job_id)
	applicants = job.applicants

	applicants_list = []
	for index, applicant in enumerate(applicants):
		user_job_row = db.session.query(user_job).filter_by(user_id = applicant.id, job_id = job_id).first()
		dictionary = {
			'id': applicant.id,
			'name': applicant.full_name,
			'age': applicant.age,
			'email': applicant.email,
			'profile_picture': applicant.profile_picture,
			'resume': applicant.resume,
			'strength': user_job_row.match,
			'status': user_job_row.status
		}
		print(dictionary['strength'])
		applicants_list.append(dictionary)

	return render_template('applicants.html', applicants = applicants_list, job = job)

@app.route('/shortlist/<int:job_id>', methods = ['POST'])
def shortlist(job_id):
	if (request.method == 'POST'):
		user_id = int(request.form.get('hid'))
		db.session.query(user_job).filter_by(user_id = user_id, job_id = job_id).update(dict(status='Shortlisted'))
		db.session.commit()
	return redirect(url_for('applicants', job_id = job_id))

@app.route('/job-form', methods = ['GET', 'POST'])
@login_required
def job_form():
	if (current_user.is_admin == True):
		form = AddJobForm()
		if form.validate_on_submit():
			job = Job(role = form.role.data, job_desc = form.job_desc.data, skills_required = form.skills_required.data, work_location = form.work_location.data, salary = form.salary.data, deadline = form.deadline.data)
			db.session.add(job)
			db.session.commit()

			preprocessed = preprocess.preprocess_text(str(form.job_desc.data) + ' ' + str(form.skills_required.data))
			txtfile = open(f"./static/jd_preprocessed/{job.id}.txt", "w")
			txtfile.write(preprocessed)
			txtfile.close()
			
			flash('New Position has been floated successfully!', 'success')
		return render_template('new-position.html', title = 'Add new Job', form = form)
	else:
		return '<h2>Only admin can view this page</h2>'


@app.route('/apply/<job_id>', methods=['GET', 'POST'])
@login_required
def apply(job_id):
	if (request.method == 'GET'):
		return redirect(url_for('position', job_id = job_id))
	if (current_user.resume == ''):
		flash('Please upload your resume in the profile section before applying', 'danger')
		return redirect(url_for('position', job_id = job_id))
	
	user = User.query.get(current_user.id)
	job = Job.query.get(job_id)

	if (datetime.datetime.now() > job.deadline):
		flash('Deadline has already been passed!', 'danger')
		return redirect(url_for('position', job_id = job_id))

	user.applied_at.append(job)
	db.session.commit()

	docs = []
	filename = user.resume.split('.')[0]
	with open(f"./static/resume_preprocessed/{filename}.txt", "r") as f:
		docs.append(f.readlines()[0])

	with open(f"./static/jd_preprocessed/{job_id}.txt", "r") as f:
		docs.append(f.readlines()[0])

	vectors = vectorizer.get_tfidf(docs)
	similarity = int(cosine_similarity(vectors[0], vectors[1]) * 100)

	db.session.query(user_job).filter_by(user_id = user.id, job_id = job_id).update(dict(match=similarity))
	db.session.commit()

	flash(f'You have successfully applied for {job.role} position!', 'success')
	return redirect(url_for('explore'))


if (__name__ == '__main__'):
	app.run(debug = True)