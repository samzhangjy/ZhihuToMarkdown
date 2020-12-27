# Flask 开发论坛 - 数据库

这个项目的全部目录在
[这里](https://zhuanlan.zhihu.com/p/113539585)

在
[上一篇文章](https://zhuanlan.zhihu.com/p/113371160)
里，我们搭建好了最最基本的首页，现在让我们来实现用户登录，注册的环节。

首先，在开始前，我们需要一个数据库。这里我选择的是MySQL数据库，具体可以从
[这篇博客](https://link.zhihu.com/?target=https%3A//blog.csdn.net/yangwei234/article/details/89028314)
里进行配置（他使用的是Windows系统，如果是Mac的话也是差不多的，就是跳过了安装Visual Studio的步骤）。

配置好数据库后，我们需要连接它。这里我也是费了好久才配置好，用的是PyMysql。首先，让我们来创建一个数据库。打开mysql终端，输入：
```mysql
CREATE DATABASE <database-name>;
```
把其中的&lt;database-name&gt;替换成你自己的数据库名称，然后关闭MySQL终端，在命令行里输入
把其中的&lt;database-name&gt;替换成你自己的数据库名称，然后关闭MySQL终端，在命令行里输入
```bash
pip install flask-sqlalchemy
```
来安装SQLAlchemy。然后，在extensions.py中实例化它：
```python
from flask_bootstrap import Bootstrap  # 导入Bootstrap-Flask
from flask_sqlalchemy import SQLAlchemy

bootstrap = Bootstrap()  # 实例化扩展
db = SQLAlchemy()

```
现在如果运行程序，可能会发现有几个警告，不过那是因为我们还没有设置数据库呢。现在让我们就来设置。先打开命令行，输入
```bash
pip install pymysql
```
来安装pymysql。安装完之后，在app文件夹里创建config.py，来存放所有的设置。在config.py里输入：
```python
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


class ProductionConfig:
    DEBUG = False  # 关闭调试
    # 设置在生产环境中使用的数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'mysql+pymysql://root:%s@localhost:3306/%s?charset' \
                               '=utf8mb4' % (os.environ.get('DATABASE_PASS'), os.environ.get('DATABASE_NAME'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# 设置在不同情况下使用的config
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}

```
现在，我们就可以在init.py中引入它了：
```text
import os

from flask import Flask  # 导入Flask
from .extensions import *  # 导入已经实例化了的扩展
from app.config import config  # 导入config


def create_app():
    app = Flask(__name__)  # 创建app实例
    app.config.from_object(config[os.environ.get('FLASK_ENV')])  # 设置从config中导入设置

    # ...

    return app  # 返回app

```
但是这还不行，因为在config.py中，我们使用了2个环境变量，所以我们需要先定义他们，再运行程序。但是这样太太麻烦了，因为环境变量只在当前会话中有用。但是，我们可以用python-dotenv来简化。首先，安装它：
```bash
pip install python-dotenv
```
然后，再在根目录下创建一个.env文件，来存放环境变量：
```text
FLASK_APP=app.py
DEV_DATABASE_PASS=<database-password>
DEV_DATABASE_NAME=<database-name>
```
把&lt;database-password&gt;和&lt;database-name&gt;替换成你的数据库密码和名称就好了。现在我们再运行程序，应该一切都跟以前一样，因为我们还没有创建表。现在在app下创建models.py，来存放数据库模型：
把&lt;database-password&gt;和&lt;database-name&gt;替换成你的数据库密码和名称就好了。现在我们再运行程序，应该一切都跟以前一样，因为我们还没有创建表。现在在app下创建models.py，来存放数据库模型：
```text
from .extensions import db  # 导入SQLAlchemy


class User(db.Model):  # User类继承自db.Model
    __tablename__ = 'users'  # 定义表名
    id = db.Column(db.Integer, primary_key=True)  # 定义id，并且为主键
    username = db.Column(db.String(64))  # 用户名
    email = db.Column(db.String(128))  # 邮箱地址

    def __repr__(self):  # 定义User类的返回名称
        return '<User %s>' % self.username  # 返回 <User 用户名>

```
类创建好了，现在我们要更新数据库了。我这里用的是flask-migrate来管理版本。
```text
pip install flask-migrate
```
初始化：
```python
# app/extensions.py

from flask_bootstrap import Bootstrap  # 导入Bootstrap-Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 实例化扩展
bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()

```
```text
# app/__init__.py

# ...

def create_app():
    app = Flask(__name__)  # 创建app实例
    app.config.from_object(config[os.environ.get('FLASK_ENV')])  # 设置从config中导入设置

    # 初始化扩展
    # ...
    migrate.init_app(app, db)

    # ...

    return app  # 返回app

```
现在，我们来初始化flask-migrate：
```bash
flask db init
```
这时，出现了错误：
```py3tb
Traceback (most recent call last):
  File "/Users/sam/Desktop/Python/AttributeError/venv/bin/flask", line 10, in <module>
    sys.exit(main())
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/cli.py", line 966, in main
    cli.main(prog_name="python -m flask" if as_module else None)
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/cli.py", line 586, in main
    return super(FlaskGroup, self).main(*args, **kwargs)
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/click/core.py", line 782, in main
    rv = self.invoke(ctx)
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/click/core.py", line 1259, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/click/core.py", line 1259, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/click/core.py", line 1066, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/click/core.py", line 610, in invoke
    return callback(*args, **kwargs)
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/click/decorators.py", line 21, in new_func
    return f(get_current_context(), *args, **kwargs)
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/cli.py", line 425, in decorator
    with __ctx.ensure_object(ScriptInfo).load_app().app_context():
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/cli.py", line 388, in load_app
    app = locate_app(self, import_name, name)
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/cli.py", line 257, in locate_app
    return find_best_app(script_info, module)
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/cli.py", line 83, in find_best_app
    app = call_factory(script_info, app_factory)
  File "/Users/sam/Desktop/Python/AttributeError/venv/lib/python3.8/site-packages/flask/cli.py", line 119, in call_factory
    return app_factory()
  File "/Users/sam/Desktop/Python/AttributeError/app/__init__.py", line 12, in create_app
    app.config.from_object(config[os.environ.get('FLASK_ENV')])  # 设置从config中导入设置
KeyError: None
```
这需要我们更改一处代码：
```python
# app/__init__.py

# ...


def create_app():
    app = Flask(__name__)  # 创建app实例
    # 设置从config中导入设置，如果没有设置环境，则从default导入
    app.config.from_object(config[os.environ.get('FLASK_ENV') or 'default'])

    # ...

    return app  # 返回app
```
这里，我们设置如果FLASK_ENV是None，就从default导入。现在再初始化：
```text
flask db init
```
就不会报错了。应该会在根目录下创建一个名为migrations的文件夹，用来存储数据库模型的改动。现在，来升级数据库：
```text
flask db migrate
```
会出现「No changes in schema detected.」。原因是flask-migrate是从文件的import来判断是否出现改动的，而我们没有在任何文件里引入models.py。现在，在app中创建auth文件夹，并创建__init__.py：
```text
# app/auth/__init__.py

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views

```
然后，创建views.py：
```text
# app/auth/views.py

from . import auth
from app.models import User

```
然后，注册auth蓝本：
```text
# app/__init__.py

# ...


def create_app():
    app = Flask(__name__)  # 创建app实例
    # ...

    from .main import main as main_bp  # 导入蓝图
    app.register_blueprint(main_bp)  # 注册蓝图到应用

    from .auth import auth as auth_bp
    app.register_blueprint(auth_bp)

    return app  # 返回app

```
现在再执行flask db migrate，就可以正常生成更新文件了。要想让这个文件生效，需要升级数据库：
```bash
flask db upgrade
```
现在，让我们来测试一下数据库，使用flask shell来打开flask的交互式shell：
```python
Python 3.8.1 (v3.8.1:1b293b6006, Dec 18 2019, 14:08:53) 
[Clang 6.0 (clang-600.0.57)] on darwin
App: app [production]
Instance: /Users/sam/Desktop/Python/AttributeError/instance
>>> from app.models import User
>>> u = User(username='Test', email='test@example.com')  # 创建用户名是Test的用户
>>> from app.extensions import db
>>> db.session.add(u)  # 在本次会话中添加用户
>>> db.session.commit()  # 将更改提交到数据库中
>>> u
<User Test>
>>> u.username  # 获取用户的用户名
'Test'
>>> u.email  # 获取用户的邮箱
'test@example.com'
>>> u.id  # 获取用户的id
1
>>> db.session.delete(u)  # 删除用户
>>> db.session.commit()
>>> User.query.all()  # 获取所有用户
[]

```
你可能会发现，现在的模型中，所有的用户都是平等的，没有管理员。现在，让我们来解决这个问题：
```text
# app/models.py

from .extensions import db  # 导入SQLAlchemy


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    users = db.relationship('User', backref='role', lazy='dynamic')  # 创建一个关联

    def __repr__(self):
        return '<Role %s>' % self.name


class User(db.Model):  # User类继承自db.Model
    __tablename__ = 'users'  # 定义表名
    id = db.Column(db.Integer, primary_key=True)  # 定义id，并且为主键
    username = db.Column(db.String(64))  # 用户名
    email = db.Column(db.String(128))  # 邮箱地址
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __repr__(self):  # 定义User类的返回名称
        return '<User %s>' % self.username  # 返回 <User 用户名>

```
我们来更新数据库：
```bash
flask db migrate -m "Added role"
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'role'
INFO  [alembic.autogenerate.compare] Detected added column 'users.role_id'
INFO  [alembic.autogenerate.compare] Detected added foreign key (role_id)(id) on table users
  Generating /Users/sam/Desktop/Python/AttributeError/migrations/versions/93740ecd2a4a_added_role.py ...  done

flask db upgrade
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 8f7a7e6cb8af -> 93740ecd2a4a, Added role
```
现在在flask shell中测试一下：
```python
Python 3.8.1 (v3.8.1:1b293b6006, Dec 18 2019, 14:08:53) 
[Clang 6.0 (clang-600.0.57)] on darwin
App: app [production]
Instance: /Users/sam/Desktop/Python/AttributeError/instance
>>> from app.models import Role, User
>>> from app.extensions import db
>>> admin = Role(name='Admin')
>>> db.session.add(admin)
>>> user = Role(name='Users')
>>> db.session.add(user)
>>> db.session.commit()
>>> # Role.query.filter_by(name='Users').first()，从所有Role里查找name为Users的那一个
>>> u1 = User(username='Test User', email='testuser@example.com', role=Role.query.filter_by(name='Users').first())
>>> db.session.add(u1)
>>> db.session.commit()
>>> u1.role
<Role Users>
>>> u2 = User(username='Test Admin', email='testadmin@example.com', role=Role.query.filter_by(name='Admin').first())
>>> db.session.add(u2)
>>> db.session.commit()
>>> u2.role
<Role Admin>
>>> admin.users.all()
[<User Test Admin>]
>>> user.users.all()
[<User Test User>]
```
好了，今天就先写到这里吧。我已经把代码放到了
[GitHub](https://link.zhihu.com/?target=https%3A//github.com/PythonSamZhang/AttributeError)
上，你可以git checkout ef00826来查出这个版本，注意要新建.env文件，填入环境变量，并且执行flask db upgrade来升级数据库。

## 写在最后

这是这个系列的第2篇文章，因为我也是一个小白，所以如果哪里有误还请大神多多指教
