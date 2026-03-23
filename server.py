import socket
import threading
import json
import time
import os

ADMIN_TOKEN = "admin123"  # Change this for security

posts = []
post_id = 1

def load_posts():
    global posts, post_id
    if os.path.exists('data.json'):
        try:
            with open('data.json', 'r') as f:
                posts = json.load(f)
                if posts:
                    post_id = max(p['id'] for p in posts) + 1
        except json.JSONDecodeError:
            print("Error loading data.json, starting fresh")

def save_posts():
    with open('data.json', 'w') as f:
        json.dump(posts, f, indent=2)

def handle_client(conn, addr):
    username = None
    try:
        conn.send(b"Welcome to Neighborhood Helpboard!\nEnter your username: ")
        username_data = conn.recv(1024).decode().strip()
        if not username_data:
            return
        username = username_data
        print(f"Client {addr} connected as {username}")
        conn.send(b"Connected. Type HELP for commands.\n")
        while True:
            data = conn.recv(1024).decode().strip()
            if not data:
                break
            parts = data.split()
            if not parts:
                continue
            cmd = parts[0].upper()
            if cmd == "POST":
                if len(parts) < 3:
                    conn.send(b"Usage: POST <type> <message>\n")
                    continue
                post_id = len(posts) + 1
                type_ = parts[1]
                message = ' '.join(parts[2:])
                post = {
                    'id': post_id,
                    'username': username,
                    'type': type_,
                    'message': message,
                    'timestamp': time.time()
                }
                posts.append(post)
                if len(posts) > 50:
                    posts.pop(0)
                post_id += 1
                save_posts()
                conn.send(b"~~~Post added~~~\n")
                print(f"New post by {username}: {type_} - {message}")
            elif cmd == "LIST":
                type_filter = parts[1] if len(parts) > 1 else None
                filtered = [p for p in posts if not type_filter or p['type'] == type_filter]
                recent = filtered[-10:]  # last 10
                if not recent:
                    response = "~~~No posts found~~~\n"
                else:
                    response = "\n".join(f"{p['id']}: {p['type']} by {p['username']} at {time.ctime(p['timestamp'])}" for p in recent) + "\n"
                conn.send(response.encode())
            elif cmd == "GET":
                if len(parts) < 2:
                    conn.send(b"Usage: GET <id>\n")
                    continue
                try:
                    id_ = int(parts[1])
                    post = next((p for p in posts if p['id'] == id_), None)
                    if post:
                        response ="="*50 + "\n" + f"ID: {post['id']}\nUsername: {post['username']}\nType: {post['type']}\nMessage: {post['message']}\nTimestamp: {time.ctime(post['timestamp'])}\n"+ "\n" + "="*50
                    else:
                        response = "~~~Post not found~~~\n"
                    conn.send(response.encode())
                except ValueError:
                    conn.send(b"Invalid ID.\n")
            elif cmd == "EXIT":
                conn.send(b"~~~Goodbye!~~~\n")
                break
            elif cmd == "SHUTDOWN":
                if len(parts) < 2 or parts[1] != ADMIN_TOKEN:
                    conn.send(b"Invalid token.\n")
                    continue
                conn.send(b"~~~Server shutting down~~~\n")
                print("~~~Shutdown command received~~~")
                os._exit(0)
            elif cmd == "HELP":
                help_text = """Available commands:
POST <type> <message> - Post a new message
LIST [type] - List recent posts (optional filter by type)
GET <id> - Get full post by ID
EXIT - Disconnect from server
SHUTDOWN <token> - Shutdown server (admin only)
"""
                conn.send(help_text.encode())
            else:
                conn.send(b"Unknown command. Type HELP for help.\n")
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        conn.close()
        print(f"Client {addr} disconnected")

def main():
    load_posts()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 65432))
    server.listen(5)
    print("Server listening on 127.0.0.1:65432")
    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("~~~Server shutting down~~~")
    finally:
        server.close()
        save_posts()

if __name__ == "__main__":
    main()