import curses

screen = curses.initscr()
height,width=screen.getmaxyx()
curses.noecho()
curses.cbreak()
screen.keypad(True)
curses.curs_set(2)	

scrollback = []
commandhist = []
currentline = 0

begin_x=0
begin_y=0
wheight = height
wwidth = width
window = curses.newwin(wheight,wwidth,begin_y,begin_x)
screen.move(height-2,0)
window.refresh()

window.idlok(1)

screen.move(height-2,0)
screen.clear()
window.refresh()
inbuf = ""


def sendText(text):
	window.addstr(currentline,0,text)
	window.clrtoeol()
	screen.move(height-2,0)
	window.scrollback.append(text)
	currentline += 1
	window.refresh()

while True:
	ch = screen.getch()
	if ch == ord('q'):
		exit(0)
	elif ch == curses.KEY_ENTER or ch == 10 or ch == 13:
		screen.move(0,0)
		window.clrtoeol()
		screen.move(height-2,0)
		window.clrtoeol()
		window.addstr(height-2,0," ")
		window.clrtoeol()
		window.refresh()

		scrollback.append(inbuf)
		commandhist.append(inbuf)

		window.addstr(currentline,0,inbuf)
		currentline += 1
		if  currentline  >=  height-3:
			for line in range(currentline):
				if len(scrollback) >= height-3:
					scrollback.remove(scrollback[line])
					currentline = 0
					break
				window.addstr(currentline,0,line)
				window.clrtoeol()
				screen.move(height-2,0)
				currentline += 1
		if currentline == 0:
			for line in scrollback:
				window.addstr(currentline,0,line)
				window.clrtoeol()
				screen.move(height-2,0)
				currentline += 1
				window.refresh()

		window.clrtoeol()
		screen.move(height-2,0)
		window.refresh()
		inbuf = ""
		continue
	elif ch == curses.KEY_BACKSPACE or ch == 127 or ch == 800 or ch == 8:
		if len(inbuf) > width:
			inbuf = inbuf[:-1]
			if len(inbuf) < width:
				screen.move(height-2,len(inbuf))
			else:
				screen.move(height-2,width-1)
			if len(inbuf) - width > 0:
				extra= len(inbuf) - width
				curbuf =  inbuf[:-extra]
			else:
				curbuf = inbuf
			window.addstr(height-2,0,curbuf)
			if len(curbuf) < width:
				screen.move(height-2,len(curbuf))
			else:
				screen.move(height-2,width-1)
			window.clrtoeol()
			window.refresh()
		elif len(inbuf) > 0:
			inbuf = inbuf[:-1]
			window.addstr(height-2,0,inbuf)
			if  len(inbuf) - width > 0:
				screen.move(height-2,len(inbuf)-width)
			else:
				screen.move(height-2,len(inbuf))
			window.clrtoeol()
			window.refresh()
	else:
		inbuf = "%s%s" % (inbuf,str(chr(ch)))
		if len(inbuf) >= width:
			tempbuf = inbuf[len(inbuf) - width :]
			window.addstr(height-2,0,tempbuf)
			window.clrtoeol()
			screen.move(height-2,width-1)
			window.refresh()
		elif len(inbuf) < width:
			window.addstr(height-2,0,inbuf)
			screen.move(height-2,len(inbuf))
			window.clrtoeol()
			screen.move(height-2,len(inbuf))
			window.refresh()

curses.nocbreak()
screen.keypad(0)
curses.echo()
curses.endwin()