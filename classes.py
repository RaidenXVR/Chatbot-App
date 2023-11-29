import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import email_validator
from email_validator import validate_email, EmailNotValidError
from PIL import Image
from ai_response import sign_up, get_profile, logout, load_from_yaml, decrypt
import os
from dotenv import load_dotenv


class KawankuError(ctk.CTkToplevel):
    def __init__(self, text: str):
        super().__init__()
        self.text = text
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate position
        x = int((screen_width) / 2)
        y = int((screen_height) / 2)

        # Set position
        self.geometry(f"+{x}+{y}")

    def warning_message(self, titles: str):
        msg = CTkMessagebox(
            width=600,
            height=300,
            master=self,
            title=titles,
            message=self.text,
            icon="./assets/warning.png",
            option_1="Ok",
            justify="left",
        )
        if msg.get() == "Ok":
            self.destroy()

    def cancel_message(self, titles: str):
        msg = CTkMessagebox(
            master=self,
            title=titles,
            message=self.text,
            icon="./assets/cross.png",
            option_1="Ok",
        )
        if msg.get() == "Ok":
            self.destroy()

    def success_message(self, titles: str):
        msg = CTkMessagebox(
            master=self,
            title=titles,
            message=self.text,
            icon="./assets/check.png",
            option_1="OK",
        )
        if msg.get() == "OK":
            self.destroy()


