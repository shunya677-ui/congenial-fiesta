import pandas as pd
from typing import List, Tuple

class SalaryData:
    """Инкапсуляция строки данных по зарплате."""
    def __init__(self, year: int, total: float, male: float, female: float):
        self.year = year
        self.total = total
        self.male = male
        self.female = female

class DataLoader:
    """Загрузка данных из CSV. Отвечает только за чтение и парсинг (Single Responsibility)."""
    @staticmethod
    def load(filename: str) -> List[SalaryData]:
        df = pd.read_csv(filename)
        data = []
        for _, row in df.iterrows():
            data.append(SalaryData(
                year=int(row['year']),
                total=float(row['median_total']),
                male=float(row['median_male']),
                female=float(row['median_female'])
            ))
        return data

class StatisticsCalculator:
    """Вычисление статистических показателей."""
    @staticmethod
    def yearly_percent_changes(data: List[SalaryData]) -> Tuple[List[float], List[float]]:
        """Возвращает списки изменений для мужчин и женщин (в %)."""
        male_changes = []
        female_changes = []
        for i in range(1, len(data)):
            prev = data[i-1]
            curr = data[i]
            male_change = (curr.male - prev.male) / prev.male * 100
            female_change = (curr.female - prev.female) / prev.female * 100
            male_changes.append(male_change)
            female_changes.append(female_change)
        return male_changes, female_changes

class MovingAverageForecaster:
    """Прогноз методом экстраполяции по скользящей средней."""
    def __init__(self, window: int):
        self.window = window

    def forecast(self, series: List[float], steps: int) -> List[float]:
        """Возвращает список прогнозных значений длины steps."""
        if len(series) < self.window:
            raise ValueError("Ряд короче окна")
        current_series = series.copy()
        predictions = []
        for _ in range(steps):
            next_val = sum(current_series[-self.window:]) / self.window
            predictions.append(next_val)
            current_series.append(next_val)
        return predictions