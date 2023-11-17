import tkinter as tk
from tkinter import *
import customtkinter as ctk
import classes as clss
from PIL import Image

width_ = 800
height_ = 600

ctk.set_default_color_theme("blue")
ctk.set_appearance_mode("dark")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry(
            f"{width_}x{height_}+{(self.winfo_screenwidth()-width_)/2}+{(self.winfo_screenheight()-height_)/2}"
        )
        self.title = "Kawanku.AI"
        self.images = ctk.CTkImage(
            dark_image=Image.open("./assets/logoDM.png"),
            light_image=Image.open("./assets/logoLM.png"),
            size=(140, 200),
        )
        self.frame = ctk.CTkFrame(self, width=400, height=500)
        self.Label = ctk.CTkLabel(
            self.frame, width=100, text="Login", font=("consolas", 30), anchor="center"
        )
        self.id = ctk.CTkEntry(self.frame, width=360, placeholder_text="Username")
        self.passn = ctk.CTkEntry(
            self.frame, width=360, placeholder_text="Password", show="*"
        )
        self.login = ctk.CTkButton(
            self.frame, text="Login", font=("consolas", 20), command=self.get_text
        )
        self.logo = ctk.CTkFrame(
            self.frame, width=100, height=100, fg_color="transparent"
        )
        self.images_label = ctk.CTkLabel(self.logo, image=self.images, text="")
        self.forget_password_button = ctk.CTkButton(
            self.frame,
            text="Forget Password?",
            fg_color="transparent",
            command=self.goto_forget_pass,
        )

        self.register_button = ctk.CTkButton(
            self.frame,
            text="Belum punya akun? buat yuk",
            fg_color="transparent",
            command=self.goto_regist,
        )
        # atur penempatan
        self.logo.pack(side=ctk.TOP)
        self.Label.pack(side=ctk.TOP, expand=False, fill=ctk.X)
        self.id.pack(side=ctk.TOP, pady=30)
        self.passn.pack(side=ctk.TOP)
        self.forget_password_button.pack()
        self.login.pack(side=ctk.TOP, pady=30)
        self.frame.pack_propagate((False))
        self.frame.pack(side=ctk.TOP, expand=True)
        self.images_label.pack(side=ctk.TOP)
        self.register_button.pack(side=ctk.BOTTOM, expand=True)

    def get_text(self):
        a = (self.id.get(), self.passn.get())
        if len(a[0]) < 1 or len(a[1]) < 1:
            clss.KawankuError("Username Atau Password Kosong.").warning_message(
                "Isian Kosong."
            )
            return
        try:
            import main

            login = aires.login(a[0], a[1])
            if login:
                self.destroy()
                main1 = main.main()
                main1.mainloop()

            else:
                clss.KawankuError(
                    "Password atau Username salah. Jika Belum Registrasi, Registrasi Untuk Bergabung."
                ).warning_message("Username atau Password salah.")
        except Exception as e:
            clss.KawankuError(
                "Terjadi Kesalahan Koneksi. Periksa Internet Anda Dan Coba Lagi."
            ).warning_message("Masalah Koneksi")

    def goto_regist(self):
        app = clss.Register()

    def goto_forget_pass(self):
        app = clss.ForgetPassword()


if "__name__" == "__main__":
    app = App()

    app.mainloop()
