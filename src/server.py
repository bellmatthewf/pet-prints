#!/usr/bin/env python3

#Author: Matthew Bell - 2018

"""Server script for the Pet Prints client. 
Takes a command from the client and performs requisite actions"""

import custom_socket, picamera
from subprocess import Popen
from threading import Thread
from os import remove
from time import sleep
import traceback

show_tracebacks = False

src_host = ""
src_port = 2222
dest_host = "192.168.3.2"
dest_port = 2222

class Server:
	def __init__(self, src_host, src_port, dest_host, dest_port):
		self.src_host = src_host
		self.src_port = src_port
		self.dest_host = dest_host
		self.dest_port = dest_port
		self.sockets = custom_socket.Sockets(self.src_host, self.src_port, 
		self.dest_host, self.dest_port)
		Thread(target=self.ping).start()
		self.decode_calls()

	def ping(self):
		self.sockets.create_socket(tcp = True)
		counter = 0
		while counter < 5:
			try:
				self.sockets.send_tcp_data(b"ping", 1024, True)
				break
			except Exception as e:
				print("Failed to ping client")
				if show_tracebacks:
					traceback.print_exc()
				counter += 1
				sleep(5)
		self.sockets.close_socket(tcp = True)

	def decode_calls(self):
		self.sockets.create_socket(udp = True)
		while True:
			print("Server listening")
			data = self.sockets.recv_udp_data(1024)
			print("Received data")
			Thread(target=self.interpret_command, args=(data,)).start()

	def interpret_command(self, data):
		command = data.decode("utf-8")
		if command == "take_photo":
			print("Taking photo")
			self.take_photo()
		elif command == "remit_photo":
			print("Remitting photo to client")
			self.remit_photo()
		elif command == "shutdown":
			print("Shutting down")
			self.shutdown()

	def take_photo(self):
		camera = picamera.PiCamera()
		try:
			with camera:
				camera.resolution = (1280, 720)
				camera.capture("/home/pi/Pictures/img.jpg")
		except Exception as e:
			if show_tracebacks:
				traceback.print_exc()
		else:
			self.sockets.send_udp_data(b"Taken")

	def remit_photo(self):
		file_loc = "/home/pi/Pictures/img.jpg"
		self.sockets.create_socket(tcp = True)
		try:
			f = open(file_loc, "rb")
			data = f.read()
		except Exception as e:
			traceback.print_exc()
			data = None
		if data:
			try:
				self.sockets.send_tcp_data(data, 8192, True)
			except Exception as e:
				if show_tracebacks:
					traceback.print_exc()
		self.sockets.close_socket(tcp = True)
		remove(file_loc)

	def shutdown(self):
		self.sockets.close_socket(udp = True)
		Popen(["sudo", "poweroff"])

def main(src_host, src_port, dest_host, dest_port):
	Server(src_host, src_port, dest_host, dest_port)

if __name__ == "__main__":
	main(src_host, src_port, dest_host, dest_port)
