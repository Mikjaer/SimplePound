#!/usr/bin/python3

# Copyright (c) 2021 Mikkel Mikjaer Christensen
# Released publicly under GNU GPL v2.0

import sys;
import os;
import keyboard;
import time;
import termios
import tty
import select
 
class Console:
	nonBlockingStarted = False
	old_settings = ""

	# https://en.wikipedia.org/wiki/Box-drawing_character

	DOUBLE_CORNER_TOP_LEFT = "\u2554";
	DOUBLE_CORNER_TOP_RIGHT = "\u2557";
	
	DOUBLE_CORNER_BOTTOM_LEFT = "\u255A";
	DOUBLE_CORNER_BOTTOM_RIGHT = "\u255D";
	
	DOUBLE_HORIZONTAL = "\u2550";
	DOUBLE_VERTICAL = "\u2551";

	DOUBLE_TEE_RIGHT = "\u2560";
	DOUBLE_TEE_LEFT = "\u2563";
	
	@staticmethod
	def clearscreen():
		print(chr(27) + "\033[2J")
		Console.gotoxy(0,0)

	@staticmethod
	def isatty():
		return sys.stdout.isatty()
	
	@staticmethod
	def savepos():
		print(chr(27) + "\033[s")

	@staticmethod
	def restorepos():
		print(chr(27) + "\033[U")


	@staticmethod
	def gotoxy(x,y):
		sys.stdout.write( chr(27) + "["+str(y)+";"+str(x)+"H");

	@staticmethod
	def terminalSize():
		height, width = os.popen('stty size', 'r').read().split()
		return int(width), int(height) 
	
	@staticmethod
	def write(str):
		sys.stdout.write( str );
		sys.stdout.flush()

	@staticmethod
	def writeAt(x,y,string,length=0,align='left'):
		if align == "left":
			Console.gotoxy(x,y)
		
		elif align == "right" and length != 0:
			Console.gotoxy(x + length - len(string), y)	

		elif align == "center" and length != 0:
			Console.gotoxy(x + round((length / 2) - (len(string) /2)), y)

		Console.write(string)
	
	def nonBlockStart(self):
		if self.nonBlockingStarted:
			print ("nonBlock already started");
		
		Console.write("\x1b[?25l") # hide cursor
		self.nonBlockingStarted = True;
		self.old_settings = termios.tcgetattr(sys.stdin)
		tty.setcbreak(sys.stdin.fileno())


	def nonBlockStop(self):
		termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
		Console.write("\x1b[?25h") # show cursor again

	def keyPressed(self):
		return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])	

	def readKey(self):
		return sys.stdin.read(1);

