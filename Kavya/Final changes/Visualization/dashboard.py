import panel as pn
from Framework.data_quality import DataQualityChecker

class Dashboard:
    def __init__(self, data):
        self.data = data
        self.visualizer = DataQualityChecker(data)

    def basic_data_summary(self):
        print("insde")
        summary = pn.Column()
        summary.append(self.visualizer.display_first_few_rows())
        summary.append(self.visualizer.display_summary_stats())
        summary.append(self.visualizer.display_missing_values())
        summary.append(self.visualizer.display_skewness())
        return summary