import subprocess
import shlex

if __name__ == "__main__":
    cmd = shlex.split("pip install -r requirements.txt")
    proc = subprocess.Popen(cmd)
    proc.wait()