import sys, os
from PyQt5.QtWidgets import *
sys.path.append(os.path.join(os.getcwd(), 'controller'))
from controller import layout

def main(*args, **kwargs):
    curr_dir = os.getcwd()
    os.chdir('./safety_case')

    script = kwargs["script"]
    app = QApplication(sys.argv)
    main = layout.MainLayout(script)
    main.show()
    sys.exit(app.exec_())

    # os.chdir(curr_dir)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = layout.MainLayout()
    main.show()
    sys.exit(app.exec_())