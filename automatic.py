import subprocess
import time

def run_python_file(file_name):
    while True:
        try:
            process = subprocess.Popen(["python", file_name])
            time.sleep(2)  # Wait for 2 seconds
            process.terminate()  # Terminate the process
        except KeyboardInterrupt:
            print("Terminating the program.")
            break

if __name__ == "__main__":
    python_file = "restart.py"  # Replace this with your Python file name
    run_python_file(python_file)
