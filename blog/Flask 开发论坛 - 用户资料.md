# Flask 开发论坛 - 用户资料

## 写在前面

在
[上一篇文章](https://zhuanlan.zhihu.com/p/114090284)
（为什么我每次都要提到它）里，我们已经把用户的认证做完了。但是，我觉得还有一点不足的地方（除了表单外），就是登录表单（好吧，还是表单）中的CheckBox在不同的操作系统上（甚至浏览器上）的显示效果都不一样。我查找到了
[Bootstrap4 官方文档](https://link.zhihu.com/?target=https%3A//getbootstrap.com/docs/4.4/components/forms/%23checkboxes)
中有样式统一的CheckBox，不过必须要添加几个特点的类。这还不够，
*它还要一个div类。*要知道，在wtf中是不能做到的。虽然我们可以用普通HTML表单实现，但那样的话表单管理起来很不整洁（不，是懒，逃）。于是，我百度了一下，找到了一个类似于Bootstrap中的单选框的css。它只需要引入，剩下的事情就可以交给Bootstrap-Flask自动生成了（因为它覆盖了原有的CheckBox）。在app/static目录下新建css文件夹，再在那里新建名为styles.css的样式表，用来存储所有的自定义样式：
```css
/*app/static/css/styles.css*/

@supports (-webkit-appearance: none) or (-moz-appearance: none) {
    input[type='checkbox'],
    input[type='radio'] {
        --active: #ffc107;
        --active-inner: #3b4146;
        --input-border: #CDD9ED;
        --input-border-hover: #ffd718;
        --background: #fff;
        --disabled: #F5F9FF;
        --disabled-inner: #E4ECFA;
        --shadow-inner: rgba(18, 22, 33, .1);
        outline: none;
        position: relative;
        -webkit-appearance: none;
        -moz-appearance: none;
        box-shadow: none;
        cursor: pointer;
        height: 17px;
        border: 1px solid var(--input-border);
        background: var(--background);
        transition: background .3s ease, border-color .3s ease;
    }

    input[type='checkbox']:after,
    input[type='radio']:after {
        content: '';
        display: block;
        left: 0;
        top: 0;
        position: absolute;
        transition: opacity .2s ease, -webkit-transform .3s ease, -webkit-filter .3s ease;
        transition: transform .3s ease, opacity .2s ease, filter .3s ease;
        transition: transform .3s ease, opacity .2s ease, filter .3s ease, -webkit-transform .3s ease, -webkit-filter .3s ease;
    }

    input[type='checkbox']:checked,
    input[type='radio']:checked {
        background: var(--active);
        border-color: var(--active);
    }

    input[type='checkbox']:checked:after,
    input[type='radio']:checked:after {
        -webkit-filter: drop-shadow(0 1px 2px var(--shadow-inner));
        filter: drop-shadow(0 1px 2px var(--shadow-inner));
        transition: opacity 0.3s ease, -webkit-filter 0.3s ease, -webkit-transform 0.6s cubic-bezier(0.175, 0.88, 0.32, 1.2);
        transition: opacity 0.3s ease, filter 0.3s ease, transform 0.6s cubic-bezier(0.175, 0.88, 0.32, 1.2);
        transition: opacity 0.3s ease, filter 0.3s ease, transform 0.6s cubic-bezier(0.175, 0.88, 0.32, 1.2), -webkit-filter 0.3s ease, -webkit-transform 0.6s cubic-bezier(0.175, 0.88, 0.32, 1.2);
    }

    input[type='checkbox']:disabled,
    input[type='radio']:disabled {
        cursor: not-allowed;
        opacity: .9;
        background: var(--disabled);
    }

    input[type='checkbox']:disabled:checked,
    input[type='radio']:disabled:checked {
        background: var(--disabled-inner);
        border-color: var(--input-border);
    }

    input[type='checkbox']:hover:not(:checked):not(:disabled),
    input[type='radio']:hover:not(:checked):not(:disabled) {
        border-color: var(--input-border-hover);
    }

    input[type='checkbox']:not(.switch),
    input[type='radio']:not(.switch) {
        width: 17px;
    }

    input[type='checkbox']:not(.switch):after,
    input[type='radio']:not(.switch):after {
        opacity: 0;
    }

    input[type='checkbox']:not(.switch):checked:after,
    input[type='radio']:not(.switch):checked:after {
        opacity: 1;
    }

    input[type='checkbox']:not(.switch) {
        border-radius: 4px;
    }

    input[type='checkbox']:not(.switch):after {
        width: 4px;
        height: 8px;
        border: 2px solid var(--active-inner);
        border-top: 0;
        border-left: 0;
        left: 6px;
        top: 3px;
        -webkit-transform: rotate(20deg);
        transform: rotate(20deg);
    }

    input[type='checkbox']:not(.switch):checked:after {
        -webkit-transform: rotate(43deg);
        transform: rotate(43deg);
    }

    input[type='checkbox'].switch {
        width: 38px;
        border-radius: 11px;
    }

    input[type='checkbox'].switch:after {
        left: 2px;
        top: 2px;
        border-radius: 50%;
        width: 15px;
        height: 15px;
        background: var(--input-border);
    }

    input[type='checkbox'].switch:checked:after {
        background: var(--active-inner);
        -webkit-transform: translateX(17px);
        transform: translateX(17px);
    }

    input[type='checkbox'].switch:disabled:not(:checked):after {
        opacity: .6;
    }

    input[type='radio'] {
        border-radius: 50%;
    }

    input[type='radio']:after {
        width: 19px;
        height: 19px;
        border-radius: 50%;
        background: var(--active-inner);
        opacity: 0;
        -webkit-transform: scale(0.7);
        transform: scale(0.7);
    }

    input[type='radio']:checked:after {
        background: var(--active-inner);
        -webkit-transform: scale(0.5);
        transform: scale(0.5);
    }
}
```
然后，让我来更正一波上一篇文章中的错误~

在login视图中，我们在上一篇的文末将它改成了跳转到指定页面（用next参数），但是没有验证next存不存在。这是一个巨大的bug，赶紧补上：(这个更改我将跟随本文的git版本发布）
```python
# app/auth/views.py

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
            if next:  # 验证有没有next
                if is_safe_url(next):
                    return redirect(next)
            return redirect(url_for('main.index'))
        flash('用户名或密码不正确', 'warning')
    return render_template('auth/login.html', form=form)

# ...

```
## 咳咳，进入正题

既然用户已经能够登入登出了，那么我们也能给他们定义资料了。首先，在数据库中建立几个行，用来存储用户信息：
```python
# app/models.py
# ...
from datetime import datetime

# ...

class User(db.Model, UserMixin):  # User类继承自db.Model
    # ...
    real_name = db.Column(db.String(64))  # 真实名称
    about = db.Column(db.Text)  # 自我简介
    member_since = db.Column(db.DateTime, default=datetime.utcnow())  # 注册时间

    # ...

```
接下来，更新数据库：
```text
(venv) flask db migrate
(venv) flask db upgrade
```
因为之前创建的用户这些值都为None，而必须的只有member_since，也就是在用户注册时就设置为当前时间。我们可以在flask shell中更改它：
```python
Python 3.8.1 (v3.8.1:1b293b6006, Dec 18 2019, 14:08:53) 
[Clang 6.0 (clang-600.0.57)] on darwin
App: app [development]
Instance: /Users/sam/Desktop/Python/AttributeError/instance
>>> # 这里如果有多个注册的用户可以用User.query.all()，并循环遍历
>>> u = User.query.first()
>>> u.member_since  # 这里其实是None，但是打印不出来
>>> from datetime import datetime
>>> u.member_since = datetime.utcnow()  # 将它设置为当前时间（UTC）
>>> u.member_since
datetime.datetime(2020, 3, 22, 9, 32, 2, 505903)
>>> db.session.add(u)
>>> db.session.commit()
```
现在数据库设置好了，让我们先来编写用户资料的视图吧。首先，我觉得有必要要创建一个新的蓝图，专门用来存放用户有关的视图，在app目录下创建user文件夹，然后创建init.py：
```python
# app/user/__init__.py

from flask import Blueprint

user = Blueprint('user', __name__, url_prefix='/user')
```
之后，注册蓝图：
```python
# app/__init__.py

# ...

def create_app():
    app = Flask(__name__)  # 创建app实例
    # ...

    from .main import main as main_bp  # 导入蓝图
    app.register_blueprint(main_bp)  # 注册蓝图到应用

    from .auth import auth as auth_bp
    app.register_blueprint(auth_bp)
    
    from .user import user as user_bp
    app.register_blueprint(user_bp)

    return app  # 返回app

```
现在，在user中新建views.py，开始编写视图（别忘了在user的init.py中加入from . import views这一行）：
```python
from . import user
from flask import render_template, abort
from ..models import User


@user.route('/<username>/')
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user/user-profile.html', user=user)

```
现在，我们给它加上模板：
```html
<!--app/templates/user/user-profile.html-->
{% extends 'base.html' %}

{% block title %}{{ user.username }} - AttributeError{% endblock %}

{% block content %}
    <div class="container">
        <h1>{{ user.username }}{% if user.real_name %} <small class="text-muted font-weight-light h5"> {{ user.real_name }}</small>{% endif %}</h1>
        <hr>
        {% if user.about %}{{ user.about }}{% endif %}
    </div>
{% endblock %}
```
现在运行程序，在地址栏中输入/user/用户名就会出现该用户的资料。但是，如果你没有设置的话，网页上只有用户名显示着。让我们把其他资料设置上：
```python
Python 3.8.1 (v3.8.1:1b293b6006, Dec 18 2019, 14:08:53) 
[Clang 6.0 (clang-600.0.57)] on darwin
App: app [development]
Instance: /Users/sam/Desktop/Python/AttributeError/instance
>>> u = User.query.filter_by(username='Sam').first()  # 这里把Sam替换成要修改的用户名
>>> u.real_name = 'Sam Zhang'  # 设置真实名称，将它改成你的就行
>>> u.about = 'Keep conding forever...'  # 设置个人简介
>>> db.session.add(u)
>>> db.session.commit()
```
现在再查看程序，应该会显示类似下面的内容：
![https://pic4.zhimg.com/v2-e6b8c30507c5a95d01eb131642afbe83_r.jpg](https://pic4.zhimg.com/v2-e6b8c30507c5a95d01eb131642afbe83_r.jpg)

但是，我们还没有显示用户从注册到现在有多长时间呢。这需要flask扩展flask-moment（它集成了moment.js）。先安装它：
```python
(venv) pip install flask-moment
```
初始化它：
```python
# app/extensions.py

# ...
from flask_moment import Moment

# 实例化扩展
# ...
moment = Moment()

```
```python
# app/__init__.py

# ...


def create_app():
    app = Flask(__name__)  # 创建app实例
    # ...

    # 初始化扩展
    # ...
    moment.init_app(app)

    # ...

    return app  # 返回app

```
现在，我们需要基模板中加载flask-moment：
```html
<!--app/templates/base.html-->
{# 导入Bootstrap-Flask的内置函数 #}
{% from 'bootstrap/nav.html' import render_nav_item %}
{% from 'bootstrap/utils.html' import render_messages %}
<!DOCTYPE html>
<html lang="en">
<!--...-->
{% block scripts %} {# JS代码块 #}
    {{ bootstrap.load_js() }} {# 引入bootstrap-flask内置的JavaScript #}
    {{ moment.include_moment() }}
    {{ moment.locale('zh-cn') }} {# 设置flask-moment的语言，默认是英文 #}
{% endblock %}
</html>
```
终于，我们可以在模板中使用它了：
```html
<!--app/templates/user/user-profile.html-->
{% extends 'base.html' %}

{% block title %}{{ user.username }} - AttributeError{% endblock %}

{% block content %}
    <div class="container">
        <h1>{{ user.username }}{% if user.real_name %} <small class="text-muted font-weight-light h5"> {{ user.real_name }}</small>{% endif %}</h1>
        {% if user.about %}<blockquote class="blockquote font-italic font-weight-light">{{ user.about }}</blockquote>{% endif %}
        注册于{{ moment(user.member_since).fromNow() }}
        <hr>
    </div>
{% endblock %}
```
上面代码中的moment(user.member_since).fromNow()渲染了从用户注册时间开始到现在的时间长度。可以是几年，几天，几个月，几小时，甚至几分钟。现在再运行程序，就可以看到类似这样的页面了：
![https://pic2.zhimg.com/v2-d2e7c929da1166163b8b3b6d15500131_r.jpg](https://pic2.zhimg.com/v2-d2e7c929da1166163b8b3b6d15500131_r.jpg)

但是，总感觉少了些什么。一般的网站还有一些其他信息，比如性别，网站等。但是最重要的好像还是少了一个头像。但是，让我们先把性别和网站加上：
```python
# app/models.py
# ...

class User(db.Model, UserMixin):  # User类继承自db.Model
    __tablename__ = 'users'  # 定义表名
    id = db.Column(db.Integer, primary_key=True)  # 定义id，并且为主键
    username = db.Column(db.String(64))  # 用户名
    email = db.Column(db.String(128))  # 邮箱地址
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    password = db.Column(db.String(255))  # 存放密码
    confirmed = db.Column(db.Boolean, default=False)
    real_name = db.Column(db.String(64))  # 真实名称
    about = db.Column(db.Text)  # 自我简介
    member_since = db.Column(db.DateTime, default=datetime.utcnow())  # 注册时间
    gender = db.Column(db.String(64))
    site = db.Column(db.String(256))

    # ...

```
升级数据库：
```text
(venv) flask db migrate
(venv) flask db upgrade
```
现在，让我们对模板做一下更改：
```html
<!--app/templates/user/user-profile.html-->
{% extends 'base.html' %}

{% block title %}{{ user.username }} - AttributeError{% endblock %}

{% block content %}
    <div class="container">
        <h1>{{ user.username }}{% if user.real_name %} <small class="text-muted font-weight-light h5"> {{ user.real_name }}</small>{% endif %}{% if user.gender %} <small class="h5">{{ user.gender }}</small>{% endif %}</h1>
        {% if user.site %}<p>网站：<a href="//{{ user.site }}" target="_blank">{{ user.site }}</a></p>{% endif %}
        {% if user.about %}<blockquote class="blockquote font-italic font-weight-light">{{ user.about }}</blockquote>{% endif %}
        注册于{{ moment(user.member_since).fromNow() }}
        <hr>
    </div>
{% endblock %}
```
现在，你可以对你的资料做一些更改：
```python
Python 3.8.1 (v3.8.1:1b293b6006, Dec 18 2019, 14:08:53) 
[Clang 6.0 (clang-600.0.57)] on darwin
App: app [development]
Instance: /Users/sam/Desktop/Python/AttributeError/instance
>>> u = User.query.first()
>>> u.gender = 'male'
>>> u.site = 'samzhangjy.github.io'
>>> db.session.add(u)
>>> db.session.commit()
```
现在更改完的页面是这样的：
![https://pic2.zhimg.com/v2-364e30d0e80e88c290bccdea5a2a9701_r.jpg](https://pic2.zhimg.com/v2-364e30d0e80e88c290bccdea5a2a9701_r.jpg)

这样的页面看起来很不整洁。我们需要一些图标来美化它，我用到了
[font-awesome](https://link.zhihu.com/?target=http%3A//www.fontawesome.com.cn/)
。首先，我们需要下载它。我下载的是4.7版，一般就够用了。把下载完的压缩包解压，放到static目录下，命名为font-awesome-4.7.0。

然后，我们引入它：
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
    {# 引入自定义的Bootstrap css #}
    <link rel="stylesheet" href="{{ url_for('static', filename='Bootstrap/bootstrap.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='font-awesome-4.7.0/css/font-awesome.css') }}">
</head>
<!--...-->
</html>
```
现在，我们就可以使用font-awesome了。再打开user-profile.html，加入图标：
```html
<!--app/templates/user/user-profile.html-->
{% extends 'base.html' %}

{% block title %}{{ user.username }} - AttributeError{% endblock %}

{% block content %}
    <div class="container">
        <h1>{{ user.username }}{% if user.real_name %} <small><small><small class="text-muted font-weight-light"> {{ user.real_name }}</small></small></small>{% endif %}{% if user.gender == 'male' %} <span class="fa fa-mars" style="font-size: 50%; color: #007bff"></span>{% elif user.gender == 'female' %} <span class="fa fa-venus" style="font-size: 50%; color: #e83e8c"></span>{% endif %}</h1>
        {% if user.site %}<p><a href="//{{ user.site }}" target="_blank">{{ user.site }} <small class="fa fa-external-link text-secondary"></small></a></p>{% endif %}
        {% if user.about %}<span class="fa fa-quote-left"></span> <blockquote class="blockquote font-italic font-weight-light">{{ user.about }}</blockquote>{% endif %}
        注册于{{ moment(user.member_since).fromNow() }}
        <hr>
    </div>
{% endblock %}
```
现在，我们的资料页面就好看很多了：
![https://pic2.zhimg.com/v2-0c9a32e2ad8c9a231ef57b3c57ee8c95_r.jpg](https://pic2.zhimg.com/v2-0c9a32e2ad8c9a231ef57b3c57ee8c95_r.jpg)

但是，正如我上面所说的，它还缺少一个头像。我们需要一个头像。这需要我们用到flask-avatars。(插一个小插曲，还记得上一篇文章中知乎崩溃吗？现在又崩了，我已经受不了它啦，一直502，首页都打不开。。哎，什么时候知乎能把技术弄好点啊）

先安装它：
```python
pip install flask-avatars
```
初始化：
```python
# app/extensions.py

# ...
from flask_avatars import Avatars

# 实例化扩展
# ...
avatars = Avatars()

```
```python
# app/__init__.py

# ...

def create_app():
    app = Flask(__name__)  # 创建app实例
    # ...

    # 初始化扩展
    # ...
    avatars.init_app(app)

    # ...

    return app  # 返回app

```
除此之外，flask-avatars还需要设置头像的储存位置。让我们来定义：
```python
# app/config.py

import os


class DevelopmentConfig:
    # ...
    AVATARS_SAVE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/avatars/')


class ProductionConfig:
    # ...
    AVATARS_SAVE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/avatars/')


# ...

```
现在，我们就可以开始编写用户的最初的头像了：
```python
# app/models.py
# ...
from flask_avatars import Identicon

# ...


class User(db.Model, UserMixin):  # User类继承自db.Model
    # ...
    avatar_s = db.Column(db.String(128))
    avatar_m = db.Column(db.String(128))
    avatar_l = db.Column(db.String(128))

    def __init__(self, password, **kwargs):
        super().__init__(password=password, **kwargs)
        self.password = self.set_password(password)  # 初始化时将未加密的密码加密
        self.generate_avatar()

    def generate_avatar(self):
        avatar = Identicon()
        filenames = avatar.generate(text=self.username)
        self.avatar_s = filenames[0]
        self.avatar_m = filenames[1]
        self.avatar_l = filenames[2]
        db.session.commit()

    # ...
    def __repr__(self):  # 定义User类的返回名称
        return '<User %s>' % self.username  # 返回 <User 用户名>

```
在这里，我们为用户创建了一个用
*Identicon*来生成的头像，嗯，就是GitHub使用的默认头像。类似这样：
![https://pic3.zhimg.com/v2-00f63bb1282195e5249935eede625c76_r.jpg](https://pic3.zhimg.com/v2-00f63bb1282195e5249935eede625c76_r.jpg)

好了，现在我们应该先执行数据库迁移，再创建用户头像：
```python
(venv) flask db migrate
(venv) flask db upgrade
(venv) flask shell
Python 3.8.1 (v3.8.1:1b293b6006, Dec 18 2019, 14:08:53) 
[Clang 6.0 (clang-600.0.57)] on darwin
App: app [development]
Instance: /Users/sam/All/Python/AttributeError/instance
>>> u = User.query.first()
>>> u.generate_avatar()  # 生成头像
```
现在，查看app/static/avatars目录，应该会有三张以用户名_l.png，用户名_m.png，用户名_s.png三张图片。分别代表图片大，中，小。我们现在在用户资料中引入它：
```html
<!--app/templates/user/user-profile.html-->
{% extends 'base.html' %}

{% block title %}{{ user.username }} - AttributeError{% endblock %}

{% block content %}
    <div class="container">
        <div class="row container">
            <div class="col col-3">
                <img class="rounded-circle img-fluid" src="{{ url_for('static', filename='avatars/%s' % user.avatar_l) }}" onerror="this.src='{{ avatars.default(size='l') }}';">
            </div>
            <div class="col col-9">
                <h1>{{ user.username }}{% if user.real_name %} <small><small><small class="text-muted font-weight-light"> {{ user.real_name }}</small></small></small>{% endif %}{% if user.gender == 'male' %} <span class="fa fa-mars" style="font-size: 50%; color: #007bff"></span>{% elif user.gender == 'female' %} <span class="fa fa-venus" style="font-size: 50%; color: #e83e8c"></span>{% endif %}</h1>
                {% if user.site %}<p><a href="//{{ user.site }}" target="_blank">{{ user.site }} <small class="fa fa-external-link text-secondary"></small></a></p>{% endif %}
                {% if user.about %}<span class="fa fa-quote-left"></span> <blockquote class="blockquote font-italic font-weight-light">{{ user.about }}</blockquote>{% endif %}
                注册于{{ moment(user.member_since).fromNow() }}
            </div>
        </div>
        <hr>
    </div>
{% endblock %}
```
此外，我们还有JavaScript设置了当用户头像不存在时的默认头像，来源自Flask-Avatars内置函数。现在，我们的用户资料页面应该类似这样：
![https://pic4.zhimg.com/v2-741d6e31d9d53a157a2acade65afb5bb_r.jpg](https://pic4.zhimg.com/v2-741d6e31d9d53a157a2acade65afb5bb_r.jpg)

嗯。。好看多了。现在，我们完全可以就这样完成头像部分了，但大多数网站都有能自己更改头像的功能，我们也来实现应该吧。其实，Flask-Avatars已经给我们做好了，我们只需要调用它就好了。先来编写它的模板，命名为change-avatar-upload.html：
```html
{% extends 'base.html' %}

{% block title %}上传头像 - AttributeError{% endblock %}

{% block content %}
    <div class="container">
        <h1>上传头像</h1>
        <hr>
        <form method="post" enctype="multipart/form-data">
            <div class="input-group">
                <input id='location' class="form-control" onclick="$('#file').click();">
                <label class="input-group-prepend">
                    <input type="button" value="上传头像" id="i-check" class="btn btn-primary rounded-right"
                            onclick="$('#file').click();">
                </label>
            </div>
            <input type="file" name="file" id='file' accept="image/png image/jpg image/jpeg image/gif"
                   onchange="$('#location').val(getFileName(this.value));" style="display: none">
            <button class="btn btn-success" type="submit">上传</button>
        </form>
    </div>
{% endblock %}

{% block scripts %}
    {{ super() }}
    <script>
        function getFileName(path) {
            var pos1 = path.lastIndexOf('/');
            var pos2 = path.lastIndexOf('\\');
            var pos = Math.max(pos1, pos2);
            if (pos < 0)
                return path;
            else
                return path.substring(pos + 1);
        }
    </script>
{% endblock %}

```
这里，我们没有使用flask-wtf，是因为默认的文件上传表单实在
*太*丑了，这里我使用的是先把原有文件上传表单隐藏，再通过按钮点击让js来触发那个表单，实现了模拟它的效果。然后，我们就来编写视图吧：
```python
from flask_login import current_user

from . import user
from flask import render_template, abort, request, session, url_for, current_app, send_from_directory, redirect

from ..extensions import avatars, db
from ..models import User


# ...


@user.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory('static/avatars', filename)


@user.route('/change-avatar/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        raw_filename = avatars.save_avatar(f)
        session['raw_filename'] = raw_filename
        return redirect(url_for('user.crop'))
    return render_template('user/change-avatar-upload.html')


# ...

```
这里我们不仅定义了视图，还定义了一个函数来获取头像，让程序更简单。这个程序的大部分代码我都是从
[Flask-Avatars官方文档](https://link.zhihu.com/?target=https%3A//flask-avatars.readthedocs.io/en/latest/%23avatar-crop)
中获取的，下面裁剪的也一样。但是，现在我们把用户上传的头像存储在了session里，这是不正确的，我们应该将它存储到数据库中。更改users模型：
```python
class User(db.Model, UserMixin):  # User类继承自db.Model
    # ...
    raw_avatar = db.Column(db.String(128))

    # ...
```
数据库迁移：
```text
flask db migrate
flask db upgrade
```
然后，我们来做一些小改动：
```python
@user.route('/change-avatar/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        raw_filename = avatars.save_avatar(f)
        u = current_user._get_current_object()
        u.raw_avatar = raw_filename
        db.session.add(u)
        db.session.commit()
        return redirect(url_for('user.crop'))
    return render_template('user/change-avatar-upload.html')
```
好了，用户能上传头像了，那我们就应该开始编写剪裁头像的函数了。Flask-Avatars也为我们包装好了，我们调用它就行了：
```python
# app/user/views.py
# ...

@user.route('/change-avatar/crop/', methods=['GET', 'POST'])
def crop():
    if request.method == 'POST':
        x = request.form.get('x')
        y = request.form.get('y')
        w = request.form.get('w')
        h = request.form.get('h')
        filenames = avatars.crop_avatar(current_user.raw_avatar, x, y, w, h)
        u = current_user._get_current_object()
        u.avatar_s = filenames[0]
        u.avatar_m = filenames[1]
        u.avatar_l = filenames[2]
        db.session.add(u)
        db.session.commit()
        return redirect(url_for('user.user_profile', username=u.username))
    return render_template('user/change-avatar-crop.html')

```
模板：
```html
<!--app/templates/user/change-avatar-crop.html-->
{% extends 'base.html' %}

{% block title %}更改头像 - AttributeError{% endblock %}

{% block content %}
    {{ avatars.jcrop_css() }}  <!--导入内置的jcrop css-->
    <div class="container">
        <h1>更改头像</h1>
        <hr>
        <div class="card">
            <div class="card-body container-fluid">
                {{ avatars.crop_box('user.get_avatar', current_user.raw_avatar) }}
                {{ avatars.preview_box('user.get_avatar', current_user.raw_avatar) }}
                <br>
                <form method="post">
                    <input type="hidden" id="x" name="x">
                    <input type="hidden" id="y" name="y">
                    <input type="hidden" id="w" name="w">
                    <input type="hidden" id="h" name="h">
                    <button type="submit" class="btn btn-primary">完成</button>
                </form>
            </div>
        </div>
    </div>
{% endblock %}

{% block scripts %}
    {{ avatars.jcrop_js() }}  <!--导入Flask-Avatars内置的jcrop js-->
    {{ avatars.init_jcrop() }}
{% endblock %}
```
注意，这个模板中有一处我添加了css，把它先加入到styles.css中：
```css
/*app/static/css/styles.css*/

/*...*/
#preview-box {
    display: block;
    position: absolute;
    top: 10px;
    right: -280px;
    padding: 6px;
    border: 1px rgba(0, 0, 0, .4) solid;
    background-color: white;

    -webkit-border-radius: 6px;
    -moz-border-radius: 6px;
    border-radius: 6px;

    -webkit-box-shadow: 1px 1px 5px 2px rgba(0, 0, 0, 0.2);
    -moz-box-shadow: 1px 1px 5px 2px rgba(0, 0, 0, 0.2);
    box-shadow: 1px 1px 5px 2px rgba(0, 0, 0, 0.2);
}
```
好了，现在所有模板都编写完成了，我们也应该在用户主页添加一个链接，让用户好找到修改头像的地方：
```html
<!--app/templates/user/user-profile.html-->
{% extends 'base.html' %}

{% block title %}{{ user.username }} - AttributeError{% endblock %}

{% block content %}
    <!--...-->
            <div class="col col-3 text-center">
                <img class="rounded-circle img-fluid" src="{{ url_for('static', filename='avatars/%s' % user.avatar_l) }}" onerror="this.src='{{ avatars.default(size='l') }}';">
                {% if user == current_user %} {# 判断用户是不是当前用户 #}
                    <br><a style="margin-top: 10px" href="{{ url_for('user.upload') }}" class="btn btn-primary">更改头像 <span class="fa fa-edit"></span></a>
                {% endif %}
            </div>
    <!--...-->
{% endblock %}
```
到目前为止，我们的用户资料主页看起来类似这样：
![https://pic1.zhimg.com/v2-907390ebafb6b3493ff1bfbd5d3ab660_r.jpg](https://pic1.zhimg.com/v2-907390ebafb6b3493ff1bfbd5d3ab660_r.jpg)

除此之外，我们也应该给用户一个选项，来恢复默认头像。这个实现很简单，只需要将头像文件名重新设定回用户名.png就可以了，因为每个用户在注册时就已经自动生成了头像。我们现在来编写它：
```python
# app/user/views.py
# ...
from flask import render_template, abort, request, url_for, send_from_directory, redirect, flash

# ...

@user.route('/change-avatar/default/')
def default_avatar():
    u = current_user._get_current_object()
    u.avatar_l = '%s_l.png' % u.username
    u.avatar_m = '%s_m.png' % u.username
    u.avatar_s = '%s_s.png' % u.username
    db.session.add(u)
    db.session.commit()
    flash('头像已恢复为默认头像', 'success')
    return redirect(url_for('user.user_profile', username=u.username))

```
再把它插入到上传头像的模板中：
```html
<!--app/templates/user/change-avatar-upload.html-->
{% extends 'base.html' %}

{% block title %}上传头像 - AttributeError{% endblock %}

{% block content %}
    <div class="container">
        <h1>上传头像</h1>
        <button class="btn btn-outline-primary" data-toggle="modal" data-target="#confirm">
            恢复为默认头像
        </button>
        <hr>
        <div class="modal fade" id="confirm" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel"
             aria-hidden="true">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="exampleModalLabel">你确定吗？</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        你确定要将头像恢复为默认头像吗？你之后还可以将其设置为自定义头像
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">取消</button>
                        <a class="btn btn-primary" href="{{ url_for('user.default_avatar') }}">确定</a>
                    </div>
                </div>
            </div>
        </div>
        <!--...-->
    </div>
{% endblock %}

<!--...-->
```
这里，我们在真正执行恢复默认头像之前询问了用户是否要更换为默认头像，再去执行操作。但是，现在更改头像还有一个错误，就是所有人都可以通过链接来更改头像，哪怕是未登录的用户。我们需要对这个情况加上login_required装饰器：
```python
# app/user/views.py
from flask_login import current_user, login_required

# ...


@user.route('/change-avatar/', methods=['GET', 'POST'])
@login_required
def upload():
    # ...


@user.route('/change-avatar/crop/', methods=['GET', 'POST'])
@login_required
def crop():
    # ...


@user.route('/change-avatar/default/')
@login_required
def default_avatar():
    # ...

```
现在，未登录的用户就会先执行登录，再来更换头像了。此外，我们也应该在更换完头像之后提醒用户：
```text
# app/user/views.py
# ...

@user.route('/change-avatar/crop/', methods=['GET', 'POST'])
@login_required
def crop():
    if request.method == 'POST':
        # ...
        flash('更改头像成功', 'success')
        return redirect(url_for('user.user_profile', username=u.username))
    return render_template('user/change-avatar-crop.html')


# ...

```
好了，现在我们已经完成了用户头像的设置。

个人主页的设计也就差不多完成了。这篇文章写了好几个月，终于可以发布了。好开心呀！

这篇文章的源码我已经发布到了
[GitHub](https://link.zhihu.com/?target=https%3A//github.com/samzhangjy/AttributeError)
上，可以自行获取，版本是eef2294。
