import tkinter as tk
import main
from tkinter import *
import customtkinter as ctk
import ai_response as aires

width_ = 800
height_ = 600

ctk.set_default_color_theme("blue")
ctk.set_appearance_mode("dark")


class app(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry(f"{width_}x{height_}+{width_*0.1}+{height_*0.1}")
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.frame = ctk.CTkFrame(self, width=400, height=500)
        self.Label = ctk.CTkLabel(
            self.frame, width=400, text="Login", font=("consolas", 30), anchor="center"
        )
        self.id = ctk.CTkEntry(self.frame, width=360, placeholder_text="Username")
        self.passn = ctk.CTkEntry(
            self.frame, width=360, placeholder_text="Password", show="*"
        )
        self.login = ctk.CTkButton(
            self.frame, text="Login", font=("consolas", 20), command=self.get_text
        )
        # atur penempatan
        self.frame.grid_propagate((False))
        self.frame.grid(row=0, column=1, rowspan=4)
        self.Label.grid(row=1, column=1, sticky="nsew", ipady=60)
        self.id.grid(row=2, column=1, pady=40)
        self.passn.grid(row=3, column=1)
        self.login.grid(row=4, column=1, pady=50)

    def get_text(self):
        a = (self.id.get(), self.passn.get())
        login = aires.login(a[0], a[1])
        if login:
            self.destroy()
            main1 = main.main()
            main1.mainloop()


app = app()

app.mainloop()
