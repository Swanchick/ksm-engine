from server import InstanceManager, ServerOutput, ServerInstance, ServerState
from tkinter import *
from typing import Optional, List


instance_manager = InstanceManager()
instance_manager.start()
instance_manager.load_instances()

current_instance: Optional[ServerInstance] = None

instances: List[ServerInstance] = []


def select_instance(new_instance: ServerInstance):
    print(new_instance.name)

    global current_instance

    for i in instance_manager.instances:
        i.unregister_all_callbacks()

    current_instance = new_instance

    command_entry.delete(0, END)
    output_text.configure(state='normal')
    output_text.delete("1.0", END)
    output_text.configure(state='disabled')

    current_instance.register_callback("on_output_get", output_get)

    label.config(text=current_instance.name)


def enter_command(event):
    command = command_entry.get()
    command_entry.delete(0, END)
    command_entry.insert(0, "")


def output_get(output: ServerOutput):
    output_text.configure(state='normal')
    output_text.insert(END, output.message)
    output_text.configure(state='disabled')


def start_server():
    if not current_instance:
        return

    if current_instance.server_state == ServerState.START:
        return

    current_instance.start()


def stop_server():
    if current_instance.server_state == ServerState.STOP:
        return

    current_instance.stop()


def create_button(instance: ServerInstance, panel):
    def on_click():
        select_instance(instance)

    return Button(panel, width=30, text=instance.name, command=on_click)


root = Tk()
root.title("Kyryls Server Manager")
root.geometry("800x600")

frame_instances = Frame(root)
frame_instances.pack(side=LEFT, fill=Y)

for k, instance in enumerate(instance_manager.instances):
    but = create_button(instance, frame_instances)
    but.pack(side=TOP, fill=X)

frame_instance = Frame(root)
frame_instance.pack(side=RIGHT, fill=BOTH)

label = Label(frame_instance, text="No server", width=105)
label.pack(fill=X)

output_text = Text(frame_instance, state='disabled')
output_text.pack(side=TOP, fill=BOTH)

command_entry = Entry(frame_instance)
command_entry.bind("<Return>", enter_command)
command_entry.pack(side=TOP, fill=X)

stop_server_button = Button(frame_instance, text="Stop server", command=stop_server)
stop_server_button.pack(side=BOTTOM, fill=X)

start_server_button = Button(frame_instance, text="Start server", command=start_server)
start_server_button.pack(side=BOTTOM, fill=X)

root.mainloop()
