# Flask 开发论坛 - 用户验证

## 写在前面

昨天我用Python+很多很多的诗词数据做了一个随机诗词生成器，忙活了一天，到最后程序写的诗也没有韵律，直接放弃，还是再来写论坛吧。

完整目录在
[这里](https://zhuanlan.zhihu.com/p/113539585)

## 请注意

这次的文章有点长（32150字），可能要花点时间，可以分段阅读。（我听别人说知乎有两万字的字数限制，没有发现啊）

## 进入正题

在
[上一篇文章](https://zhuanlan.zhihu.com/p/113477674)
里，我们已经创建了数据库，现在就是时候让用户注册，登录了。首先，打开app/auth/init.py，更改一处代码：
```python
# app/auth/__init__.py

from flask import Blueprint

auth = Blueprint('auth', __name__, url_prefix='/auth')  # 设置URL前缀

from . import views
```
这里我更改了创建Blueprint的部分，添加了URL前缀，即所有在auth蓝图中的视图URL都以/auth开头，就不用再敲它了（归根结底还是懒，逃）

现在，开始写视图函数：
```python
# app/auth/views.py

from . import auth
from app.models import User
from flask import render_template


@auth.route('/register/')
def register():
    return render_template('auth/register.html')

```
这里必须要吐槽一下Pycharm，昨天还没有显示我main视图中没有模板文件呢，结果今天把Pycharm重启了一下就提示了（当然我创建了模板），无奈之下只好把这个功能关了。。。

好了，回归正题。在这个视图中，我们只渲染了模板，没有做数据库操作，但是一会会弄的。但是不管是登录还是注册，都必须有表单，所以我用了flask-wtf（这里其实我纠结了很久，因为wtf渲染的表单限制太多了，但是还是用了，因为懒）。

先安装它：
```text
pip install flask-wtf
```
初始化：

没有初始化，开箱即用

先在auth目录下新建forms.py，来存储所有表单：
```python
# app/auth/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Regexp, Email, Length


class RegistrationForm(FlaskForm):  # RegistrationForm继承自FlaskForm
    # StringField用来获取字符型数据，validators是验证器，Regexp中填写的是正则表达式
    username = StringField('用户名', validators=[DataRequired(message='请输入用户名'), Regexp('^[A-Za-z][A-Za-z0-9_.]*$',
                                                                                     0, '用户名只能包含字母，数字，点'
                                                                                        '或下划线'), Length(1, 64)])
    # Email验证器用来验证输入是否是邮箱格式，但不确保邮箱是否存在
    email = StringField('邮箱', validators=[DataRequired(message='请输入邮箱'), Email(message='请输入真实的邮箱地址')])
    password = PasswordField('密码', validators=[DataRequired(message='请输入密码')])
    submit = SubmitField('注册')

```
现在，更改register视图：
```python
# app/auth/views.py

from . import auth
from app.models import User
from flask import render_template
from .forms import RegistrationForm  # 导入表单


@auth.route('/register/')
def register():
    form = RegistrationForm()  # 实例化表单
    return render_template('auth/register.html', form=form)

```
好了，视图总算写完了，现在来编写HTML模板，在templates中新建auth/register.html：
```html
<!--app/templates/register.html-->
{% extends 'base.html' %}
{% from 'bootstrap/form.html' import render_form %}

{% block title %}注册 - AttributeError{% endblock %}

{% block content %}
    <div class="container">
        {{ render_form(form) }}
    </div>
{% endblock %}
```
这里我们使用了Bootstrap-Flask自带的宏渲染模板，让我们来运行一下看看：
![https://pic2.zhimg.com/v2-0a2765695e218fcab0c71b51b6a04069_r.jpg](https://pic2.zhimg.com/v2-0a2765695e218fcab0c71b51b6a04069_r.jpg)

程序发生了RuntimeError！这是因为我没有设置SECRET_KEY。在config.py中加入两行：
```python
# app/config.py

import os


class DevelopmentConfig:
    # ...
    # 不跟踪变化
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'this is my secret key!!'  # 设置密钥


class ProductionConfig:
    # ...
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret key'  # 生产环境首先使用环境变量中的密钥


# ...
```
现在在运行程序，就正常了：
![https://pic3.zhimg.com/v2-242a73f9a09ac4663211bbaffd5ebb66_r.jpg](https://pic3.zhimg.com/v2-242a73f9a09ac4663211bbaffd5ebb66_r.jpg)

但是，表单的提交按钮不是我们想要的样子。按照计划，它应该是黄色的（primary），但是它是灰色的！Bing了好久之后，发现在官方文档中：
![https://pic2.zhimg.com/v2-ef556e1ea55152cdbcb4097af4d6bc79_r.jpg](https://pic2.zhimg.com/v2-ef556e1ea55152cdbcb4097af4d6bc79_r.jpg)

也就是说，当没有指定button_map时，它默认使用default类的button！让我们更改到primary看看：
```html
<!--app/templates/register.html-->
{% extends 'base.html' %}
{% from 'bootstrap/form.html' import render_form %}

{% block title %}注册 - AttributeError{% endblock %}

{% block content %}
    <div class="container">
        <h1>注册</h1>
        <hr>
        {{ render_form(form, button_map={'submit': 'primary'}) }} {# 将button_map设置为primary #}
    </div>
{% endblock %}
```![https://pic1.zhimg.com/v2-5d28e0d2d4e7216d9ee2a424fc722834_r.jpg](https://pic1.zhimg.com/v2-5d28e0d2d4e7216d9ee2a424fc722834_r.jpg)

但是，当我们提交表单时，Flask返回了Method not allowed错误！再看看flask-bootstrap的文档，发现：
![https://pic2.zhimg.com/v2-2f9a305524fcbc955bf898bc7089ba65_r.jpg](https://pic2.zhimg.com/v2-2f9a305524fcbc955bf898bc7089ba65_r.jpg)

可是不对啊！render_form默认就是使用post，那发生了什么？？？看看自己的代码，发现是自己的视图中没有填写post方式，现在补上：
```python
# app/auth/views.py

from . import auth
from app.models import User
from flask import render_template
from .forms import RegistrationForm  # 导入表单


@auth.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # 实例化表单
    return render_template('auth/register.html', form=form)
```
再刷新网页，bug修复了。但是，可能你注意到了，当提交空信息时，表单中的DataRequired验证器返回的错误信息却还是浏览器默认信息。我搜索了好半天，也没有找到解决办法，无奈只好在GitHub上提了一个issue。目前还没有回复，有的话我会立即更新文章。让我们先暂时不管这个小毛病。

现在，我们再在控制台中打印一下刚刚表单中的信息：
```python
# app/auth/views.py

from . import auth
from app.models import User
from flask import render_template
from .forms import RegistrationForm  # 导入表单


@auth.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # 实例化表单
    if form.validate_on_submit():  # 当form被提交时执行
        print(form.username.data, form.email.data, form.password.data)  # 获取表单信息
    return render_template('auth/register.html', form=form)
```
重新提交后，在控制台中应该会出现类似下面的内容：
```text
Sam sam@example.com 123
```
其中依次是用户名，邮箱，和密码。在这里，注册时只输入一次密码非常容易输错，所以我们应该再添加一个验证密码的区域：
```python
# app/auth/forms.py
# ...
class RegistrationForm(FlaskForm):  # RegistrationForm继承自FlaskForm
    # ...
    password = PasswordField('密码', validators=[DataRequired(message='请输入密码')])
    password2 = PasswordField('确认密码', validators=[DataRequired(message='请输入确认密码'), EqualTo('password', 
                                                                                           message='密码不一致')])
    submit = SubmitField('注册')
```
刷新页面，奇怪的事发生了。原来的DataRequired错误信息竟然在password2中修复了，不过其他表单还是原封不动。。好了，先不管他。我们可以现在开始编写真正的注册功能，但把密码直接放在数据库里不是一个好办法。但是，通过加密，我们可以解决这个问题。我找到了
[Flask-Bcrypt](https://link.zhihu.com/?target=https%3A//flask-bcrypt.readthedocs.io/en/latest/)
用来加密密码。先下载并初始化它：
```text
pip install flask-bcrypt  # 下载
```
初始化：
```python
# app/extensions.py

# ...
from flask_bcrypt import Bcrypt

# 实例化扩展
# ...
bcrypt = Bcrypt()
```
```python
# app/__init__.py

# ...


def create_app():
    app = Flask(__name__)  # 创建app实例
    # ...
    bcrypt.init_app(app)

    # ...

    return app  # 返回app

```
要使用Flask-Bcrypt，要编辑User类：
```python
# app/models.py

from .extensions import db, bcrypt  # 导入SQLAlchemy

# ...

class User(db.Model):  # User类继承自db.Model
    # ...
    password = db.Column(db.String(255))  # 存放密码

    def __init__(self, password, **kwargs):
        super().__init__(password=password, **kwargs)
        self.password = self.set_password(password)  # 初始化时将未加密的密码加密

    def set_password(self, password):
        return bcrypt.generate_password_hash(password)  # 调用Flask-Bcrypt内置函数生成密码哈希值

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)  # 检查密码是否与哈希值对应

    # ...

```
为了为生产环境做准备，我们也可以在Role类里制作一个函数，来自动生成所需的role：
```python
# app/models.py

from .extensions import db, bcrypt  # 导入SQLAlchemy


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    users = db.relationship('User', backref='role', lazy='dynamic')  # 创建一个关联
    
    @staticmethod
    def insert_role():
        print('Inserting roles...', end='')
        roles = ['普通用户', '协管员', '管理员']
        for role in roles:
            if Role.query.filter_by(name=role).first() is None:
                role = Role(name=role)
                db.session.add(role)
        db.session.commit()
        for user in User.query.all():
            if user.role is None:
                user.role = Role.query.filter_by(name='普通用户').first()
                db.session.add(user)
        db.session.commit()
        print('done')

    def __repr__(self):
        return '<Role %s>' % self.name


class User(db.Model):  # User类继承自db.Model
    # ...

```
为了更方便地开发和部署，我们可以制作一个命令来一键部署，并且将各个模型类都自动在flask shell里导入：
```python
# app.py

from app import create_app  # 导入create_app
from app.models import Role, User
from app.extensions import db

app = create_app()  # 创建应用


@app.shell_context_processor  # Flask内置的shell上下文装饰器
def make_shell_context():
    return dict(db=db, Role=Role, User=User)  # 返回包含所有模型的字典


@app.cli.command()  # Flask集成了click，我们可以使用它的命令来轻松创建命令行命令
def deploy():
    """Deploy the application"""
    Role.insert_role()


if __name__ == '__main__':
    app.run(debug=True)  # 运行应用，并开启调试模式

```
在这里，我查看flask的所有命令时，deploy没有出现。但是我把app.py重命名成AttributeError.py（或者其他的名字也可以），就好了。另外我也发现flask shell一直都处在production模式下，我就在根目录下的.env中添加了FLASK_ENV=development这一句，等要部署时再换回来。现在，让我们先把之前测试用的用户和角色删除，打开flask shell：
```python
Python 3.8.1 (v3.8.1:1b293b6006, Dec 18 2019, 14:08:53) 
[Clang 6.0 (clang-600.0.57)] on darwin
App: app [development]
Instance: /Users/sam/Desktop/Python/AttributeError/instance
>>> for user in User.query.all():  # 这里不用导入是因为我们已经在上下文中定义过了
...     db.session.delete(user)  # 循环删除
... 
>>> db.session.commit()  # 提交更改
>>> for role in Role.query.all():
...     db.session.delete(role)
... 
>>> db.session.commit()
```
现在，我们可以用刚才的命令deploy了：
```text
(venv) flask deploy
Inserting roles...done
```
终于，我们可以继续编写视图了：
```python
# app/auth/views.py

from . import auth
from app.models import User, Role
from flask import render_template, flash
from .forms import RegistrationForm  # 导入表单
from app.extensions import db


@auth.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # 实例化表单
    if form.validate_on_submit():  # 当form被提交时执行
        # 获取表单信息
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = User(username=username, email=email, password=password, role=Role.query.filter_by(name='普通用户').first())
        db.session.add(user)
        db.session.commit()
        flash('注册成功', 'success')
    return render_template('auth/register.html', form=form)

```
为了让闪现的消息能够显示，我们需要更改base.html：
```html
<!--app/templates/base.html-->
{# 导入Bootstrap-Flask的内置函数 #}
{% from 'bootstrap/nav.html' import render_nav_item %}
{% from 'bootstrap/utils.html' import render_messages %}
<!DOCTYPE html>
<html lang="en">
<head>
    <!--...-->
</head>
<body>
    <!--...-->
    <br>
    {{ render_messages(container=True, dismissible=True, dismiss_animate=True) }} {# 使用Bootstrap-Flask内置函数渲染闪现消息 #}
    <br>
    {% block content %}{% endblock %} {# 内容块 #}
</body>
{% block scripts %} {# JS代码块 #}
    {{ bootstrap.load_js() }} {# 引入bootstrap-flask内置的JavaScript #}
{% endblock %}
</html>
```
现在，运行程序看看：
![https://pic4.zhimg.com/v2-baff98d7093ef5431847fcdb3abc3267_r.jpg](https://pic4.zhimg.com/v2-baff98d7093ef5431847fcdb3abc3267_r.jpg)

当用户名或邮箱已经被注册时，程序会提示我们。密码和确认密码不一致时，程序也会给我们提示。当注册成功时，程序也会告诉我们。现在，我们可以来编写登录功能了。首先，安装flask-login，它集成了登录所需的东西，比如记住我和访客模式：
```text
pip install flask-login
```
初始化：
```python
# app/extensions.py

from flask_bootstrap import Bootstrap  # 导入Bootstrap-Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# 实例化扩展
bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

```
```python
# app/__init__.py

# ...

def create_app():
    app = Flask(__name__)  # 创建app实例
    # ...
    login_manager.init_app(app)

    # ...

    return app  # 返回app

```
但是，flask-login还需要设置user_loader，来加载用户。让我们定义它：
```python
# app/extensions.py

# ...
from flask_login import LoginManager
from app.models import User

# 实例化扩展
# ...
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # 定义flask-login的登录视图
login_manager.login_message = "请登录后再访问本页"  # 定义flask-login的登录消息，默认为'Please log in to access this page.'


@login_manager.user_loader  # 定义用户加载器
def load_user(id):
    return User.query.get(id)
```
但这还不够。flask-login还需要让User类继承自UserMixin基类，让我们更改models.py：
```python
# app/models.py

from .extensions import db, bcrypt
from flask_login import UserMixin

# ...

class User(db.Model, UserMixin):  # User类继承自db.Model
    # ...
```
现在，我们来编写登录视图，先来创建表单：
```python
# app/auth/forms.py

# ...

class RegistrationForm(FlaskForm):  # RegistrationForm继承自FlaskForm
    # ...
        

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message='请输入用户名')])
    password = PasswordField('密码', validators=[DataRequired(message='请输入密码')])
```
现在，打开auth/views.py，编写视图函数：
```python
@auth.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember_me.data
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('登录成功！', 'success')
            return redirect(url_for('main.index'))
        flash('用户名或密码不正确', 'warning')
    return render_template('auth/login.html', form=form)
```
接下来，编写HTML模板：
```html
<!--app/templates/login.html-->
{% extends 'base.html' %}
{% from 'bootstrap/form.html' import render_form %}

{% block title %}登录 - AttributeError{% endblock %}

{% block content %}
    <div class="container">
        <h1>登录</h1>
        <p>还没有账号？<a href="{{ url_for('auth.register') }}">点击这里</a>注册</p>
        <hr>
        {{ render_form(form, button_map={'submit': 'primary'}) }}
    </div>
{% endblock %}
```
另外，我们也应该在注册页面给出登录的链接：
```html
<!--app/templates/register.html-->
{% extends 'base.html' %}
{% from 'bootstrap/form.html' import render_form %}

{% block title %}注册 - AttributeError{% endblock %}

{% block content %}
    <div class="container">
        <h1>注册</h1>
        <p>已有账号？<a href="{{ url_for('auth.login') }}">点击这里</a>登录</p>
        <hr>
        {{ render_form(form, button_map={'submit': 'primary'}) }} {# 将button_map设置为primary #}
    </div>
{% endblock %}
```
一般的网站也会在导航条上显示登录/注册链接，我们也加上：
```html
<!--app/templates/base.html-->
{# 导入Bootstrap-Flask的内置函数 #}
{% from 'bootstrap/nav.html' import render_nav_item %}
{% from 'bootstrap/utils.html' import render_messages %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}{% endblock %} {# 标题块 #}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='Bootstrap/bootstrap.css') }}"> {# 引入自定义的Bootstrap css #}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <!--...-->
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    {{ render_nav_item('main.index', '首页') }} {# 使用Bootstrap-Flask内置的函数渲染导航链接 #}
                </ul>
                <ul class="navbar-nav ml-auto">
                    {% if not current_user.is_authenticated %}
                        {{ render_nav_item('auth.login', '登录') }}
                        {{ render_nav_item('auth.register', '注册') }}
                    {% else %}
                        <span class="navbar-text">
                            Hi, {{ current_user.username }}
                        </span>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
    <!--...-->
</html>
```
这里，如果用户登录了，导航条右侧将显示Hi, 用户名，否则显示登录和注册链接。

除了登录，注册外，我们还需要登出。flask-login已经为我们做完了，我们只需要调用它就好了：
```python
# app/auth/views.py

from . import auth
from app.models import User, Role
from flask import render_template, flash, redirect, url_for
from .forms import RegistrationForm, LoginForm  # 导入表单
from app.extensions import db
from flask_login import login_user, login_required, logout_user, current_user

# ...

@auth.route('/logout/')
@login_required  # 只有用户登录了才能登出
def logout():
    logout_user()
    flash('你已登出', 'success')
    return redirect(url_for('main.index'))

```
现在，让我们在导航条上显示该链接：
```html
<!--app/templates/base.html-->
<!--...-->
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <a class="navbar-brand" href="/">AttributeError</a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    {{ render_nav_item('main.index', '首页') }} {# 使用Bootstrap-Flask内置的函数渲染导航链接 #}
                </ul>
                <ul class="navbar-nav ml-auto">
                    {% if not current_user.is_authenticated %}
                        {{ render_nav_item('auth.login', '登录') }}
                        {{ render_nav_item('auth.register', '注册') }}
                    {% else %}
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                Hi, {{ current_user.username }}
                            </a>
                            <div class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
                                <a class="dropdown-item" href="{{ url_for('auth.logout') }}">登出</a>
                            </div>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
    <!--...-->
</html>
```
现在，用户就可以登入，登出了。但是，我们还没有验证用户的邮箱是否真实。大多数网站使用的都是验证邮箱的方法，我们也来采取这种方式。首先，你需要在
[Sendgrid](https://link.zhihu.com/?target=http%3A//www.sendgrid.com/)
上注册一个账号，然后在控制面板中创建一个apikey，并将它复制下来，或者放到一个文件里。下面，我们来使用它来认证用户。首先，在User模型中加入confirmed行：
```python
# app/models.py

# ...


class User(db.Model, UserMixin):  # User类继承自db.Model
    # ...
    confirmed = db.Column(db.Boolean, default=False)

    # ...

```
然后迁移数据库：
```text
(venv) flask db migrate
# ... 
(venv) flask db upgrade
```
但是，我们也要限制未认证用户的使用。如果用户未认证（confirmed=False），则不让用户访问除auth蓝图中的视图外的所有页面。取而代之的是一个提醒用户认证的页面。让我们先完成这个功能：（这里插一个小插曲，就在我写这篇文章的时候，在5:37分，知乎除了首页外全部报错502，惊讶）
```python
# app/main/views.py

from flask import render_template, request  # 导入渲染模板函数
from . import main  # 导入蓝图
from flask_login import current_user


@main.route('/')  # 定义路由
def index():
    return render_template('main/index.html')  # 返回渲染后的页面正文

@auth.route('/unconfirmed/')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@main.before_app_request  # 在应用执行每一个请求之前执行的函数
def before_request():
    if not current_user.confirmed and request.blueprint != 'auth':
        return redirect(url_for('auth.unconfirmed'))

```
```html
<!--app/templates/auth/unconfirmed.html-->
{% extends 'base.html' %}

{% block title %}认证你的账号 - AttributeError{% endblock %}

{% block content %}
    <div class="container">
        <h1>Hi, {{ current_user.username }}!</h1>
        <hr>
        <p>你还没有认证你的账号呢！</p>
    </div>
{% endblock %}
```
现在运行程序，如果你上次已经登出或没有选择记住我选项，你可能会看到这个错误：（知乎看来还没完全恢复，无法上传图片，我先复制错误了）
```py3tb
Traceback (most recent call last):
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/app.py", line 2463, in __call__
    return self.wsgi_app(environ, start_response)
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/app.py", line 2449, in wsgi_app
    response = self.handle_exception(e)
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/app.py", line 1866, in handle_exception
    reraise(exc_type, exc_value, tb)
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/_compat.py", line 39, in reraise
    raise value
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/app.py", line 2446, in wsgi_app
    response = self.full_dispatch_request()
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/app.py", line 1951, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/app.py", line 1820, in handle_user_exception
    reraise(exc_type, exc_value, tb)
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/_compat.py", line 39, in reraise
    raise value
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/app.py", line 1947, in full_dispatch_request
    rv = self.preprocess_request()
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/app.py", line 2241, in preprocess_request
    rv = func()
  File "/Users/sam/Desktop/Python/AttributeError/app/main/views.py", line 15, in before_request
    if not current_user.confirmed and request.blueprint != 'auth':
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/werkzeug/local.py", line 347, in __getattr__
    return getattr(self._get_current_object(), name)
AttributeError: 'AnonymousUserMixin' object has no attribute 'confirmed'
```
这次真的是报AttributeError了。。不行，必须修好，要不然白起这个名字了。看了看，是因为原本flask-login内置的AnonymousUserMixin没有confirmed属性，我们给它加上这个判断就好了：
```python
@main.before_app_request  # 在应用执行每一个请求之前执行的函数
def before_request():
    if not current_user.is_anonymous and not current_user.confirmed and request.blueprint != 'auth':
        return redirect(url_for('auth.unconfirmed'))
```
嗯，问题解决了。现在让我们先编写发邮件的函数，首先，我们需要flask-mail来简化操作。先安装它：
```text
(venv) pip install flask-mail
```
初始化：
```python
# app/extensions.py

# ...
from flask_mail import Mail

# 实例化扩展
# ...
mail = Mail()

```
```python
# app/__init__.py

# ...


def create_app():
    app = Flask(__name__)  # 创建app实例
    # ...
    mail.init_app(app)

    # ...

    return app  # 返回app

```
在编写发送邮件的函数前，我们需要添加一些设置。打开根目录下的.env文件，添加如下内容：
```text
MAIL_PASSWORD=<your-apikey>
```
将上面的&lt;your-apikey&gt;替换成你刚刚在Sendgrid生成的apikey，然后，打开config.py：
将上面的&lt;your-apikey&gt;替换成你刚刚在Sendgrid生成的apikey，然后，打开config.py：
```python
# app/config.py

import os


class DevelopmentConfig:
    DEBUG = True  # 设置为调试模式
    # 设置数据库位置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or 'mysql+pymysql://root:%s@localhost:3306/%s' \
                                                                    '?charset'\
                                                                    '=utf8mb4' % (os.environ.get('DEV_DATABASE_PASS'),
                                                                                  os.environ.get('DEV_DATABASE_NAME'))
    # 不跟踪变化
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'this is my secret key!!'  # 设置密钥
    MAIL_USERNAME = 'apikey'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 465
    MAIL_USE_SSL = True


class ProductionConfig:
    DEBUG = False  # 关闭调试
    # 设置在生产环境中使用的数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'mysql+pymysql://root:%s@localhost:3306/%s?charset' \
                               '=utf8mb4' % (os.environ.get('DATABASE_PASS'), os.environ.get('DATABASE_NAME'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret key'  # 生产环境首先使用环境变量中的密钥
    MAIL_USERNAME = 'apikey'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 465
    MAIL_USE_SSL = True


# 设置在不同情况下使用的config
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}

```
这里，我们设置了邮箱的用户名（sendgrid都是「apikey」），密码（真正的apikey，从环境变量中获取），邮箱服务器（
[http://smtp.sendgrid.net](https://link.zhihu.com/?target=http%3A//smtp.sendgrid.net)
），邮箱发送端口（465，sendgrid唯一使用SSL的端口），和邮箱发送服务器是否使用SSL（True）。现在开始使用flask-mail来发送邮件，新建app/utils.py：
```python
# app/utils.py

from flask_mail import Message
from flask import render_template
from .extensions import mail


def send_email(from_address, to_address, title, template=None, **kwargs):
    msg = Message(title, sender=from_address, recipients=[to_address])  # 创建消息
    if template:
        msg.body = render_template('%s.txt' % template, **kwargs)  # 渲染文本正文
        msg.html = render_template('%s.html' % template, **kwargs)  # 渲染HTML正文
    else:
        msg.body = title
    mail.send(msg)  # 发送邮件

```
现在，让我们来测试一下，打开flask shell：
```python
Python 3.8.1 (v3.8.1:1b293b6006, Dec 18 2019, 14:08:53) 
[Clang 6.0 (clang-600.0.57)] on darwin
App: app [development]
Instance: /Users/sam/Desktop/Python/AttributeError/instance
>>> from app.utils import send_email  # 导入该函数
>>> # 这里可以将参数设置成别的，第一个是发件人地址，第二个是收件人地址，最后是邮件正文（因为没有设置template，所以直接使用它作为正文和标题）
>>> send_email('noreply@attributeerror.com', 'sam@example.com', 'Hi, User! This is a test email and sent by Python. Can you see it?')
send: 'ehlo [127.0.0.1]\r\n'
reply: b'250-smtp.sendgrid.net\r\n'
reply: b'250-8BITMIME\r\n'
reply: b'250-PIPELINING\r\n'
reply: b'250-SIZE 31457280\r\n'
reply: b'250-AUTH PLAIN LOGIN\r\n'
reply: b'250 AUTH=PLAIN LOGIN\r\n'
reply: retcode (250); Msg: b'smtp.sendgrid.net\n8BITMIME\nPIPELINING\nSIZE 31457280\nAUTH PLAIN LOGIN\nAUTH=PLAIN LOGIN'
send: 'AUTH PLAIN AGFwaWtleQBTRy55bWRPMVBYSlFmMkZTZDZjcG9jMVRRLjZVU09jVjBJOHRuWUg1ZF9sMkg2OEZXUVFnSW0wRzFVZ1R0QTI5di04bDQ=\r\n'
reply: b'235 Authentication successful\r\n'
reply: retcode (235); Msg: b'Authentication successful'
send: 'mail FROM:<noreply@attributeerror.com> size=402\r\n'
reply: b'250 Sender address accepted\r\n'
reply: retcode (250); Msg: b'Sender address accepted'
send: 'rcpt TO:<samzhang951@outlook.com>\r\n'
reply: b'250 Recipient address accepted\r\n'
reply: retcode (250); Msg: b'Recipient address accepted'
send: 'data\r\n'
reply: b'354 Continue\r\n'
reply: retcode (354); Msg: b'Continue'
data: (354, b'Continue')
send: b'Content-Type: text/plain; charset="utf-8"\r\nMIME-Version: 1.0\r\nContent-Transfer-Encoding: 7bit\r\nSubject: Hi, User! This is a test email and sent by Python. Can you see it?\r\nFrom: noreply@attributeerror.com\r\nTo: samzhang951@outlook.com\r\nDate: Sat, 21 Mar 2020 19:01:13 +0800\r\nMessage-ID: <158478847246.17263.7630660357922288153@bogon>\r\n\r\nHi, User! This is a test email and sent by Python. Can you see it?\r\n.\r\n'
reply: b'250 Ok: queued as wkngCyhORL6Q5SKRAqPjuQ\r\n'
reply: retcode (250); Msg: b'Ok: queued as wkngCyhORL6Q5SKRAqPjuQ'
data: (250, b'Ok: queued as wkngCyhORL6Q5SKRAqPjuQ')
send: 'quit\r\n'
reply: b'221 See you later\r\n'
reply: retcode (221); Msg: b'See you later'
```
下面，让我们来编写验证用户的函数。首先，我们需要生成令牌。itsdangerous提供给了我们这个功能，我们只需要调用它即可（但其实自己还是没明白具体为什么这样写，是从
[Flasky](https://link.zhihu.com/?target=https%3A//github.com/miguelgrinberg/flasky)
 copy过来的，还请大神指点）：
```python
# app/models.py
from flask import current_app
from itsdangerous import Serializer

from .extensions import db, bcrypt
from flask_login import UserMixin


# ...

class User(db.Model, UserMixin):  # User类继承自db.Model
    # ...

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # ...

```
现在，我们就可以编写认证的视图了：
```python
# app/auth/views.py

# ...


@auth.route('/confirm/<token>/')
@login_required
def confirm_user(token):
    user = current_user._get_current_object()
    if user.confirm(token):
        db.session.commit()
        flash('验证用户成功！', 'success')
        return redirect(url_for('main.index'))
    flash('令牌不正确，验证失败', 'error')
    return redirect(url_for('main.index'))


# ...

```
但是这还不够。我们必须在注册时就生成验证令牌，并发送验证邮件给用户。再更改views.py：
```python
# app/auth/views.py

# ...
from flask_login import login_user, login_required, logout_user, current_user
from app.utils import send_email


@auth.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # 实例化表单
    if form.validate_on_submit():  # 当form被提交时执行
        # 获取表单信息
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = User(username=username, email=email, password=password, role=Role.query.filter_by(name='普通用户').first())
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email('noreply@attributeerror.com', user.email, '认证你的账号', template='auth/email/confirm', user=user, 
                   token=token)
        flash('注册成功', 'success')
    return render_template('auth/register.html', form=form)

# ...

```
现在，我们可以把之前创建的用户删除，重新创建一个，来测试该功能。

但是，有时可能用户没有收到邮件或把邮件不小心删除了，因此我们需要提供重新发送按钮。首先，创建该视图：
```python
# app/auth/views.py

# ...

@auth.route('/confirm/re-send/')
@login_required
def re_send_confirm():
    user = current_user._get_current_object()
    token = user.generate_confirmation_token()
    send_email('noreply@attributeerror.com', user.email, '认证你的账号', template='auth/email/confirm', user=user,
               token=token)
    flash('一封新的验证邮件发送成功！', 'success')
    return redirect(url_for('main.index'))

# ...

```
然后，更改unconfirmed.html，来让用户能重新发送邮件：
```html
<!--app/templates/auth/unconfirmed.html-->
{% extends 'base.html' %}

{% block title %}认证你的账号 - AttributeError{% endblock %}

{% block content %}
    <div class="container">
        <h1>Hi, {{ current_user.username }}!</h1>
        <hr>
        <p>你还没有认证你的账号呢！</p>
        <p>没有收到验证邮件？请检查您的垃圾邮件，或<a href="{{ url_for('auth.re_send_confirm') }}">点击这里</a>重新发送验证邮件！</p>
    </div>
{% endblock %}
```
你可能发现了，现在发送邮件，网页都会无响应1-2秒钟，这是程序在发送邮件。我们可以使用异步发送邮件来解决这个问题：
```python
# app/utils.py

from flask_mail import Message
from flask import render_template, current_app
from .extensions import mail
import threading


def send_async_email(msg):
    with current_app.app_context():
        mail.send(msg)


def send_email(from_address, to_address, title, template=None, **kwargs):
    msg = Message(title, sender=from_address, recipients=[to_address])  # 创建消息
    if template:
        msg.body = render_template('%s.txt' % template, **kwargs)  # 渲染文本正文
        msg.html = render_template('%s.html' % template, **kwargs)  # 渲染HTML正文
    else:
        msg.body = title
    threading.Thread(target=send_async_email, args=[msg])  # 异步发送邮件
```
你可能注意到了，现在我们的注册页面没有实现跳转到登录页面，这很不方便。让我们把它加上：
```python
# app/auth/views.py

# ...

@auth.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # 实例化表单
    if form.validate_on_submit():  # 当form被提交时执行
        # 获取表单信息
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = User(username=username, email=email, password=password, role=Role.query.filter_by(name='普通用户').first())
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email('noreply@attributeerror.com', user.email, '认证你的账号', template='auth/email/confirm', user=user,
                   token=token)
        flash('注册成功，你现在可以登录了', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

# ...

```
但是，一旦有用户进入了需要登录才能访问的页面，他会先进入登录页面，然后直接跳转到首页，而不是他刚刚访问的页面。flask-login已经在地址栏中告诉我们用户来自哪个页面了，我们只需要跳转即可。但是，我们必须验证url的安全性。在utils.py中添加一些代码：
```python
# app/utils.py
from urllib.parse import urlparse, urljoin

from flask_mail import Message
from flask import render_template, current_app, request
from .extensions import mail
import threading


# ...

def is_safe_url(target):
    ref_url = urlparse(request.host_url)  # 获取程序内的主机url
    test_url = urlparse(urljoin(request.host_url, target))  # 将目标URl转换为绝对路径
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc  # 验证是否属于内部url

```
接下来，是跳转功能的实现：
```python
# app/auth/views.py

# ...
from app.utils import send_email, is_safe_url


# ...

@auth.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember_me.data
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next = request.args.get('next')
            flash('登录成功！', 'success')
            if is_safe_url(next):
                return redirect(next)
            return redirect(url_for('main.index'))
        flash('用户名或密码不正确', 'warning')
    return render_template('auth/login.html', form=form)

```
到目前为止，我们已经将用户登入，登出，注册，和验证邮箱的功能做完了。这篇文章我花了将近5天才写完，很可能没有人能看到这了，不过还是要做一下笔记。

如果你看到这里了并且你不想敲代码，可以clone我在GitHub上的仓库：（本次版本号为694e079）
[https://github.com/samzhangjy/AttributeError​github.com](https://link.zhihu.com/?target=https%3A//github.com/samzhangjy/AttributeError)

别忘了执行 pip install -r requirements.txt和flask db upgrade来下载Flask扩展和更新数据库！最后，你也要更新你的.env文件，写上你的sendgrid信息。

## 写在最后

啊，终于写完了。如果哪里有错误，还请大神指教！

还有，我在Bootstrap-Flask提的issue还没有回复，如果有我会更新文章。
