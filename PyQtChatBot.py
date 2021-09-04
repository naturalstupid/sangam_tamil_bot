from PyQt6 import QtTest
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from requests import Session
from threading import Thread
from time import sleep
import regex
import json
bot_config_file = "./ChatBot.json"
with open(bot_config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)
poem_file = __import__(config["poem_file"])
poem_class = getattr(poem_file,config["poem_class"])()
display_mode = config["display_mode"] # "plain" #html
user_name = config["USER_NAME"]
bot_name = config["BOT_NAME"]
if display_mode == "html":
    user_name = "<p style=\"color:"+config["USER_NAME_COLOR"]+"\">"+ config["USER_NAME"]+": </p>"
    bot_name = "<p style=\"color:"+config["BOT_NAME_COLOR"]+"\">"+ config["BOT_NAME"]+": </p>"
application_title = config["CHATBOT_TITLE"]
new_messages = []

class MyAppWidget(QWidget):
    def __init__(self):
        super(MyAppWidget,self).__init__()
        self.text_area = QPlainTextEdit()
        self.text_area.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.message = QLineEdit()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_area)
        self.layout.addWidget(self.message)
        self.message.returnPressed.connect(self.send_message)
        self.setLayout(self.layout)
        self.setWindowTitle(application_title)
        self.show()
    def quit(self):
        sleepSecs = (int(config["wait_time_msec_before_closing_chat_window"]))*1000
        QtTest.QTest.qWait(sleepSecs)
        self.close()
    def display_new_messages(self):
        while new_messages:
            if display_mode == "html":
                self.text_area.appendHtml(new_messages.pop(0))
            else:
                self.text_area.appendPlainText(new_messages.pop(0))
    def send_message(self):
        user_message = self.message.text()
        user_response_function_name = config["user_response_function_name"]
        bot_response = getattr(poem_class,user_response_function_name)(user_message)
        print('bot_response',bot_response)
        if display_mode == "html":
            bot_response = bot_response.replace("\n","<br>")
        else:
            bot_response = bot_response.replace("<br>","\n")
        #bot_response = get_response(user_message)
        if bot_response:
            new_messages.append(bot_response)#+"\n")
        while new_messages:
            bot_message = new_messages.pop(0)
            line_break = "\n"
            if display_mode == "html":
                user_message = "<p style=\"color:"+config["USER_MSG_COLOR"]+"\">"+ user_message+" </p>"
                bot_message ="<p style=\"color:"+config["BOT_MSG_COLOR"]+"\">"+ bot_message+" </p>"
                line_break = ""
            message_to_append = user_name+user_message+line_break +bot_name+bot_message
            if display_mode == "html":
                self.text_area.appendHtml(message_to_append)
            else:
                self.text_area.appendPlainText(message_to_append)
            self.text_area.verticalScrollBar().value = self.text_area.verticalScrollBar().maximum()-4
        self.message.clear()
        if bot_response == config["QUIT_MSG"]:
            self.quit()
if __name__ == "__main__":
    import sys
    """ Following def and sys.excepthook line needed to trap PyQt exceptions """
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    window = MyAppWidget()
    sys.exit(app.exec())

