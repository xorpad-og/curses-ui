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

class CursesWindow(object):
	def __init__(self,height,width,loc_y,loc_x):
		self.window = curses.newwin(height,length,loc_y,loc_x,box=True,showcursor=False)
		self.height = height
		self.width = width
		self.loc_y = loc_y
		self.loc_x = loc_x
		self.box = box
		self.scrollback= []

		if showcursor == False:
			self.window.leaveok(1)
		else:
			self.window.leaveok(0)
		window.keypad(0)

	def resize(self,height,length):
		self.window.resize(height,length)
		self.height = hieght
		self.width = width
		#redraw the window backlog

	def move(self,y,x):
		self.loc_y = y
		self.loc_x = x

	def write(self,text):
		if self.box == True:
			lines = wordwrap(text,self.width-2)
		else:
			lines = wordwrap(text,self.width)
		for line in lines:
			self.scrollback.append(line)
		if self.box == True:
			bufferlen = self.height-2
		else:
			bufferlen = self.height

		if self.box == True:
			startx = 1
		else:
			startx = 0
		if len(self.scrollback) < bufferlen:
			curline = bufferlen - len(self.scrollback) + startx
			for lnum in range(len(scrollback)):
				if self.box == True:
					self.window.addstr(curline,1,scrollback[lnum])
					self.window.clrtoeol()
				else:
					self.window.addstr(curline,0,scrollback[lnum])
					self.window.clrtoeol()
			return
		if len(self.scrollback) >= bufferlen:
			curline = startx
			for line in self.scrollback[:-bufferlen-startx,startx]:
				self.window.addstr(curline,startx,line)
				self.window.clrtoeol
		return


def ScreenRefresh(uiobj):
	if uiobj.bufposition > uiobj.width -2 and uiobj.bufposition == len(uiobj.inbuf):
		uiobj.screen.move(uiobj.height-2,uiobj.width-1)
	elif uiobj.bufposition > uiobj.width-2 and uiobj.bufposition <= uiobj.width -2:
		uiobj.screen.move(uiobj.height-2,uiobj.width-1)
	else:
		uiobj.screen.move(uiobj.height-2,uiobj.bufposition+1)
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

def initWindows(uiobj):
	curses.noecho()
	curses.cbreak()
	uiobj.screen.keypad(True)
	curses.curs_set(1)

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
		elif ch == curses.KEY_RESIZE:
			pass	#resize the window
		elif ch == curses.KEY_LEFT or ch == 260:
			if uiobj.bufposition > 0:
				if uiobj.bufposition+1 < uiobj.width-2:
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
				bufposition -= 1
				if len(uiobj.inbuf)+1 < uiobj.width-1:
					uiobj.screen.move(uiobj.height-2,len(uiobj.inbuf)+1)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.width-1)
				if len(uiobj.inbuf) - uiobj.width -2 > 0:
					extra= len(uiobj.inbuf) - uiobj.width-2
					curbuf =  uiobj.inbuf[:-extra]
				else:
					curbuf = uiobj.inbuf
				uiobj.inputwin.addstr(1,1,curbuf[-width-2:])
				if len(curbuf) < uiobj.width-2:
					uiobj.screen.move(uiobj.height-2,len(uiobj.curbuf)+1)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.width-1)
				uiobj.inputwin.clrtoeol()
			elif len(uiobj.inbuf) > 0:
				uiobj.inbuf = uiobj.inbuf[:-1]
				uiobj.bufposition -= 1
				uiobj.inputwin.addstr(1,1,uiobj.inbuf[-uiobj.width-2:])
				if  len(uiobj.inbuf) - uiobj.width-2 > 0:
					uiobj.screen.move(uiobj.height-2,len(uiobj.inbuf)+1-uiobj.width-1)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.bufposition+1)
				uiobj.inputwin.clrtoeol()
		else:
			if uiobj.bufposition < len(uiobj.inbuf):
				if uiobj.bufposition == 0:
					uiobj.inbuf = str(chr(ch)) + uiobj.inbuf
					uiobj.bufposition += 1
				else:
					uiobj.inbuf = uiobj.inbuf[:uiobj.bufposition] + str(chr(ch)) + uiobj.inbuf[uiobj.bufposition:]
					uiobj.bufposition += 1
			else:
				uiobj.inbuf = "%s%s" % (uiobj.inbuf,str(chr(ch)))
				uiobj.bufposition += 1
			if len(uiobj.inbuf) >= uiobj.width-2:
#				tempbuf = uiobj.inbuf[len(uiobj.inbuf) - uiobj.width -2:]
#				tempbuf = uiobj.inbuf[:uiobj.width -2 - len(uiobj.inbuf)]
#				tempbuf = uiobj.inbuf[uiobj.width -2 - len(uiobj.inbuf):]
				tempbuf = uiobj.inbuf[-uiobj.width+2:]
				sendText(uiobj,str(len(tempbuf)))
				sendText(uiobj,str(uiobj.width-2))
				uiobj.inputwin.addstr(1,1,tempbuf)
				uiobj.screen.move(uiobj.height-2,uiobj.width-1)
			elif len(uiobj.inbuf) <= uiobj.width-2:
				uiobj.inputwin.addstr(1,1,uiobj.inbuf)
				uiobj.screen.move(uiobj.height-2,len(uiobj.inbuf)+1)
				uiobj.inputwin.clrtoeol()
		ScreenRefresh(uiobj)

def killCurses(uiobj):
	curses.nocbreak()
	uiobj.screen.keypad(0)
	curses.echo()
	curses.endwin()

interface = InterfaceObject()
initWindows(interface)
ScreenRefresh(interface)
InputLoop(interface)
killCurses(interface)
