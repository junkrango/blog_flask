from functools import wraps

from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, session
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import main
from .. import db
from .forms import PostForm, LoginForm, CommentForm, CateForm
from ..models import Post, User, Category, Comment
from werkzeug.security import generate_password_hash, check_password_hash



@main.route('/test/', methods=['GET','POST'])
def test():
    return render_template('edit.html')


def user_login_req(f):
    """
    登录装饰器
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            flash("请登录后操作", "err")
            return redirect(url_for(".login"))
        return f(*args, **kwargs)

    return decorated_function


@main.route('/', methods=['GET','POST'])
def index():
    cates = Category.query.all()
    posts = Post.query.all()
    category = None
    return render_template('index.html',cates=cates, posts=posts, category=category)


@main.route('/cate/<cate>/', methods=['GET','POST'])
def category(cate):
    cates = Category.query.all()
    if cate is None:
        posts = Post.query.all()
    else:
        posts = Post.query.filter_by(cate_id=cate).all()
    category = Category.query.filter_by(id=cate).first()
    return render_template('index.html',cates=cates, posts=posts, category=category)


@main.route("/login/", methods=["GET", "POST"])
def login():
    """
    登录
    """
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=data["name"]).first()
        if user:
            if not user.check_pwd(data["pwd"]):
                flash("密码错误！", "err")
                return redirect(url_for(".login"))
        else:
            flash("账户不存在！", "err")
            return redirect(url_for(".login"))
        session["user"] = user.name
        session["user_id"] = user.id
        return redirect(url_for(".index"))
    return render_template("login.html", form=form)


@main.route("/logout/")
def logout():
    """
    退出登录
    """
    # 重定向到home模块下的登录。
    session.pop("user", None)
    session.pop("user_id", None)
    return redirect(url_for('.login'))

@main.route("/add/", methods=['GET','POST'])
@user_login_req
def add():
    """
    添加文章
    """
    category = Category.query.all()
    form = PostForm()
    res = Category.query.all()
    '''
    动态添加wtforms SelectField 怎么动态添加option项
    '''
    form.cate.choices += [(str(r.id), r.cate) for r in res]
    if form.validate_on_submit():
        post = Post(name=form.name.data,body=form.body.data,cate_id=form.cate.data)
        db.session.add(post)
        db.session.commit()
        form.cate.choices = []
        return redirect(url_for('.index'))
    return render_template('add.html',form=form,category=category)


@main.route("/detail/<id>", methods=['GET','POST'])
def detail(id):
    form = CommentForm()
    post = Post.query.filter_by(id=id).first()
    comments = Comment.query.filter_by(post_doc_id=id)
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,post_doc_id=id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('.detail', id=id))
    return render_template('markdown_to_html.html', post=post,comments=comments,form=form)


@main.route("/edit/<int:id>", methods=['GET','POST'])
@user_login_req
def edit(id):
    category = Category.query.all()
    form = PostForm()
    res = Category.query.all()
    '''
    动态添加wtforms SelectField 怎么动态添加option项
    '''
    form.cate.choices += [(str(r.id), r.cate) for r in res]
    post = Post.query.filter_by(id=id).first()
    if form.validate_on_submit():
        post = Post.query.filter_by(id=id).first()
        post.name = form.name.data
        post.body = form.body.data
        post.cate_id = form.cate.data
        db.session.add(post)
        db.session.commit()
        form.cate.choices = []
        return redirect(url_for('.detail', id=id))
    return render_template('edit.html',form=form,post=post,category=category)


@main.route("/add_cate/", methods=['GET','POST'])
@user_login_req
def add_cate():
    form = CateForm()
    if form.validate_on_submit():
        cate = Category(cate= form.body.data)
        db.session.add(cate)
        db.session.commit()
        return redirect(url_for('.index'))
    return render_template('add_cate.html',form=form)























