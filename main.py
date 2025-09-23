from flask import Flask, render_template, request, redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_bootstrap import Bootstrap
import os

app = Flask(__name__)
app.config['DEBUG'] = True

#configure the app
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\742232\\DB.Browser.for.SQLite-v3.13.1-win64\\coffee.db'
app.config['SECRET_KEY'] = 'your-secret-key-here'  # change to your secret key
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#initialize database and Bcrypt
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
bootstrap = Bootstrap(app)

#initialize LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

#set the upload folder (if needed)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#user Model for authentication
class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    def __repr__(self):
        return f'<User {self.username}>'

#customer Model for registration and login
class Customer(db.Model, UserMixin):
    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    def __repr__(self):
        return f'<Customer {self.username}>'
    from flask import flash

"""
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
"""

@login_manager.user_loader
def load_user(id):
    return Customer.query.get(int(id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        checkemail = Customer.query.filter_by(email=email).first()
        checkuser = Customer.query.filter_by(username=username).first()

        if checkemail:
            flash("Please register using a different email.", 'danger')
            return render_template("register.html")

        elif checkuser:
            flash("Username already exists!", 'danger')
            return render_template("register.html")
        
        new_customer = Customer(username=username, email=email, password=hashed_password)
        db.session.add(new_customer)
        db.session.commit()
        flash("Registration successful! Please log in.", 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
#Check if the user exists in the database
        customer = Customer.query.filter_by(username=username).first()
        if customer and bcrypt.check_password_hash(customer.password, password):
            login_user(customer)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    return render_template('home.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        #export_to_xml()
    app.run(debug=True)
 