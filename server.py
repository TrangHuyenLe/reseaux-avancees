"""
server.py - Central server script for the Random Speed-Dating Chat Application.
This script represents the server-side application, allowing multiple clients to:
- Accept incoming connections from clients.
- Pair clients randomly for chat sessions.
- Handle real-time messaging between paired clients.
- Notify clients when their partner has disconnected.
- Store conversation history in a JSON file.
Author: Le Huyen-Trang
Date: April 2025
Version: 1.0
"""
import socket
import threading
import time
import datetime
import time
from queue import Queue
import json
from threading import Lock


# Global constants
PORT = 55555
SERVER = '127.0.0.1'

# Global state
waiting_clients = []  # Clients waiting to be paired
active_pairs = {}     # Mapping from client to their partner
usernames = {}        # Mapping from socket to username
chat_history = []     # List of all chat logs
lock = Lock() # Lock for thread-safe operations
# Initialize the server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER, PORT))
server.listen(5)
print(f"Server started on {SERVER}:{PORT}. Waiting for clients to connect...")
# Function to handle incoming client connections
def handle_client(client):
    """
    Handle incoming client connections and manage their chat sessions.
    
    This function runs in a separate thread for each client. It handles the
    client's connection, pairing them with another client, and managing their
    chat session.
    
    Args:
        client (socket.socket): The client socket object.
    
    Returns:
        None
    """
    username = receive_username(client)
    if not username:
        return

    # Notify the client of successful connection
    client.send("[CONNECTED]".encode('utf-8'))
    print(f"{username} connected.")
    if client not in waiting_clients:
        # Add the client to the waiting list
        with lock:
            waiting_clients.append(client)
            print(f"{username} added to waiting list.")
    # Ensure the client is in the waiting list then wait for a partner
    while client not in waiting_clients:
        time.sleep(1)
        print(f"{username} is not in the waiting list.")
        
    wait_for_partner(client)

    # Handle client disconnection
    handle_client_disconnection(client, username)
def receive_username(client):
    """Receives and validates the username from the client."""
    try:
        message = client.recv(1024).decode('utf-8')
        if message.startswith("[USERNAME]"):
            username = message.split("[USERNAME]")[1]
            usernames[client] = username
            print(f"Username received: {username}")
            return username
        else:
            print(f"Invalid username format from {client}.")
            client.send("[INVALID_USERNAME]".encode('utf-8'))
            client.close()
            return None
    except Exception as e:
        print(f"Error receiving username: {e}")
        client.close()
        return None

def wait_for_partner(client):
    """
    Waits for a partner to be available for the client.

    This function checks if there are any clients in the waiting list.
    If a partner is found, it pairs them and starts a chat session.
    If no partner is found, it keeps the client in the waiting list.

    Args:
        client (socket.socket): The client socket object.

    Returns:
        None
    """
    while True:
        # Check if the client in the active pairs
        if len(waiting_clients) > 1 and client not in active_pairs:
            partner = waiting_clients.pop(0)
            if partner and partner != client:
                pair_clients(client, partner)
                break
                # Check if the client is still in the waiting list and not having a partner
            else:
                # No partner found, wait for a while before checking again
                time.sleep(10)
                print(f"{usernames.get(client, 'Unknown')} is waiting for a partner...")
                client.send("[NO_PARTNER_FOUND]".encode('utf-8'))
def handle_client_disconnection(client, username):
    """Handles client disconnection and any associated errors."""
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == "[DISCONNECTED]":
                print(f"{username} disconnected.")
                break
            elif message == "[HELP]":
                client.send("[HELP]".encode('utf-8'))
            else:
                # Save chat history
                chat_history.append({"user": username, "message": message})
        except Exception as e:
            print(f"Error handling client {username}: {e}")
            cleanup_client(client)
            break
    
def cleanup_client(client):
    """
    Cleans up client resources, removes them from active lists, and notifies their partner.

    This function ensures that when a client disconnects (either intentionally or due to an error),
    they are properly removed from the `waiting_clients` list and `active_pairs` dictionary.
    If the client was actively paired with someone, their partner is notified of the disconnection.

    Args:
        client (socket.socket): The socket object of the client to be cleaned up.
    """
    try:
        username = usernames.get(client, "Unknown")

        # Remove client from waiting clients if present
        if client in waiting_clients:
            waiting_clients.remove(client)

        # Handle active pair disconnection
        if client in active_pairs:
            partner = active_pairs.pop(client)
            try:
                partner.send("[PARTNER_LEFT]".encode('utf-8'))
                print(f"Notified {usernames.get(partner, 'Unknown')} of disconnection.")
            except Exception as e:
                print(f"Error notifying partner: {e}")
                # Optionally, handle the partner's disconnection as well
                cleanup_client(partner)  # Recursive call if needed
        elif any(client == v for v in active_pairs.values()):
            # Find the client that has client as a value
            partner = next(k for k, v in active_pairs.items() if v == client)
            del active_pairs[partner]
            try:
                partner.send("[PARTNER_LEFT]".encode('utf-8'))
                print(f"Notified {usernames.get(partner, 'Unknown')} of disconnection.")
            except Exception as e:
                print(f"Error notifying partner: {e}")
                # Optionally, handle the partner's disconnection as well
                cleanup_client(partner)  # Recursive call if needed

    except Exception as e:
        print(f"Error during cleanup: {e}")
    finally:
        try:
            client.close()
            print(f"Connection with {username} closed.")
        except Exception:
            print("Client already closed")

