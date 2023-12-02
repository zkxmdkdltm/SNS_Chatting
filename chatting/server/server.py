from threading import Thread
from socket import *
from PyQt5.QtCore import Qt, pyqtSignal, QObject


class ServerSocket(QObject):
    update_signal = pyqtSignal(tuple, bool)
    recv_signal = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bListen = False
        self.clients = []
        self.ip = []
        self.threads = []
        self.client_ids = {}  # 각 클라이언트의 고유 id를 저장할 딕셔너리
        self.update_signal.connect(self.parent.updateClient)
        self.recv_signal.connect(self.parent.updateMsg)

    def __del__(self):
        self.stop()

    def start(self, ip, port):
        self.server = socket(AF_INET, SOCK_STREAM)

        try:
            self.server.bind((ip, port))
        except Exception as e:
            print('Bind Error : ', e)
            return False
        else:
            self.bListen = True
            self.t = Thread(target=self.listen, args=(self.server,))
            self.t.start()
            print('Server Listening...')

        return True

    def stop(self):
        self.bListen = False
        if hasattr(self, 'server'):
            self.server.close()
            print('Server Stop')

    def listen(self, server):
        while self.bListen:
            server.listen(5)
            try:
                client, addr = server.accept()
            except Exception as e:
                print('Accept() Error : ', e)
                break
            else:
                self.clients.append(client)
                self.ip.append(addr)
                self.client_ids[addr] = len(self.clients)  # 새로운 클라이언트의 주소를 키로 추가
                self.update_signal.emit(addr, True)
                t = Thread(target=self.receive, args=(addr, client))
                self.threads.append(t)
                t.start()

        self.removeAllClients()
        self.server.close()

    def receive(self, addr, client):
        client_id = self.client_ids[addr]  # 클라이언트의 고유 id를 가져옴
        while True:
            try:
                recv = client.recv(1024)
            except Exception as e:
                print('Recv() Error:', e)
                break
            else:
                msg = str(recv, encoding='utf-8')
                if msg:
                    self.send(f'익명 [{client_id}] {msg}')  # 메세지 앞에 클라이언트 id를 붙여서 전송
                    self.recv_signal.emit(f'[{client_id}] {msg}')
                    print('[RECV]:', addr, msg)

        self.removeClient(addr, client)

    def send(self, msg):
        try:
            for c in self.clients:
                c.send(msg.encode())
        except Exception as e:
            print('Send() Error : ', e)

    def removeClient(self, addr, client):
        client_id = self.client_ids[addr]  # 클라이언트의 고유 id를 가져옴
        print("removeClient")
        # find closed client index
        idx = -1
        for k, v in enumerate(self.clients):
            if v == client:
                idx = k
                break

        client.close()
        self.ip.remove(addr)
        self.clients.remove(client)

        del (self.threads[idx])
        self.update_signal.emit(addr, False)
        self.resourceInfo()

    def removeAllClients(self):
        print("removeAllClients")
        for c in self.clients:
            c.close()

        for addr, client_id in self.client_ids.items():
            self.update_signal.emit(addr, False)

        self.ip.clear()
        self.clients.clear()
        self.threads.clear()
        self.client_ids.clear()

        self.resourceInfo()
    def resourceInfo(self):
        print('Number of Client ip\t: ', len(self.ip))
        print('Number of Client socket\t: ', len(self.clients))
        print('Number of Client thread\t: ', len(self.threads))