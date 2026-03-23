# Neighborhood Helpboard

A simple TCP client-server application for neighborhood communication using Python's standard library.

## Purpose

This project demonstrates basic TCP networking with a multi-threaded server that handles multiple clients concurrently. It provides a helpboard where users can post messages of different types (errand, offer, alert) and retrieve them.

## Prerequisites

- Python 3.8 or higher

## How to Run

1. Start the server in one terminal:

   `python server.py`

2. Start one or more clients in other terminals:

   `python client.py`

## Example Session

### Server Terminal

```
Server listening on 127.0.0.1:65432
Client ('127.0.0.1', 54321) connected as Alice
New post by Alice: errand - Buy groceries
Client ('127.0.0.1', 54321) disconnected
```

### Client Terminal

```
Welcome to Neighborhood Helpboard!
Enter your username: Alice
Connected. Type HELP for commands.
Type HELP for commands.
> POST errand Buy groceries
Post added.
> LIST
1: errand by Alice at Mon Mar 23 12:00:00 2026
> GET 1
ID: 1
Username: Alice
Type: errand
Message: Buy groceries
Timestamp: Mon Mar 23 12:00:00 2026
> EXIT
Goodbye!
```

## Notes

- The server handles graceful shutdown on KeyboardInterrupt (Ctrl+C) or SHUTDOWN command with correct token.
- No encryption; for demonstration only.
- Posts are persisted to data.json.
- Suggested improvements: Add authentication, encryption, database storage, web interface.