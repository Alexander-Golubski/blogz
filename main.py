from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:cheesy@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship("Blog", backref="owner") 
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ["login", "signup"]
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")

@app.route('/blog', methods=['POST', 'GET'])
def index():
    blogs = Blog.query.all()
    blog_id = request.args.get('id')
    sel_blog = Blog.query.filter_by(id=blog_id).first()

    if blog_id:
        return render_template('blog-page.html', blog=sel_blog)

    return render_template('index.html', title='Blog', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    title_error = ''
    body_error = ''

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        
        blog_title = request.form['title']
        if blog_title == '':
            title_error = 'Please enter a title.'
        
        body = request.form['body']
        if body == '':
            body_error = 'Please enter the body text.'

        if not title_error and not body_error:
            
            new_post = Blog(blog_title, body, owner)
            db.session.add(new_post)
            db.session.commit()

            blog_id = new_post.id
            
            return redirect('/blog?id={}'.format(blog_id))
        else:
            return render_template('newpost.html', title='New Post', 
        title_error=title_error, body_error=body_error, blog_title=blog_title, body=body)

    return render_template('newpost.html', title='New Post', 
        title_error=title_error, body_error=body_error)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Username not in database', 'error')
        elif user.password == password:
            session["username"] = username
            flash("Logged in")
            return redirect("/newpost")
        else:
            flash("Incorrect password", 'error')        

    return render_template("login.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():

    error = ''

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        verify = request.form["verify"]
        existing_user = User.query.filter_by(username=username).first()

        if len(username) > 20:
            error = "Username must be 20 characters or less"
        elif len(username) < 3:
            error = "Username must have 3 or more characters"
        elif len(password) < 3:
            error = "Password must have 3 or more characters"
        elif password != verify:
            error = "Password and verification do not match"
        elif username == '' or password == '' or verify == '':
            error =  "Please enter a username, password, and verification"
        if not existing_user:
        #elif len(username) <= 20 and len(username) > 3 and len(password) > 3 and password == verify and not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            return redirect("/newpost")
        else:
            error = 'Username already exists'

    return render_template("signup.html", error=error)

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/blog")

if __name__ == '__main__':
    app.run()