from manygui import *
from manygui.Utils import log

app = Application()

g_y = 150

win = Window(width = 110, height = 210)
app.add(win)
newbtn = None

def say_hello(**kw):
    log("Hello, world!")
    global newbtn
    if newbtn is None:
        newbtn = Button(opt, y = g_y)
        newbtn.text = TextModel('new')
        win.add(newbtn)
    else:
        newbtn.text.append('x')

opt = Options(x = 30, width = 50, height = 30)
btn = Button(opt, y = 30, text = "Hello")
link(btn, say_hello)
dis = Button(opt, y = 90, text = "Goodbye", enabled = 0)
link(dis, say_hello)

win.add(btn)
win.add(dis)

app.run()
