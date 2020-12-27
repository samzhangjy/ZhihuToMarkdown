# Flask 开发论坛 - 添加问题

到目前为止，我们已经做好了用户资料和登录，但是用户资料还没有在主页中加上链接。现在让我们加上它：
```html
<!-- app/templates/base.html -->
<!--...-->
<!DOCTYPE html>
<html lang="en">

<head>
    <!--...-->
</head>

<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <!--...-->
        <div class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
            <a class="dropdown-item" href="{{ url_for('user.user_profile', username=current_user.username) }}">个人资料</a>
            <a class="dropdown-item" href="{{ url_for('auth.logout') }}">登出</a>
        </div>
    </nav>
    <!--...-->
</body>
<!--...-->

</html>
```
可能你也注意到了，现在我们的网页加载十分缓慢，其原因是由于我们使用了CDN而不是本地资源。我们可以通过下载资源来加快速度，其中需要的资源我已经放在了GitHub上，有需要可以自行获取。下面是从本地加载资源的代码：
```text
<!-- app/templates/base.html -->
{# 导入Bootstrap-Flask的内置函数 #}
{% from 'bootstrap/nav.html' import render_nav_item %}
{% from 'bootstrap/utils.html' import render_messages %}
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>{% block title %}{% endblock %} {# 标题块 #}</title>
    {# 引入自定义的Bootstrap css #}
    <link rel="stylesheet" href="{{ url_for('static', filename='css/bootstrap.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='fonts/font-awesome-4.7.0/css/font-awesome.css') }}">
</head>

<body>
    <!--...-->
</body>
{% block scripts %} {# JS代码块 #}
<!--引入js-->
<script src="{{ url_for('static', filename='js/jquery.js') }}"></script>
<script src="{{ url_for('static', filename='js/popper.js') }}"></script>
<script src="{{ url_for('static', filename='js/bootstrap.js') }}"></script>
{{ moment.include_moment(local_js=url_for('static', filename='js/moment-with-locales.js')) }}
{{ moment.locale('zh-cn') }} {# 设置flask-moment的语言，默认是英文 #}
{% endblock %}

</html>
```
好了，现在加载资源速度就快很多了。下面我们进入今天的正题：添加问题。

## 咳咳

要添加问题，首先要建立数据库模型。打开models.py，建立一个Question模型：
```python
# app/models.py
# ...

class Question(db.Model):
    """问题模型"""
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    # 问题标题
    title = db.Column(db.String(64))
    # Markdown格式的问题正文
    body_markdown = db.Column(db.Text)
    # HTML格式的问题正文
    body_html = db.Column(db.Text)
    # 发布者id
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Question %d>' % self.id

```
然后在User模型中添加relationship：
```text
class User(db.Model, UserMixin):  # User类继承自db.Model
    """用户模型"""
    __tablename__ = 'users'  # 定义表名
    # ...
    # 提过的问题
    questions = db.relationship('Question', backref='author', lazy='dynamic')
    # ...
```
之后，升级数据库：
```text
flask db migrate
flask db upgrade
```
好了，现在最基本的问题模型我们已经搭建好了，现在让我们来编写视图吧。新创建一个question文件夹，用于存放问题视图。

i>__init__.py
**```text
# app/question/__init__.py

from flask import Blueprint

question = Blueprint('question', __name__, url_prefix='/question')

from . import views

```
i>views.py
**```python
# app/question/views.py
from . import question
from flask_login import current_user, login_required
from flask import request, render_template
from ..models import Question
from ..extensions import db
from .forms import AddQuestionForm


@question.route('/add/', methods=['GET', 'POST'])
@login_required
def add():
    form = AddQuestionForm()
    if form.validate_on_submit():
        title = form.title.data
        body_markdown = form.body_markdown.data
        # 获取Editor.md自动生成的HTML
        body_html = request.form['editormd-html-code']
        # 创建问题
        _question = Question(
            title=title, body_markdown=body_markdown, body_html=body_html, author=current_user)
        db.session.add(_question)
        # 保存到数据库
        db.session.commit()
    return render_template('question/add.html', form=form)

```
i>forms.py
**```python
# app/question/forms.py

from wtforms import StringField, TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class AddQuestionForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired()], render_kw={'autocomplete': 'off', 'autofocus': 'true'})
    body_markdown = TextAreaField('介绍')
    submit = SubmitField('添加问题')


```
好了，接下来让我们来完成最棘手的部分：模版。

