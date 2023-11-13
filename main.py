import customtkinter as ctk
import ai_response as aires
from PIL import Image, ImageTk
import threading
import asyncio


class main(ctk.CTk):
    message = []
    is_new_button_clicked: bool = False
    buttons = []

    def __init__(self):
        super().__init__()
        self.index = 0
        self.states = ["dark", "light"]
        self.conversation = []
        self.title("Kawanku.ai")
        ctk.set_appearance_mode(self.states[self.index])
        ctk.set_default_color_theme("green")
        self.geometry(f"{1280}x{720}")
        self.grid_columnconfigure((0, 3), weight=1)
        self.grid_columnconfigure((1), weight=1)
        self.grid_columnconfigure((2), weight=0)

        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_rowconfigure((2, 3), weight=0)

        self.grid_propagate(0)

        # buat frame pinggir kiri
        self.frame_1 = ctk.CTkFrame(self, width=320, corner_radius=10)
        self.frame_1.grid(row=0, column=1, rowspan=4, sticky="nsw")
        self.button_1 = ctk.CTkButton(
            self.frame_1, text="new chat", command=self.new_button_clicked
        )
        self.button_1.grid(row=0, column=0, padx=50, pady=40, sticky="nsew")
        self.history = ctk.CTkScrollableFrame(
            self.frame_1, label_text="History", height=400
        )
        self.history.grid(row=1, column=0, pady=40, sticky="ew")
        self.switch = ctk.CTkSwitch(
            master=self.frame_1,
            text=f"{self.states[self.index]} Mode",
            command=self.change_mode,
        )
        self.switch.grid(row=2, column=0, pady=30, sticky="nsew")

        # buat frame pinggir kanan
        self.frame_2 = ctk.CTkFrame(
            self, width=1000, corner_radius=10, fg_color="transparent"
        )
        self.frame_2.grid(row=0, column=2, rowspan=3, sticky="nsew")
        # buat bisa scroll

        self.title2 = ctk.CTkLabel(
            master=self.frame_2,
            text="",
            anchor="center",
            width=800,
            height=100,
            font=("consolas", 20),
        )
        self.title2.grid(row=0, column=2, sticky="s")
        self.chatframe = ctk.CTkScrollableFrame(
            self, width=700, height=450, corner_radius=0
        )
        self.chatframe.grid(row=0, column=2, pady=80, rowspan=1, sticky="nsew")
        self.text_box = ctk.CTkTextbox(self.frame_2, width=700, height=80, wrap="word")
        self.text_box.grid(row=1, column=2, pady=540, sticky="nsew")
        self.submit_button = ctk.CTkButton(
            self.frame_2, text="kirim", width=100, height=80, command=self.get_text
        )
        self.submit_button.grid(row=1, column=2, sticky="e")
        # tambahin teks di chatframe
        # self.text1 = ctk.CTkLabel(
        #     self.chatframe,
        #     width=800,
        #     fg_color="purple",
        #     anchor="w",
        #     font=("Times new roman", 25),
        # )

        # self.text1.grid(row=0, column=2, sticky="nsew")

    def change_mode(self):
        self.index = (self.index + 1) % 2
        ctk.set_appearance_mode(self.states[self.index])
        self.switch.configure(text=f"{self.states[self.index]} Mode")

    def get_text(self):
        def stream_text():
            if len(echo_text._text) < len(response):
                echo_text.configure(text=response[: len(echo_text._text) + 5])
                self.after(100, stream_text)

            else:
                echo_text.configure(text=response)

        max_width = 350
        a = self.text_box.get("0.0", "end")
        self.text_box.delete("0.0", "end")

        new_frame = ctk.CTkFrame(
            self.chatframe,
            corner_radius=10,
            fg_color="green",
            width=max_width,
        )
        new_frame.pack(pady=5, padx=20, anchor="e")
        new_label = ctk.CTkLabel(new_frame, text=a, wraplength=max_width)
        new_label.configure(justify="left")
        new_label.pack(pady=10, padx=10, anchor="nw")

        load_frame = ctk.CTkFrame(
            self.chatframe, corner_radius=10, fg_color="#999999", width=max_width
        )

        load_image = Image.open("loading.gif")
        load_image = ctk.CTkImage(
            light_image=load_image, dark_image=load_image, size=(100, 100)
        )
        load_icon = ctk.CTkLabel(load_frame, text="", image=load_image, width=100)
        load_icon.pack(pady=5, padx=5)
        load_frame.pack(pady=5, padx=5, anchor="w", fill="both")

        response, message_type = asyncio.run(aires.get_first_response(a, 1))
        # response = "testing"
        # message_type = "new topic"
        load_frame.pack_forget()
        echo_frame = ctk.CTkFrame(
            self.chatframe, corner_radius=10, fg_color="#999999", width=max_width
        )
        if message_type == "image":
            pass
        else:
            if message_type != "chat":
                self.title2.configure(text=message_type)
                new_button = ctk.CTkButton(
                    self.history,
                    width=self.history.winfo_width(),
                    height=50,
                    text=message_type,
                    command=self.debug_print,
                )
                new_button.pack(padx=5, pady=10, anchor="center")
                self.buttons.append(new_button)

            echo_frame.pack(pady=5, padx=20, anchor="w")
            echo_text = ctk.CTkLabel(echo_frame, text="", wraplength=max_width)
            echo_text.configure(justify="left")
            echo_text.pack(pady=10, padx=10, anchor="nw")
            stream_text()

        # history_button = ctk.CTkButton(self.history, corner_radius=10, text="test")

    def new_button_clicked(self):
        self.is_new_button_clicked = True

    def debug_print(self):
        self.message = [
            {"role": "user", "content": "testing 1"},
            {"role": "assistant", "content": "bot test2"},
        ]

        children = self.chatframe.winfo_children()
        for child in children:
            child.destroy()

        print("test test test")
