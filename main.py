import sys

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5 import QtGui
from PyQt5.QtGui import QFont

from GuiHelper import *
from ChatAssistant import ChatAssistant

assistant = ChatAssistant(True)

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

    answerIsStreaming = False

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('UraniumGPT')
        self.layout = QHBoxLayout() 
        self.setGeometry(100, 100, 1000, 800)

        self.closeEvent = self.closeEvent

        left_column = QWidget()
        left_column.setStyleSheet("background-color: %s;" % self.DARK_GRAY)
        left_column.setFixedWidth(200)

        left_column_layout = QVBoxLayout(left_column)
        left_column_layout.setContentsMargins(20, 20, 20, 20)
        left_column_layout.setAlignment(Qt.AlignTop)
        self.left_column_layout = left_column_layout
        left_column_layout.addWidget(createButton('New Chat', self.new_chat, self.GREEN, "white", 20, 50))
        
        right_column = QWidget()
        right_column.setStyleSheet("background-color: %s;" % self.LIGHT_GRAY)
        right_column_layout = QVBoxLayout(right_column)
        right_column_layout.setContentsMargins(20, 20, 20, 20)

        self.chat_textbox = createTextBox(True, self.LIGHT_GRAY, None, None)
        right_column_layout.addWidget(self.chat_textbox)

        self.send_textbox = createTextBox(False, self.LIGHT_GRAY, self.GREEN, 200)
        right_column_layout.addWidget(self.send_textbox)
        
        bottom_layout = QHBoxLayout()
        right_column_layout.addLayout(bottom_layout)

        bottom_layout.addWidget(createButton('Delete Chat', self.delete, self.SIDEBAR_BUTTON, "white", 20, 50, 150))
        bottom_layout.addStretch()

        for i in range(len(assistant.models)):
            bottom_layout.addWidget(createRadioButton(assistant.models[i], self.setModel, i == assistant.selectedModel))

        bottom_layout.addWidget(createButton('Send', self.send_message, self.GREEN, "white", 20, 50, 150))

        layout = QHBoxLayout()
        layout.setSpacing(0)  
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(left_column)
        layout.addWidget(right_column)
        self.setLayout(layout)

        self.reset_chat_buttons()

    def add_chat_button(self, button_number):
        new_chat_button = createButton('Chat ' + str(button_number), self.chat_selected, self.SIDEBAR_BUTTON, "white", 20, 50)

        self.left_column_layout.addWidget(new_chat_button)
        self.chat_buttons.append(new_chat_button)

    def reset_chat_buttons(self):
        for button in self.chat_buttons:
            self.left_column_layout.removeWidget(button)
            button.deleteLater()

        self.chat_buttons = []

        for i in range(len(assistant.chats)):
            self.add_chat_button(i + 1)

        self.highlight_chat_button(assistant.selectedChat)
        self.updateChatBox(assistant.getChatText())


    def new_chat(self):
        if assistant.newChat():
            self.add_chat_button(len(assistant.chats))

            self.chat_textbox.clear()
            self.highlight_chat_button(assistant.selectedChat)
        
    def chat_selected(self):
        assistant.selectedChat = int(self.sender().text().split(' ')[1]) - 1

        self.updateChatBox(assistant.getChatText())

        self.highlight_chat_button(assistant.selectedChat)

    def highlight_chat_button(self, chat_index):
        for button in range(len(self.chat_buttons)):
            if button == chat_index:
                self.chat_buttons[button].setStyleSheet("background-color: %s; color: white; font-size: 20px;" % self.SIDEBAR_BUTTON)
            else:
                self.chat_buttons[button].setStyleSheet("background-color: %s; color: white; font-size: 20px;" % self.LIGHT_GRAY)

    def delete(self):
        assistant.deleteChat()
        self.updateChatBox(assistant.getChatText())

        self.reset_chat_buttons()

    def setModel(self):
        assistant.selectedModel = assistant.models.index(self.sender().text())

    def send_message(self):
        message = self.send_textbox.toPlainText().strip()

        if message and not self.answerIsStreaming:
            self.send_textbox.clear()
            self.send_message_multithread(message)
            
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
        self.chat_textbox.setHtml(chatText + "<br><br>") # This ensures the horizontal scrollbar is not on top of the text

        # scroll to the bottom
        self.chat_textbox.moveCursor(QtGui.QTextCursor.End)

    def closeEvent(self, event):  
        assistant.saveChats()
        print("Saving to chats.txt")
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    font = QFont("Arial", 14)
    app.setFont(font)

    chat_app = ChatApp()
    chat_app.show()
    sys.exit(app.exec_())