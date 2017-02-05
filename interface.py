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
		self.commandpointer = -2

class CursesWindow(object):
	def __init__(self,uiobj,height,width,loc_y,loc_x,box=True,keeplog=False,loglength=0,showcursor=False):
		self.uiobj = uiobj
		self.window = curses.newwin(height,width,loc_y,loc_x)
		self.height = height
		self.width = width
		self.loc_y = loc_y
		self.loc_x = loc_x
		self.box = box
		self.scrollback = []
		self.scrollbacknosplit = []
		if loglength == 0:
			self.loglength = height
		else:
			self.loglength = loglength
		if showcursor == False:
			self.window.leaveok(1)
		else:
			self.window.leaveok(0)
		if box == True:
			self.loglength -= 2
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

	def resize(self,height,width):
		self.window.resize(height,width)
		self.height = height
		self.width = width
		if self.box == True:
			bufferlen = height-2
			startx = 1
		else:
			bufferlen = height
			startx = 0
		if self.keeplog == False:
			self.scrollbacknosplit = self.scrollbacknosplit[-bufferlen:]
		self.scrollback = []
		if len(self.scrollbacknosplit) > 0:
			for line in self.scrollbacknosplit:
				lines = wordwrap(line,width-startx-startx)
				for curline in lines:
					self.scrollback.append(curline)

		if self.keeplog == False:
			self.scrollback = self.scrollback[-bufferlen:]

		if len(self.scrollback) < bufferlen:
			curline = startx
			for line in self.scrollback:
				self.window.addstr(curline,startx,line)
				self.window.clrtoeol()
				curline += 1
			self.refresh()
		else:
			curline = startx
			for line in self.scrollback[-bufferlen:]:
				self.window.addstr(curline,startx,line)
				self.window.clrtoeol()
				curline += 1
			self.refresh()

	def move(self,y,x):
		self.loc_y = y
		self.loc_x = x

	def write(self,text):
		self.scrollbacknosplit.append(text)
		if self.box == True:
			lines = wordwrap(text,self.width-2)
		else:
			lines = wordwrap(text,self.width)
		for line in lines:
			self.scrollback.append(line)

		if self.box == True:
			bufferlen = self.height-2
			startx = 1
		else:
			bufferlen = self.height
			startx = 0

		if self.keeplog == False:
			self.scrollback = self.scrollback[-bufferlen:]
			self.scrollbacknosplit = self.scrollbacknosplit[-bufferlen:]
		if len(self.scrollback) > self.loglength and self.keeplog == True:
			self.scrollback = self.scrollback[-self.loglength:]
		if len(self.scrollbacknosplit) > self.loglength and self.keeplog==True:
			self.scrollbacknosplit = self.scrollbacknosplit[-self.loglength:]

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
				self.window.clrtoeol()
				curline += 1
			self.refresh()
			return

def initWindows(uiobj):
	curses.noecho()
	curses.cbreak()
	uiobj.screen.keypad(True)
	curses.curs_set(1)

	height,width= uiobj.screen.getmaxyx()
	uiobj.mainwindow = CursesWindow(uiobj,height-3,width-25,0,0,keeplog=True,loglength=1000)
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

def InputLoop(uiobj):
	uiobj.inbuf = ""
	while True:
		ch = uiobj.screen.getch()
		if ch == curses.KEY_DOWN:
			if uiobj.commandpointer == -2 and len(uiobj.commandhist)> 0:
				uiobj.commandpointer = len(uiobj.commandhist)
				uiobj.inbuf = uiobj.commandhist[uiobj.commandpointer]
				uiobj.bufposition = len(uiobj.inbuf)
				if uiobj.bufposition <= uiobj.width -3:
					uiobj.screen.move(uiobj.height-2,uiobj.bufposition)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.width-1)
				uiobj.commandpointer -= 1
			elif uiobj.commandpointer > -1:
				uiobj.inbuf = uiobj.commandhist[uiobj.commandpointer]
				uiobj.bufposition = len(uiobj.inbuf)
				if uiobj.bufposition <= uiobj.width -3:
					uiobj.screen.move(uiobj.height-2,uiobj.bufposition)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.width-1)
				uiobj.commandpointer -= 1
			else:
				continue

		elif ch == curses.KEY_UP:
			if uiobj.commandpointer == -2:
				continue
			elif uiobj.commandpointer > len(uiobj.commandhist)-1:
				uiobj.inbuf = ""
				uiobj.bufposition = 0
				uiobj.screen.move(uiobj.height-2,1)
				uiobj.commandpointer = -2
			else:
				uiobj.inbuf = uiobj.commandhist[uiobj.commandpointer]
				uiobj.bufposition = len(uiobj.inbuf)
				if uiobj.bufposition <= uiobj.width -3:
					uiobj.screen.move(uiobj.height-2,uiobj.bufposition+1)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.width-1)
				uiobj.commandpointer += 1
			if len(uiobj.inbuf) >= uiobj.width-3:
				tempbuf = uiobj.inbuf[-uiobj.width+2:]
				uiobj.inputwin.write(tempbuf)
				uiobj.screen.move(uiobj.height-2,uiobj.width-1)
			else:
				uiobj.inputwin.write(uiobj.inbuf)
				uiobj.inputwin.window.clrtoeol()
				uiobj.screen.move(uiobj.height-2,len(uiobj.inbuf)+1)

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
			if uiobj.inbuf.lower() == "quit":
				killCurses(uiobj)
				exit(0)
			uiobj.commandhist.append(uiobj.inbuf)
			uiobj.mainwindow.write(uiobj.inbuf)
			uiobj.inputwin.write(" ")
			uiobj.inputwin.window.clrtoeol()
			uiobj.screen.move(uiobj.height-2,1)
			uiobj.inbuf = ""
			uiobj.bufposition = 0
			uiobj.commandpointer = -1
			uiobj.mainwindow.refresh()
			uiobj.inputwin.refresh()
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
			else:
				uiobj.inputwin.write(uiobj.inbuf)
				uiobj.inputwin.window.clrtoeol()
				uiobj.screen.move(uiobj.height-2,len(uiobj.inbuf)+1)

def killCurses(uiobj):
	curses.nocbreak()
	uiobj.screen.keypad(0)
	curses.echo()
	curses.endwin()

interface = InterfaceObject()
initWindows(interface)
InputLoop(interface)
killCurses(interface)
