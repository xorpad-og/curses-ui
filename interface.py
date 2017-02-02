import curses


class InterfaceObject(object):
	def __init__(self):
		self.bufposition = 0
		self.scrollback = []
		self.commandhist = []
		self.currentline = 0
		self.screen = curses.initscr()
		self.window = None
		self.sidebar = None
		self.inputwin = None
		self.height,self.width=self.screen.getmaxyx()
		self.inbut = ""

def ScreenRefresh(uiobj):
	if uiobj.bufposition > uiobj.width and uiobj.bufposition == len(uiobj.inbuf):
		uiobj.screen.move(uiobj.height-2,uiobj.width-1)
	elif uiobj.bufposition <= uiobj.width:
		uiobj.screen.move(uiobj.height-2,uiobj.width-1)
	else:
		uiobj.screen.move(uiobj.height-2,uiobj.bufposition - uiobj.width)
#	uiobj.screen.clear()
	uiobj.screen.refresh()
	uiobj.window.box()
	uiobj.window.refresh()
	uiobj.inputwin.box()
	uiobj.inputwin.refresh()
	uiobj.sidebar.box()
	uiobj.sidebar.refresh()

def sendText(uiobj,text):
	uiobj.window.addstr(uiobj.currentline,0,text)
	uiobj.window.clrtoeol()
	uiobj.screen.move(height-2,0)
	uiobj.window.scrollback.append(text)
	uiobj.currentline += 1
	ScreenRefresh(uiobj)

def initWindows(uiobj):
	curses.noecho()
	curses.cbreak()
	uiobj.screen.keypad(True)
	curses.curs_set(2)	

	begin_x=0
	begin_y=0
	window = curses.newwin(uiobj.height-3,uiobj.width-25,0,0)
	sidebar = curses.newwin(uiobj.height-3, 25, 0, uiobj.width-25)
	inputwin = curses.newwin(3,uiobj.width,uiobj.height-3,0)

	
	window.idlok(False)
	window.leaveok(False)
	window.scrollok(False)
	window.box()
	uiobj.window = window

	sidebar.idlok(False)
	sidebar.leaveok(False)
	sidebar.scrollok(False)
	sidebar.box()
	uiobj.sidebar = sidebar

	inputwin.idlok(False)
	inputwin.leaveok(False)
	inputwin.scrollok(False)
	inputwin.box()
	uiobj.inputwin = inputwin
	
	ScreenRefresh(uiobj)
def wordwrap(text):
	lines = []
	split = text.split()

	linestring = ""
	for word in split:
		if len(linestring) + len(word) < width:
			linestring = linestring+word
		else:
			lines.append(linestring)
			linestring = word

def get_scrollrange(uiobj):
	length = len(uiobj.scrollback)
	visible = uiobj.height-5
	scrollrange = (len(uiobj.scrollback)-visible, len(uiobj.scrollback))
	if len(uiobj.scrollback) > uiobj.height - 5:
		return (len(uiobj.scrollback)-uiobj.height-5,len(uiobj.scrollback))
	else:
		return (0, len(uiobj.scrollback))
	
def draw_main(uiobj):
	count = 0
	for x in range(get_scrollrange(uiobj)[0],get_scrollrange(uiobj)[1]):
		uiobj.window.addstr(count+1,1,uiobj.scrollback[x])
		count += 1
	ScreenRefresh(uiobj)

def InputLoop(uiobj):
	uiobj.inbuf = ""
	while True:
		ch = uiobj.screen.getch()
		if ch == ord('q'):
			exit(0)
		elif ch == curses.KEY_LEFT or ch == 260:
			if uiobj.bufposition > 0:
				uiobj.bufposition -= 1
				if uiobj.bufposition < uiobj.width:
					uiobj.screen.move(uiobj.height-2,uiobj.bufposition+1)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.width-1-uiobj.bufposition+1)
		elif ch == curses.KEY_RIGHT or ch == 261:
			if uiobj.bufposition < len(uiobj.inbuf):
				uiobj.bufposition += 1
				if uiobj.bufposition+1 <uiobj. width-1:
					uiobj.screen.move(uiobj.height-2,uiobj.bufposition+1)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.width-1)
		elif ch == curses.KEY_ENTER or ch == 10 or ch == 13:
			uiobj.screen.move(uiobj.height-2,1)
			uiobj.inputwin.addstr(1,1," ")
			uiobj.inputwin.clrtoeol()
			uiobj.scrollback.append(uiobj.inbuf)
			uiobj.commandhist.append(uiobj.inbuf)

			ScreenRefresh(uiobj)

