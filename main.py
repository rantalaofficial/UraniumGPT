import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QRadioButton, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, Qt

from openai import OpenAI

import time;

from ChatAssistant import ChatAssistant

assistant = ChatAssistant()

class WorkerThread(QThread):
    data_processed = pyqtSignal(str)

    def __init__(self, message, parent=None):
        self.message = message
        super(WorkerThread, self).__init__(parent)

    def run(self):
        stream = assistant.sendMessageAndStream(self.message)

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                self.data_processed.emit(assistant.addChunk(chunk))

class ChatApp(QWidget):

    DARK_GRAY = "#181717"
    LIGHT_GRAY = "#212121"

    SIDEBAR_BUTTON = "#2F2F2F"

    GREEN = "rgb(0, 100, 0)"

    chat_buttons = []

    def __init__(self):
        super().__init__()
        self.initUI()
        self.answerIsStreaming = False

    def addButton(self, layout, label, function, green=False):
        button = QPushButton(label)
        button.clicked.connect(function)
        button.setFixedHeight(int(self.height() * 0.05))
        button.setFixedWidth(int(self.width() * 0.15))

        layout.addWidget(button)

    def initUI(self):
        self.setWindowTitle('UraniumGPT')
        self.layout = QHBoxLayout() 
        self.setGeometry(100, 100, 800, 600)

        left_column = QWidget()
        left_column.setStyleSheet("background-color: %s;" % self.DARK_GRAY)
        left_column_layout = QVBoxLayout(left_column)
        left_column_layout.setContentsMargins(20, 20, 20, 20)
        left_column.setFixedWidth(200)
        left_column_layout.setAlignment(Qt.AlignTop)
        self.left_column_layout = left_column_layout

        new_chat_button = QPushButton('New Chat')
        new_chat_button.clicked.connect(self.new_chat)
        new_chat_button.setStyleSheet("background-color: %s; color: white; font-size: 20px;" % self.GREEN)
        new_chat_button.setFixedHeight(50)
        self.new_chat_button = new_chat_button

        left_column_layout.addWidget(new_chat_button)

        right_column = QWidget()
        right_column.setStyleSheet("background-color: %s;" % self.LIGHT_GRAY)
        right_column_layout = QVBoxLayout(right_column)
        right_column_layout.setContentsMargins(20, 20, 20, 20)

        chat_textbox = QTextEdit()
        chat_textbox.setStyleSheet("background-color: %s; color: white; padding: 10px; font-size: 14px; border: none;" % self.LIGHT_GRAY)
        chat_textbox.setReadOnly(True)
        self.chat_textbox = chat_textbox

        send_textbox = QTextEdit()
        send_textbox.setStyleSheet("background-color: %s; color: white; padding: 10px; font-size: 14px; border: 2px solid %s;" % (self.LIGHT_GRAY, self.GREEN))
        send_textbox.setFixedHeight(100) 
        self.send_textbox = send_textbox

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        right_column_layout.addWidget(chat_textbox)
        right_column_layout.addWidget(send_textbox)
        right_column_layout.addLayout(bottom_layout)

        for i in range(len(assistant.models)):
            radio_button = QRadioButton(assistant.models[i])
            radio_button.toggled.connect(self.setModel)
            radio_button.setChecked(i == assistant.selectedModel)
            radio_button.setStyleSheet("color: white; font-size: 15px;")
            bottom_layout.addWidget(radio_button)

        send_button = QPushButton('Send')
        send_button.clicked.connect(self.send_message)
        send_button.setStyleSheet("background-color: %s; color: white; font-size: 20px;" % self.GREEN)
        send_button.setFixedHeight(50)
        send_button.setFixedWidth(150)
        bottom_layout.addWidget(send_button)

        layout = QHBoxLayout()
        layout.setSpacing(0)  
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(left_column)
        layout.addWidget(right_column)
        self.setLayout(layout)

        self.new_chat()

    def new_chat(self):
        if assistant.newChat():
            self.chat_textbox.clear()

            new_chat_button = QPushButton('Chat ' + str(len(assistant.chats)))
            new_chat_button.clicked.connect(self.chat_selected)
            new_chat_button.setStyleSheet("background-color: %s; color: white; font-size: 20px;" % self.SIDEBAR_BUTTON)
            new_chat_button.setFixedHeight(50)
            self.left_column_layout.addWidget(new_chat_button)
            self.chat_buttons.append(new_chat_button)

    def chat_selected(self):
        chat_number = int(self.sender().text().split(' ')[1]) - 1

        assistant.selectedChat = chat_number
        self.chat_textbox.clear()
        self.chat_textbox.append(assistant.getChatText())

    def backward(self):
        assistant.backward()
        self.chat_textbox.clear()
        self.chat_textbox.append(assistant.getChatText())

    def forward(self):
        assistant.forward()
        self.chat_textbox.clear()
        self.chat_textbox.append(assistant.getChatText())

    def delete(self):
        assistant.deleteChat()
        self.chat_textbox.clear()
        self.chat_textbox.append(assistant.getChatText())

        self.updateNewChatButton()

    def setModel(self):
        assistant.selectedModel = assistant.models.index(self.sender().text())

    def send_message(self):
        message = self.send_textbox.toPlainText().strip()

        if message and not self.answerIsStreaming:
            self.send_textbox.clear()
            self.send_message_multithread(message)

            #self.chat_box.clear()
            #self.chat_box.append(assistant.sendMessage(message))
            
    def send_message_multithread(self, message):
        self.answerIsStreaming = True

        self.worker_thread = WorkerThread(message)
        self.worker_thread.data_processed.connect(self.updateChatBox)  # Connect signal to slot

        self.worker_thread.finished.connect(self.multithread_finished)
        self.worker_thread.start()

    def multithread_finished(self):
        self.worker_thread.quit()
        self.answerIsStreaming = False

    def updateChatBox(self, chatText):
        self.chat_textbox.clear()
        self.chat_textbox.append(chatText)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat_app = ChatApp()
    chat_app.show()
    sys.exit(app.exec_())