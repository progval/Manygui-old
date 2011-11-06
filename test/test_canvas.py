from manygui import *
from manygui.Utils import log
from manygui.Colors import *

# Not all backends support this -- it is not a part of 0.1:
from manygui import Canvas

app = Application()
win = Window(size=(300,300))
app.add(win)
cvs = Canvas(size=win.size)
win.add(cvs)

def click(source, event):
    log('[Mouse clicked at (%i, %i)]' % (event.x, event.y))
    if 30 <= event.x <= 100 and 30 <= event.y <= 100:
        log('Yay! You clicked the round rect!')

link(cvs, events.LeftClickEvent, click)

# Taken from http://piddle.sourceforge.net/sample1.html

cvs.defaultLineColor = Color(0.7,0.7,1.0)    # light blue
if not backend() in 'text curses'.split():
    cvs.drawLines([(i*10,0,i*10,300) for i in range(30)])
    cvs.drawLines([(0,i*10,300,i*10) for i in range(30)])
cvs.defaultLineColor = colors.black

cvs.drawLine(10, 200, 20, 190, color=colors.red)
cvs.drawEllipse(130, 30, 200, 100, fillColor=colors.yellow, edgeWidth=4)

cvs.drawArc(130, 30, 200, 100, 45, 50, fillColor=colors.blue, edgeColor=colors.navy, edgeWidth=4)

cvs.defaultLineWidth = 4
cvs.drawRoundRect(30, 30, 100, 100, fillColor=colors.blue, edgeColor=colors.maroon)
cvs.drawCurve(20, 20, 100, 50, 50, 100, 160, 160)

#cvs.drawString("This is a test!", 30,130, Font(face="times",size=16,bold=1), 
#                color=green, angle=-45)

polypoints = [(160,120), (130,190), (210,145), (110,145), (190,190)]
cvs.drawPolygon(polypoints, fillColor=colors.lime, edgeColor=colors.red, edgeWidth=3, closed=1)

cvs.drawRect(200, 200, 260, 260, edgeColor=colors.yellow, edgeWidth=5)
cvs.drawLine(200, 260, 260, 260, color=colors.green, width=5)
cvs.drawLine(260, 200, 260, 260, color=colors.red, width=5)

#cvs.flush()

app.run()
