import curses

class InterfaceObject(object):
	def __init__(self):
		self.bufposition = 0
		self.commandhist = []
		self.screen = curses.initscr()
		self.mainwindow = None
		self.sidebar = None
		self.inputwin = None
		self.height,self.width=self.screen.getmaxyx()
		self.inbuf = ""

class CursesWindow(object):
	def __init__(self,uiobj,height,width,loc_y,loc_x,box=True,keeplog=False,showcursor=False):
		self.uiobj = uiobj
		self.window = curses.newwin(height,width,loc_y,loc_x)
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
		if box == True:
			self.window.box()
		self.keeplog = keeplog
		self.window.keypad(0)
		self.window.idlok(False)
		self.window.scrollok(False)
		self.refresh()

	def refresh(self):
		if self.box == True:
			self.window.box()
		self.window.refresh()
		self.uiobj.screen.refresh()

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
		if self.keeplog == False:
			self.scrollback = self.scrollback[-bufferlen:]
		if len(self.scrollback) < bufferlen:
			curline = startx
			for line in self.scrollback:
				self.window.addstr(curline,startx,line)
				self.window.clrtoeol()
				curline += 1
			self.refresh()
			return
		if len(self.scrollback) >= bufferlen:
			curline = startx
			for line in self.scrollback[-bufferlen:]:
				self.window.addstr(curline,startx,line)
				self.window.clrtoeol
				curline += 1
			self.refresh()
			return

def initWindows(uiobj):
	curses.noecho()
	curses.cbreak()
	uiobj.screen.keypad(True)
	curses.curs_set(1)

	height,width= uiobj.screen.getmaxyx()
	uiobj.mainwindow = CursesWindow(uiobj,height-3,width-25,0,0,keeplog=True)
	uiobj.sidebar = CursesWindow(uiobj,height-3,width-uiobj.mainwindow.width,0,uiobj.mainwindow.width)
	uiobj.inputwin = CursesWindow(uiobj,3,width,uiobj.mainwindow.height,0,showcursor=True)

	uiobj.mainwindow.refresh()
	uiobj.sidebar.refresh()
	uiobj.inputwin.refresh()

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

def get_scrollrange(window):
	if window.box == True:
		offset = 2
	else:
		offet = 0
	if len(window.scrollback) <= window.height - offset:
		return(0,len(window.scrollback))
	elif len(window.scrollback) > window.height - offset:
		return(len(window.scrollback)-window.height - offset, len(window.scrollback))
	else:
		return (0, len(window.scrollback))

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
				if uiobj.bufposition+1 < uiobj.width-3:
					uiobj.screen.move(uiobj.height-2,uiobj.bufposition+1)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.width-1-uiobj.bufposition+1)
				uiobj.bufposition -= 1
		elif ch == curses.KEY_RIGHT or ch == 261:
			if uiobj.bufposition < len(uiobj.inbuf):
				if uiobj.bufposition+1 <uiobj.width-1:
					uiobj.screen.move(uiobj.height-2,uiobj.bufposition+1)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.width-1)
				uiobj.bufposition += 1
		elif ch == curses.KEY_ENTER or ch == 10 or ch == 13:
			uiobj.mainwindow.write(uiobj.inbuf)

			uiobj.screen.move(uiobj.height-2,1)
			uiobj.inbuf = ""
			uiobj.bufposition = 0
			uiobj.mainwindow.refresh()
			continue

		elif ch == curses.KEY_BACKSPACE or ch == 127 or ch == 800 or ch == 8:
			if uiobj.bufposition-1 > uiobj.width - 2:
				uiobj.bufposition -= 1
				uiobj.inbuf = uiobj.inbuf[:-1]
				uiobj.inputwin.write(uiobj.inbuf[-uiobj.width-3:])
			elif len(uiobj.inbuf) >= uiobj.width-3:
				uiobj.inbuf = uiobj.inbuf[:-1]
				uiobj.bufposition -= 1
				if len(uiobj.inbuf)+1 < uiobj.width-3:
					uiobj.screen.move(uiobj.height-2,len(uiobj.inbuf)+1)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.width-1)
				if len(uiobj.inbuf) - uiobj.width -2 > 0:
					extra= len(uiobj.inbuf) - uiobj.width-3
					curbuf =  uiobj.inbuf[:-extra]
				else:
					curbuf = uiobj.inbuf
				uiobj.inputwin.write(curbuf[-uiobj.width-3:])
				if len(curbuf) < uiobj.width-3:
					uiobj.screen.move(uiobj.height-2,len(curbuf)+1)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.width-1)
				uiobj.inputwin.window.clrtoeol()
			elif len(uiobj.inbuf) > 0:
				uiobj.inbuf = uiobj.inbuf[:-1]
				uiobj.bufposition -= 1
				uiobj.inputwin.write(uiobj.inbuf[-uiobj.width-3:])
				if  len(uiobj.inbuf) - uiobj.width-3 > 0:
					uiobj.screen.move(uiobj.height-2,obj.width-1)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.bufposition+1)
				uiobj.inputwin.window.clrtoeol()
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
			if len(uiobj.inbuf) >= uiobj.width-3:
				tempbuf = uiobj.inbuf[-uiobj.width+2:]
				uiobj.inputwin.write(tempbuf)
				uiobj.screen.move(uiobj.height-2,uiobj.width-1)
			elif len(uiobj.inbuf) < uiobj.width-3:
				uiobj.inputwin.write(uiobj.inbuf)
				uiobj.screen.move(uiobj.height-2,len(uiobj.inbuf)+1)
				uiobj.inputwin.window.clrtoeol()
#		Screenrefresh()

def killCurses(uiobj):
	curses.nocbreak()
	uiobj.screen.keypad(0)
	curses.echo()
	curses.endwin()

interface = InterfaceObject()
initWindows(interface)
#ScreenRefresh(interface)
InputLoop(interface)
killCurses(interface)