你可能已经注意到了，我们的模型中定义了Markdown和HTML格式的问题正文，所有需要Markdown编辑器。我这里选择的是
[Editor.md](https://link.zhihu.com/?target=https%3A//pandao.github.io/editor.md/%23Heading%25206)
，它是由中国人维护的，所以对中文十分友好。

下载Editor.md，解压后重命名为editormd，放在static目录下。然后，在templates文件夹中创建question文件夹，用于存放有关问题的Jinja模版。

i>templates/question/add.html
**```html
<!--app/templates/question/add.html-->
{% extends 'base.html' %}
{% from 'bootstrap/form.html' import render_field %}

{% block title %}创建问题{% endblock %}

{% block content %}
<div class="container">
    <h1>创建问题</h1>
    <hr>
    <!--手动生成表单-->
    <form method="POST" action="{{ url_for('question.add') }}">
        <!--WTF的CSRF令牌-->
        {{ form.csrf_token() }}
        <!--渲染标题-->
        {{ render_field(form.title) }}
        <!--手动渲染正文框-->
        <div id="editormd" style="border-radius: 5px;">
            {{ form.body_markdown() }}
        </div>
        <!--渲染提交按钮-->
        {{ render_field(form.submit, button_map={'submit': 'primary'}) }}
    </form>
</div>
{% endblock %}

{% block scripts %}
{{ super() }}
<!--加载Editor.md的依赖文件-->
<link rel="stylesheet" href="{{ url_for('static', filename='editormd/css/editormd.min.css') }}">
<script src="{{ url_for('static',filename='editormd/editormd.min.js') }}"></script>
<script>
    // editor 变量
    var editor;
    $(function () {
        // editor.md会自动定位位于“editormd”div中的第一个textarea
        editor = editormd('editormd', {
            // 站位文字
            placeholder: '请输入问题介绍',
            // 编辑器的高度
            height: 640,
            // 滚动锁定
            syncScrolling: 'both',
            // editormd的依赖库位置
            path: "{{ url_for('static',filename='editormd/lib/') }}",
            // 启用代码折叠
            codeFold : true,
            // 自动保存html到textarea中
            saveHTMLToTextarea : true,
            // 替换搜索
            searchReplace : true,
            // 表情
            emoji : true,
            // TODO表
            taskList : true,
            // 目录
            tocm: true,
            // tex公式
            tex : true,
            // 流程图
            flowChart : true,
            // 顺序图
            sequenceDiagram : true,
            // 不启用图片上传
            imageUpload : false
        });
    });
</script>
{% endblock %}
```
好了，现在最基本的问题我们已经能够创建了。下面我们在base.html中加入一个链接：
```text
<!-- app/templates/base.html -->
<!--...-->
<!DOCTYPE html>
<html lang="en">

<head>
    <!--...-->
</head>

<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <!--...-->
        <div class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
            <a class="dropdown-item" href="{{ url_for('question.add') }}">添加问题</a>
            <a class="dropdown-item" href="{{ url_for('user.user_profile', username=current_user.username) }}">个人资料</a>
            <a class="dropdown-item" href="{{ url_for('auth.logout') }}">登出</a>
        </div>
        <!--...-->
    </nav>
    <br>
    {{ render_messages(container=True, dismissible=True, dismiss_animate=True) }} {# 使用Bootstrap-Flask内置函数渲染闪现消息 #}
    <br>
    {% block content %}{% endblock %} {# 内容块 #}
</body>
<!--...-->

</html>
```
现在做成的页面长这模样：
![https://pic3.zhimg.com/v2-87ed90bef282515c6be3160c7c8fe2da_r.jpg](https://pic3.zhimg.com/v2-87ed90bef282515c6be3160c7c8fe2da_r.jpg)

好了，今天先写到这里吧，回头再写。本文章的相关代码我已经放在了
[GitHub](https://link.zhihu.com/?target=https%3A//github.com/samzhangjy/AttributeError/tree/b2cab15ab9e4e9ff1868e8c383854f925b5f667d)
上，版本号是b2cab15，有需要可以自行获取。
