from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Blogz:password@localhost:3306/Blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "mF7%z9LWw4$zj20a"


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    def __init__(self, title, body,owner):
        self.title = title
        self.body = body
        self.owner = owner     

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self,username,password):
        self.username = username
        self.password = password

@app.before_request  #Require login function
def require_login():
    allowed_routes = ['login', 'blog', 'signup', 'index']

    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()  #create userlist
   # print (users)
    return render_template('index.html', users=users,header="ALL USERS")

@app.route('/blog')
def blog():
    blog_id = request.args.get('id')
    posts = Blog.query.all()
    #amending Blog constructor to take in user object
    user_id = request.args.get('user')

    #if blog_id == None:
     #   posts = Blog.query.all()
      #  return render_template('blog.html', posts=posts, title='Build-a-blog')
    #else:
     #   post = Blog.query.get(blog_id)
      #  return render_template('entry.html', post=post, title='Blog Entry')

    #Gotta make user pages work now....
    if user_id:
        posts = Blog.query.filter_by(owner_id=user_id)
        return render_template('user.html', posts=posts, header="User Posts")
    if blog_id:
        post = Blog.query.get(blog_id)
        return render_template('entry.html', post=post )

    return render_template('blog.html', posts=posts, header='All Posts')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    #add user that owns post to post
    owner = User.query.filter_by(username=session['username']).first()

    
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-entry']
        title_error = ''
        body_error = ''

        if not blog_title:
            title_error = "Please enter a blog title"
        if not blog_body:
            body_error = "Please enter a blog entry"

        if not body_error and not title_error:
            new_entry = Blog(blog_title, blog_body, owner)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) 
        else:
            return render_template('newpost.html', title='New Entry', title_error=title_error, body_error=body_error, 
                blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newpost.html', header='New Entry')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()     

        if user and user.password == password:                      
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        else:
            flash('User password incorrect, or incorrect username', 'error')
    
    return render_template('login.html', header='Login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()

        if password != verify:
            flash('Password does not match', "error")
        elif len(username) < 3 or len(password) < 3:
            flash('Username and password must be more than 3 characters', 'error')
        elif existing_user:
            flash('User already exists', 'error')/newpost
        else:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html', header='Signup')

@app.route('/logout')     #Adding Logout Function/Navigation in base.html too
def logout():
    del session['username']
    return redirect('/blog') 

if  __name__ == "__main__":
    app.run()