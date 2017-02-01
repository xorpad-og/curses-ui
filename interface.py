import curses
import curses.textpad

screen = curses.initscr()
height,width=screen.getmaxyx()
curses.noecho()
curses.cbreak()
screen.keypad(True)
curses.curs_set(1)

window = curses.newwin(height-1,width-1,0,0)
window.clrtoeol()
cursor_position = 0
screen.move(height-2,0)
command_history = []

screenbuffer = []

def send_to_screen(text):
	screenbuffer.append(text)

inbuf = ""
while True:
	screen.move(height-2,cursor_position)
	key = screen.getch()
#	window.addstr(0,0,str(key))
	if key == ord('q'):
		exit(0)
	elif key == curses.KEY_ENTER or key == 10 or key == 13:
		if inbuf != "":
			window.addstr(0,0,inbuf)
			window.refresh()
			commandhistory.append(inbuf)
			inbuf = ""
			cursor_position = 0
			screen.move(height-2,0)
	elif key == curses.KEY_BACKSPACE or key == 127:
		if cursor_postion > 0:
			inbuf = inbuf[:1]
			cursor_position -= 1
			screen.move(height-2,cursor_position)
			if len(inbuf) > width-1:
				tempbuf = inbuf[len(inbuf)-width-1:]
			else:
				window.addstr(height-2,0,tempbuf)		
				padding = width - len(inbuf)-2
				tempbuf = inbuf
				for i in range(padding):
					tempbuf = tempbuf + " "
				window.addstr(height-2,0,tempbuf)
	else:
		inbuf = "%s%s" % (inbuf, chr(key))
		screen.move(height-2,0)
		padding = width - len(inbuf)-2
		tempbuf = inbuf
		for i in range(padding):
			tempbuf = tempbuf + " "
		if len(inbuf) > width-1:
			tempbuf = inbuf[len(inbuf)-width-1:]
			screen.move(height-2,cursor_position)
			window.addstr(height-2,0,tempbuf)
		else:
			window.addstr(height-2,0,tempbuf)
			cursor_position += 1
		window.refresh()

curses.nocbreak()
screen.keypad(False)
curses.echo()
curses.endwin()