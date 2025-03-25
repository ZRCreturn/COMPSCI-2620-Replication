import tkinter as tk
from tkinter import messagebox
import socket
from common.protocol import Protocol
from common.utils import send_data, recv_data
from common.message import Chatmsg


class ChatClientApp:
    def __init__(self, root, host='127.0.0.1', port=5000):
        self.root = root
        self.host = host
        self.port = port
        self.client_socket = None
        self.username = None
        self.protocol = Protocol()

        self.current_screen = None

        self.login_screen()

    def login_screen(self):
        # Clear the screen
        self.clear_screen()


        self.current_screen = None 

        # Username entry
        self.username_label = tk.Label(self.root, text="Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        self.login_button = tk.Button(self.root, text="Login", command=self.handle_username)
        self.login_button.pack()

    def handle_username(self):
        username = self.username_entry.get()
        if not username:
            messagebox.showwarning("Input Error", "Username cannot be empty!")
            return
        
        self.username = username
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        
        # Phase 1: Send username for login
        send_data(self.client_socket, Protocol.REQ_LOGIN_1, username)
        
        # Receive response for username
        resp_type, resp = recv_data(self.client_socket)
        print(f"Received response: {resp_type}, {resp}")  # debugging output
        
        if resp_type == Protocol.RESP_USER_EXISTING:
            self.handle_password_screen()
        elif resp_type == Protocol.RESP_USER_NOT_EXISTING:
            self.handle_password_screen()
        else:
            messagebox.showerror("Login Error", "Unexpected response from server.")
            self.client_socket.close()


    def handle_password_screen(self):
        # Clear the screen
        self.clear_screen()

        self.current_screen = "password"

        # Password entry
        self.password_label = tk.Label(self.root, text="Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        self.submit_button = tk.Button(self.root, text="Submit", command=self.handle_password)
        self.submit_button.pack()

    def handle_password(self):
        password = self.password_entry.get()
        if not password:
            messagebox.showwarning("Input Error", "Password cannot be empty!")
            return

        # Send password for login (Phase 2)
        send_data(self.client_socket, Protocol.REQ_LOGIN_2, password)

        # Receive response for password
        resp_type, resp = recv_data(self.client_socket)
        if resp_type == Protocol.RESP_LOGIN_SUCCESS:
            self.show_user_list_screen()
        elif resp_type == Protocol.RESP_LOGIN_FAILED:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            self.client_socket.close()
        else:
            messagebox.showerror("Login Error", "Unexpected response from server.")
            self.client_socket.close()

    def show_user_list_screen(self):
        # Clear the screen
        self.clear_screen()

        self.current_screen = "user_list"

        # Request the list of users
        send_data(self.client_socket, Protocol.REQ_LIST_USERS, None)
        resp_type, resp = recv_data(self.client_socket)

        if resp_type == Protocol.RESP_LIST_USERS:
            self.users = resp
            self.display_user_list()

    def display_user_list(self):
        self.user_list_label = tk.Label(self.root, text="User List:")
        self.user_list_label.pack()

        self.user_buttons = {}
        for user, unread_count in self.users.items():
            button = tk.Button(self.root, text=f"{user} ({unread_count} unread)", 
                               command=lambda user=user: self.show_message_list_and_read(user))
            button.pack()
            self.user_buttons[user] = button
            
    def show_message_list_and_read(self, username):
        # Clear the screen
        self.clear_screen()

        self.current_screen = f"chat_{username}"

        send_data(self.client_socket, Protocol.REQ_READ_MSG, username)

        # Request the list of messages for the selected user
        send_data(self.client_socket, Protocol.REQ_LIST_MESSAGES, username)
        resp_type, resp = recv_data(self.client_socket)

        if resp_type == Protocol.RESP_LIST_MESSAGES:
            self.display_messages(resp, username)
            
    def show_message_list(self, username):
        # Clear the screen
        self.clear_screen()

        self.current_screen = f"chat_{username}"
        # Request the list of messages for the selected user
        send_data(self.client_socket, Protocol.REQ_LIST_MESSAGES, username)
        resp_type, resp = recv_data(self.client_socket)

        if resp_type == Protocol.RESP_LIST_MESSAGES:
            self.display_messages(resp, username)


    def on_message_click(self, event, messages, username):
        try:
            selected_index = self.message_listbox.curselection()[0]
            selected_message = messages[selected_index]

            if messagebox.askyesno("Delete Message", f"Do you want to delete:\n\n{selected_message.content}?"):
                self.delete_message(selected_message.id, username)
        except IndexError:
            pass 

    def display_messages(self, messages, username):
        self.chat_label = tk.Label(self.root, text=f"Chat with {username}:")
        self.chat_label.pack()

        self.message_listbox = tk.Listbox(self.root, height=10, width=50)
        self.message_listbox.pack()

        for message in messages:
            display_message = f"{message.sender}: {message.content}"
            self.message_listbox.insert(tk.END, display_message)
        
        self.message_listbox.bind("<<ListboxSelect>>", lambda event: self.on_message_click(event, messages, username))

        self.message_entry = tk.Entry(self.root)
        self.message_entry.pack()

        self.send_button = tk.Button(self.root, text="Send", command=lambda: self.send_message(username))
        self.send_button.pack()

        self.delete_button = tk.Button(self.root, text="Delete Account", command=self.delete_account)
        self.delete_button.pack()

        # Add back button
        self.back_button = tk.Button(self.root, text="Back", command=self.navigate_back)
        self.back_button.pack()
    def navigate_back(self):
        if self.current_screen == "user_list":
            self.show_user_list_screen()
        elif self.current_screen.startswith("chat_"):
            # Extract username from the screen name (e.g., "chat_user123" -> "user123")
            username = self.current_screen.split("_")[1]
            self.show_user_list_screen()

    def send_message(self, recipient):
        message = self.message_entry.get()
        if not message:
            messagebox.showwarning("Input Error", "Message cannot be empty!")
            return

        send_data(self.client_socket, Protocol.REQ_SEND_MSG, [recipient, message])

        # Refresh message list after sending the message
        self.show_message_list(recipient)

    def delete_message(self, msg_id, recipient):

        send_data(self.client_socket, Protocol.REQ_DELETE_MESSAGE, msg_id)

        # Refresh message list after sending the message
        self.show_message_list(recipient)

    def delete_account(self):
        send_data(self.client_socket, Protocol.REQ_DELETE_ACCOUNT, None)
        self.client_socket.close()
        self.root.quit()

    def clear_screen(self):
        # Clears all widgets from the current screen
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientApp(root)
    root.mainloop()
