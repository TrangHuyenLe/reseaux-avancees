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
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message == "[CHAT_FOUND]":
                print("You have been paired with another user. Start chatting!")
            elif message == "[PARTNER_LEFT]":
                print("Your chat partner has left the chat.")
            else:
                print(f"{message}")
        except Exception as e:
            print(f"Error receiving message: {e}")
            client_socket.close()
            break
        except KeyboardInterrupt:
            print("\nExiting chat...")
            client_socket.close()
            break

def handle_server_response():
    """
    Receives and handles messages from the server during the pairing phase.

    Returns:
        bool: True if a partner is found, False otherwise.
    """
    try:
        message = client_socket.recv(1024).decode('utf-8')
        if message == "[CHAT_FOUND]":
            print("You have been paired with another user. Start chatting!")
            return True
        elif message == "[NO_PARTNER_FOUND]":
            print("No partner found. Please wait, don't send messages yet.")
            return False
        elif message == "[DISCONNECTED]":
            print("You have been disconnected from the server.")
            client_socket.close()
            return False
        elif message == "[PARTNER_LEFT]":
            print("Your chat partner has left the chat.")
            client_socket.close()
            return False
    except Exception as e:
        print(f"Error receiving message: {e}")
        client_socket.close()
        return False
    except KeyboardInterrupt:
        print("\nExiting chat...")
        client_socket.close()
        return False
    return False

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

    # Wait for the other user to join
    print("Waiting for a partner to join...")
    partner_found = False
    while not partner_found:
        partner_found = handle_server_response()
        print(partner_found)
        if partner_found == True:
            break
        
    # Now the user can send messages
    print("You can start sending messages now. Type '/exit' to leave the chat.")
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

    Returns:
        None
    """
    print("Connected to the server. Waiting for a partner...")
    print("Type '/exit' to leave the chat.")
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