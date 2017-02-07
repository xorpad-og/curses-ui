import curses
import shutil
import platform
import os
import sys

def refreshscreen(uiobj):
	uiobj.screen.refresh()
	uiobj.mainwindow.refresh()
	uiobj.sidebar.refresh()
	uiobj.inputwin.refresh()

def ResizeScreen(x,y):
		clientos = platform.system()
		if clientos == 'Windows':
			os.system("mode {rows},{columns}".format(rows=x,columns=y))
		elif clientos == 'Linux' or clientos == 'Darwin' or clientos.startswith('CYGWIN'):
			sys.stdout.write("\x1b[8;{columns};{rows}t".format(rows=x,columns=y))

class InterfaceObject(object):
	def __init__(self):
		self.bufposition = 0
		self.commandhist = []
		self.screen = curses.initscr()
		self.mainwindow = None
		self.sidebar = None
		self.inputwin = None
		self.width,self.height=shutil.get_terminal_size()
		self.inbuf = ""
		self.commandpointer = -2
		self.lastpointer = -2

class CursesWindow(object):
	def __init__(self,uiobj,height,width,loc_y,loc_x,minwidth,box=True,keeplog=False,loglength=0,showcursor=False):
		self.uiobj = uiobj
		self.window = curses.newwin(height,width,loc_y,loc_x)
		self.height = height
		self.width = width
		self.loc_y = loc_y
		self.loc_x = loc_x
		self.minwidth = minwidth
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
		self.keeplog = keeplog
		self.window.keypad(0)
		self.window.idlok(False)
		self.window.scrollok(False)
		self.window.immedok(True)
		self.box = box
		self.refresh()

	def refresh(self):
		if self.box == True:
			self.window.box()
		self.uiobj.screen.refresh()
		self.window.refresh()

	def drawinput(self,text,length):
		if self.box == True:
			startx = 1
		textlen = self.width-startx-startx
		if len(text) > self.width-startx-startx:
			self.window.addstr(1,startx,text[-textlen:])
		else:
			self.window.addstr(1,startx,text)
		self.window.clrtoeol()
		self.refresh()

	def resize(self,height,width):
		self.window.resize(height,width)
		self.height = height
		self.width = width
		if self.box == True:
			bufferlen = self.height - 2
			startx = 1
		else:
			bufferlen = self.height
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
		self.window.mvwin(y,x)

	def redraw_scrollback(self):
		if self.box == True:
			bufferlen = self.height-2
			startx = 1
		else:
			bufferlen = self.height
			startx = 0

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

	def write(self,text):
		self.scrollbacknosplit.append(text)
		if self.box == True:
			bufferlen = self.height-2
			startx = 1
		else:
			bufferlen = self.height
			startx = 0
		lines = wordwrap(text,self.width-startx-startx)

		for line in lines:
			self.scrollback.append(line)

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
	uiobj.mainwindow = CursesWindow(uiobj,height-3,width-25,0,0,35,keeplog=True,loglength=1000)
	uiobj.sidebar = CursesWindow(uiobj,height-3,width-uiobj.mainwindow.width,0,uiobj.mainwindow.width,25)
	uiobj.inputwin = CursesWindow(uiobj,3,width,uiobj.mainwindow.height,0,3,showcursor=True)

	refreshscreen(uiobj)

def wordwrap(text,length):
	lines = []

	linestring = ""
	words = 0
	x = 0
	while x < len(text):
		if text[x] != ' ':
			nextspace = text[x:].find(' ')
			if nextspace == -1:
				if len(linestring) + len(text[x:]) <= length:
					linestring = linestring+text[x:]
					lines.append(linestring)
				else:
					lines.append(linestring)
					linestring = ""
					linestring = linestring+text[x:]
					lines.append(linestring)
				return(lines)
			linestring = linestring + text[x:x+nextspace]
			if len(linestring) == length:
				lines.append(linestring)
				linestring = ""
			x = x + nextspace
			while text[x] == ' ':
				x += 1
				if len(linestring) == 0:
					pass
				elif len(linestring) == length:
					lines.append(linestring)
					linestring = ""
				elif len(linestring) > 0 and len(linestring) + 1 < length:
					linestring = linestring + " "
				else:
					linestring = linestring + " "
					lines.append(linestring)
					linestring = ""
		else:
			x += 1
			if len(linestring) == 0:
				pass
			elif len(linestring)+1 <= length:
				linestring = linestring + " "
				if len(linestring) == length:
					lines.append(linestring)
					linestring = ""
	return lines

