import javax.sound.sampled.*;
import java.io.IOException;
import java.net.*;

public class AudioStreamer {

    // Constants
    private static final AudioFormat FORMAT = new AudioFormat(44100, 16, 1, true, false);
    private static final int CHUNK = 1024;
    private static final int MAX_CONNECTIONS = 4;

    // Audio stream setup
    private static final TargetDataLine microphone;
    private static final SourceDataLine[] speakers;
    private static final InetAddress[] destinations;
    private static final int[] ports;
    private static DatagramSocket socket;

    static {
        try {
            microphone = AudioSystem.getTargetDataLine(FORMAT);
            microphone.open(FORMAT);
            microphone.start();

            speakers = new SourceDataLine[MAX_CONNECTIONS];
            for (int i = 0; i < MAX_CONNECTIONS; i++) {
                speakers[i] = AudioSystem.getSourceDataLine(FORMAT);
                speakers[i].open(FORMAT);
                speakers[i].start();
            }

            destinations = new InetAddress[]{
                    InetAddress.getByName("192.168.1.102"),
                    InetAddress.getByName("127.0.0.1"),
                    InetAddress.getByName("127.0.0.1"),
                    InetAddress.getByName("127.0.0.1")
            };

            ports = new int[]{12345, 12347, 12348, 12349};

            socket = new DatagramSocket();
        } catch (LineUnavailableException | UnknownHostException | SocketException e) {
            throw new RuntimeException("Initialization failed: " + e.getMessage());
        }
    }

    // Function to receive audio
    private static void receiveAudio() {
        try {
            byte[] buffer = new byte[CHUNK * FORMAT.getFrameSize()];
            DatagramPacket packet = new DatagramPacket(buffer, buffer.length);

            while (true) {
                socket.receive(packet);
                for (int i = 0; i < MAX_CONNECTIONS; i++) {
                    if (packet.getAddress().equals(destinations[i]) && packet.getPort() == ports[i]) {
                        speakers[i].write(packet.getData(), 0, packet.getData().length);
                        break;
                    }
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // Function to send audio
    private static void sendAudio(int index) {
        try {
            byte[] buffer = new byte[CHUNK * FORMAT.getFrameSize()];
            DatagramPacket packet;

            while (true) {
                int bytesRead = microphone.read(buffer, 0, buffer.length);
                packet = new DatagramPacket(buffer, bytesRead, destinations[index], ports[index]);
                socket.send(packet);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        // Create threads for sending and receiving audio
        Thread receiveThread = new Thread(AudioStreamer::receiveAudio);
        receiveThread.setDaemon(true);
        receiveThread.start();

        Thread[] sendThreads = new Thread[MAX_CONNECTIONS];
        for (int i = 0; i < MAX_CONNECTIONS; i++) {
            final int index = i;
            sendThreads[i] = new Thread(() -> sendAudio(index));
            sendThreads[i].setDaemon(true);
            sendThreads[i].start();
        }

        // Keep the main thread alive
        while (true) {
            // Your application's main logic here
        }
    }
}
