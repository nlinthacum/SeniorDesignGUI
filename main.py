from PyQt5.QtWidgets import *
from PyQt5 import uic

class MyGUI(QMainWindow):

    def __init__(self):
        super(MyGUI, self).__init__()
        uic.loadUi("HomePage.ui", self)
        self.show()
        self.create_new_button.clicked.connect(self.login)

    def login(self):
        uic.loadUi("CreateNew.ui", self)
        self.show()



def main():
    app = QApplication([])
    window = MyGUI()
    app.exec_()

if __name__ == '__main__':
    main()