import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import email_validator
from email_validator import validate_email, EmailNotValidError
from PIL import Image
from ai_response import sign_up

global DB_ceritanya
DB_ceritanya = []


class KawankuError(ctk.CTk):
    def __init__(self, text: str):
        super().__init__()
        self.text = text
        self.error_type = {1: "cancel", 2: "warning"}
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
            icon=self.error_type[2],
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
            icon=self.error_type[1],
            option_1="Ok",
        )
        if msg.get() == "Ok":
            self.destroy()


class ForgetPassword(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.grab_set()
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        x = (self.screen_width / 2) - (300) + 100
        y = (self.screen_height / 2) - (200)
        self.geometry("%dx%d+%d+%d" % (600, 400, x, y))
        self.resizable(False, False)
        self.attributes("-topmost", "true")
        self.title("Forget Password")
        self.frame = ctk.CTkFrame(self, width=540, height=340)
        self.title_label = ctk.CTkLabel(
            self.frame,
            text="Buktikan Bahwa Ini Anda:",
            anchor="w",
            width=500,
            font=("consolas", 30),
        )
        self.text_box = ctk.CTkTextbox(self.frame, width=500, height=200)
        self.button = ctk.CTkButton(
            self.frame, text="Confirm", height=40, command=self.send_request
        )

        # penempatan
        self.frame.pack_propagate((0))
        self.frame.pack(expand=True)
        self.title_label.pack()
        self.text_box.pack(pady=20)
        self.button.pack(side=ctk.BOTTOM, expand=True)

    def send_request(self):
        if self.text_box.get("1.0", "end") == "\n":
            error("Mohon isi alasan terlebih dahulu...").warning_message("Peringatan")
        else:
            a = CTkMessagebox(
                title="request terkirim",
                message="permintaan telah dikirim ke admin...",
                icon="check",
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
        self.title = "Registasi"
        self.frame = ctk.CTkFrame(self, width=340, height=500)
        self.images = ctk.CTkImage(
            dark_image=Image.open("./assets/logoDM.png"),
            light_image=Image.open("./assets/logoLM.png"),
            size=(140, 200),
        )
        self.base = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.logo = ctk.CTkLabel(self.base, image=self.images, text="")
        self.title = ctk.CTkLabel(self.frame, text="Register", font=("consolas", 30))
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
        self.title.pack(side=ctk.TOP, pady=20)
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


class Confirmation(ctk.CTk):
    def __init__(self):
        super().__init__()

    def confirm(self, username: str, pasw: str, passs: str, email: str):
        email_check = False

        try:
            email_check = validate_email(email, check_deliverability=False)
        except EmailNotValidError as e:
            b = KawankuError("Email is invalid or fake")
            b.warning_message("Error: Invalid Email")
        if pasw != passs:
            a = KawankuError("Password and confirmed password is not equal...")
            a.warning_message("Error: Unequal Password Confirmation")

        elif email_check and (pasw == passs):
            sign_up_success = sign_up(email=email, username=username, password=pasw)
            if sign_up_success:
                CTkMessagebox(
                    title="Success",
                    icon="check",
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
            c = error("Registrasi gagal dilakukan")
            c.warning_message("Error: Unknown Error")
