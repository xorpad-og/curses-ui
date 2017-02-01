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


window.addstr(0,0,str(width))
window.addstr(1,0,str(width-1))

cursor_position = 0
screen.move(height-2,0)
commandhistory = []

screenbuffer = []
command_history = []
def send_to_screen(text):
	screenbuffer.append(text)
	
def refresh_screen():
	if len(screenbuffer) > height - 3:
		for line, lnum in screenbuffer[height-3:],range(height-3):
			window.addstr(lnum,0, line)
	else:
		for line, lnum in screenbuffer,range(len(screenbuffer)):
			window.addstr(lnum,0, line)
	

inbuf = ""
while True:
	screen.move(height-2,cursor_position)
	key = screen.getch()
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
		if cursor_postion > 0 :
			inbuf = inbuf[:1]
			cursor_position -= 1
			screen.move(height-2,cursor_position)
			if len(inbuf) > 0 and len(inbuf) < width-1:
				padding = width-1  - len(inbuf)-1
				tempbuf = inbuf
				for i in range(padding):
					tempbuf = tempbuf + " "
				window.addstr(height-2,0,tempbuf)
				screen.move(height-2,cursor_position)
			elif len(inbuf) > width-1:
				tempbuf = inbuf[width-1:]
				window.addstr(height-2,0,tempbuf)
				screen.move(height-2,cursor_position)
			elif len(inbuf) == widith-1:
				window.addstr(height-2,0,inbuf)
				padding = width-1  - len(inbuf)-1
				window.addstr(4,0,str(len(inbuf)-1+width-1))
				tempbuf = inbuf
				for i in range(padding):
					tempbuf = tempbuf + " "
				window.addstr(height-2,0,tempbuf)
				cursor_position -= 1
				screen.move(height-2,cursor_position)
			else:
				cursor_position -= 1
				tempbuf = inbuf
				for i in range(padding):
					tempbuf = tempbuf + " "
				screen.move(height-2,cursor_position)
				window.addstr(height-2,0, tempbuf)
	else:
		inbuf = "%s%s" % (inbuf, chr(key))
		screen.move(height-2,0)
		padding = width - len(inbuf)-2
		if len(inbuf) > width-1:
#			tempbuf = inbuf[width-1:]
			window.addstr(height-2,0,inbuf[width-1:])
			cursor_position=width-1
			screen.move(height-2,cursor_position)
		else:
			tempbuf = inbuf
			for i in range(padding):
				tempbuf = tempbuf + " "
			window.addstr(height-2,0,tempbuf)
			cursor_position += 1
			screen.move(height-2,cursor_position)
	window.refresh()

curses.nocbreak()
screen.keypad(False)
curses.echo()
curses.endwin()