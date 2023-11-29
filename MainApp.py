import customtkinter as ctk
import ai_response as aires
from PIL import Image, ImageTk
import threading
import asyncio
from pymongo import MongoClient, errors
import os
from dotenv import load_dotenv
import classes as clss
import certifi
from tkinter import filedialog


class MainApp(ctk.CTk):
    message = []
    is_new_button_clicked: bool = True
    current_topic = ""

    def __init__(self):
        super().__init__()
        try:
            env = eval(
                aires.decrypt(
                    aires.load_from_yaml("./assets/env.yaml"),
                    b"ftrn80827310103rdnxvrnzr",
                )
            )
            lsr = eval(
                aires.decrypt(
                    aires.load_from_yaml("./assets/lsr.yaml"),
                    b"ftrn80827310103rdnxvrnzr",
                )
            )
            self.client = MongoClient(env["MONGODB"], tlsCAfile=certifi.where())
            self.db = self.client["Chatbot"]
            self.collection = self.db["users"]
            self.user_id = lsr["USER_ID"]

        except errors.PyMongoError as e:
            emsg = clss.KawankuError(
                "Ada Suatu Masalah Menghubungkan Ke Server. Periksa Koneksi Dan Coba Lagi Nanti."
            )
            emsg.warning_message("Masalah Koneksi")

        self.index = 0
        self.states = ["Dark", "Light"]
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
        logo_img_dark = Image.open("./assets/logoDM.png")
        logo_img_light = Image.open("./assets/logoLM.png")

        self.logo = ctk.CTkImage(
            light_image=logo_img_light,
            dark_image=logo_img_dark,
            size=(100, 125),
        )

        self.iconbitmap(default="./assets/logo.ico")

        # buat frame pinggir kiri
        self.frame_1 = ctk.CTkFrame(
            self,
            width=self.winfo_width() * 0.5,
            height=self.winfo_height() - 50,
            corner_radius=10,
        )
        self.frame_1.pack(anchor="w", side="left", pady=20, padx=20)
        self.logo_icon = ctk.CTkLabel(self.frame_1, text="")
        self.logo_icon.configure(image=self.logo)
        self.logo_icon.pack(pady=20, padx=30, side="top")
        self.profile_button = ctk.CTkButton(
            self.frame_1,
            text="Profile",
            fg_color="#0086b3",
            image=profile_image,
            command=self.show_profile,
        )
        self.profile_button.pack(pady=20, padx=10)
        self.button_1 = ctk.CTkButton(
            self.frame_1,
            text="New Chat...",
            command=self.new_button_clicked,
            fg_color="#0086b3",
            image=add_image,
            compound="left",
            anchor="w",
        )
        self.button_1.pack(padx=30, pady=10)
        self.history = ctk.CTkScrollableFrame(
            self.frame_1, label_text="History", height=270
        )
        self.history.pack(padx=10, pady=10, anchor="center")
        self.switch = ctk.CTkSwitch(
            master=self.frame_1,
            text=f"{self.states[self.index]} Mode",
            command=self.change_mode,
        )
        self.switch.pack(pady=10, anchor="s", side="bottom")
        topics = self.collection.find_one({"_id": self.user_id})["topics"]

        # make topic buttons

        for topic in topics:
            for key in topic.keys():
                self.make_button(topic=str(key))

        # buat frame pinggir kanan
        self.frame_2 = ctk.CTkFrame(
            self,
            width=self.winfo_width() * 0.6,
            height=self.winfo_height() - 50,
            corner_radius=10,
        )
        self.frame_2.pack(
            side="right", anchor="e", padx=30, pady=20, expand=True, fill="both"
        )

        # buat bisa scroll
        self.title2 = ctk.CTkLabel(
            master=self.frame_2,
            text="",
            anchor="center",
            width=700,
            height=70,
            font=("Roboto", 23),
            wraplength=500,
        )
        self.title2.pack(
            side="top", anchor="center", pady=10, padx=20, expand=True, fill="x"
        )
        self.chatframe = ctk.CTkScrollableFrame(
            self.frame_2,
            width=700,
            height=400,
            corner_radius=10,
        )
        self.chatframe.pack(pady=20, padx=10, anchor="s", expand=True, fill="both")
        self.text_box = ctk.CTkTextbox(
            self.frame_2,
            width=self.chatframe.winfo_width() - 100,
            height=80,
            wrap="word",
            font=("Roboto", 18),
        )
        self.text_box.pack(
            pady=20, padx=10, anchor="sw", side="left", expand=True, fill="both"
        )
        self.submit_button = ctk.CTkButton(
            self.frame_2,
            text="Kirim",
            width=100,
            height=80,
            command=self.get_text,
            fg_color="#0086b3",
        )
        self.submit_button.pack(anchor="se", side="right", padx=10, pady=20)

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
                    "Anda Belum Melakukan Pembayaran Untuk Memakai Aplikasi Ini. Jika Sudah Mohon Hubungi Admin: kawanku.ai@gmail.com."
                )
                e.warning_message("Pembayaran Tidak Terdeteksi.")
                self.submit_button.configure(state="normal")

                return
        except errors.PyMongoError as e:
            err = clss.KawankuError(
                "Error: MongoDB Error. Periksa Koneksi Anda dan Coba Lagi"
            )
            err.warning_message("Error")
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
                response, message_type, tp = aires.get_first_response(
                    ipt, user_id=self.user_id
                )

            else:
                response, message_type, tp = aires.get_response(
                    ipt, self.user_id, self.title2._text
                )

            thread.result = response, message_type, tp

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
                new_frame, text=ipt, wraplength=max_width, font=("Roboto", 18)
            )
            new_label.configure(justify="left")
            new_label.pack(pady=10, padx=10, anchor="nw", side="right")
            new_label.bind("<Enter>", self.entered)
            new_frame.bind("<Leave>", self.leave)

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
            response, message_type, tp = thread.result

            global load_frame
            load_frame.destroy()
            if message_type != "error":
                self.is_new_button_clicked = False
                if message_type == "image":
                    img_frame = ctk.CTkFrame(
                        self.chatframe, width=350, height=350, corner_radius=10
                    )
                    img_frame.pack(padx=10, pady=10, anchor="w")
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
                    image_label.pack(padx=10, pady=10, anchor="w")
                    if tp != "":
                        self.title2.configure(text=tp)
                        self.make_button(topic=tp)
                    self.submit_button.configure(state="normal")

                else:
                    if message_type != "chat":
                        self.title2.configure(text=message_type)
                        self.make_button(message_type)

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
                        font=("Roboto", 18),
                    )
                    response_text.configure(justify="left")
                    response_text.pack(pady=10, padx=10, anchor="nw", side="left")
                    response_text.bind("<Enter>", self.entered)
                    response_frame.bind("<Leave>", self.leave)
                    stream_text()
                    self.submit_button.configure(state="normal")

            else:
                e = clss.KawankuError(response)
                e.warning_message("Error")
                self.submit_button.configure(state="normal")

    def new_button_clicked(self):
        self.is_new_button_clicked = True
        self.submit_button.configure(state="normal")
        children = self.chatframe.winfo_children()
        self.title2.configure(text="")
        for child in children:
            child.destroy()

    # make the thread when button clicked
    def topic_button(self, button, topic: str):
        self.is_new_button_clicked = False
        topics = self.collection.find_one({"_id": self.user_id})["topics"]
        topic = button.winfo_children()[0]._textvariable
        self.title2.configure(text=topic)

        for tpc in topics:
            if topic in tpc.keys():
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
                master=new_frame,
                text=self.message[i]["content"],
                wraplength=max_width,
                font=("Roboto", 18),
            )
            new_label.configure(justify="left")
            new_label.pack(pady=5, padx=20, anchor="e", side="right")
            new_label.bind("<Enter>", self.entered)
            # new_frame.bind("<Enter>", self.entered)
            new_frame.bind("<Leave>", self.leave)

            response_frame = ctk.CTkFrame(
                self.chatframe, corner_radius=10, fg_color="#999999", width=max_width
            )

            response_frame.pack(pady=5, padx=20, anchor="w")
            if "Generated Image Path: " in self.message[i + 1]["content"]:
                try:
                    image_chat = ctk.CTkImage(
                        dark_image=Image.open(self.message[i + 1]["content"][22:]),
                        light_image=Image.open(self.message[i + 1]["content"][22:]),
                        size=(350, 350),
                    )
                    response_text = ctk.CTkLabel(
                        response_frame,
                        text="",
                        image=image_chat,
                    )
                    response_text.bind("<Enter>", self.entered)
                    response_frame.bind("<Leave>", self.leave)

                except FileNotFoundError as e:
                    err = clss.KawankuError("Gambar Tidak Ditemukan di dalam file.")
                    err.warning_message("Gambar Tidak Ditemukan.")
            else:
                response_text = ctk.CTkLabel(
                    response_frame,
                    text=self.message[i + 1]["content"],
                    wraplength=max_width,
                    font=("Roboto", 18),
                )
                response_text.configure(justify="left")
                response_text.bind("<Enter>", self.entered)
                response_frame.bind("<Leave>", self.leave)

            response_text.pack(pady=5, padx=20, anchor="nw", side="left")
            i += 2

    def entered(self, event):
        frame = event.widget.master.master
        if not self.button_exist(frame=frame):
            try:
                res_frame = int(str(frame)[59:])
            except ValueError:
                res_frame = 1
            frame.configure(width=420)
            is_image = False
            for child in frame.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    if len(child._text) == 0 and child._image != None:
                        is_image = True
            if not is_image:
                button = ctk.CTkButton(
                    frame,
                    width=80,
                    corner_radius=10,
                    text="Copy",
                    command=lambda frm=frame: self.copy_text(frm),
                )
            else:
                button = ctk.CTkButton(
                    frame,
                    width=80,
                    corner_radius=10,
                    text="Save",
                    command=lambda frm=frame: self.export_img(frm),
                )
            if res_frame % 2 == 0:
                button.pack(padx=10, pady=10, anchor="e", side="right")
            else:
                button.pack(padx=10, pady=10, anchor="w", side="left")

    def button_exist(self, frame):
        for child in frame.winfo_children():
            if isinstance(child, ctk.CTkButton):
                return True

        return False

    def leave(self, event):
        frame = event.widget.master
        frame.configure(width=350)
        children = frame.winfo_children()
        try:
            res_frame = int(str(frame)[59:])
        except ValueError:
            res_frame = 1

        # Get the mouse coordinates
        x = event.x
        y = event.y
        for child in children:
            # Get the child widget's bounding box
            child_bbox = child.bbox("all")

            # Check if the mouse is within the child widget's bounding box
            if (
                x >= child_bbox[0]
                and x <= child_bbox[2]
                and y >= child_bbox[1]
                and y <= child_bbox[3]
                and res_frame % 2 == 1
            ):
                # If the mouse is within the child widget, don't destroy the button
                return
            elif (
                x >= child_bbox[0]
                and x >= child_bbox[2]
                and y >= child_bbox[1]
                and y <= child_bbox[3]
                and res_frame % 2 == 0
            ):
                return
        # If the mouse is not within the bounds of any child widgets, destroy the button
        for child in children:
            if isinstance(child, ctk.CTkButton):
                child.destroy()

    def copy_text(self, the_master):
        for child in the_master.winfo_children():
            if isinstance(child, ctk.CTkLabel):
                self.clipboard_clear()
                self.clipboard_append(child._text)

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

    def show_profile(self):
        self.grab_release()
        clss.Profile(root=self)

    def make_button(self, topic):
        trash_img = ctk.CTkImage(
            light_image=Image.open("./assets/trash-can.png"),
            dark_image=Image.open("./assets/trash-can.png"),
            size=(20, 20),
        )
        button_frame = ctk.CTkFrame(
            self.history,
            width=self.history.winfo_width(),
            height=self.history.winfo_height(),
        )
        new_button = ctk.CTkButton(
            button_frame,
            width=170,
            height=30,
            text=topic[:17] + "...",
            fg_color="#0086b3",
            textvariable=topic,
        )
        new_button.configure(
            command=lambda btn=button_frame: self.topic_button(button=btn, topic=topic)
        )
        new_del_button = ctk.CTkButton(
            button_frame,
            width=30,
            height=30,
            text="",
            fg_color="#ff0000",
            image=trash_img,
        )
        new_del_button.configure(
            command=lambda delbtn=new_del_button: self.delete_topic(
                frame_button_to_delete=button_frame
            )
        )
        new_del_button.pack(padx=5, pady=5, anchor="e", side="right")
        new_button.pack(padx=5, pady=5, anchor="w", side="left")
        button_frame.pack(fill="both")

    def export_img(self, image_frame):
        save_path = filedialog.asksaveasfilename(
            filetypes=[("PNG Files", ".png")], defaultextension=".png"
        )

        if not save_path:
            return

        image_path = ""
        for child in image_frame.winfo_children():
            if isinstance(child, ctk.CTkLabel):
                image = child._image
                image_path = image._dark_image.filename

        img = Image.open(image_path)
        img.save(save_path)
