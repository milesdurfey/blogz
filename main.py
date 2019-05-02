from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blogger@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text())

    def __init__(self,title,body):
        self.title = title
        self.body = body


@app.route('/newpost', methods=['POST', 'GET'])
def new_blog_entry():
    display_title = "Add a Blog Entry"
    title_of_blog = ''
    body_of_blog = ''
    title_error = ''
    body_error = ''

    if request.method == 'POST':
        
        title_of_blog = request.form['title_of_blog']
        body_of_blog = request.form['body_of_blog']
        load_to_database = Blog(title_of_blog, body_of_blog)

        if title_of_blog == "":
            title_error = "Please title your blog"

        if body_of_blog == "":
            body_error = "Please fill in your new blog"

        if (not title_error) and (not body_error):
            db.session.add(load_to_database)
            db.session.commit()
            return redirect('/blog?id={}'.format(load_to_database.id))

    return render_template('newpost.html', title=display_title, title_of_blog=title_of_blog, title_error=title_error, body_of_blog = body_of_blog, body_error=body_error)    

@app.route('/blog', methods=['POST', 'GET'])
def blog_display():
    display_id = request.args.get('id')
    display_title = "Main Blog Page"

    if display_id:
        display_blog = Blog.query.filter_by(id=display_id).all()
        return render_template('blog.html', title = display_title, blog = display_blog, id = display_id)
    else:
        display_blog = Blog.query.order_by(Blog.id.desc()).all()
        return render_template('blog.html', title = display_title, blog = display_blog)

@app.route("/", methods=['POST','GET'])
def index():
    return render_template('index.html', title="Loading Page")


if __name__ == '__main__':
    app.run()