def InputLoop(uiobj):
	uiobj.inbuf = ""
	uiobj.screen.move(uiobj.height - 2, 1)
	while True:
		newx,newy = shutil.get_terminal_size()
		ch = uiobj.screen.getch()
		if ch == curses.KEY_RESIZE or newx != uiobj.width or newy != uiobj.height:
			if newx < uiobj.width:
				if newx-uiobj.sidebar.minwidth >= uiobj.mainwindow.minwidth:
					uiobj.mainwindow.resize(uiobj.mainwindow.height,newx-uiobj.sidebar.minwidth)
					uiobj.sidebar.move(uiobj.sidebar.loc_y,newx-uiobj.sidebar.minwidth)
					uiobj.inputwin.resize(3,newx)
					refreshscreen(uiobj)
					uiobj.width = newx
				else:
					msgx,msgy = shutil.get_terminal_size()
					windowx = uiobj.width
					windowy = uiobj.height
					mainy = uiobj.mainwindow.height
					mainx = uiobj.mainwindow.width
					mainxloc = uiobj.mainwindow.loc_x
					mainyloc = uiobj.mainwindow.loc_y
					inwiny = uiobj.inputwin.height
					inwinx = uiobj.inputwin.width
					inwinyloc = uiobj.inputwin.loc_y
					inwinxloc = uiobj.inputwin.loc_x
					sidey = uiobj.sidebar.height
					sidex = uiobj.sidebar.width
					sideyloc = uiobj.sidebar.loc_y
					sidexloc = uiobj.sidebar.loc_x
					del uiobj.mainwindow.window
					del uiobj.sidebar.window
					del uiobj.inputwin.window
					del uiobj.screen
					uiobj.screen = curses.initscr()
					tempwindow = CursesWindow(uiobj,msgy,msgx,0,0,1)
					tempwindow.write("You have resized the window too small for this client.")
					tempwindow.write("would you like to undo the resize? Selecting no will end the game.")
					tempwindow.write("[y/n]")
					while True:
						ch = uiobj.screen.getch()
						if ch == ord('Y') or ch == ord('y'):
							del uiobj.screen
							curses.endwin()
							ResizeScreen(windowx,windowy)
							uiobj.screen = curses.initscr()
							curses.cbreak()
							uiobj.screen.keypad(True)
							curses.curs_set(1)
							uiobj.width, uiobj.height = shutil.get_terminal_size()
							uiobj.mainwindow = CursesWindow(uiobj,mainy,mainx,mainyloc,mainxloc,35,keeplog=True,loglength=128)
							uiobj.sidebar = CursesWindow(uiobj,sidey,sidex,sideyloc,sidexloc,25)
							uiobj.inputwin = CursesWindow(uiobj,inwiny,inwinx,inwinyloc,inwinxloc,3)
							uiobj.mainwindow.redraw_scrollback()
							uiobj.sidebar.redraw_scrollback()
							refreshscreen(uiobj)
							break
						elif ch == ord('n') or ch == ord('N'):
							killCurses(uiobj)
							clientos = platform.system()
							if clientos == 'Windows':
								os.system("cls")
							elif clientos == 'Linux' or clientos == 'Darwin' or clientos.startswith('CYGWIN'):
								os.system("clear")
							print("Good bye!")
							exit(0)
		elif ch == curses.KEY_DOWN:
			if uiobj.commandpointer == -2:
				uiobj.inputwin.drawinput(" ",uiobj.width-2)
			elif uiobj.commandpointer < len(uiobj.commandhist) and len(uiobj.commandhist) > 0:
				uiobj.commandpointer += 1
				if uiobj.commandpointer <= len(uiobj.commandhist)-1:
					uiobj.inbuf = uiobj.commandhist[uiobj.commandpointer]
					uiobj.bufposition = len(uiobj.inbuf)
				else:
					uiobj.bufposition = 0
					uiobj.inbuf = ""
					uiobj.commandpointer = -2
					uiobj.inputwin.drawinput(" ",uiobj.width-2)
			elif uiobj.commandhistpointer < len(uiobj.commandhist) and uiobj.commandpointer > -1:
				uiobj.commandpointer += 1
				uiobj.inbuf = uiobj.commandhist[uiobj.commandpointer]
				uiobj.bufposition = len(uiobj.inbuf)
			if len(uiobj.inbuf) >= uiobj.width-3:
				tempbuf = uiobj.inbuf[-uiobj.width+2:]
				uiobj.inputwin.drawinput(uiobj.inbuf,uiobj.width-2)
				uiobj.screen.move(uiobj.height-2,uiobj.width-1)
			else:
				uiobj.inputwin.write(uiobj.inbuf)
				uiobj.inputwin.drawinput(uiobj.inbuf,uiobj.width-2)
				uiobj.screen.move(uiobj.height-2,len(uiobj.inbuf)+1)

		elif ch == curses.KEY_UP:
			if uiobj.commandpointer == -2 and len(uiobj.commandhist) > 0:
				uiobj.commandpointer = len(uiobj.commandhist)-1
				uiobj.inbuf = uiobj.commandhist[uiobj.commandpointer]
				uiobj.bufposition = len(uiobj.inbuf)
			elif uiobj.commandpointer < len(uiobj.commandhist) and uiobj.commandpointer > 0:
				uiobj.commandpointer -= 1
				if uiobj.commandpointer < 0:
					uiobj.commandpointer = 0
				uiobj.inbuf = uiobj.commandhist[uiobj.commandpointer]
				uiobj.bufposition = len(uiobj.inbuf)

			if len(uiobj.inbuf) >= uiobj.width-3:
				tempbuf = uiobj.inbuf[-uiobj.width+2:]
				uiobj.inputwin.drawinput(tempbuf,uiobj.width-2)
				uiobj.screen.move(uiobj.height-2,uiobj.width-1)
			else:
				uiobj.inputwin.drawinput(uiobj.inbuf,uiobj.width-2)
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
			uiobj.inputwin.drawinput(" ",uiobj.width-2)
			uiobj.screen.move(uiobj.height-2,1)
			uiobj.inbuf = ""
			uiobj.bufposition = 0
			uiobj.commandpointer = -2
			refreshscreen(uiobj)
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
				uiobj.inputwin.window.refresh()
			elif len(uiobj.inbuf) > 0:
				uiobj.inbuf = uiobj.inbuf[:-1]
				uiobj.bufposition -= 1
				uiobj.inputwin.write(uiobj.inbuf[-uiobj.width-3:])
				if  len(uiobj.inbuf) - uiobj.width-3 > 0:
					uiobj.screen.move(uiobj.height-2,obj.width-1)
				else:
					uiobj.screen.move(uiobj.height-2,uiobj.bufposition+1)
				uiobj.inputwin.window.clrtoeol()
				uiobj.inputwin.window.refresh()
		else:
			if uiobj.bufposition == len(uiobj.inbuf):
				uiobj.inbuf = "%s%s" % (uiobj.inbuf,str(chr(ch)))
				uiobj.bufposition += 1
			elif uiobj.bufposition < len(uiobj.inbuf):
				uiobj.inbuf = uiobj.inbuf[:uiobj.bufposition] + str(chr(ch)) + uiobj.inbuf[uiobj.bufposition:]
				uiobj.bufposition += 1

			if len(uiobj.inbuf) >= uiobj.width-3:
				uiobj.inputwin.drawinput(uiobj.inbuf,uiobj.width-3)
				uiobj.screen.move(uiobj.height-2,uiobj.width-1)
			else:
				uiobj.inputwin.drawinput(uiobj.inbuf,uiobj.width-3)
				uiobj.screen.move(uiobj.height-2,len(uiobj.inbuf)+1)

def killCurses(uiobj):
	curses.nocbreak()
	uiobj.screen.keypad(0)
	curses.echo()
	curses.endwin()

if "idlelib" in sys.modules:
	print("You cannot run this program from IDLE")
	input("Press enter to exit")
	exit(0)
interface = InterfaceObject()
initWindows(interface)
InputLoop(interface)
killCurses(interface)