class ForgetPassword(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.grab_set()
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        x = (self.screen_width / 2) - (300) + 100
        y = (self.screen_height / 2) - (200)
        self.geometry("%dx%d+%d+%d" % (600, 200, x, y))
        self.resizable(False, False)
        self.attributes("-topmost", "true")
        self.title("Forget Password")
        self.frame = ctk.CTkFrame(self, width=540, height=150)
        self.title_label = ctk.CTkLabel(
            self.frame,
            text="Silahkan Hubungi Admin Di Email kawanku.ai@gmail.com untuk bantuan lebih lanjut.",
            anchor="w",
            width=500,
            font=("consolas", 20),
            wraplength=500,
        )
        self.button = ctk.CTkButton(
            self.frame, text="OK", height=40, command=self.destroy
        )

        # penempatan
        self.frame.pack_propagate((0))
        self.frame.pack(expand=True)
        self.title_label.pack()
        self.button.pack(side=ctk.BOTTOM, expand=True)

    def send_request(self):
        if self.text_box.get("1.0", "end") == "\n":
            err = KawankuError("Mohon isi alasan terlebih dahulu...")
            err.warning_message("Peringatan")
        else:
            a = CTkMessagebox(
                title="request terkirim",
                message="permintaan telah dikirim ke admin...",
                icon="./assets/check.png",
                option_1="Ok",
            )
            if a.get() == "Ok":
                self.destroy()


class Register(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.grab_set()
        self.geometry(
            f"400x600+{(self.winfo_screenwidth()-400)/2}+{(self.winfo_screenheight()-600)/2}"
        )
        self.resizable(False, False)
        self.title("Register")
        self.frame = ctk.CTkFrame(self, width=340, height=500)
        self.images = ctk.CTkImage(
            dark_image=Image.open("./assets/logoDM.png"),
            light_image=Image.open("./assets/logoLM.png"),
            size=(140, 200),
        )
        self.base = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.logo = ctk.CTkLabel(self.base, image=self.images, text="")
        self.title2 = ctk.CTkLabel(self.frame, text="Register", font=("consolas", 30))
        self.id = ctk.CTkEntry(self.frame, width=300, placeholder_text="Username")
        self.passn = ctk.CTkEntry(
            self.frame, width=300, placeholder_text="Password", show="*"
        )
        self.email = ctk.CTkEntry(self.frame, width=300, placeholder_text="Email")
        self.confirm_passn = ctk.CTkEntry(
            self.frame, width=300, placeholder_text="Confirm Password", show="*"
        )
        self.confirm_button = ctk.CTkButton(
            self.frame, text="Confirm", width=100, command=self.get_confirm
        )
        # penempatan
        self.frame.pack_propagate((0))
        self.frame.pack(expand="True")
        self.base.pack(side=ctk.TOP)
        self.logo.pack(side=ctk.TOP)
        self.title2.pack(side=ctk.TOP, pady=20)
        self.id.pack(side=ctk.TOP, pady=5)
        self.passn.pack(side=ctk.TOP, pady=5)
        self.email.pack(side=ctk.TOP, pady=5)
        self.confirm_passn.pack(side=ctk.TOP, pady=5)
        self.confirm_button.pack(side=ctk.BOTTOM, expand=True, pady=20)
        self.wait_window()

    def get_confirm(self):
        username = self.id.get()
        pass_awal = self.passn.get()
        pass_akhir = self.confirm_passn.get()
        alamat_email = self.email.get()
        self.grab_release()

        Confirmation.confirm(self, username, pass_awal, pass_akhir, alamat_email)


class Confirmation(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()

    def confirm(self, username: str, pasw: str, passs: str, email: str):
        email_check = False

        try:
            email_check = validate_email(email, check_deliverability=False)
        except EmailNotValidError as e:
            b = KawankuError("Email is invalid or fake")
            b.warning_message("Error: Invalid Email")
        except email_validator.exceptions_types.EmailSyntaxError as e:
            b = KawankuError("Email is invalid or fake")
            b.warning_message("Error: Invalid Email")
        if pasw != passs:
            a = KawankuError("Password and confirmed password is not equal...")
            a.warning_message("Error: Unequal Password Confirmation")

        elif email_check and pasw == passs:
            sign_up_success = sign_up(email=email, username=username, password=pasw)
            if sign_up_success:
                CTkMessagebox(
                    title="Success",
                    icon="./assets/check.png",
                    message="Registrasi berhasil dilakukan, silakan login di menu login.",
                    option_1="Ok",
                )
                self.destroy()
            else:
                err = KawankuError(
                    "Registrasi Gagal. Periksa Koneksi Atau Gunakan Email Atau Username Lain."
                )
                err.warning_message("Error: Registrasi Gagal")

        else:
            c = KawankuError("Registrasi gagal dilakukan")
            c.warning_message("Error: Unknown Error")


class Profile(ctk.CTkToplevel):
    main_root = ""

    def __init__(self, root):
        super().__init__()
        self.main_root = root
        self.title("Profil")
        self.geometry(f"{400}x{500}")
        self.grab_set()

        try:
            uid = eval(
                decrypt(
                    load_from_yaml("./assets/lsr.yaml"), b"ftrn80827310103rdnxvrnzr"
                )
            )["USER_ID"]

            username, email = get_profile(user_id=uid)
        except Exception as e:
            print(e)
            err = KawankuError(
                "Ada Kesalahan Dalam Memuat Profil. Periksa Koneksi Dan Coba Lagi."
            )
            err.warning_message("Gagal Memuat Profil.")
            self.destroy()
            return

        frame_profile = ctk.CTkFrame(self, width=400, height=500, corner_radius=10)
        frame_profile.pack(
            padx=10,
            pady=10,
            fill="x",
        )
        username_label = ctk.CTkLabel(
            frame_profile, text="Username: " + username, font=("Roboto", 12)
        )
        email_label = ctk.CTkLabel(
            frame_profile, text="Email: " + email, font=("Roboto", 12)
        )
        username_label.pack(padx=20, pady=20)
        email_label.pack(padx=10, pady=20)
        logout_button = ctk.CTkButton(
            frame_profile,
            width=100,
            height=80,
            text="Logout",
            command=self.logout_handle,
        )
        cancel_button = ctk.CTkButton(
            frame_profile, width=100, height=80, text="Cancel", command=self.destroy
        )
        logout_button.pack(pady=40, padx=20)
        cancel_button.pack(pady=10, padx=20)

        self.wait_window()

    def logout_handle(self):
        log = logout()
        if log:
            self.main_root.destroy()
