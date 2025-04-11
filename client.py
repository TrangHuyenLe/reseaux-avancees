"""
client.py – Client-side script for the Random Speed-Dating Chat Application.

This script represents the client application, allowing a user to:
- Connect to a central server.
- Wait for a random pairing with another user.
- Engage in private real-time messaging.
- Exit the chat gracefully and return to idle state.

Author: Le Huyen-Trang
Date: April 2025
Version: 1.0
"""

import socket
import threading

# Global constants
PORT = 55555
SERVER = '127.0.0.1'

# Initialize the client socket
username = input("Enter your username: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER, PORT))

def receive_messages():
    """
    Receive and handle incoming messages from the server.

    This function runs in a separate thread, constantly listening for messages
    from the server and printing them to the user's console.

    Message types handled:
    - "[CHAT_FOUND]": Notifies that a partner has been found.
    - "[PARTNER_LEFT]": Informs that the chat partner has disconnected.
    - Regular text messages from the partner.

    Args:
        None
    Returns:
        None
    """
    partner_found = False
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message == "[CHAT_FOUND]":
                print("You're allowed to type message now!")
                partner_found = True
            elif message == "[PARTNER_LEFT]":
                print("Your chat partner has left the chat. Trying to find a new partner...")
                partner_found = False
            elif partner_found:
                print(f"{message}")
                partner_found = True
            elif message == "[DISCONNECTED]":
                print("Disconnected from the server.")
                partner_found = False
                client_socket.close()
                break
            else:
                print(f"Unknown message: {message}")
                partner_found = False
        except Exception as e:
            partner_found = False
            print(f"Error receiving message: {e}")
            client_socket.close()
            break
        except KeyboardInterrupt:
            partner_found = False
            print("\nExiting chat...")
            client_socket.close()
            break

def send_messages():
    """
    Sends a message to the server, encoding it in UTF-8.

    Args:
        message (str): The message to send.

    Returns:
        None
    """
    # Sending first message to the server with the username
    client_socket.send(f"[USERNAME]{username}".encode('utf-8'))
    # Loop to send messages until the user exits
    while True:
        try:
            message = input()
            if message.lower() == '/exit':
                print("Exiting chat...")
                client_socket.send("[DISCONNECTED]".encode('utf-8'))
                client_socket.close()
                break
            elif message.lower() == '/help':
                client_socket.send("[HELP]".encode('utf-8'))
                print("Available commands: /exit - Leave chat, /help - Show this message")
            elif message.startswith('/history'):
                client_socket.send("[HISTORY]".encode('utf-8'))
                print("Fetching chat history in the previous sessions.")
            else:
                client_socket.send(f"{username}: {message}".encode('utf-8'))
                print(f"{username}: {message}")
        except Exception as e:
            print(f"Error sending message: {e}")
            client_socket.close()
            break
        except KeyboardInterrupt:
            print("\nExiting chat...")
            client_socket.close()
            break
def start_client():
    """
    Initialize and run the client-side application.

    This function establishes a connection to the central server,
    starts a background thread for receiving messages, and handles
    user input in the main thread. Users can send messages or exit the chat
    using commands.

    Commands:
    - /exit : Leaves the chat session.
    - /help : Displays available commands.
    - /history : Fetches chat history from previous sessions.

    Returns:
        None
    """
    print("Connected to the server. Waiting for a partner...")
    print("Type '/exit' to leave the chat.")
    print("Type '/history' to fetch chat history.")
    print("Type '/help' for available commands.")
    # Start the threads for receiving and sending messages
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()
    send_thread = threading.Thread(target=send_messages)
    send_thread.start()
    # Wait for threads to finish
    receive_thread.join()
    send_thread.join()
    # Close the client socket
    client_socket.close()
    print("Client socket closed. Exiting program.")
if __name__ == "__main__":
    start_client()