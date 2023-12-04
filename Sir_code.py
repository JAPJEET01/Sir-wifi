import pyaudio
import socket
import threading
import time

# Constants
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
UDP_IP = "127.0.0.1"  # Change this to your IP address
UDP_PORT = 12345
MAX_CONNECTIONS = 4

# Audio stream setup
audio = pyaudio.PyAudio()

# Function to receive audio
def receive_audio():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    streams = {}
    while True:
        data, addr = sock.recvfrom(CHUNK * CHANNELS * 2)
        if addr not in streams:
            streams[addr] = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

        streams[addr].write(data)

# Function to send audio
def send_audio(stream, addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        data = stream.read(CHUNK)
        sock.sendto(data, addr)

# Create threads for sending and receiving audio
receive_thread = threading.Thread(target=receive_audio)
receive_thread.daemon = True
receive_thread.start()

streams = []
for i in range(MAX_CONNECTIONS):
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    streams.append(stream)

# Assuming all users are on the same network with their IP addresses
destinations = [("127.0.0.1", 12346), ("127.0.0.1", 12347), ("127.0.0.1", 12348), ("127.0.0.1", 12349)]

send_threads = []
for i in range(MAX_CONNECTIONS):
    send_thread = threading.Thread(target=send_audio, args=(streams[i], destinations[i]))
    send_thread.daemon = True
    send_thread.start()
    send_threads.append(send_thread)

# Keep the main thread alive and rerun the script every 5 seconds
while True:
    time.sleep(5)
    # Close existing audio streams and sockets before restarting
    for stream in streams:
        stream.stop_stream()
        stream.close()
    audio.terminate()
    # Restart the script
    exec(open(__file__).read())
