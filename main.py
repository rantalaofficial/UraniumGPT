import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QRadioButton, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal

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
    def __init__(self):
        super().__init__()
        self.initUI()
        self.answerIsStreaming = False

    def initUI(self):
        self.setWindowTitle('UraniumGPT')
        self.layout = QVBoxLayout()
        self.setGeometry(100, 100, 1000, 800)

        buttonLabels = ["New Chat", "Backward", "Forward", "Delete"]
        clickFunctions = [self.new_chat, self.backward, self.forward, self.delete]
        buttons_layout = QHBoxLayout()
        for i in range(len(buttonLabels)):
            
            button = QPushButton(buttonLabels[i])
            button.setFixedHeight(int(self.height() * 0.05))
            button.setFixedWidth(int(self.width() * 0.15))
            if (i == 0): 
                self.new_chat_button = button
                button.setStyleSheet("background-color: rgb(0, 100, 0); color: white; font-size: 15px;")
            else:
                button.setStyleSheet("color: white; font-size: 15px;")

            button.clicked.connect(clickFunctions[i])
            buttons_layout.addWidget(button)
        buttons_layout.addStretch()
        self.layout.addLayout(buttons_layout)

        # Chat box
        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        self.layout.addWidget(self.chat_box)

        # make a for loop to add radio buttons for each model
        for i in range(len(assistant.models)):
            radio_button = QRadioButton(assistant.models[i])
            radio_button.toggled.connect(self.setModel)
            radio_button.setChecked(i == assistant.selectedModel)
            radio_button.setStyleSheet("color: white; font-size: 15px;")
            self.layout.addWidget(radio_button)

        # Message box
        self.message_box = QTextEdit()
        self.layout.addWidget(self.message_box)

        self.message_box.setSizePolicy(
            self.message_box.sizePolicy().Expanding,
            self.message_box.sizePolicy().Preferred
        )
        self.message_box.setFixedHeight(int(self.height() * 0.3))

        # Send button
        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setFixedHeight(int(self.height() * 0.05))
        self.send_button.setFixedWidth(int(self.width() * 0.2))
        send_button_layout = QHBoxLayout()
        send_button_layout.addStretch()

        send_button_layout.addWidget(self.send_button)
        self.layout.addLayout(send_button_layout)

        self.send_button.setStyleSheet("background-color: rgb(0, 100, 0); color: white; font-size: 20px;")
        self.setStyleSheet("background-color: rgb(50, 50, 50)")
        self.chat_box.setStyleSheet("background-color: rgb(50, 50, 50); color: white; border: 2px solid rgb(100, 100, 100); font-size: 14px; padding: 10px;")
        self.message_box.setStyleSheet("background-color: rgb(50, 50, 50); color: white; border: 2px solid rgb(100, 100, 100); font-size: 14px; padding: 10px;")

        self.setLayout(self.layout)




    def updateNewChatButton(self):
        numberOfChats = len(assistant.chats)
        if numberOfChats > 1:
            self.new_chat_button.setText("New Chat (" + str(numberOfChats) + ")")
        else:
            self.new_chat_button.setText("New Chat")

    def new_chat(self):
        assistant.newChat()
        self.chat_box.clear()

        self.updateNewChatButton()


    def backward(self):
        assistant.backward()
        self.chat_box.clear()
        self.chat_box.append(assistant.getChatText())

    def forward(self):
        assistant.forward()
        self.chat_box.clear()
        self.chat_box.append(assistant.getChatText())

    def delete(self):
        assistant.deleteChat()
        self.chat_box.clear()
        self.chat_box.append(assistant.getChatText())

        self.updateNewChatButton()

    def setModel(self):
        assistant.selectedModel = assistant.models.index(self.sender().text())

    def send_message(self):
        message = self.message_box.toPlainText().strip()

        if message and not self.answerIsStreaming:
            self.message_box.clear()
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
        self.chat_box.clear()
        self.chat_box.append(chatText)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat_app = ChatApp()
    chat_app.show()
    sys.exit(app.exec_())