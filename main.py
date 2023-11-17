import customtkinter as ctk
import ai_response as aires
from PIL import Image, ImageTk
import threading
import asyncio
from pymongo import MongoClient, errors
import os
from dotenv import load_dotenv
import classes as clss


class main(ctk.CTk):
    message = []
    is_new_button_clicked: bool = True
    current_topic = ""
    client = MongoClient(os.getenv("MONGO_DB"))
    db = client["Chatbot"]
    collection = db["users"]
    user_id = int(os.getenv("USER_ID"))
    # buttons = collection.find_one({"_id": user_id})["buttons"]
    buttons = []

    def __init__(self):
        super().__init__()

        self.index = 0
        self.states = ["dark", "light"]
        self.conversation = []
        self.title("Kawanku.AI")

        ctk.set_appearance_mode(self.states[self.index])
        ctk.set_default_color_theme("dark-blue")
        screen_x = self.winfo_screenwidth()
        screen_y = self.winfo_screenheight()

        self.geometry(
            f"{screen_x*0.8}x{screen_y*0.7}+{(screen_x*0.8)*0.1}+{(screen_y*0.7)*0.1}"
        )

        add_img = Image.open("./assets/add.png")
        add_image = ctk.CTkImage(light_image=add_img, dark_image=add_img, size=(30, 30))
        profile_image = ctk.CTkImage(
            light_image=Image.open("./assets/user.png"),
            dark_image=Image.open("./assets/user.png"),
            size=(30, 30),
        )
        logo = ctk.CTkImage(
            light_image=Image.open("./assets/logoLM.png"),
            dark_image=Image.open("./assets/logoDM.png"),
            size=(100, 125),
        )

        self.iconbitmap(default="./assets/logo.ico")

        # self.wm_iconphoto(True, logo_w)
        # buat frame pinggir kiri
        self.frame_1 = ctk.CTkFrame(
            self,
            width=self.winfo_width() * 0.4,
            height=800,
            corner_radius=10,
        )
        self.frame_1.pack(anchor="w", side="left", pady=30, padx=30)
        self.logo_icon = ctk.CTkLabel(self.frame_1, image=logo, text="")
        self.logo_icon.pack(pady=20, padx=30, side="top")
        self.profile_button = ctk.CTkButton(
            self.frame_1,
            text="Profile",
            fg_color="#0086b3",
            image=profile_image,
        )
        self.profile_button.pack(pady=20, padx=20)
        self.button_1 = ctk.CTkButton(
            self.frame_1,
            text="New Chat...",
            command=self.new_button_clicked,
            fg_color="#0086b3",
            image=add_image,
            compound="left",
            anchor="w",
        )
        self.button_1.pack(padx=30, pady=20)
        self.history = ctk.CTkScrollableFrame(
            self.frame_1, label_text="History", height=self.frame_1.winfo_height() - 50
        )
        self.history.pack(padx=20, pady=20, anchor="center")
        self.switch = ctk.CTkSwitch(
            master=self.frame_1,
            text=f"{self.states[self.index]} Mode",
            command=self.change_mode,
        )
        self.switch.pack(pady=10, anchor="s", side="bottom")

        # buat frame pinggir kanan
        self.frame_2 = ctk.CTkFrame(
            self,
            width=self.winfo_width() * 0.6,
            height=self.winfo_height() - 50,
            corner_radius=10,
        )
        self.frame_2.pack(side="right", anchor="e", padx=30, pady=20)

        # buat bisa scroll
        self.title2 = ctk.CTkLabel(
            master=self.frame_2,
            text="",
            anchor="center",
            width=700,
            height=100,
            font=("Roboto", 20),
            wraplength=500,
        )
        self.title2.pack(side="top", anchor="center", pady=20, padx=20)
        self.chatframe = ctk.CTkScrollableFrame(
            self.frame_2,
            width=700,
            height=350,
            corner_radius=10,
        )
        self.chatframe.pack(
            pady=30,
            anchor="s",
        )
        self.text_box = ctk.CTkTextbox(self.frame_2, width=700, height=80, wrap="word")
        self.text_box.pack(pady=40, padx=10, anchor="sw", side="left")
        self.submit_button = ctk.CTkButton(
            self.frame_2,
            text="Kirim",
            width=100,
            height=80,
            command=self.get_text,
            fg_color="#0086b3",
        )
        self.submit_button.pack(anchor="se", side="right", padx=10, pady=40)

    def change_mode(self):
        self.index = (self.index + 1) % 2
        ctk.set_appearance_mode(self.states[self.index])
        self.switch.configure(text=f"{self.states[self.index]} Mode")

    def get_text(self):
        # cek for paying validity
        self.submit_button.configure(state="disabled")

        try:
            user = self.collection.find_one({"_id": self.user_id})
            if user["num_valid_msg"] < 1 and not user["payed"]:
                e = clss.KawankuError(
                    "Anda Belum Melakukan Pembayaran Untuk Memakai Aplikasi Ini. Jika Sudah Mohon Hubungi Admin: fitran.nizar@gmail.com."
                )
                e.warning_message("Pembayaran Tidak Terdeteksi.")
                self.submit_button.configure(state="normal")

                return
        except errors.PyMongoError as e:
            clss.KawankuError(
                "Error: MongoDB Error. Periksa Koneksi Anda dan Coba Lagi"
            ).warning_message("Error")
            self.submit_button.configure(state="normal")

            return

        # for text streaming/typing effect
        def stream_text():
            if len(response_text._text) < len(response):
                response_text.configure(text=response[: len(response_text._text) + 5])
                self.after(100, stream_text)

            else:
                response_text.configure(text=response)

        # processing response in a thread
        def processing_response():
            if self.is_new_button_clicked:
                # response, message_type = aires.get_first_response(
                #     ipt, user_id=self.user_id
                # )
                response, message_type = aires.test_input(
                    ipt,
                    "topic panjang 122 345 4 534 975 294 129 128391 238729 84719 4798372 943792 398423 29472 3974 92 3",
                )
            else:
                response, message_type = aires.test_input(ipt, "chat")
                # response, message_type = aires.get_response(
                #     ipt, self.user_id, self.title2._text
                # )

            thread.result = response, message_type

        def user_input_handle():
            # input frame
            new_frame = ctk.CTkFrame(
                self.chatframe,
                corner_radius=10,
                fg_color="#0086b3",
                width=max_width,
            )
            new_frame.pack(pady=5, padx=20, anchor="e")
            new_label = ctk.CTkLabel(
                new_frame, text=ipt, wraplength=max_width, font=("Roboto", 15)
            )
            new_label.configure(justify="left")
            new_label.pack(pady=10, padx=10, anchor="nw")

            # loading frame
            global load_frame
            load_frame.pack(padx=20, pady=10, anchor="w")
            progress_bar = ctk.CTkProgressBar(
                load_frame,
                width=max_width,
                mode="indeterminate",
                indeterminate_speed=2,
                progress_color="#0086b3",
                fg_color="#999999",
            )
            progress_bar.pack(padx=10, pady=10)
            progress_bar.start()

        # handle the button input
        max_width = 350
        ipt = self.text_box.get("0.0", "end")
        self.text_box.delete("0.0", "end")

        # check if input empty. If empty, return
        if len(ipt) <= 1:
            self.submit_button.configure(state="normal")
            return

        # main GUI thread
        global thread_main
        thread_main = threading.Thread(target=user_input_handle)
        thread_main.start()

        # loading frame
        global load_frame
        load_frame = ctk.CTkFrame(
            self.chatframe,
            corner_radius=10,
            fg_color="#999999",
            width=100,
            height=100,
        )
        # threading
        global thread
        thread = threading.Thread(target=processing_response)
        thread.start()
        self.check_result()

    def check_result(self):
        # for text streaming/typing effect
        def stream_text():
            if len(response_text._text) < len(response):
                response_text.configure(text=response[: len(response_text._text) + 5])
                self.after(100, stream_text)

            else:
                response_text.configure(text=response)

        # check the threading
        if thread.is_alive():
            self.after(100, self.check_result)
        else:
            response, message_type = thread.result

            global load_frame
            load_frame.destroy()
            if message_type != "error":
                self.is_new_button_clicked = False
                if message_type == "image":
                    img_frame = ctk.CTkFrame(
                        self.chatframe, width=350, height=350, corner_radius=10
                    )
                    img_frame.pack(padx=10, pady=10)
                    img = ctk.CTkImage(
                        light_image=Image.open(response),
                        dark_image=Image.open(response),
                        size=(350, 350),
                    )
                    image_label = ctk.CTkLabel(
                        img_frame,
                        width=350,
                        height=350,
                        text="",
                        image=img,
                    )
                    image_label.pack()
                else:
                    if message_type != "chat":
                        self.title2.configure(text=message_type)
                        trash_img = ctk.CTkImage(
                            light_image=Image.open("./assets/trash-can.png"),
                            dark_image=Image.open("./assets/trash-can.png"),
                            size=(30, 30),
                        )
                        button_frame = ctk.CTkFrame(
                            self.history,
                            width=self.history.winfo_width(),
                            height=self.history.winfo_height(),
                        )
                        new_button = ctk.CTkButton(
                            button_frame,
                            width=150,
                            height=50,
                            text=message_type[:17] + "...",
                            command=lambda: self.topic_button(
                                button=new_button, topic=message_type
                            ),
                            fg_color="#0086b3",
                            textvariable=message_type,
                        )
                        new_del_button = ctk.CTkButton(
                            button_frame,
                            width=50,
                            height=50,
                            text="",
                            fg_color="#ff0000",
                            command=lambda: self.delete_topic(
                                frame_button_to_delete=button_frame
                            ),
                            image=trash_img,
                        )
                        new_del_button.pack(padx=5, pady=10, anchor="e", side="right")
                        new_button.pack(padx=5, pady=10, anchor="w", side="left")
                        button_frame.pack(fill="both")

                        self.buttons.append(button_frame)

                    max_width = 350
                    response_frame = ctk.CTkFrame(
                        self.chatframe,
                        corner_radius=10,
                        fg_color="#999999",
                        width=max_width,
                    )
                    response_frame.pack(pady=5, padx=20, anchor="w")
                    response_text = ctk.CTkLabel(
                        response_frame,
                        text="",
                        wraplength=max_width,
                        font=("Roboto", 15),
                    )
                    response_text.configure(justify="left")
                    response_text.pack(pady=10, padx=10, anchor="nw")

                    stream_text()
                    self.submit_button.configure(state="normal")

            else:
                e = clss.KawankuError(response)
                e.warning_message("Error")
                self.submit_button.configure(state="normal")

    def new_button_clicked(self):
        self.is_new_button_clicked = not self.is_new_button_clicked
        children = self.chatframe.winfo_children()
        self.title2.configure(text="")
        for child in children:
            child.destroy()

    def topic_button(self, button, topic: str):
        self.is_new_button_clicked = False
        topics = self.collection.find_one({"_id": self.user_id})["topics"]
        topic = button._text
        for tpc in topics:
            if topic in tpc._keys:
                self.message = tpc[topic]
                break

        # destroying the frames in current thread
        children = self.chatframe.winfo_children()
        for child in children:
            child.destroy()

        # generate new frame from messages
        max_width = 350
        i = 0
        while i < len(self.message):
            new_frame = ctk.CTkFrame(
                self.chatframe,
                corner_radius=10,
                fg_color="#0086b3",
                width=max_width,
            )
            new_frame.pack(pady=5, padx=20, anchor="e")
            new_label = ctk.CTkLabel(
                new_frame, text=self.message[i]["content"], wraplength=max_width
            )
            new_label.configure(justify="left")
            new_label.pack(pady=10, padx=10, anchor="nw")

            response_frame = ctk.CTkFrame(
                self.chatframe, corner_radius=10, fg_color="#999999", width=max_width
            )
            response_frame.pack(pady=5, padx=20, anchor="w")
            response_text = ctk.CTkLabel(
                response_frame,
                text=self.message[i + 1]["content"],
                wraplength=max_width,
            )
            response_text.configure(justify="left")
            response_text.pack(pady=10, padx=10, anchor="nw")
            i += 2

    def delete_topic(self, frame_button_to_delete):
        topic = frame_button_to_delete.winfo_children()[0]._textvariable
        try:
            chat_to_delete = {"$pull": {"topics": {topic: {"$exists": True}}}}
            self.collection.update_one({"_id": self.user_id}, chat_to_delete)
            frame_button_to_delete.destroy()
            frame_children = self.chatframe.winfo_children()

            self.title2.configure(text="")

            for child in frame_children:
                child.destroy()

            self.is_new_button_clicked = True
        except Exception:
            e = clss.KawankuError(
                "Gagal Menghapus Pesan. Periksa Koneksi Anda Dan Coba Lagi."
            )
            e.warning_message("Gagal Menghapus Pesan.")
