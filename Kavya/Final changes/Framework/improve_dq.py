from functools import wraps
import panel as pn
import pandas as pd
from scipy.stats import skew
from statsmodels.tsa.stattools import adfuller

class Improve_DQ:

    def __init__(self, data):
        self.data = data
        self.expectations = []

    