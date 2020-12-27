# Flask 开发论坛 - 起步

## 写在前面

好久没来知乎写文章了，都有点不熟悉了，感觉知乎的编辑器用的不是很顺手，估计用用就习惯了吧

之前其实就有想做一个类Segmentfault的论坛，但一直都没做，这次正好也正在学Flask，就用Flask开发吧。我之前因为已经读过Flask的狗书，所以对Flask有一点基础知识，但总感觉自己写的代码不是自己想的，想再实战一下，于是就有了用Flask开发论坛的想法，也顺便提升一下自己代码的整洁度。

这个项目的全部目录在
[这里](https://zhuanlan.zhihu.com/p/113539585)

如果有哪里出错了或者有更好的解决方案，还请大神们指教~

## 进入正题

首先，先在Pycharm中创建一个Flask项目，选择Flask，再选论坛的名字（这里我选的是AttributeError，因为Python中太常见了。。）：
![https://pic2.zhimg.com/v2-5e201ad7a412849a4926fadd33c91519_r.jpg](https://pic2.zhimg.com/v2-5e201ad7a412849a4926fadd33c91519_r.jpg)

如果你用的是其他IDE，也可以直接新建文件夹，创建虚拟环境，然后pip install flask

创建完之后，删除Pycharm自动生成的app.py中的代码，并且在根目录中创建一个文件夹，名为app，再在app中创建main文件夹，为使用Flask的蓝图做准备。

之后，把Pycharm生成的static和template文件夹也移动到app文件夹里，并再app文件夹里创建__init__.py，输入以下代码：
```python
from flask import Flask  # 导入Flask


def create_app():
    app = Flask(__name__)  # 创建app实例

    return app  # 返回app

```
在create_app里，我们创建了flask实例，名为app，并且让整个函数返回app。在根目录的app.py里，我们调用整个函数来创建app：
```text
from app import create_app  # 导入create_app

app = create_app()  # 创建应用

if __name__ == '__main__':
    app.run()  # 运行应用

```
现在，如果我们运行app.py，并访问127.0.0.1:5000，会发现网页抛出了404异常，这是因为我们还没有创建任何页面。现在，在main文件夹里创建__init__.py，来创建一个蓝图：
```text
from flask import Blueprint  # 导入Flask中的蓝图

main = Blueprint('main', __name__)  # 创建一个名叫main的蓝图

from . import views  # 导入视图

```
但这还不行，还要在app文件夹中的__init__.py里注册蓝本：
```text
def create_app():
    app = Flask(__name__)  # 创建app实例
    
    from .main import main as main_bp  # 导入蓝图
    app.register_blueprint(main_bp)  # 注册蓝图到应用

    return app  # 返回app
```
现在，你的IDE上可能会显示找不到views，我们现在就在main文件夹中创建views.py：
```text
from . import main  # 导入蓝图


@main.route('/')  # 定义路由
def index():
    return '<h1>Welcome to AttributeError!</h1>'  # 返回页面正文

```
现在再运行程序，应该能看到Welcome to AttributeError!了，但是十分丑陋。如果想要开发一个像样的论坛，页面必须要好看。于是，我找到了Bootstrap-Flask，一个集成
[Bootstrap4](https://link.zhihu.com/?target=http%3A//www.getbootstrap.com/)
的Flask扩展。在命令行里输入pip install bootstrap-flask来安装它。

安装完之后，我们再在app文件夹中创建一个名为extensions.py的文件，来实例化所有扩展：
```text
from flask_bootstrap import Bootstrap  # 导入Bootstrap-Flask

bootstrap = Bootstrap()  # 实例化扩展

```
但是现在bootstrap-flask还没有被初始化。我们现在在__init__.py中初始化它：
```python
from flask import Flask  # 导入Flask
from .extensions import *  # 导入已经实例化了的扩展


def create_app():
    app = Flask(__name__)  # 创建app实例
    
    bootstrap.init_app(app)  # 初始化扩展

    from .main import main as main_bp  # 导入蓝图
    app.register_blueprint(main_bp)  # 注册蓝图到应用

    return app  # 返回app

```
现在，我们应该在页面中引入它，但是刚才直接返回字符串型的模板太不适合大型网站了，我们现在在templeates文件夹里创建main文件夹，之后在main文件夹里添加index.html：
```django
{% from 'bootstrap/nav.html' import render_nav_item %} {# 导入Bootstrap-Flask的内置函数 #}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AttributeError</title>
    {{ bootstrap.load_css() }} {# 引入bootstrap-flask内置的css #}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <a class="navbar-brand" href="/">AttributeError</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
                {{ render_nav_item('main.index', '首页') }} {# 使用Bootstrap-Flask内置的函数渲染导航链接 #}
            </ul>
          </div>
    </nav>
    <br>
    <div class="container">
        <h1>AttributeError</h1>
        <hr>
        <p>Welcome to AttributeError!</p>
    </div>
</body>
{{ bootstrap.load_js() }} {# 引入bootstrap-flask内置的JavaScript #}
</html>
```
现在，让我们在视图函数中引入模板：
```python
from flask import render_template  # 导入渲染模板函数
from . import main  # 导入蓝图


@main.route('/')  # 定义路由
def index():
    return render_template('main/index.html')  # 返回渲染后的页面正文
```
现在再运行程序，界面就会好看很多：
![https://pic3.zhimg.com/v2-62094478abd98e6e05963f24b576f9a6_r.jpg](https://pic3.zhimg.com/v2-62094478abd98e6e05963f24b576f9a6_r.jpg)

但是，现在在更改程序代码时，更改不会在运行时体现，必须要重新运行程序才可以。这对开发很不方便，所以让我们开启Flask的调试模式，它会在任何代码有更改后自动刷新应用：
```python
from app import create_app  # 导入create_app

app = create_app()  # 创建应用

if __name__ == '__main__':
    app.run(debug=True)  # 运行应用，并开启调试模式

```
现在，重新运行程序，应用就可以实时刷新了。

在现在的应用中，我们还没有创建数据库，所以还不能开发论坛最重要的功能，但是我们会在之后创建。也许你会注意到，现在的模板很复杂，如果每个模板中都敲一遍的话太麻烦了，所以我们要创建基模板来解决这个问题。先在templates文件夹中创建base.html，也就是基模板，输入下面的代码：
```django
{% from 'bootstrap/nav.html' import render_nav_item %} {# 导入Bootstrap-Flask的内置函数 #}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}{% endblock %} {# 标题块 #}</title>
    {{ bootstrap.load_css() }} {# 引入bootstrap-flask内置的css #}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <a class="navbar-brand" href="/">AttributeError</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
                {{ render_nav_item('main.index', '首页') }} {# 使用Bootstrap-Flask内置的函数渲染导航链接 #}
            </ul>
          </div>
    </nav>
    <br>
    {% block content %}{% endblock %} {# 内容块 #}
</body>
{% block scripts %} {# JS代码块 #}
    {{ bootstrap.load_js() }} {# 引入bootstrap-flask内置的JavaScript #}
{% endblock %}
</html>
```
现在，我们就可以使用基模板来简化index.html：
```django
{% extends 'base.html' %} {# 表示继承自base.html #}

{% block title %}AttributeError{% endblock %} {# 定义标题 #}

{% block content %} {# 定义内容 #}
    <div class="container">
        <h1>AttributeError</h1>
        <hr>
        <p>Welcome to AttributeError!</p>
    </div>
{% endblock %}
```
也许你去了Bootstrap的官网上了解了Bootstrap的控件，他们都是以蓝色为主色调，搭配不同程度的灰色。这样的配色当然很好看，但是许多网站都在使用它，完全不能突出网站特点，所以我又深入了解了一下自定义Bootstrap，但是从4.0开始，都是要自定义Scss，对我这种CSS小白来说十分不友好，于是我找到了Bootstrap.build:
[Free Bootstrap Themes & Theme Builder​bootstrap.build](https://link.zhihu.com/?target=http%3A//bootstrap.build)

我利用这个工具自定义了一份以黄色为主色调的主题，具体可以在文末的Github上找到。来使用自定义的CSS，需要更改base.html：
```django
{% from 'bootstrap/nav.html' import render_nav_item %} {# 导入Bootstrap-Flask的内置函数 #}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}{% endblock %} {# 标题块 #}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='Bootstrap/bootstrap.css') }}"> {# 引入自定义的Bootstrap css #}
</head>
<!--...-->
{% block scripts %} {# JS代码块 #}
    {{ bootstrap.load_js() }} {# 引入bootstrap-flask内置的JavaScript #}
{% endblock %}
</html>

```
现在如果刷新网页，可能看不到所做的更改，但是我们更改了Bootstrap的primary颜色，而我们没有使用它。我们会在之后的开发中使用。

好了，今天就先写到这里吧。这里的代码我放到了GitHub上，如果你不愿意手敲代码，可以
```text
git clone https://github.com/PythonSamZhang/AttributeError.git
```
之后
```text
git checkout f63784c
```
最后
```text
pip install -r requirements.txt
```
GitHub仓库：
[GitHub仓库​github.com](https://link.zhihu.com/?target=https%3A//github.com/PythonSamZhang/AttributeError)

自定义的Bootstrap CSS我也放在了仓库里，位于/app/static/Bootstrap中。


## 写在最后

因为我自己也是一枚小白，所以如果有写的不正确的地方还请大神们指教 :-)
