import sys
import time
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QTimer
from functools import wraps

class Worker(QThread):
    time_update = pyqtSignal(int)
    finished = pyqtSignal()
    start_timer = pyqtSignal()
    result_ready = pyqtSignal(object)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.elapsed_time = 0

    def run(self):
        self.start_timer.emit()  # Emit the signal to start the timer in the main thread
        result = self.func(*self.args, **self.kwargs)
        self.result_ready.emit(result)
        self.finished.emit()

    @pyqtSlot()
    def update_time(self):
        self.elapsed_time += 1
        self.time_update.emit(self.elapsed_time)

class WaitDialog(QDialog):
    def __init__(self, msg, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Please Wait')
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(300, 150)
        layout = QVBoxLayout()
        self.msg = QLabel(msg)
        self.label = QLabel(f'Language Model Processing...')
        self.time_label = QLabel('Elapsed Time: 0s')
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.close_button = QPushButton('Close')
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.accept)
        layout.addWidget(self.msg)
        layout.addWidget(self.label)
        layout.addWidget(self.time_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.close_button)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)

        self.result = None

    @pyqtSlot()
    def update_time(self):
        self.worker.update_time()  # Call the worker's update_time method

    @pyqtSlot(int)
    def update_time_label(self, elapsed_time):
        self.time_label.setText(f'Elapsed Time: {elapsed_time}s')

    def on_finished(self):
        self.label.setText('Execution Finished')
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        self.close_button.setEnabled(True)
        self.timer.stop()  # Stop the timer when the task is finished
        self.accept()  # Close the dialog

    def start_timer(self):
        self.timer.start(1000)

    @pyqtSlot(object)
    def handle_result(self, result):
        self.result = result

    def get_result(self):
        return self.result

def show_wait_dialog(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Extract the 'seconds' parameter to show in the dialog
        msg = ''
        for v in args:
            if isinstance(v, str) and v.startswith('# '):
                msg = v
                break
        # seconds = args[0] if args else kwargs.get('seconds', 0)

        wait_dialog = WaitDialog(msg)
        worker = Worker(func, *args, **kwargs)
        
        wait_dialog.worker = worker  # Store a reference to the worker in the dialog
        
        worker.time_update.connect(wait_dialog.update_time_label)
        worker.finished.connect(wait_dialog.on_finished)
        worker.start_timer.connect(wait_dialog.start_timer)  # Connect the signal to start the timer
        worker.result_ready.connect(wait_dialog.handle_result)  # Connect the signal to handle the result
        
        worker.start()

        wait_dialog.exec_()

        return wait_dialog.get_result()

    return wrapper

# Example usage
@show_wait_dialog
def long_time_function(seconds, msg):
    print(f"Starting a long time function for {seconds} seconds...")
    time.sleep(seconds)
    result = f"Function finished in {seconds} seconds"
    print(result)
    return result

if __name__ == "__main__":
    msg = f'# [1/3] long_time_function.'
    ret = long_time_function(5, msg)
    print('ret=', ret)