#			uiobj.window.addstr(uiobj.currentline+1,1,uiobj.inbuf)
#			uiobj.scrollback.append(uiobj.inbuf)
#			uiobj.currentline += 1
			if  uiobj.currentline+1  >=  uiobj.height-4:
				for line in range(uiobj.currentline-1):
					if len(uiobj.scrollback) >= uiobj.height-4:
#						uiobj.scrollback.remove(uiobj.scrollback[line])
						uiobj.currentline = 0
						break
					if uiobj.bufposition != 0 and uiobj.bufposition != len(uiobj.inbuf):
						str1 = line[:uiobj.bufposition] + str(chr(ch)) +line[uiobj.bufposition:]
						uiobj.window.addstr(uiobj.currentline+1,1,str1)
						uiobj.commandhist.append(str1)
						uiobj.window.clrtoeol()
						uiobj.screen.move(height-2,1)
						uiobj.currentline += 1
						ScreenRefresh(uiobj)
			if uiobj.currentline == 0:
				for line in uiobj.scrollback:
					uiobj.window.addstr(uiobj.currentline+1,1,line)
					uiobj.window.clrtoeol()
					uiobj.screen.move(uiobj.height-2,1)
					uiobj.currentline += 1
					ScreenRefresh(uiobj)

			uiobj.screen.move(uiobj.height-2,1)
			ScreenRefresh(uiobj)
			uiobj.inbuf = ""
			uiobj.bufposition = 0
			draw_main(uiobj)
			continue
		elif ch == curses.KEY_BACKSPACE or ch == 127 or ch == 800 or ch == 8:
			if len(inbuf) > uiobj.width:
				uiobj.inbuf = uiobj.inbuf[:-1]
				if len(uiobj.inbuf)+1 < uiobj.width-1:
					uiobj.screen.move(uiobj.height-2,len(uiobj.inbuf)+1)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.width-1)
				if len(uiobj.inbuf) - uiobj.width > 0:
					extra= len(uiobj.inbuf) - uiobj.width
					curbuf =  uiobj.inbuf[:-extra]
				else:
					curbuf =uiobj.inbuf
				uiobj.inputwin.addstr(1,1,curbuf[-width-2:])
				if len(curbuf) < uiobj.width-2:
					uiobj.screen.move(uiobj.height-2,len(uiobj.curbuf)+1)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.width-1)
				uiobj.inputwin.clrtoeol()
				ScreenRefresh(uiobj)
			elif len(inbuf) > 0:
				uiobj.inbuf = uiobj.inbuf[:-1]
				uiobj.inputwin.addstr(1,1,uiobj.inbuf[-width-2:])
				if  len(uiobj.inbuf) - uiobj.width-2 > 0:
					uiobj.screen.move(uiobj.height-2,len(uiobj.inbuf)+1-uiobj.width-1)
				else:
					uiobj.screen.move(uiobj.height-2,len(uiobj.inbuf)+1)
				inputwin.clrtoeol()
				ScreenRefresh(uiobj)
		else:
			uiobj.bufposition += 1
			if uiobj.bufposition < uiobj.width-2:
				uiobj.screen.move(uiobj.height-2,uiobj.bufposition+1)
			if uiobj.bufposition-1 != len(uiobj.inbuf):
#				uiobj.inbuf = uiobj.inbuf[:uiobj.bufposition-1] + str(chr(ch)) + uiobj.inbuf[uiobj.bufposition-1]
				uiobj.inbuf = uiobj.inbuf[:uiobj.bufposition] + str(chr(ch)) + uiobj.inbuf[uiobj.bufposition]
			else:
				uiobj.inbuf = "%s%s" % (uiobj.inbuf,str(chr(ch)))
			if len(uiobj.inbuf) >= uiobj.width:
				tempbuf = uiobj.inbuf[len(uiobj.inbuf) - uiobj.width -2:]
				uiobj.inputwin.addstr(1,1,tempbuf)
				uiobj.inputwin.clrtoeol()
				uiobj.screen.move(uiobj.height-2,uiobj.width-1)
				ScreenRefresh(uiobj)
			elif len(uiobj.inbuf) < uiobj.width-2:
				uiobj.inputwin.addstr(1,1,uiobj.inbuf)
				uiobj.screen.move(uiobj.height-2,len(uiobj.inbuf)-1)
				uiobj.inputwin.clrtoeol()
				ScreenRefresh(uiobj)
def killCurses(uiobj):
	curses.nocbreak()
	uiobj.screen.keypad(0)
	curses.echo()
	curses.endwin()

interface = InterfaceObject()

initWindows(interface)

InputLoop(interface)

killCurses(interface)