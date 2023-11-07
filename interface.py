from datetime import datetime
from ttkthemes import ThemedTk
import customtkinter as ct

# initialization
root = ct.CTk()
root.title = "Chatbot"

# get size
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

window_width = int(screen_width * 0.8)
window_height = int(screen_height * 0.7)

root.geometry(
    f"{window_width}x{window_height}+{int(screen_width*0.1)}+{int(screen_height*0.1)}"
)

# frame for buttons
frame = ct.CTkFrame(master=root, width=window_width * 0.25)
frame.pack(pady=20, padx=10, fill="both", expand=True, side="left")
# frame for chats and inputs
frame2 = ct.CTkFrame(master=root, width=window_width * 0.7)
frame2.pack(pady=20, padx=10, fill="both", expand=True, side="right")


# main run
root.mainloop()
