from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

from auto_build_llm.show_chart import Show_Similarity_Chart

class ChartDialog(QDialog):
    def __init__(self):
        super(ChartDialog, self).__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        self.canvas = FigureCanvas(plt.Figure())
        layout.addWidget(self.canvas)

        self.button = QPushButton('绘制图表')
        self.button.clicked.connect(self.plot)
        layout.addWidget(self.button)
        
        self.setLayout(layout)

    def plot(self):
        # 在这里调用之前的 matplotlib 代码
        self.canvas.figure.clear()
        ax = self.canvas.figure.subplots()
        
        Show_Similarity_Chart(ax, src_path='auto_build_llm/compare_data.json')

        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    chartDialog = ChartDialog()
    chartDialog.show()
    sys.exit(app.exec_())
