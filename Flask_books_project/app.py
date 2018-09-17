from flask import Flask,render_template,flash,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
app = Flask(__name__)

#数据库配置：数据库地址/关闭自动跟踪
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:xxh19971124@127.0.0.1/flask_books'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key='ithie'
#创建数据库对象
db = SQLAlchemy(app)
'''
1. 配置数据库
    a.导入SQLAlchemy扩展     
    b.创建db对象并配置参数
    c.创建数据库
2. 添加书和作者的模型
    a.模型继承db.Model
    b.表名__tablename__
    c.db.Column：字段
    d.db.relationship:关系引用
3. 添加数据
4. 使用模板显示数据库查询数据
    a.查询所有作者信息，让信息传递给模板
    b.模板中按照格式依次for循环作者和书籍（作者获取书籍用关系引用）
5. 使用WTF显示表单
    a.自定义表单类
    b.模板中显示
    c.设置secret_key/csrf_token
6. 实现相关增删逻辑
    a.增加数据
    b.删除数据-->网页中删除-->点击发送书籍ID给删除书籍的路由-->路由需要接受参数
    url_for使用/for else的使用/redirect的使用
    c.删除作者
'''

# 定义书和作者模型
# 作者模型

class Author(db.Model):
    __tablename__ = 'authors' # 表名
    # 字段
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(16),unique=True)
    # 关系引用
    # books是给自己（Author模型）用的，author是给Book模型用
    books = db.relationship('Book',backref='author')

    def __repr__(self):
        return 'Author:%s' %self.name

class Book(db.Model):
    __tablename__='books'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(16),unique=True)
    author_id = db.Column(db.Integer,db.ForeignKey('authors.id'))

    def __repr__(self):
        return 'Book:%s %s' %(self.name,self.author_id)

#自定义表单类
class AuthorForm(FlaskForm):
    author = StringField('作者：',validators=[DataRequired()])
    book = StringField('书籍：',validators=[DataRequired()]) #validators必须是一个iteration
    submit = SubmitField('提交')

@app.route('/delete_author/<author_id>')
def delete_author(author_id):
    # 1.查询数据库，是否有该ID的作者，如果有就删除(先删书，再删作者)，没有提示错误
    author = Author.query.get(author_id)

    # 2.如果有就删除(先删书，再删作者)
    if author:
        try:
            # 查询之后直接删除
            Book.query.filter_by(author_id=author_id).delete()
            # 删除作者
            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除作者错误')
            db.session.rollback()
    else:
        flash('作者找不到')

    return redirect(url_for('index'))


@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    # 1.查询数据库是否有该ID的书，如果有就删除，没有就提示错误
    book = Book.query.get(book_id)
    # 2. 如果有就删除
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除书籍出错')
            db.session.rollback()
    # 没有就提示错误
    else:
        flash('书籍找不到')
    # 如何返回当前网址 --> 重定向
    # redirect:重定向，需要传入网络/路由地址
    # url_for():需要传入视图函数名，返回该视图函数对应的路由地址
    return redirect(url_for('index'))
    # 相当于return redirect('/')


@app.route('/',methods=['GET','POST'])
def index():

    #创建自定义表单类
    author_form = AuthorForm()
    # 查询所有的作者信息，将信息传递给模板

    '''
    验证逻辑：
    1.调用wtf的函数实现验证
    2.验证通过获取数据
    3.判断作者是否存在
    4.如果作者存在，判断书籍是否存在，没有重复书籍就添加书籍，如果重复提示错误
    5.如果作者不存在，添加作者和书籍
    6.验证不通过就提示错误
    '''

    1.
    # 调用wtf的函数实现验证
    if author_form.validate_on_submit():
        # 2.验证通过获取数据
        author_name = author_form.author.data
        book_name = author_form.book.data
        # 3.判断作者是否存在
        author = Author.query.filter_by(name=author_name).first()
        # 4.如果作者存在，
        if author:
            # 判断书籍是否存在，
            book = Book.query.filter_by(name=book_name).first()
            # 如果重复提示错误
            if book:
                flash('已存在同名书籍')
            # 没有重复书籍就添加书籍，
            else:
                try:
                    new_book = Book(name=book_name,author_id=author.id)
                    db.session.add(new_book)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    flash('添加书籍失败')
                    db.session.rollback()

        # 5.如果作者不存在，添加作者和书籍
        else:
            try:
                new_author = Author(name=author_name)
                db.session.add(new_author)
                db.session.commit()

                new_book = Book(name=book_name,author_id=new_author.id)
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                print(e)
                flash('添加作者和书籍失败')
                db.session.rollback()

    else:
        # 6.验证不通过就提示错误
        if request.method=='POST':
            flash('参数不全')
    authors = Author.query.all()
    return render_template('books.html',authors = authors,form = author_form)


db.drop_all()

db.create_all()

# 生成数据
au1 = Author(name='老王')
au2 = Author(name='老惠')
au3 = Author(name='老刘')

# 把数据提交给用户会话
db.session.add_all([au1,au2,au3])
#提交会话
db.session.commit()

bk1 = Book(name='老王回忆录',author_id=au1.id)
bk2 = Book(name='我读书少，你别骗我',author_id=au1.id)
bk3 = Book(name='如何才能让自己更骚',author_id=au2.id)
bk4 = Book(name='如何征服美丽少女',author_id=au3.id)
bk5 = Book(name='如何征服英俊少男',author_id=au3.id)

# 把数据提交给用户会话
db.session.add_all([bk1,bk2,bk3,bk4,bk5])
db.session.commit()


app.run(debug=True)
