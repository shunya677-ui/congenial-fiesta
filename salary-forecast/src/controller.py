from PyQt6.QtWidgets import QFileDialog
from model import DataLoader, StatisticsCalculator, MovingAverageForecaster
from view import MainWindow
import sys

class AppController:
    def __init__(self, view: MainWindow):
        self.view = view
        self.data = None

        # Привязываем обработчики
        self.view.load_file = self.load_file  # переопределяем метод главного окна
        self.view.tab_forecast.calc_btn.clicked.connect(self.run_forecast)

    def load_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self.view, "Выберите файл CSV", "", "CSV Files (*.csv)"
        )
        if not filename:
            return
        try:
            self.data = DataLoader.load(filename)
            self.view.tab_table.update_data(self.data)
            self.view.tab_plot.plot(self.data)

            # Вычисляем максимальный и минимальный рост (можно вывести в статусную строку)
            male_ch, fem_ch = StatisticsCalculator.yearly_percent_changes(self.data)
            if male_ch:
                max_m = max(male_ch)
                min_m = min(male_ch)
                max_f = max(fem_ch)
                min_f = min(fem_ch)
                self.view.statusBar().showMessage(
                    f"Мужчины: мин рост {min_m:.1f}%, макс рост {max_m:.1f}% | "
                    f"Женщины: мин рост {min_f:.1f}%, макс рост {max_f:.1f}%"
                )
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self.view, "Ошибка", f"Не удалось загрузить данные:\n{e}")

    def run_forecast(self):
        if self.data is None:
            return
        window = self.view.tab_forecast.window_spin.value()
        steps = self.view.tab_forecast.steps_spin.value()
        forecaster = MovingAverageForecaster(window)
        # прогнозируем общую медианную зарплату
        series = [d.total for d in self.data]
        predictions = forecaster.forecast(series, steps)
        self.view.tab_forecast.plot_forecast(self.data, predictions, window)

def run_app():
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    controller = AppController(window)
    window.show()
    sys.exit(app.exec())