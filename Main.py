import customtkinter as ctk
from tkinter import messagebox, END, INSERT
import RemoteAccessServer
import threading


class SSHClientApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.ssh_thread = None
        self.text_area = None
        self.Exit_button = None
        self.Connect_button = None
        self.password = None
        self.username = None
        self.port_key = None
        self.Host_key = None
        self.iconbitmap("PuTTY.ico")
        self.title("RemoteAccessServer")
        self.geometry("750x700")
        self.resizable(width=False, height=False)
        self.current_input = ""
        self.input_start = "0.0"

        self.createWidgets()

    def createWidgets(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(self, text="HostName =").grid(row=0, column=0, pady=10, padx=10, sticky="e")
        self.Host_key = ctk.CTkEntry(self, width=200)
        self.Host_key.grid(row=0, column=1, pady=10, padx=10, sticky="ew")

        ctk.CTkLabel(self, text="Port =").grid(row=1, column=0, pady=10, padx=10, sticky="e")
        self.port_key = ctk.CTkEntry(self, width=100)
        self.port_key.grid(row=1, column=1, pady=10, padx=10, sticky="w")
        self.port_key.insert(0, "22")  # Default port

        ctk.CTkLabel(self, text="username =").grid(row=2, column=0, pady=10, padx=10, sticky="e")
        self.username = ctk.CTkEntry(self, width=200)
        self.username.grid(row=2, column=1, pady=10, padx=10, sticky="ew")

        ctk.CTkLabel(self, text="Password =").grid(row=3, column=0, pady=10, padx=10, sticky="e")
        self.password = ctk.CTkEntry(self, width=200, show="*")
        self.password.grid(row=3, column=1, pady=10, padx=10, sticky="ew")

        self.Connect_button = ctk.CTkButton(self, text="Connect", command=self.connect)
        self.Connect_button.grid(row=4, column=0, pady=10, padx=10)

        self.Exit_button = ctk.CTkButton(self, text="Exit", command=self.ExitButton, fg_color="red",
                                         hover_color="dark red")
        self.Exit_button.grid(row=4, column=1, pady=10, padx=10)

        self.text_area = ctk.CTkTextbox(self, wrap="word", width=300, height=400)
        self.text_area.grid(row=5, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")
        self.text_area.bind("<Key>", self.on_key_press)

    def ExitButton(self):
        if messagebox.askokcancel("Quit", "Do you want to Quit?"):
            if RemoteAccessServer.ssh_client:
                RemoteAccessServer.ssh_client.close()
            self.quit()
            self.destroy()

    def connect(self):
        host = self.Host_key.get()
        port = self.port_key.get()
        username = self.username.get()
        password = self.password.get()

        if not host or not port or not username or not password:
            messagebox.showerror("Input Error", "All fields are required.")
            return
        try:
            port = int(port)
        except ValueError:
            messagebox.showerror("Input Error", "Port number must be an integer.")
            return

        self.ssh_thread = threading.Thread(target=self.ssh_connect_thread, args=(host, port, username, password))
        self.ssh_thread.start()

    def ssh_connect_thread(self, host, port, username, password):
        success, message = RemoteAccessServer.SSH_Connect(host, port, username, password)
        if success:
            self.after(0, self.update_text_area, message)
            self.after(0, self.show_prompt)
        else:
            self.after(0, messagebox.showerror, "Connection Error", message)

    def on_key_press(self, event):
        if event.keysym == "Return":
            command = self.current_input.strip()
            self.text_area.insert(END, "\n")
            threading.Thread(target=self.execute_command, args=(command,)).start()
            self.current_input = ""
            return "break"
        elif event.keysym == "BackSpace":
            if self.text_area.index(INSERT) > self.input_start:
                self.text_area.delete("insert-1c")
                self.current_input = self.current_input[:-1]
            return "break"
        elif event.keysym in ("Left", "Right", "Up", "Down"):
            return "break"
        else:
            self.current_input += event.char

    def execute_command(self, command):
        if command == "clear":
            self.text_area.delete("1.0", END)
            self.after(0, self.show_prompt)
        else:
            success, output = RemoteAccessServer.ExecutingCommands(command)
            self.after(0, self.update_text_area, output)
            if command != "exit":
                self.after(0, self.show_prompt)
            else:
                self.after(0, self.update_text_area, "SSH connection closed.")

    def update_text_area(self, text):
        self.text_area.insert(END, text + "\n")
        self.text_area.see(END)

    def show_prompt(self):
        prompt = RemoteAccessServer.get_prompt()
        self.text_area.insert(END, prompt)
        self.text_area.see(END)
        self.input_start = self.text_area.index(INSERT)


if __name__ == "__main__":
    app = SSHClientApp()
    app.mainloop()
