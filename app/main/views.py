from flask import render_template,redirect,url_for,abort,request,flash
from . import main
from app.models import User,Blog,Comment,Subscriber
from .forms import UpdateProfile,CreateBlog
from .. import db, photos
from app.requests import get_posts
from flask_login import login_required,current_user
from ..email import mail_message


@main.route('/')
def index():
    posts = get_posts()
    blogs = Blog.query.order_by(Blog.date.desc())
    return render_template('index.html', post = posts,blogs=blogs)



@main.route('/user/<name>')
def profile(name):
    user = User.query.filter_by(username = name).first()
    user_id = current_user._get_current_object().id
    #blog = Blog.query.filter_by(user_id = user_id).all()
    if user is None:
        abort(404)
    return render_template("profile/profile.html", user = user,blog=blog)

@main.route('/user/<name>/updateprofile', methods = ['POST','GET'])
@login_required
def updateprofile(name):
    form = UpdateProfile()
    user = User.query.filter_by(username = name).first()
    if user == None:
        abort(404)
    if form.validate_on_submit():
        user.bio = form.bio.data
        user.username = form.username.data
        user.email = form.email.data
        user.save()
        return redirect(url_for('main.index',name = name))
    return render_template('profile/update.html',form =form)


@main.route('/user/<name>/update/profile',methods= ['POST'])
@login_required
def update_profile(name):
    user = User.query.filter_by(username = name).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        db.session.commit()
    return redirect(url_for('main.profile',name=name))


@main.route('/new_post', methods=['POST','GET'])
@login_required
def new_blog():
    subscribers = Subscriber.query.all()
    form = CreateBlog()
    if form.validate_on_submit():
        title = form.title.data
        post = form.post.data
        user_id =  current_user._get_current_object().id
        blog = Blog(title=title,post=post,user_id=user_id)
        blog.save()
        return redirect(url_for('main.index'))
        flash('New Post have been created')
    return render_template('newblog.html', form = form)


@main.route('/blog/<id>')
def blog(id):
    comments = Comment.query.filter_by(blog_id=id).all()
    blog = Blog.query.get(id)
    return render_template('blog.html',blog=blog,comments=comments)
    

@main.route('/blog/<blog_id>/update', methods = ['GET','POST'])
@login_required
def updateblog(blog_id):
    blog = Blog.query.get(blog_id)
    if blog.user != current_user:
        abort(403)
    form = CreateBlog()
    if form.validate_on_submit():
        blog.title = form.title.data
        blog.post = form.post.data
        db.session.commit()
        flash("post updated")
        return redirect(url_for('main.blog',id = blog.id)) 
    if request.method == 'GET':
        form.title.data = blog.title
        form.post.data = blog.post
    return render_template('newblog.html', form = form)


@main.route('/blog/<blog_id>/delete', methods = ['POST'])
@login_required
def delete_post(blog_id):
    blog = Blog.query.get(blog_id)
    if blog.user != current_user:
        abort(403)
    blog.delete()
    flash("Done")
    return redirect(url_for('main.index'))

@main.route('/comment/<blog_id>', methods = ['Post','GET'])
@login_required
def comment(blog_id):
    blog = Blog.query.get(blog_id)
    comment =request.form.get('newcomment')
    new_comment = Comment(comment = comment, user_id = current_user._get_current_object().id, blog_id=blog_id)
    new_comment.save()
    return redirect(url_for('main.blog',id = blog.id))



@main.route('/comment/<comment_id>/delete', methods = ['POST'])
@login_required
def delete_comment(comment_id):
    comment = comment.query.get(comment_id)
    if comment.user != current_user:
        abort(403)
    comment.delete()
    flash("Done")
    return redirect(url_for('main.blog'))


@main.route('/subscribe',methods = ['POST','GET'])
def subscribe():
    email = request.form.get('subscriber')
    new_subscriber = Subscriber(email = email)
    new_subscriber.save_subscriber()
    flash('Done')
    return redirect(url_for('main.index'))






