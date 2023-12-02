from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import socket
import server

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

port = 5614


class CWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.s = server.ServerSocket(self)

        self.initUI()

    def initUI(self):
        self.setWindowTitle('새로운 서버')

        # 전체 배경 색상
        self.setStyleSheet('background-color: white;')

        # 서버 설정 부분
        ipbox = QHBoxLayout()

        gb = QGroupBox('서버 설정')
        gb.setStyleSheet('color: #333333; background-color: #D3D3D3; border: 1px solid #A9A9A9; border-radius: 5px; padding: 10px;')
        ipbox.addWidget(gb)

        box = QHBoxLayout()

        label = QLabel('Server IP')
        label.setStyleSheet('color: #333333;')
        self.ip = QLineEdit(socket.gethostbyname(socket.gethostname()))
        box.addWidget(label)
        box.addWidget(self.ip)

        label = QLabel('Server Port')
        label.setStyleSheet('color: #333333;')
        self.port = QLineEdit(str(port))
        box.addWidget(label)
        box.addWidget(self.port)

        self.btn = QPushButton('Start Server')
        self.btn.setCheckable(True)
        self.btn.setStyleSheet('color: #333333; background-color: #4CAF50; color: white; border: none; padding: 8px 16px; text-align: center; text-decoration: none; display: inline-block; font-size: 14px; margin: 4px 2px; cursor: pointer; border-radius: 5px;')
        self.btn.toggled.connect(self.toggleButton)
        box.addWidget(self.btn)

        gb.setLayout(box)

        # 접속자 정보 부분
        infobox = QHBoxLayout()
        gb = QGroupBox('접속자 정보')
        gb.setStyleSheet('color: #333333; background-color: #D3D3D3; border: 1px solid #A9A9A9; border-radius: 5px; padding: 10px;')
        infobox.addWidget(gb)

        box = QHBoxLayout()

        self.guest = QTableWidget()
        self.guest.setColumnCount(2)
        self.guest.setHorizontalHeaderItem(0, QTableWidgetItem('IP'))
        self.guest.setHorizontalHeaderItem(1, QTableWidgetItem('Port'))

        box.addWidget(self.guest)
        gb.setLayout(box)

        # 채팅창 부분
        gb = QGroupBox('새로운 메시지')
        gb.setStyleSheet('color: #333333; background-color: #D3D3D3; border: 1px solid #A9A9A9; border-radius: 5px; padding: 10px;')
        infobox.addWidget(gb)

        box = QVBoxLayout()

        label = QLabel('Received Messages')
        label.setStyleSheet('color: #333333; font-weight: bold;')
        box.addWidget(label)

        self.msg = QListWidget()
        self.msg.setStyleSheet('background-color: white;')  # 채팅창 배경 색상
        box.addWidget(self.msg)

        label = QLabel('Type Your Message')
        label.setStyleSheet('color: #333333; font-weight: bold;')
        box.addWidget(label)

        self.sendmsg = QLineEdit()
        box.addWidget(self.sendmsg)

        hbox = QHBoxLayout()

        self.sendbtn = QPushButton('Send Message')
        self.sendbtn.setStyleSheet('color: #333333; background-color: #008CBA; color: white; border: none; padding: 8px 16px; text-align: center; text-decoration: none; display: inline-block; font-size: 14px; margin: 4px 2px; cursor: pointer; border-radius: 5px;')
        self.sendbtn.clicked.connect(self.sendMsg)
        hbox.addWidget(self.sendbtn)

        self.clearbtn = QPushButton('Clear Chat')
        self.clearbtn.setStyleSheet('color: #333333; background-color: #D32F2F; color: white; border: none; padding: 8px 16px; text-align: center; text-decoration: none; display: inline-block; font-size: 14px; margin: 4px 2px; cursor: pointer; border-radius: 5px;')
        self.clearbtn.clicked.connect(self.clearMsg)
        hbox.addWidget(self.clearbtn)

        box.addLayout(hbox)

        gb.setLayout(box)

        # 전체 배치
        vbox = QVBoxLayout()
        vbox.addLayout(ipbox)
        vbox.addLayout(infobox)
        self.setLayout(vbox)

        self.show()



    def toggleButton(self, state):
        if state:
            ip = self.ip.text()
            port = self.port.text()
            if self.s.start(ip, int(port)):
                self.btn.setText('서버 종료')
        else:
            self.s.stop()
            self.msg.clear()
            self.btn.setText('서버 실행')

        # Server의 windows.py 파일에서 updateClient 메서드 수정
    def updateClient(self, addr, isConnect=False):
        row = self.guest.rowCount()
        if isConnect:
            self.guest.setRowCount(row + 1)
            self.guest.setItem(row, 0, QTableWidgetItem(addr[0]))
            self.guest.setItem(row, 1, QTableWidgetItem(str(addr[1])))
            self.updateMsg(f'[{addr[1]}] 클라이언트가 접속했습니다. (ID: {self.s.client_ids[addr]})')
        else:
            for r in range(row):
                ip = self.guest.item(r, 0).text()
                port = self.guest.item(r, 1).text()
                if addr[0] == ip and str(addr[1]) == port:
                    self.guest.removeRow(r)
                    self.updateMsg(f'[{addr[1]}] 클라이언트가 연결을 종료했습니다. (ID: {self.s.client_ids[addr]})')
                    break

    # updateMsg 메서드 수정
    def updateMsg(self, msg):
        self.msg.addItem(QListWidgetItem(msg))
        self.msg.setCurrentRow(self.msg.count() - 1)


    def sendMsg(self):
        if not self.s.bListen:
            self.sendmsg.clear()
            return
        sendmsg = self.sendmsg.text()
        self.updateMsg(sendmsg)
        print(sendmsg)
        self.s.send(sendmsg)
        self.sendmsg.clear()

    def clearMsg(self):
        self.msg.clear()

    def closeEvent(self, e):
        self.s.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CWidget()
    sys.exit(app.exec_())