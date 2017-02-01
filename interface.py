import curses

screen = curses.initscr()
height,width=screen.getmaxyx()
curses.noecho()
curses.cbreak()
screen.keypad(True)
curses.curs_set(2)	

begin_x=0
begin_y=0
wheight = height
wwidth = width
window = curses.newwin(wheight,wwidth,begin_y,begin_x)

window.idlok(1)


screen.move(height-2,0)
screen.clear()
window.refresh()
inbuf = ""
while True:
	ch = screen.getch()
	if ch == ord('q'):
		exit(0)
	elif ch == curses.KEY_ENTER or ch == 10 or ch == 13:
		window.addstr(0,0,inbuf)
		window.clrtoeol()
		screen.move(height-2,0)
		window.refresh()
		inbuf = ""
		continue
	elif ch == curses.KEY_BACKSPACE or ch == 127 or ch == 800 or ch == 8:
		if len(inbuf) > width:
			#screen.clear()
			inbuf = inbuf[:-1]
			if len(inbuf) > width:
				curbuf =  inbuf[-width:]
				window.addstr(10,0,inbuf[-width:])
			else:
				curbuf = inbuf
			#window.addstr(10,0,curbuf)
			#screen.move(height-2,len(curbuf))
			window.addstr(height-2,0,curbuf)
			window.clrtoeol()
			window.refresh()
		elif len(inbuf) > 0:
			screen.clear()
			inbuf = inbuf[:-1]
			if  len(inbuf) - width > 0:
				screen.move(height-2,len(inbuf)-width)
			window.addstr(height-2,0,inbuf[:width])
			window.clrtoeol()
			screen.move(height-2,len(inbuf))
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
			window.refresh()


		window.refresh()

curses.nocbreak()
screen.keypad(0)
curses.echo()
curses.endwin()