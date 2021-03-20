#!/usr/bin/python3

# Copyright (c) 2021 Mikkel Mikjaer Christensen
# Released publicly under GNU GPL v2.0

from console import Console
import time
import threading
import subprocess 
import re
import random,datetime,math
import argparse
import pprint

deltaMax = -1
deltaMin = -1 

if not Console.isatty():
	print ("This application requires a tty");

my_parser = argparse.ArgumentParser(description='SimplePound - a universal tool for running parallel stresstests',
				formatter_class=argparse.ArgumentDefaultsHelpFormatter)

my_parser.add_argument('payload', help='Script or command to execute')
my_parser.add_argument('--threads', type=int, default=8, help='Number of threads to spawn automatically')

args = my_parser.parse_args()

if args.payload != "dummy": # "Undocumented" feature, used for debugging
	try:
		pass
		result = subprocess.run(args.payload.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	except subprocess.CalledProcessError as e:
		print (e.output)
		exit()

console = Console();
console.nonBlockStart();
curWidth = 0
curHeight = 0
def drawUserInterfaceThread():
	global running
	Console.clearscreen()
	while running:
		drawUserInterface()
		time.sleep(0.25)


def drawUserInterface():
	width, height = Console.terminalSize();
	
	global curWidth
	global curHeight

	if curWidth != width or curHeight != height: # Only draw gui when window size changes
		curWidth = width
		curHeight = height
		Console.gotoxy(0,0)
		Console.write(Console.DOUBLE_CORNER_TOP_LEFT + (Console.DOUBLE_HORIZONTAL * (width - 2)) + Console.DOUBLE_CORNER_TOP_RIGHT + "\n");

		for x in range(height -2):
			Console.write(Console.DOUBLE_VERTICAL + (" " * (width - 2)) + Console.DOUBLE_VERTICAL + "\n");
		# Bottom	
		Console.write(Console.DOUBLE_CORNER_BOTTOM_LEFT + (Console.DOUBLE_HORIZONTAL * (width - 2)) + Console.DOUBLE_CORNER_BOTTOM_RIGHT);
	
		# Top divider
		Console.writeAt(0,3,Console.DOUBLE_TEE_RIGHT + (Console.DOUBLE_HORIZONTAL * (width - 2)) + Console.DOUBLE_TEE_LEFT);

		# Bottom divider
		Console.writeAt(0,height - 2,Console.DOUBLE_TEE_RIGHT + (Console.DOUBLE_HORIZONTAL * (width - 2)) + Console.DOUBLE_TEE_LEFT);

		# Title
		Console.writeAt(2,2,"SimplePound v1.0", length = width - 2, align = "center")
	
		# Menu 
		Console.writeAt(0, height - 3, "+ = Increase workers, - = Decrease workers, P = Pause, R = Resume, Z = Zero, Q = Quits", length = width, align = "right")
	
	# Clock
	Console.writeAt(0, height - 1,time.strftime("%Y-%m-%d %H:%M:%S"), length = width, align = "right")

	# Uptime
	uptime = subprocess.check_output(["uptime"]).decode()
	uptime = re.search('load average: .*', subprocess.check_output(["uptime"]).decode() ).group(0)
	Console.writeAt(2, height - 1, str(uptime))

	# Threads
	
	row = 1
	col = 0
	
	itemWidth = 32 
	maxRows = height - 8
	maxCols = math.floor(width / itemWidth)

	global deltaMin
	global deltaMax

	totalDelta = 0
	totalDeltaThreads = 0
	visibleThreads = 0	
	for thread in threads:
		if col == maxCols -1 and row == maxRows -1:
			Console.writeAt(2 + ( col * itemWidth ), 3+row, "... and a "+str(len(threads)-visibleThreads)+" more")
		else:
			if thread.returncode == 0:
				Console.writeAt(2 + ( col * itemWidth ), 3+row, ("%-11s" % thread.threadName)+": "+thread.lastResult)
			else:
				Console.writeAt(2 + ( col * itemWidth ), 3+row, ("%-11s" % thread.threadName)+(" " * itemWidth))
				Console.writeAt(2 + ( col * itemWidth ), 3+row, ("%-11s" % thread.threadName)+": ErrorCode "+str(thread.returncode))

			visibleThreads = visibleThreads + 1
			row = row + 1;
			if row == maxRows:
				row = 1;
				col = col + 1

		if thread.lastDelta != -1:
			totalDeltaThreads = totalDeltaThreads +1
			totalDelta = totalDelta + thread.lastDelta

			if deltaMax < thread.lastDelta:
				deltaMax = thread.lastDelta

			if deltaMin > thread.lastDelta or deltaMin < 0:
				deltaMin = thread.lastDelta


	if totalDeltaThreads == 0:
		deltaAvg = 0;
	else:
		deltaAvg = totalDelta / totalDeltaThreads	
		Console.writeAt(2, height - 3, "Total threads:" + str(len(threads))+"   Delta average:" + ("%.2f" % deltaAvg)+"   Delta min:"+("%.2f" % deltaMin)+"   Delta max:"+("%.2f" % deltaMax))


class Worker(threading.Thread):
	def __init__(self, threadName):
		super(Worker, self).__init__()
		self.threadName = threadName;
		self.paused = False
		self.running = True
		self.lastResult = "none";
		self.lastDelta = -1;
		self.returncode = -1
	def run(self):
		while self.running:
			if not self.paused:
				before = datetime.datetime.now()

				# PAYLOAD

				if args.payload == "dummy": # "Undocumented" feature, used for debugging
					r =  float(random.randint(10,30)) / 10
					time.sleep(r);
				else:
				
					self.process = subprocess.Popen( args.payload.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					self.process.wait()
					self.returncode = self.process.returncode

				# /PAYLOAD

				after = datetime.datetime.now()

				delta = after-before
				deltafloat = delta.seconds + (delta.microseconds / 1000000)
				self.lastResult = "Took " + ("%.2f" % deltafloat) + " sec"
				self.lastDelta = deltafloat 
			else:
				self.lastResult = "Paused";
				time.sleep(1)

	def kill(self):
		try:
			self.process.kill()
		except:
			pass


	def pause(self):
		self.paused = True
		self.kill()

	def resume(self):
		self.paused = False 

	def stop(self):
		self.running = False
		self.kill()

threads = []
for i in range(1,args.threads + 1):
	threads.append(Worker("Thread "+str(len(threads)+1)));
	threads[-1].start()

running = True;

uiThread = threading.Thread(target=drawUserInterfaceThread)
uiThread.start();


while running == True:
	if console.keyPressed():
		key = console.readKey().upper();
		if key == "+":
			threads.append(Worker("Thread "+str(len(threads)+1)));
			threads[-1].start()
			drawUserInterface()


		if key == "-":
			threads[-1].stop()
			threads.pop()
			drawUserInterface()

		if key == "P":
			for thread in threads:
				thread.pause();

		if key == "R":
			for thread in threads:
				thread.resume();

		if key == "Z":
			deltaMin = -1
			deltaMax = -1
								
		if key == "Q":
			running = False
			uiThread.join();
			console.nonBlockStop();
			console.clearscreen();
			print ("Waiting for threads to exit....")
			
			for thread in threads:
				thread.stop();


			print ("Thankyou! Come again!");


