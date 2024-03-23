from server import ServerInstance, ServerState, ServerOutput
from tkinter import *


def start_server():
    if server.server_state == ServerState.STARTED:
        return

    server.start()
    text.insert(END, "Server Started\n")


def on_callback(output: ServerOutput):
    text.insert(END, output.message)


def stop_server():
    if server.server_state == ServerState.STOPPED:
        return

    server.stop()
    text.insert(END, "Server stopped\n")


def on_closing():
    if server.server_state == ServerState.STARTED:
        server.stop()

    root.destroy()


def enter():
    if server.server_state == ServerState.STOPPED:
        return

    a = command_entry.get()
    server.send(a)

    print("End 2")


server = ServerInstance("Test", "python", ["script.py"])
server.register_callback("on_callback_get", on_callback)

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
command_enter = Button(frame, text="Enter", width=10, command=enter)
command_enter.pack(side=RIGHT)

frame2 = Frame(root)
frame2.pack(side=BOTTOM, fill=X)

start_button = Button(frame2, text="Start Server", command=start_server)
start_button.pack(side=RIGHT)

stop_button = Button(frame2, text="Stop Server", command=stop_server)
stop_button.pack(side=LEFT)

root.mainloop()