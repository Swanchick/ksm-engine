from server_instance import ServerInstance, ServerState
from tkinter import *


def start_server():
    if server.server_state == ServerState.STARTED:
        return

    server.start()


def on_closing():
    if server.server_state == ServerState.STARTED:
        server.stop()

    root.destroy()


server = ServerInstance("Test", "python", ["E:\\Kyryls Server Manager\\script.py"])

root = Tk()
root.geometry("500x500")
root.resizable(False, False)
root.title("Kyryls Server Manager - Desktop Client")
root.protocol("WM_DELETE_WINDOW", on_closing)


text = Text(root)
text.pack(side=TOP)

frame = Frame(root)
frame.pack(side=TOP, fill=X)

command_entry = Entry(frame, width=70)
command_entry.pack(side=LEFT)

command_enter = Button(frame, text="Enter", width=10)
command_enter.pack(side=RIGHT)

button = Button(root, text="Start Server", command=start_server)
button.pack(side=BOTTOM)

root.mainloop()