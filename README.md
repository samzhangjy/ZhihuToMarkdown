# ZhihuToMarkdown

这是一个使用Python编写的，能够自动导出知乎文章到Markdown格式的小项目。

## 使用

目前支持获取某一个文章的Markdown，和获取一个账号下所有文章的Markdown。使用方法均在`get_articles.py`的196-203行。更详细的函数接口请自行阅读代码内注释。**请注意，如果是获取某个账号下所有文章，输入的用户名不是实际的用户名，比如我的账号实际用户名是橘子苹果香蕉，但是到程序里的时候是要输入用户主页URL的用户名的，比如我的主页链接是<https://www.zhihu.com/people/samzhangjy>，那么到程序里只需要输入`https://www.zhihu.com/people/`后面的`samzhangjy`就可以了。**

目前还有很多不足的地方，也欢迎大家来提出问题！
