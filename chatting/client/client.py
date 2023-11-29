from threading import * #Thread 모듈
from socket import * # Socket 모듈
from PyQt5.QtCore import Qt, pyqtSignal, QObject # pyqt GUI 모듈

#?
class Signal(QObject):
    recv_signal = pyqtSignal(str)
    disconn_signal = pyqtSignal()

#client 측 소켓
class ClientSocket:

    def __init__(self, parent):
        self.parent = parent #부모 윈도우

        # ?
        self.recv = Signal()
        self.recv.recv_signal.connect(self.parent.updateMsg)
        self.disconn = Signal()
        self.disconn.disconn_signal.connect(self.parent.updateDisconnect)
        self.client_id = None

        self.bConnect = False

    def __del__(self):
        self.stop() #소켓 닫기

    # 부모 윈도우 창에서 [접속]버튼을 눌렀을 때, 호출되는 함수.
    # 소켓을 생성하고 해당 IP 주소의 포트번호로 연결 시도.
    def connectServer(self, ip, port):
        self.client = socket(AF_INET, SOCK_STREAM)

        try:
            self.client.connect((ip, port))
        except Exception as e:  # 에러 처리
            print('Connect Error:', e)
            return False
        else:  # 접속 성공
            self.bConnect = True
            self.start_receive_thread()  # 새로운 스레드에서 메시지 수신 시작
            print('Connected')

        return True

    #소켓을 닫고 부모에게 알림
    def stop(self):
        self.bConnect = False
        if hasattr(self, 'client'):
            self.client.close()
            del (self.client)
            print('Client Stop')
            self.disconn.disconn_signal.emit()

    # 클라이언트 소켓 연결이 정상 -> 쓰레드 생성 -> 아래 함수 호출
    # 소켓의 데이터 수신을 대기함. (데이터를 수신하기 전까지 블록되어 다음 코드를 수행하지 않음.)
    # Client의 client.py 파일에서 receive 메서드 수정
    def receive(self, client):
        while self.bConnect:  # 무한 루프
            try:
                recv = client.recv(1024)
            except Exception as e:
                print('Recv() Error:', e)
                break
            else:  # 데이터 수신
                if not recv:
                    print('Server disconnected')
                    self.stop()
                    break

                msg = str(recv, encoding='utf-8')
                if msg:
                    self.recv.recv_signal.emit(msg)
                    print('[RECV]:', msg)

        print('Receive thread exited') 

    def start_receive_thread(self):
        self.receive_thread = Thread(target=self.receive, args=(self.client,))
        self.receive_thread.start()


    # 부모 윈도우의 [보내기] 버튼 누르면 호출됨.
    # 보낼 메세지 내용을 복사해 연결된 소켓으로 전송함.
    def send(self, msg):
        if not self.bConnect:
            return

        try:
            self.client.send(f'{msg}'.encode())
        except Exception as e:
            print('Send() Error:', e)