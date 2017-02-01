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
		window.refresh()
		inbuf = ""
		continue
	else:
		inbuf = "%s%s" % (inbuf,str(chr(ch)))
		if len(inbuf) >= width:
			tempbuf = inbuf[len(inbuf) - width - 1:]
			window.addstr(height-2,0,tempbuf)
			window.clrtoeol()
			window.refresh()
		else:
			window.addstr(height-2,0,inbuf)
			window.clrtoeol()
			window.refresh()


curses.nocbreak()
screen.keypad(0)
curses.echo()
curses.endwin()