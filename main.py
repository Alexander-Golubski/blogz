from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildthisblog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
#inherits some traits from existing class Model within SQLAlchemy

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    #owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body):
        self.title = title
        self.body = body

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

    if request.method == 'POST':
        
        blog_title = request.form['title']
        if blog_title == '':
            title_error = 'Please enter a title.'
        
        body = request.form['body']
        if body == '':
            body_error = 'Please enter the body text.'

        if not title_error and not body_error:
            new_post = Blog(blog_title, body)
            db.session.add(new_post)
            db.session.commit()

            blog_id = new_post.id
            
            return redirect('/blog?id={}'.format(blog_id))
        else:
            return render_template('newpost.html', title='New Post', 
        title_error=title_error, body_error=body_error, blog_title=blog_title, body=body)

    return render_template('newpost.html', title='New Post', 
        title_error=title_error, body_error=body_error)

if __name__ == '__main__':
    app.run()