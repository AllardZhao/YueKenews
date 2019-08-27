# -*- coding:UTF-8 -*-
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# 引入forms模块
from forms import NewsForm

app = Flask(__name__)
# mysql://username:password@server/db
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost:3306/mysql_wangyinews?charset=utf8'
# 设置flask app secret key
app.config['SECRET_KEY'] = 'a random string'
# 通过app构建一个新的对象
db = SQLAlchemy(app)


class News(db.Model):
    __tablename__ = 'news'      # 新建数据库表名

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(2000), nullable=False)
    types = db.Column(db.String(10), nullable=False)
    image = db.Column(db.String(300), )
    author = db.Column(db.String(20), )
    view_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    is_valid = db.Column(db.Boolean)

    # 通过用__repr__()方法将返回地址对应的数据
    def __repr__(self):
        return '<News %r>' % self.title


@app.route('/')
def index():   # 根目录
    ''' 新闻首页 '''
    # 传入所有数据有效信息is_valid=1
    news_list = News.query.filter_by(is_valid=1)
    # 使用 render_template() 方法来渲染模板
    return render_template('index.html', news_list=news_list)


@app.route('/cat/<name>/')
def cat(name):
    ''' 新闻类别 '''
    news_list = News.query.filter(News.types == name)
    # 查询类别为 name 的新闻数据
    return render_template('cat.html', name=name, news_list=news_list)


# pk前面加(int:)限制传入的参数为整形
@app.route('/detail/<int:pk>/')
def detail(pk):
    ''' 新闻详细信息 '''
    new_obj = News.query.get(pk)
    return render_template('detail.html', new_obj=new_obj)


@app.route('/admin/')
@app.route('/admin/<int:page>/')
def admin(page=None):
    ''' 新闻管理首页'''
    # 如果没有传，则表示第一页
    if page is None:
        page = 1
    # page=第几页，per_page=每页数量,filter_by筛选出is_valid=1数据
    news_list = News.query.filter_by(is_valid=True).paginate(
        page=page, 
        per_page=3)
    return render_template('admin/index.html', news_list=news_list)


@app.route('/admin/add/',  methods=('GET', 'POST'))
def add():
    ''' 新增新闻数据 '''
    form = NewsForm()
    if form.validate_on_submit():
        # 获取数据
        new_obj = News(
            title=form.title.data,
            content=form.content.data,
            author=form.author.data,
            types=form.types.data,
            image=form.image.data,
            created_at=datetime.now(),
            is_valid=True
        )
        # 保存数据
        db.session.add(new_obj)
        db.session.commit()
        # 文字提示
        # flash
        return redirect(url_for('admin'))  # 跳转到后台首页
    return render_template('admin/add.html', form=form)


@app.route('/admin/update/<int:pk>/',  methods=('GET', 'POST'))
def update(pk):
    ''' 修改新闻数据 '''
    new_obj = News.query.get(pk)
    # 如果没有数据，则返回
    if not new_obj:
        # TODO 使用Flash进行文字提示用户
        return redirect(url_for('admin'))
    form = NewsForm(obj=new_obj)
    if form.validate_on_submit():
        # 获取数据
        new_obj.title = form.title.data
        new_obj.content = form.content.data
        new_obj.types = form.types.data
        new_obj.image = form.image.data
        # 保存数据
        db.session.add(new_obj)
        db.session.commit()
        return redirect(url_for('admin')) # 跳转到后台首页
    return render_template('admin/update.html', form=form)


@app.route('/admin/delete/<int:pk>/',  methods=('GET', 'POST'))
def delete(pk):
    ''' 删除新闻数据 '''
    new_obj = News.query.get(pk)
    if not new_obj:
        return 'no'
    new_obj.is_valid = False
    db.session.add(new_obj)
    db.session.commit()
    return 'yes'
if __name__ == '__main__':
    app.run(debug=True)