def pair_clients(client1, client2):
    """
    Pairs two clients for a chat session and starts a dedicated message handling thread.

    This function establishes a chat session between two clients by:
    1. Sending a "[CHAT_FOUND]" notification to both clients.
    2. Adding both clients to the `active_pairs` dictionary, mapping each client to their partner.
    3. Starting a new thread that executes the `handle_messages` function, responsible for
       relaying messages between the paired clients.

    Args:
        client1 (socket.socket): The socket object of the first client.
        client2 (socket.socket): The socket object of the second client.
    """
    try:
        # Notify clients that a chat partner has been found
        client1.send("[CHAT_FOUND]".encode('utf-8'))
        client2.send("[CHAT_FOUND]".encode('utf-8'))
        
        # Remove clients from waiting list
        if client1 in waiting_clients:
            waiting_clients.remove(client1)
        if client2 in waiting_clients:
            waiting_clients.remove(client2)
        
        # Update active pairs
        active_pairs[client1] = client2
        active_pairs[client2] = client1

        print(f"Paired clients: {usernames.get(client1, 'Unknown')} and {usernames.get(client2, 'Unknown')}")

        # Start a new thread to handle messages between the clients
        threading.Thread(target=handle_messages, args=(client1, client2), daemon=True).start()
        print(f"Started message handling thread for {usernames.get(client1, 'Unknown')} and {usernames.get(client2, 'Unknown')}")
        # # Start the message handling function
        # handle_messages(client1, client2)
    except Exception as e:
        print(f"Error pairing clients: {e}")
        cleanup_client(client1)
        cleanup_client(client2)

def handle_messages(client1, client2):
    """
    Handles real-time message exchange between two paired clients.

    This function continuously listens for incoming messages from both clients.
    When a message is received from one client, it is relayed to the other client.
    If a client disconnects, the other client is notified, and the function terminates.

    Args:
        client1 (socket.socket): The socket object of the first client.
        client2 (socket.socket): The socket object of the second client.
    """
    try:
        while True:
            # Receive message from client1
            try:
                message = client1.recv(1024).decode('utf-8')
            except Exception:
                message = "[DISCONNECTED]"
            # Check for disconnection or special commands    
            if message == "[DISCONNECTED]":
                print(f"Client {usernames.get(client1)} disconnected.")
                client2.send("[PARTNER_DISCONNECTED]".encode('utf-8'))
                break
            elif message == "[HELP]":
                client1.send("[HELP]".encode('utf-8'))
            else:
                # Relay the message to client2
                client2.send(message.encode('utf-8'))
                # Save chat history
                chat_history.append({"user": usernames.get(client1), "message": message})
                # Print the message to the server console
                print(f"{message}")

            # Receive message from client2
            try:
                message = client2.recv(1024).decode('utf-8')
            except Exception:
                message = "[DISCONNECTED]"

            if message == "[DISCONNECTED]":
                print(f"Client {usernames.get(client2)} disconnected.")
                client1.send("[PARTNER_DISCONNECTED]".encode('utf-8'))
                break
            elif message == "[HELP]":
                client2.send("[HELP]".encode('utf-8'))
            else:
                # Relay the message to client1
                client1.send(message.encode('utf-8'))
                # Save chat history
                chat_history.append({"user": usernames.get(client2), "message": message})
                # Print the message to the server console
                print(f"{message}")

    except Exception as e:
        print(f"Error handling messages: {e}")
    finally:
        # Save chat log when the session ends
        pair_user1 = usernames.get(client1, "Unknown")
        pair_user2 = usernames.get(client2, "Unknown")
        messages = chat_history
        # Save chat log to JSON file
        save_chat_log(pair_user1, pair_user2, messages)
        # Notify history has been saved
        print(f"Chat log saved for {pair_user1} and {pair_user2}.")
        # Cleanup clients after the chat session ends
        cleanup_client(client1)
        cleanup_client(client2)
        print("Chat session ended.")

def save_chat_log(pair_user1, pair_user2, messages):
    """
    Saves the chat log of a conversation between two users to a JSON file.

    The chat log includes the usernames of both participants, a timestamp of when the
    conversation occurred, and a list of messages exchanged.  Each chat log is
    appended as a new line in the "chat_logs.json" file.

    Args:
        pair_user1 (str): The username of the first user in the chat.
        pair_user2 (str): The username of the second user in the chat.
        messages (list): A list of strings, where each string is a message
                         exchanged between the two users.
    """
    chat_log = {
        "user1": pair_user1,
        "user2": pair_user2,
        "timestamp": datetime.datetime.now().isoformat(),
        "messages": messages
    }
    try:
        with open("history/chat_logs.json", "a") as f:
            json.dump(chat_log, f)
            f.write("\n")  # Add a newline to separate JSON objects
        print(f"Chat log saved for {pair_user1} and {pair_user2}.")
    except Exception as e:
        print(f"Error saving chat log: {e}")

def start_server():
    """
    Starts the server, listens for incoming connections, and spawns threads to handle clients.

    This function performs the following steps:
    1. Creates a socket and binds it to the specified host and port.
    2. Listens for incoming connection requests.
    3. Enters a loop that continuously accepts new client connections.
    4. For each new connection, it creates a new thread that executes the
       `handle_client` function, passing the client's socket object as an argument.
    """
    try:
        while True:
            client, address = server.accept()
            print(f"Connection established with {address}.")
            threading.Thread(target=handle_client, args=(client,)).start()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    except Exception as e:
        print(f"Error starting server: {e}")
    finally:
        server.close()
        print("Server closed.")

if __name__ == "__main__":
    start_server()