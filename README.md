# 🗨️ Speed-Dating Chat App  
**Client-Server Python Application**

A lightweight **random chat matching system** using **Python socket programming** with a **client-server architecture**. This app randomly connects two users in a private 1-on-1 chat session.

> Mini-project in Network Programming  
> Université Paris-Saclay – 2025

---

## 📌 Overview

This application is composed of:

- **🔗 Central Server**: Accepts client connections, randomly pairs users, and forwards messages between them.
- **💬 Multiple Clients**: Each client connects to the server and waits to be paired with another for a private real-time chat.

---

## ⚙️ How It Works

```
[Client 1]                         [Client 2]
     |                                |
     |------ Connect to Server ------>|
     |                                |
     |         [   SERVER   ]         |
     |<------ Paired Randomly ------->|
     |                                |
     |<----------- Chat ------------->|
     |                                |
     |---------- Exit --------------->|
     |                                |
     |        Client Disconnected     |
```

---

## 🧩 Requirements

- Python **3.6+**
- ✅ No external libraries needed (pure Python)
  
---

## 🖥️ Setup & Execution

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/speed-dating-chat.git
cd speed-dating-chat
```

### 2. (Optional) Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Start the Server

```bash
python3 server.py
```

### 4. Run the Client (in a different terminal or machine)

```bash
python3 client.py
```

> ✅ Run at least 2 clients (2 client terminals) to test the chat functionality.

---

## 💬 How to Use

- When you run the client, it waits to be paired with another user.
- Once paired, you can chat directly.
- To leave the session or see commands:

| Command  | Description                       |
|----------|-----------------------------------|
| `/exit`  | Leave the current chat session    |
| `/help`  | Show list of available commands   |


## 📁 Project Structure

```
speed-dating-chat/
├── client.py        # Client-side script
├── server.py        # Server-side script
├── README.md        # This documentation
└── history/         # Saved chat logs
```

---

## 📚 Resources

- [Python socket — Official Docs](https://docs.python.org/3/library/socket.html)
- [Threading in Python – Real Python](https://realpython.com/intro-to-python-threading/)
- [YouTube: Python Socket Tutorial](https://youtu.be/3QiPPX-KeSc)
- Lecture guidance and materials from Prof. Guillaume Béduneau (Université d'Évry)

---

## 👩‍💻 Author

**Lê Huyền Trang**  
Master 1 – Computer Networks  
Université Paris-Saclay, 2024–2025  
📧 huyen.le@etud.univ-evry.fr

---

## 📦 Submission Info

- **File to submit**: `speed-dating-chat.tar.gz`
- **Contents**: `client.py`, `server.py`, `README.md`, `history/` (optional)
- **Submit to**: guillaume.beduneau@univ-evry.fr  
- **Deadline**: Monday, April 7th, before 10h