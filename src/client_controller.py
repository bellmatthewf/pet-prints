#!/usr/bin/env python3

#Author: Matthew Bell - 2018

"""Controller for Pet Prints. Uses custom socket to communicate with servers and 
the client view module to display GUI for end user"""

import client_view, custom_socket, dropbox
import tkinter as tk
import logging
import threading
from tkinter import messagebox
from multiprocessing.pool import ThreadPool
from itertools import cycle
from PIL import Image, ImageTk
from datetime import datetime
from subprocess import Popen
from functools import partial
from os import remove

src_host = "192.168.3.2"
src_port = 2222
dest_port = 2222
broadcast_host = "192.168.3.255"
number_of_servers = 40

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

file_handler = logging.FileHandler("controller.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.info("STARTED CONTOLLER")

class Controller:

	"""self.server_dict = {*pi_id {"ip_address" : "192.168.3.39","photo_path", 
	"/home/pi/Pictures/{pi_id}.jpg", "tk_photo_frame" : tk_frame_object, 
	"tk_photo_label" : tk_label_object, "raw_photo" : tk_photo_object}}"""
	def __init__(self, src_host, src_port, dest_port, broadcast_host, number_of_servers):
		self.src_host = src_host
		self.src_port = src_port
		self.dest_port = dest_port
		self.broadcast_host = broadcast_host
		self.number_of_servers = number_of_servers
		self.server_dict = {}
		self.root, self.master = self.create_main_window()
		self.main_view = client_view.Main_View(self.master, self)
		self.review_view = client_view.Review_View(self.master, self)
		self.sockets = custom_socket.Sockets(self.src_host, self.src_port, 
		dest_port = self.dest_port, broadcast_host = self.broadcast_host)

		threading.Thread(target=self.start_animation, args=("Checking cameras",)).start()
		pool1 = ThreadPool(processes = 1)
		self.connection_list = pool1.apply_async(self.check_connections, (15,))
		pool1.close()

		threading.Thread(target=self.view_connections).start()
		threading.Thread(target=self.stop_animation, args=(self.main_view.frame_main, pool1)).start()

	def create_main_window(self):
		root = tk.Tk()
		root.title("Pet Prints")
		root.geometry("480x320")
		root.resizable(0,0)
		root.attributes("-fullscreen", True)

		container = tk.Frame(root)
		container.pack(fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)
		return root, container

	def start_animation(self, label_text, animation = ["", ".", "..", "..."]):
		self.label_text = label_text
		self.iter_animation = cycle(animation)
		self.loading_frame = tk.Frame(self.master)
		self.loading_frame.grid(row=0, column=0, sticky="NSEW")
		self.loading_label = tk.Label(self.loading_frame, text="{}{}".format(self.label_text, animation[0]), 
		font=self.main_view.font_title)
		self.loading_label.place(anchor="center", relx=.5, rely=.5)
		self.loading_frame.tkraise()
		self.loop = True

		def iterate(self):
			if self.loop == False:
				return
			self.loading_label.config(text="{}{}".format(self.label_text, next(self.iter_animation)))
			self.loop = self.root.after(1000, iterate, self)
		iterate(self)

	def config_animation(self, new_label, thread=None):
		if thread:
			thread.join()
		self.label_text = new_label

	def stop_animation(self, end_page=None, thread=None):
		if thread:
			thread.join()
		self.loop = False
		self.loading_label.destroy()
		self.loading_frame.destroy()
		if end_page:
			end_page.tkraise()

	def check_connections(self, timeout):
		self.sockets.create_socket(tcp = True, tcp_timeout = timeout, tcp_listen = True)
		connection_list = []
		pool2 = ThreadPool(processes = self.number_of_servers)
		while len(connection_list) < self.number_of_servers:
			try:
				conn, ip, pi_id = self.sockets.accept_tcp_conn()
				connection_list.append(pi_id)
				pool2.apply_async(self.sockets.recv_tcp_data, (conn, 1024, True))
			except Exception as e:
				logger.info("Timed out waiting on initial connections. Connected to:", connection_list)
				break
		pool2.close()
		pool2.join()
		self.sockets.close_socket(tcp = True)
		return connection_list

	def view_connections(self):
		connections = sorted(self.connection_list.get())
		messagebox.showinfo("Live Connections", "Connected to camera(s): {}".format(connections))

	#Take and retrieve photos while animating
	def main_take_photos(self):
		self.start_animation("Taking photos")
		self.request_take_photos()
		logger.info("Photos taken")
		self.config_animation("Retrieving photos")
		self.request_photo_files_then_load()
		logger.info("Photos loaded up")
		self.stop_animation()

	#Tell servers to take photos, then wait for a response to know photo has been taken
	def request_take_photos(self):
		self.sockets.create_socket(udp = True, udp_timeout = 5)
		self.sockets.send_udp_broadcast(b"take_photo")
		while True:
			try:
				self.sockets.recv_udp_data(1024)
			except Exception as e:
				logger.info("All photo taken responses received. Socket timed out and closed.")
				break
		self.sockets.close_socket(udp = True)

	def request_photo_files_then_load(self):
		#Request then receive photo transfer
		self.sockets.create_socket(tcp = True, udp = True, tcp_timeout = 3, tcp_listen = True)
		self.sockets.send_udp_broadcast(b"remit_photo")
		pool3 = ThreadPool(processes = self.number_of_servers)
		while True:
			try:
				conn, ip, pi_id = self.sockets.accept_tcp_conn()
				logger.info("Accepted connection from {} to send photos".format(pi_id))
				write_location = "/home/pi/Pictures/img{}.jpg".format(pi_id)
				self.server_dict[pi_id] = {"photo_path" : write_location, "ip_address" : ip}
				pool3.apply_async(self.sockets.recv_tcp_data, (conn, 8192, True, write_location))
			except Exception as e:
				logger.info("All incoming connections trying to send photos have been accepted")
				break
		pool3.close()
		pool3.join()
		logger.info("All photos received and pool closed")
		self.sockets.close_socket(tcp = True, udp = True)

		#Load photo files into view
		for pi_id in self.server_dict:
			frame = tk.Frame(self.review_view.frame_review)
			frame.place(anchor="center", relx=.5, rely=.5)
			frame.rowconfigure(0, weight=1)
			frame.columnconfigure(0, weight=1)
			photo = Image.open(self.server_dict[pi_id]["photo_path"]).resize((275,206), Image.ANTIALIAS)
			tk_photo = ImageTk.PhotoImage(photo)
			self.server_dict[pi_id]["raw_photo"] = tk_photo
			photo.close()
			label = tk.Label(frame, image=tk_photo, borderwidth=3, relief="solid")
			label.grid(sticky="NSEW")
			self.server_dict[pi_id]["tk_photo_frame"] = frame
			self.server_dict[pi_id]["tk_photo_label"] = label
		photo_list = sorted(self.server_dict)
		if len(photo_list) > 0:
			self.current_photo_idx = 0
			current_photo_id = photo_list[self.current_photo_idx]
			new_frame = self.server_dict[current_photo_id]["tk_photo_frame"]
			self.create_counter_labels(len(photo_list), current_photo_id)
			self.review_view.frame_review.tkraise()
			new_frame.tkraise()
		else:
			self.main_view.frame_main.tkraise()
			messagebox.showinfo("Photo Error", "No photos could be retrieved, please try again.")

	def scroll_photos(self, direction):
		assert direction == "left" or direction == "right"
		photo_list = sorted(self.server_dict)
		if direction == "left":
			self.current_photo_idx -= 1
			if self.current_photo_idx < 0:
				self.current_photo_idx = len(photo_list)-1
		if direction == "right":
			self.current_photo_idx += 1
			if self.current_photo_idx > len(photo_list)-1:
				self.current_photo_idx = 0
		current_photo_id = photo_list[self.current_photo_idx]
		current_photo = self.current_photo_idx + 1
		self.config_counter_labels(current_photo, len(photo_list), current_photo_id)
		new_frame = self.server_dict[current_photo_id]["tk_photo_frame"]
		new_frame.tkraise()

	def messagebox_info(self, title, text):
		messagebox.showinfo(title, text)

	def confirm_retake(self):
		answer = messagebox.askyesno(title="Retake set", message="Retake photos?")
		if answer:
			for pi_id in self.server_dict:
				remove(self.server_dict[pi_id]["photo_path"])
				self.server_dict[pi_id]["tk_photo_label"].destroy()
				self.server_dict[pi_id]["tk_photo_frame"].destroy()
			self.delete_counter_labels()
			self.server_dict.clear()
			self.main_view.frame_main.tkraise()

	def main_upload(self):
		answer = self.confirm_upload()
		if answer:
			self.start_animation("Uploading photos")
			self.upload()
			self.stop_animation(end_page = self.main_view.frame_main)
			messagebox.showinfo("Upload complete", "Photos successfully uploaded")


	def confirm_upload(self):
		answer = messagebox.askyesno(title="Confirm Upload", 
		message="Confirm photo upload?")
		return answer

	def upload(self):
		dt = datetime.now()
		folder_name = "{}-{}-{} {}-{}-{}"\
		.format((dt.day),(dt.month),(dt.year),(dt.hour),(dt.minute),(dt.second))
		dbx = dropbox.Dropbox\
		("TudMqsLxnVAAAAAAAAABinFSk__cpPA0btSQKxBeUWzZ3qPddbkTOXeZQlFDHBGF")
		dbx.files_create_folder("/Pet_Pics/{}".format(folder_name))

		def inner_upload(self, pi_id):
			try:
				photo = open(self.server_dict[pi_id]["photo_path"], "rb")
				dbx.files_upload(photo.read(),"/Pet_Pics/{}/img{}.jpg".format(folder_name,pi_id))
				photo.close()
			except Exception:
				traceback.print_exc()

		pool4 = ThreadPool(processes = len(self.server_dict))
		for pi_id in self.server_dict:
			pool4.apply_async(inner_upload, (self, pi_id))
		pool4.close()
		pool4.join()

		for pi_id in self.server_dict:
			remove(self.server_dict[pi_id]["photo_path"])
			self.server_dict[pi_id]["tk_photo_label"].destroy()
			self.server_dict[pi_id]["tk_photo_frame"].destroy()
		self.delete_counter_labels()
		self.server_dict.clear()

	def secret_quit(self):
		self.root.destroy()

	def request_shutdown(self):
		self.sockets.create_socket(udp = True)
		self.sockets.send_udp_broadcast(b"shutdown")
		self.sockets.close_socket(udp = True)
		Popen(["sudo", "poweroff"])

	"""Labels which must be applied by the controller as 
	they change based on controller variables"""
	def create_counter_labels(self, number_of_photos, starting_computer_id):
		self.label_counter = tk.Label(self.review_view.frame_review, 
		text="1/{}".format(number_of_photos), 
		font=self.review_view.font_buttonH2)
		self.label_counter.place(anchor="center", relx=.5, rely=.13)
		self.label_pi_num = tk.Label(self.review_view.frame_review, 
		text="#{}".format(starting_computer_id), font=self.review_view.font_unimportant) 
		self.label_pi_num.place(anchor="center", relx=.75, rely=.13)

	def config_counter_labels(self, current_photo, number_of_photos, current_camera_id):
		self.label_counter.config(text="{}/{}".format(current_photo, number_of_photos))
		self.label_pi_num.config(text="#{}".format(current_camera_id))	

	def delete_counter_labels(self):
		self.label_counter.destroy()
		self.label_pi_num.destroy()

def main(src_host, src_port, dest_port, broadcast_host, number_of_servers):
	main_controller = Controller(src_host, src_port, dest_port, broadcast_host,
	number_of_servers)
	main_controller.root.mainloop()	

if __name__ == "__main__":
	main(src_host, src_port, dest_port, broadcast_host, number_of_servers)
