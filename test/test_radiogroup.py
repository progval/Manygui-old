from manygui import *
from manygui.Utils import log

labels = ["Banana", "Chocolate", "Strawberry"]

grp = RadioGroup()
grp1 = RadioGroup()

def report(**kw):
    log(grp.value)
    log(labels[grp.value], "selected (%d)" % grp.value)

def report1(**kw):
    log(labels[grp1.value], "selected (%d)" % grp1.value)
    
app = Application()

win = Window(width = 260, height = 150)
app.add(win)
for i in range(0, 3):
    btn = RadioButton(x = 30, y = (i+1) * 30, width = 100, height = 30, 
                      text = labels[i],
                      group = grp, value = i)
    link(btn, report)
    win.add(btn)

for i in range(0, 3):
    btn = RadioButton(x = 130, y = (i+1) * 30, width = 100, height = 30, 
                      text = 'x'+labels[i],
                      group = grp1, value = i)
    link(btn, report1)
    win.add(btn)

grp.value = 1

app.run()
