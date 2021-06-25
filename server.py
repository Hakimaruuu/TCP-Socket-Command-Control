import socket
import threading  # menggunakan threading
from queue import Queue

# konstanta untuk thread
threads = 2     # ada 2 thread
no_job = [1, 2]     # ada job 1, ada job 2
queue = Queue()

# menyimpan conn, addr dan flag
all_conn = []
all_addr = []
flag = []

# mengkoneksikan dua komputer


def buat_soket():
    try:
        global host
        global port
        global s
        host = ""
        port = 8082
        s = socket.socket()
    except socket.error as msg:
        print('Error socket ', str(msg))

# menghubungkan antar soket dan looping listening


def hubung_socket():
    try:
        global host
        global port
        global s

        print('Binding dg port:', str(port))
        s.bind((host, port))
        s.listen(5)  # tiap 5 detik
    except socket.error as msg:
        print('Error binding socket ', str(msg))
        print('Menghubungkan lagi...')
        hubung_socket()

# THREAD PERTAMA
# menerima koneksi dan accept dari beberapa client
# dan disimpan pada list koenksi


def acc_conn():
    # refresh data koneksi
    for c in all_conn:
        c.close()

    del all_conn[:]
    del all_addr[:]
    del flag[:]

    while True:
        try:
            conn, addr = s.accept()
            s.setblocking(1)  # menghindari timeout
            all_conn.append(conn)
            all_addr.append(addr)
            flag.append('Idle')
            print('Koneksi terbentuk pada '+addr[0])
        except:
            print('Error membentuk koneksi')

# THREAD KEDUA
# Melihat semua client, Memilih client, Mengirim command ke semua client terkoneksi
# Membuat SHELL command interaktif

# kelompokdelapan> list
# 0 client-X Port
# 1 client-A Port
# 2 client-B Port

# kelompokdelapan> select 1


# referensi orang india
def start_shell():
    while True:
        cmd = input('kelompokdelapan> ')
        if cmd == 'list':
            list_connections()
        elif cmd == 'send_all':
            send_all()
        elif 'select' in cmd:
            conn, id = get_target(cmd)  # memilih client target
            if conn is not None:
                # jika ada maka
                send_target(conn, id)  # mengirim command ke client target
        else:
            print('Command tidak diketahui')

# menampilkan semua client terkoneksi


def list_connections():
    res = ''
    no = 0
    print("-------------Client-------------"+"\n")
    for i, conn in enumerate(all_conn):
        try:
            conn.send(str.encode(' '))
            conn.recv(2048)
        except:
            del all_conn[i]
            del all_addr[i]
            del flag[i]
            continue
        res = str(i) + "    "+str(all_addr[i][0]) + \
            "    "+str(all_addr[i][1]) + "   " + str(flag[i]) + "\n"
        print(res)

# memilih target


def get_target(cmd):
    try:
        target = cmd.replace('select ', '')  # mengambil id client
        target = int(target)
        conn = all_conn[target]
        print('Terkoneksi ke client :'+str(all_addr[target][0]))
        print(str(all_addr[target][0])+">", end="")
        return conn, target     # mereturn address client dan id client
        # 192.168.0.56>_

    except:
        print('Seleksi tidak valid')
        return None  # mereturn None

# mengirim command ke target


def send_target(conn, id):
    while True:
        try:
            cmd = input()
            # dalam bentuk string
            if cmd == 'quit':
                break
            if len(str.encode(cmd)) > 0:  # memastikan ada yang di type pada cmd host
                conn.send(str.encode(cmd))  # kirim command diencode
                client_resp = str(conn.recv(2048), 'utf-8')
                flag[id] = 'Processing'
                print('--------- Client ', id, ' Processing ---------')
                print(client_resp, end="")
                flag[id] = 'Idle'
        except:
            print('Error mengirim command')
            break


def get_target_all(cmd):
    try:
        target = cmd.replace('select ', '')  # mengambil id client
        target = int(target)
        conn = all_conn[target]
        return conn, target     # mereturn address client dan id client
        # 192.168.0.56>_

    except:
        print('Seleksi tidak valid')
        return None  # mereturn None


def send_target_all(conn, id, cmd):
    while True:
        try:
            if len(str.encode(cmd)) > 0:  # memastikan ada yang di type pada cmd host
                conn.send(str.encode(cmd))  # kirim command diencode
                client_resp = str(conn.recv(2048), 'utf-8')
                flag[id] = 'Processing'
                print('--------- Client ', id, ' Processing ---------')
                print(client_resp, end="")
                flag[id] = 'Idle'
                break
        except:
            print('Error mengirim command')
            break


def send_all():
    command = input('send_all> ')
    for i in range(len(all_conn)):
        cmd = 'select '+str(i)
        conn, id = get_target_all(cmd)
        if conn is not None:
            send_target_all(conn, id, command)

# menggunakan threading (karena menggunakan beberapa clinet)
# otomatis server hrs bisa threading
# dan pakai queue untuk membantu kinerja threading (process tidak tabrakan)
# jika queue 1 maka menerima koneksi
# jika queue 2 maka mengirim command

# buat thread pekerja


def buat_worker():
    for _ in range(threads):
        t = threading.Thread(target=work)
        t.daemon = True  # set thread ketika menyelesaikan job, thread juga close
        t.start()

# menghandle job yang ada didalam queue, antara handling client dan kirim data ke client


def work():
    while True:
        x = queue.get()
        if x == 1:
            buat_soket()
            hubung_socket()
            acc_conn()
        if x == 2:
            start_shell()

        queue.task_done()

# buat job untuk thread pekerja


def buat_jobs():
    for x in no_job:
        queue.put(x)
    queue.join()


# inisiasi pekerja dan job
buat_worker()
buat_jobs()
