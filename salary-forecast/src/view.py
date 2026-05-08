import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog,
    QLabel, QSpinBox, QMessageBox, QToolBar
)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from typing import List
from model import SalaryData

class PlotCanvas(FigureCanvas):
    """Холст для графиков matplotlib."""
    def __init__(self, parent=None, width=8, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.axes = self.fig.add_subplot(111)

class TabTable(QWidget):
    """Вкладка с таблицей данных."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Год", "Медианная общая", "Мужчины", "Женщины"])
        layout.addWidget(self.table)
        self.setLayout(layout)

    def update_data(self, data: List[SalaryData]):
        self.table.setRowCount(len(data))
        for i, d in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(str(d.year)))
            self.table.setItem(i, 1, QTableWidgetItem(f"{d.total:.2f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{d.male:.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{d.female:.2f}"))
        self.table.resizeColumnsToContents()

class TabPlot(QWidget):
    """Вкладка с графиком исторических данных."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.canvas = PlotCanvas(self)
        self.toolbar = self._create_toolbar()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def _create_toolbar(self):
        toolbar = QToolBar()
        export_btn = QPushButton("Экспорт PNG")
        export_btn.clicked.connect(self.export_plot)
        toolbar.addWidget(export_btn)
        return toolbar

    def plot(self, data: List[SalaryData], title="График зарплат"):
        self.canvas.axes.clear()
        years = [d.year for d in data]
        total = [d.total for d in data]
        male = [d.male for d in data]
        female = [d.female for d in data]
        self.canvas.axes.plot(years, total, label="Общая", marker='o')
        self.canvas.axes.plot(years, male, label="Мужчины", marker='s')
        self.canvas.axes.plot(years, female, label="Женщины", marker='^')
        self.canvas.axes.legend()
        self.canvas.axes.set_xlabel("Год")
        self.canvas.axes.set_ylabel("Руб.")
        self.canvas.axes.set_title(title)
        self.canvas.axes.grid(True)
        self.canvas.fig.tight_layout()
        self.canvas.draw()

    def export_plot(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить график", "", "PNG (*.png);;PDF (*.pdf)")
        if filename:
            self.canvas.fig.savefig(filename)

class TabForecast(QWidget):
    """Вкладка прогноза скользящей средней."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Окно сглаживания (n):"))
        self.window_spin = QSpinBox()
        self.window_spin.setMinimum(2)
        self.window_spin.setValue(3)
        controls.addWidget(self.window_spin)

        controls.addWidget(QLabel("Прогноз на лет:"))
        self.steps_spin = QSpinBox()
        self.steps_spin.setMinimum(1)
        self.steps_spin.setValue(3)
        controls.addWidget(self.steps_spin)

        self.calc_btn = QPushButton("Рассчитать прогноз")
        controls.addWidget(self.calc_btn)
        controls.addStretch()

        layout.addLayout(controls)

        self.canvas = PlotCanvas(self)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot_forecast(self, data: List[SalaryData], predictions: List[float], window: int):
        self.canvas.axes.clear()
        years = [d.year for d in data]
        actual = [d.total for d in data]  # прогнозируем общую зарплату

        # Исторические данные
        self.canvas.axes.plot(years, actual, label="Факт", color='blue', marker='o')

        # Прогноз
        last_year = years[-1]
        forecast_years = [last_year + i + 1 for i in range(len(predictions))]
        forecast_values = predictions
        self.canvas.axes.plot(forecast_years, forecast_values, label=f"Прогноз (n={window})",
                              linestyle='--', color='red', marker='x')

        self.canvas.axes.legend()
        self.canvas.axes.set_xlabel("Год")
        self.canvas.axes.set_ylabel("Руб.")
        self.canvas.axes.set_title("Прогноз методом скользящей средней")
        self.canvas.axes.grid(True)
        self.canvas.fig.tight_layout()
        self.canvas.draw()

class MainWindow(QMainWindow):
    """Главное окно приложения."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Анализ медианной зарплаты")
        self.resize(1000, 700)

        self.tabs = QTabWidget()
        self.tab_table = TabTable()
        self.tab_plot = TabPlot()
        self.tab_forecast = TabForecast()

        self.tabs.addTab(self.tab_table, "Таблица")
        self.tabs.addTab(self.tab_plot, "График")
        self.tabs.addTab(self.tab_forecast, "Прогноз")

        self.setCentralWidget(self.tabs)

        # Меню
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")
        file_menu.addAction("Открыть CSV", self.load_file)
        file_menu.addAction("Выход", self.close)

        help_menu = menubar.addMenu("Помощь")
        help_menu.addAction("О программе", self.show_about)

        self.data = None  # будет загружен

    def load_file(self):
        # Этот метод будет подключён к контроллеру
        pass

    def show_about(self):
        QMessageBox.information(self, "О программе", "Лабораторная работа по Git и статистическому прогнозированию")