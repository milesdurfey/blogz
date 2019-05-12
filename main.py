from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzzer@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password =db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog_display']
    if request.endpoint not in allowed_routes and'username' not in session:
        return redirect('/login')


@app.route("/", methods=['POST','GET'])
def index():
    all_users = User.query.all()
    return render_template('index.html', title="Loading Page", all_users=all_users)


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in", 'success')
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
            
    return render_template('login.html')


@app.route('/signup', methods=['POST','GET'])
def signup():
    title = "Signup"
    username = ''
    password = ''
    verify = ''
    username_error = ''
    password_error = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        
        countuserspace = 0
        countpwspace = 0
        
        if username != '':
            for i in username:
                if i == " ":
                    countuserspace += 1
            if countuserspace != 0:
                username_error = 'Spaces are not allowed in usernames.'
                flash (username_error, 'error')
                username = ''                
            else:
                if len(username) < 3 or len(username) > 20:
                    username_error = 'Username must be between 3 and 20 characters. Re-enter with a different username. '
                    flash (username_error, 'error')
                    username = ''
        else:
            username_error = 'Username cannot be blank'
            flash (username_error, 'error')
            

        if password != '':
            for i in password:
                if i == " ":
                    countpwspace += 1
            if countpwspace != 0:
                password_error = 'Spaces are not allowed in passwords.'
                flash (password_error,'error')
            else:
                if len(password) < 3 or len(password) > 20:
                    password_error = 'Password must be between 3 and 20 characters'
                    flash (password_error,'error')
                         
            if verify != password:
                password_error = 'Passwords do not match. Re-enter password and confirmation.'
                flash (password_error,'error')
                
        else:
            password_error = 'Password cannot be blank.'
            flash (password_error, 'error')
            
        # Validate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user and not username_error and not password_error :
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash ("Sign up successful. Welcome!", 'success')
            return redirect('/newpost')
        else:
            if existing_user == username:
                flash ('Duplicate username, please re-register with a different username', 'error')
                username = ''
    
    return render_template('signup.html', title = title, username = username)



@app.route('/newpost', methods=['POST', 'GET'])
def new_blog_entry():
    display_title = "Add a Blog Entry"
    title_of_blog = ''
    body_of_blog = ''
    title_error = ''
    body_error = ''

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        
        title_of_blog = request.form['title_of_blog']
        body_of_blog = request.form['body_of_blog']
        load_to_database = Blog(title_of_blog, body_of_blog, owner)

        if title_of_blog == "":
            title_error = "Please title your blog"

        if body_of_blog == "":
            body_error = "Please fill in your new blog"

        if (not title_error) and (not body_error):
            db.session.add(load_to_database)
            db.session.commit()
            flash ("Blog added successfully!", 'success')
            return redirect('/blog?id={}'.format(load_to_database.id))
    blogs = Blog.query.filter_by(owner=owner).all()

    return render_template('newpost.html', title=display_title, title_of_blog=title_of_blog, title_error=title_error, body_of_blog = body_of_blog, body_error=body_error)    

@app.route('/blog', methods=['POST', 'GET'])
def blog_display():
    display_blog = Blog.query.all()
    display_id = request.args.get('id')
    display_user = request.args.get('user')
    display_title = ""

    if display_id:
        display_blog = Blog.query.filter_by(id=display_id)
        return render_template('singleentry.html', title = "Single Blog Entry", blog = display_blog, id = display_id)
    if display_user:
        display_blog = Blog.query.filter_by(owner_id = display_user)
        return render_template('singleauthor.html', title = "Author's Blogs", blog = display_blog)
     
    return render_template('blog.html', title = "All blogs", blog = display_blog)


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')

if __name__ == '__main__':
    app.run()
