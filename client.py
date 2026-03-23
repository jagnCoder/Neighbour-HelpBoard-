import socket

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('127.0.0.1', 65432))
        # Receive welcome
        welcome = client.recv(1024).decode()
        print(welcome, end='')
        username = input()
        client.send(username.encode())
        # Receive connected message
        connected = client.recv(1024).decode()
        print(connected, end='')
        print("Type HELP for commands.")
        while True:
            cmd = input("> ")
            if cmd.upper() == 'HELP':
                print("Commands:")
                print("POST <type> <message> - Post a message")
                print("LIST [type] - List posts")
                print("GET <id> - Get post by id")
                print("EXIT - Disconnect")
                print("SHUTDOWN <token> - Shutdown server")
                continue
            client.send(cmd.encode())
            response = client.recv(1024).decode()
            print(response, end='')
            if cmd.upper() == 'EXIT':
                break
    except ConnectionRefusedError:
        print("Could not connect to server. Is it running?")
    except ConnectionAbortedError as e:
        print("Connection aborted by server:", e)
    finally:
        client.close()

if __name__ == "__main__":
    main()