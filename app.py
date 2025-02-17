from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)
app.secret_key = 'your_secret_key'

users = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/nutrition')
def nutrition():
    return render_template('nutrition.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users:
            flash('User already exists', 'danger')
            return redirect(url_for('register'))

        users[username] = generate_password_hash(password)
        flash('User registered successfully', 'success')
        return redirect(url_for('login'))
    print("Register page accessed") 
    return render_template('auth.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid credentials', 'danger')
    print("Login page accessed") 
    return render_template('auth.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please log in first', 'warning')
        return redirect(url_for('login'))
    
    return f'Hello, {session["username"]}! Welcome to your dashboard.'

# Reviews Feature
reviews = []

@app.route('/review', methods=['GET', 'POST'])
def review():
    if request.method == 'POST':
        review = {
            'name': request.form['name'],
            'email': request.form['email'],
            'title': request.form['title'],
            'message': request.form['message'],
            'rating': request.form['rating'],
            'visit_date': request.form['visit_date'],
        }
        reviews.append(review)
        flash('Review submitted successfully', 'success')

    return render_template('review.html', reviews=reviews)

# REST API User Management
api_users = [
    {"id": 1, "name": "John Doe"},
    {"id": 2, "name": "Jane Doe"}
]

class UserList(Resource):
    def get(self):
        return api_users  

    def post(self):
        if not request.is_json:
            return {"error": "Request must be JSON"}, 400
        
        new_user = request.get_json()
        new_user["id"] = len(api_users) + 1  
        api_users.append(new_user)
        return new_user, 201  

class User(Resource):
    def get(self, user_id):
        user = next((u for u in api_users if u["id"] == user_id), None)
        return user if user else {"message": "User not found"}, 404

    def delete(self, user_id):
        global api_users
        user = next((u for u in api_users if u["id"] == user_id), None)
        if not user:
            return {"message": "User not found"}, 404
        api_users = [u for u in api_users if u["id"] != user_id]
        return {"message": "User deleted"}, 200

api.add_resource(UserList, "/users")
api.add_resource(User, "/users/<int:user_id>")

if __name__ == '__main__':
    app.run(debug=True)
