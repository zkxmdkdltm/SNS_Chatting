from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import client

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

port = 5614

#CWidget : 윈도우 창을 만듦
class CWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.c = client.ClientSocket(self)

        self.initUI()

    def __del__(self):
        self.c.stop()

    def initUI(self):
        self.setWindowTitle('클라이언트')

        # 스타일 변경 부분
        self.setStyleSheet('background-color: #F0F0F0; font-family: Arial;')

        # 클라이언트 설정 부분
        ipbox = QHBoxLayout()

        gb = QGroupBox('서버 설정')
        gb.setStyleSheet('background-color: #D3D3D3; border: 1px solid #A9A9A9; border-radius: 5px; padding: 10px; color: #333333;')
        ipbox.addWidget(gb)

        box = QHBoxLayout()

        label = QLabel('Server IP')
        label.setStyleSheet('color: #333333;')
        self.ip = QLineEdit()
        self.ip.setInputMask('000.000.000.000;_')  # 접속할 서버의 ip 주소 받기
        box.addWidget(label)
        box.addWidget(self.ip)

        label = QLabel('Server Port')
        label.setStyleSheet('color: #333333;')
        self.port = QLineEdit(str(port))
        box.addWidget(label)
        box.addWidget(self.port)

        self.btn = QPushButton('connect')
        self.btn.setStyleSheet('background-color: #4CAF50; color: white; border: none; padding: 8px 16px; text-align: center; text-decoration: none; display: inline-block; font-size: 14px; margin: 4px 2px; cursor: pointer; border-radius: 5px;')
        self.btn.clicked.connect(self.connectClicked)
        box.addWidget(self.btn)

        gb.setLayout(box)

        # 채팅창 부분
        infobox = QHBoxLayout()
        gb = QGroupBox('메시지')
        gb.setStyleSheet('color: #333333; background-color: #D3D3D3; border: 1px solid #A9A9A9; border-radius: 5px; padding: 10px;')
        infobox.addWidget(gb)

        box = QVBoxLayout()

        label = QLabel('Received Messages')
        label.setStyleSheet('color: #333333; font-weight: bold;')
        box.addWidget(label)

        self.recvmsg = QListWidget()
        box.addWidget(self.recvmsg)

        label = QLabel('Type Your Message')
        label.setStyleSheet('color: #333333; font-weight: bold;')
        box.addWidget(label)

        self.sendmsg = QTextEdit()
        self.sendmsg.setFixedHeight(50)
        box.addWidget(self.sendmsg)

        hbox = QHBoxLayout()

        box.addLayout(hbox)
        self.sendbtn = QPushButton('Send Message')
        self.sendbtn.setStyleSheet('background-color: #008CBA; color: white; border: none; padding: 8px 16px; text-align: center; text-decoration: none; display: inline-block; font-size: 14px; margin: 4px 2px; cursor: pointer; border-radius: 5px;')
        self.sendbtn.setAutoDefault(True)
        self.sendbtn.clicked.connect(self.sendMsg)

        self.clearbtn = QPushButton('Clear Chat')
        self.clearbtn.setStyleSheet('background-color: #D32F2F; color: white; border: none; padding: 8px 16px; text-align: center; text-decoration: none; display: inline-block; font-size: 14px; margin: 4px 2px; cursor: pointer; border-radius: 5px;')
        self.clearbtn.clicked.connect(self.clearMsg)

        hbox.addWidget(self.sendbtn)
        hbox.addWidget(self.clearbtn)
        gb.setLayout(box)

        # 전체 배치
        vbox = QVBoxLayout()
        vbox.addLayout(ipbox)
        vbox.addLayout(infobox)
        self.setLayout(vbox)

        self.show()


    def connectClicked(self):
        if self.c.bConnect == False:
            ip = self.ip.text()
            port = self.port.text()
            if self.c.connectServer(ip, int(port)):
                self.btn.setText('접속 종료')
            else:   
                self.c.stop()
                self.sendmsg.clear()
                self.recvmsg.clear()
                self.btn.setText('접속')
        else:
            self.c.stop()
            self.sendmsg.clear()
            self.recvmsg.clear()
            self.btn.setText('접속')

    def updateMsg(self, msg):
        self.recvmsg.addItem(QListWidgetItem(msg))

    def updateDisconnect(self):
        self.btn.setText('접속')

    def sendMsg(self):
        sendmsg = self.sendmsg.toPlainText()
        self.c.send(sendmsg)
        self.sendmsg.clear()

    def clearMsg(self):
        self.recvmsg.clear()

    def closeEvent(self, e):
        self.c.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CWidget()
    sys.exit(app.exec_())