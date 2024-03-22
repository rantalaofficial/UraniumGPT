from PyQt5.QtWidgets import QTextEdit, QPushButton, QRadioButton

def createButton(label, callback, background_color, color, font_size, height = None, width = None):
    button = QPushButton(label)
    button.clicked.connect(callback)
    button.setStyleSheet(f"background-color: {background_color}; color: {color}; font-size: {font_size}px;")
    if height:
        button.setFixedHeight(height)
    if width:
        button.setFixedWidth(width)
    return button
    
def createTextBox(readonly, background_color, border_color = None, height = None):
    text_box = QTextEdit()
    style = f"QTextEdit {{ background-color: {background_color}; color: white; padding: 10px; font-size: 16px;"
    if border_color:
        style += f" border: 2px solid {border_color};"
    else:
        style += " border: none;"

    style += "} QTextEdit::verticalScrollBar { background-color: white; }"

    text_box.setStyleSheet(style)
    text_box.setReadOnly(readonly)
    if height:
        text_box.setFixedHeight(height)
    return text_box

def createRadioButton(label, callback, selected):
    radio_button = QRadioButton(label)
    radio_button.toggled.connect(callback)
    radio_button.setChecked(selected)
    radio_button.setStyleSheet("color: white; font-size: 15px;")
    return radio_button


    

