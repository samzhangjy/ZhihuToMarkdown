# Tkinter （3）---Button

前两天想写文章的时候突然发现自己用的PyCharm坏了，再一详细看原来是360杀毒把自己常用的虚拟环境文件夹给删了，无奈只好重新安装包。。。今天才弄好。。。算了，废话不多说，直接进入正题。

咱们在日常生活中用电脑或者手机除了文字看见最多的应该就是按钮了。那今天我就来记一记在Tkinter中使用Button控件吧~

先上实例：
1. Button控件最简单的使用:

```python
# Button控件
import tkinter as tk

def callback():
    """当按钮被点击时执行的命令"""
    print("You pressed the button!")


win = tk.Tk() #创建窗口win
win.minsize(100,100) #设置窗口最小大小
button = tk.Button(win,text="hit me",command=callback) #创建一个Button控件，注意command=callback不能加括号，否则会自动执行
button.pack() #打包button控件
win.mainloop() #进入主循环
```
运行结果如下:
![https://pic2.zhimg.com/v2-c2ff550b84a46786f32b5adaa1e549dd_b.jpeg](https://pic2.zhimg.com/v2-c2ff550b84a46786f32b5adaa1e549dd_b.jpeg)

点击按钮之后:
![https://pic4.zhimg.com/v2-4ce3e431b48567ac0d71e11ec70759db_b.jpg](https://pic4.zhimg.com/v2-4ce3e431b48567ac0d71e11ec70759db_b.jpg)

以下是对代码的解释:

在第3到第5行中，我们定义了一个函数callback()，这个函数是用于在函数被点击时执行的。

在第7行中，我们设置了窗口win的最小大小，要想设置最大大小可以用 
*root.maxsize(x,y) *。这里的root就代表你要设定最大大小的窗口。

第8行我们创建了一个Button实例，并在按钮点击时执行callback函数。这里一定注意不要加上括号，否则就会自动执行。

第9行我们打包了button，记住在Tkinter中几乎所有的控件都要打包才能显示，有三种打包方式，分别是 
*pack(), grid(),place(x=x,y=y)* 。pack是一般的打包，用于控件不多的情况下（个人观点），而grid则是可以更直观地进行布局，横，竖都很齐，一般用于控件多且需要美观布局的情况下（还是个人观点。。。），place就是可以指定控件的准确位置，用于需要精准布局的情况下（依旧是个人观点），注意x=和y=一定要加上，否则会报错。


2. 按钮的样式与布局:
```text
# Button控件
import tkinter as tk
from tkinter import *
win = tk.Tk()
#以下是几个常用的button样式
bt1 = Button(win,text="raised",relief=RAISED)
bt1.grid()
bt2 = Button(win,text="sunken",relief=SUNKEN)
bt2.grid()
bt3 = Button(win,text="flat",relief=FLAT)
bt3.grid()
bt4 = Button(win,text="groove",relief=GROOVE)
bt4.grid()
bt6 = Button(win,text="ridge",relief=RIDGE)
bt6.grid()
win.mainloop()
```
运行结果如下:
![https://pic2.zhimg.com/v2-bb099cce59d9a024b57d05d9a8ecdfcd_b.jpeg](https://pic2.zhimg.com/v2-bb099cce59d9a024b57d05d9a8ecdfcd_b.jpeg)

代码中relief是设置按钮样式，注意等号后面的样式名称一定要全部大小，否则Python读不懂。。。


今天就先写到这，如果有误，请及时告知我，我会及时修改！
