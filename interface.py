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
		self.inbuf = ""

def ScreenRefresh(uiobj):
	if uiobj.bufposition > uiobj.width and uiobj.bufposition == len(uiobj.inbuf):
		uiobj.screen.move(uiobj.height-2,uiobj.width-1)
	elif uiobj.bufposition <= uiobj.width:
		uiobj.screen.move(uiobj.height-2,uiobj.width-1)
	else:
		uiobj.screen.move(uiobj.height-2,uiobj.bufposition - uiobj.width)
	uiobj.window.box()
	uiobj.window.refresh()
	uiobj.inputwin.box()
	uiobj.inputwin.refresh()
	uiobj.sidebar.box()
	uiobj.sidebar.refresh()
	uiobj.screen.refresh()

def sendText(uiobj,text):
	lines = wordwrap(text,uiobj.width-25)
	for line in lines:
		uiobj.window.addstr(uiobj.currentline,1,line)
		uiobj.currentline += 1
		uiobj.window.clrtoeol()
		uiobj.screen.move(uiobj.height-2,0)
		uiobj.scrollback.append(line)
	ScreenRefresh(uiobj)

#def updateInput(uiobj):
#	if len(inbuf) > uiobj.width-2:
#	uiobj.inputwin.addstr(1,1,uiobj.inbuf)

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

def wordwrap(text,length):
	lines = []
	split = text.split()

	linestring = ""
	words = 0
	for word in split:
		if len(linestring) + len(word) <= length:
			if words > 0:
				linestring = linestring + " " + word
				words += 1
			else:
				linestring = word
				words += 1
		else:
			lines.append(linestring)
			linestring = word
			words = 1
	lines.append(linestring)
	return lines

def get_scrollrange(uiobj):
	if len(uiobj.scrollback) <= uiobj.height - 5:
		return(0,len(uiobj.scrollback))
	elif len(uiobj.scrollback) > uiobj.height - 5:
		return(len(uiobj.scrollback)-uiobj.height - 5, len(uiobj.scrollback))
	else:
		return (0, len(uiobj.scrollback))

def draw_main(uiobj):
	count = 0
	if len(uiobj.scrollback) < uiobj.height-5:
		return(0,len(uiobj.scrollback))
	for x in range(get_scrollrange(uiobj)):
		sendText(uiobj,scrollback[x])
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
				if uiobj.bufposition < uiobj.width-2:
					uiobj.screen.move(uiobj.height-2,uiobj.bufposition+1)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.width-1-uiobj.bufposition+1)
				uiobj.bufposition -= 1
			ScreenRefresh(uiobj)
		elif ch == curses.KEY_RIGHT or ch == 261:
			if uiobj.bufposition < len(uiobj.inbuf):
				if uiobj.bufposition+1 <uiobj.width-1:
					uiobj.screen.move(uiobj.height-2,uiobj.bufposition+1)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.width-1)
				uiobj.bufposition += 1
			ScreenRefresh(uiobj)
		elif ch == curses.KEY_ENTER or ch == 10 or ch == 13:
			uiobj.screen.move(uiobj.height-2,1)
			uiobj.inputwin.addstr(1,1," ")
			uiobj.inputwin.clrtoeol()
			lines = wordwrap(uiobj.inbuf,uiobj.width-25)
			for line in lines:
				uiobj.scrollback.append(line)
			uiobj.commandhist.append(uiobj.inbuf)
			ScreenRefresh(uiobj)


			if uiobj.currentline == 0:
				uiobj.currentline = 1
			if uiobj.currentline+1  >=  uiobj.height-4:
				for x in range(get_scrollrange(uiobj)):
					sendText(uiobj,uiobj.scrollback[x])
			else:
					sendText(uiobj,uiobj.inbuf)

			uiobj.screen.move(uiobj.height-2,1)
			uiobj.inbuf = ""
			uiobj.bufposition = 0
			draw_main(uiobj)
			ScreenRefresh(uiobj)
			continue
		elif ch == curses.KEY_BACKSPACE or ch == 127 or ch == 800 or ch == 8:
			if len(uiobj.inbuf) > uiobj.width:
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
			elif len(uiobj.inbuf) > 0:
				uiobj.inbuf = uiobj.inbuf[:-1]
				uiobj.inputwin.addstr(1,1,uiobj.inbuf[-uiobj.width-2:])
				if  len(uiobj.inbuf) - uiobj.width-2 > 0:
					uiobj.screen.move(uiobj.height-2,len(uiobj.inbuf)+1-uiobj.width-1)
				else:
					uiobj.screen.move(uiobj.height-2,len(uiobj.inbuf)+1)
				uiobj.inputwin.clrtoeol()
				ScreenRefresh(uiobj)
		else:
			uiobj.bufposition += 1
			if uiobj.bufposition < uiobj.width-2:
				uiobj.screen.move(uiobj.height-2,uiobj.bufposition+1)
			if uiobj.bufposition != len(uiobj.inbuf):
				if uiobj.bufposition == 0:
					uobj.inbuf = str(chr(ch)) + uobj.inbuf
				else:
					uiobj.inbuf = uiobj.inbuf[:uiobj.bufposition] + str(chr(ch)) + uiobj.inbuf[uiobj.bufposition:]
			else:
				uiobj.inbuf = "%s%s" % (uiobj.inbuf,str(chr(ch)))
			if len(uiobj.inbuf) >= uiobj.width:
				tempbuf = uiobj.inbuf[len(uiobj.inbuf) - uiobj.width -2:]
				uiobj.inputwin.addstr(1,1,tempbuf)
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
