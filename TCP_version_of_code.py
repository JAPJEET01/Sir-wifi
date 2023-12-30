import pyaudio
import socket
import threading

# Constants
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
TCP_IP = "192.168.29.90"  # Change this to your IP address
TCP_PORT_START = 12347
MAX_CONNECTIONS = 4

# Audio stream setup
audio = pyaudio.PyAudio()

# Function to handle incoming connections and receive audio
def receive_audio(conn, addr):
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    try:
        while True:
            data = conn.recv(CHUNK)
            if not data:
                break
            stream.write(data)
    except Exception as e:
        print(f"Receive Audio Error from {addr}: {e}")
    finally:
        conn.close()
        stream.stop_stream()
        stream.close()

# Create TCP server socket to accept incoming connections
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((TCP_IP, TCP_PORT_START))
server_socket.listen(MAX_CONNECTIONS)

# Function to handle connections and start receiving audio
def accept_connections():
    connections = []
    try:
        while True:
            conn, addr = server_socket.accept()
            print(f"Connected to {addr}")
            connections.append(conn)
            if len(connections) <= MAX_CONNECTIONS:
                recv_thread = threading.Thread(target=receive_audio, args=(conn, addr))
                recv_thread.daemon = True
                recv_thread.start()
    except KeyboardInterrupt:
        print("Keyboard Interrupt detected. Exiting...")
    finally:
        for conn in connections:
            conn.close()
        server_socket.close()
        audio.terminate()

# Start a thread to handle incoming connections
accept_thread = threading.Thread(target=accept_connections)
accept_thread.daemon = True
accept_thread.start()

# Function to send audio to connected clients
def send_audio(stream, dest_ip, dest_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((dest_ip, dest_port))
        while True:
            data = stream.read(CHUNK)
            client_socket.sendall(data)
    except Exception as e:
        print(f"Send Audio Error to {dest_ip}:{dest_port}: {e}")
    finally:
        client_socket.close()

# Create audio streams for sending to clients
streams = []
for i in range(MAX_CONNECTIONS):
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    streams.append(stream)

# Assuming all users are on the same network with their IP addresses
destinations = [("192.168.1.102", 12345), ("127.0.0.1", 12347), ("127.0.0.1", 12348), ("127.0.0.1", 12349)]

send_threads = []
for i in range(MAX_CONNECTIONS):
    send_thread = threading.Thread(target=send_audio, args=(streams[i], destinations[i][0], destinations[i][1]))
    send_thread.daemon = True
    send_thread.start()
    send_threads.append(send_thread)

# Keep the main thread alive
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Keyboard Interrupt detected. Exiting...")
finally:
    audio.terminate()
