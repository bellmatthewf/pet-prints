#!/usr/bin/env python3

# Author: Matthew Bell - 2018

"""GUI for the Pet Prints client"""

import threading
import tkinter as tk
from tkinter import font as tkfont


class Main_View:
    def __init__(self, master, controller):
        self.frame_main = tk.Frame(master)
        self.frame_main.grid(row=0, column=0, sticky="NSEW")

        self.font_title = tkfont.Font(family="Helvetica", size=24, weight="bold")
        self.font_buttonH1 = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.font_buttonH2 = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.font_unimportant = tkfont.Font(family="Helvetica", size=12)

        self.label_title = tk.Label(
            self.frame_main, text="Welcome to Pet Prints", font=self.font_title
        )
        self.label_title.place(anchor="center", relx=0.5, rely=0.15)

        self.frame_take_photos = tk.Frame(self.frame_main)
        self.frame_take_photos.place(
            relx=0.1, rely=0.4, anchor="w", width=384, height=75
        )
        self.frame_take_photos.rowconfigure(0, weight=1)
        self.frame_take_photos.columnconfigure(0, weight=1)
        self.button_take_photos = tk.Button(
            self.frame_take_photos,
            text="Take Photos",
            bg="powder blue",
            bd=8,
            font=self.font_buttonH1,
            command=lambda: threading.Thread(
                target=controller.main_take_photos
            ).start(),
        )
        self.button_take_photos.grid(sticky="NSEW")

        self.frame_help = tk.Frame(self.frame_main)
        self.frame_help.place(relx=0.1, rely=0.7, anchor="w", width=175, height=75)
        self.frame_help.rowconfigure(0, weight=1)
        self.frame_help.columnconfigure(0, weight=1)
        self.button_help = tk.Button(
            self.frame_help,
            text="Help",
            bg="powder blue",
            bd=8,
            font=self.font_buttonH1,
            command=lambda: controller.messagebox_info(
                "Help", "Call (416) 801-8237 for assistance!"
            ),
        )
        self.button_help.grid(sticky="NSEW")

        self.frame_shutdown = tk.Frame(self.frame_main)
        self.frame_shutdown.place(relx=0.9, rely=0.7, anchor="e", width=175, height=75)
        self.frame_shutdown.rowconfigure(0, weight=1)
        self.frame_shutdown.columnconfigure(0, weight=1)
        self.button_shutdown = tk.Button(
            self.frame_shutdown,
            text="Shutdown...",
            bg="powder blue",
            bd=8,
            font=self.font_buttonH1,
            command=lambda: controller.request_shutdown(),
        )
        self.button_shutdown.grid(sticky="NSEW")

        # Secret quit click main frame the press "Q" to quit program
        self.frame_main.bind("<Button-1>", lambda x: self.frame_main.focus_set())
        self.frame_main.bind("q", lambda x: controller.secret_quit())


class Review_View:
    def __init__(self, master, controller):
        self.frame_review = tk.Frame(master)
        self.frame_review.grid(row=0, column=0, sticky="NSEW")

        self.font_title = tkfont.Font(family="Helvetica", size=24, weight="bold")
        self.font_buttonH1 = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.font_buttonH2 = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.font_unimportant = tkfont.Font(family="Helvetica", size=12)

        self.label_Header = tk.Label(
            self.frame_review, text="Review Images", font=self.font_title
        )
        self.label_Header.place(anchor="center", relx=0.5, rely=0.06)

        self.frame_left = tk.Frame(self.frame_review)
        self.frame_left.place(relx=0.1, rely=0.5, anchor="center", width=40, height=100)
        self.frame_left.rowconfigure(0, weight=1)
        self.frame_left.columnconfigure(0, weight=1)
        self.button_left = tk.Button(
            self.frame_left,
            text="L",
            bd=8,
            bg="powder blue",
            font=self.font_buttonH2,
            command=lambda: controller.scroll_photos("left"),
        )
        self.button_left.grid(sticky="NSEW")

        self.frame_right = tk.Frame(self.frame_review)
        self.frame_right.place(
            relx=0.9, rely=0.5, anchor="center", width=40, height=100
        )
        self.frame_right.rowconfigure(0, weight=1)
        self.frame_right.columnconfigure(0, weight=1)
        self.button_right = tk.Button(
            self.frame_right,
            text="R",
            bd=8,
            bg="powder blue",
            font=self.font_buttonH2,
            command=lambda: controller.scroll_photos("right"),
        )
        self.button_right.grid(sticky="NSEW")

        self.frame_upload = tk.Frame(self.frame_review)
        self.frame_upload.place(
            anchor="center", relx=0.31, rely=0.91, width=170, height=45
        )
        self.frame_upload.rowconfigure(0, weight=1)
        self.frame_upload.columnconfigure(0, weight=1)
        self.button_upload = tk.Button(
            self.frame_upload,
            text="Upload Photos",
            bd=8,
            bg="powder blue",
            font=self.font_buttonH2,
            command=lambda: threading.Thread(target=controller.main_upload).start(),
        )
        self.button_upload.grid(sticky="NSEW")

        self.frame_retake = tk.Frame(self.frame_review)
        self.frame_retake.place(
            anchor="center", relx=0.69, rely=0.91, width=170, height=45
        )
        self.frame_retake.rowconfigure(0, weight=1)
        self.frame_retake.columnconfigure(0, weight=1)
        self.button_retake_photos = tk.Button(
            self.frame_retake,
            text="Retake Photos",
            bd=8,
            bg="powder blue",
            font=self.font_buttonH2,
            command=lambda: controller.confirm_retake(),
        )
        self.button_retake_photos.grid(sticky="NSEW")
