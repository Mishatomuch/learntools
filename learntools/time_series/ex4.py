from learntools.core import *
from learntools.time_series.checking_utils import load_store_sales
from learntools.time_series.utils import make_lags, make_leads


class Q1(ThoughtExperiment):  # Time and serial dependence
    _hint = ""
    _solution = ""


class Q2(ThoughtExperiment):  # Serial dependence in Store Sales
    _solution = """None of the lags seem especially significant from the correlogram (except possibly lag 5). With linear regression alone, it's unlikely any of these lags would lead to much improvement.

The lag plot, however, indicates that there may be some non-linear dependence, especially in the first lag. In the next lesson, we'll construct a forecaster with XGBoost, an algorithm capable of learning this kind of dependence.
"""


class Q3(ThoughtExperiment):  # Time series features
    _hint = ""
    _solution = ""


class Q4(EqualityCheckProblem):  # Create time series features
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    from statsmodels.tsa.deterministic import (CalendarFourier,
                                               DeterministicProcess)
    average_sales = load_store_sales().groupby(
        'date').mean().squeeze().loc['2017']
    y = average_sales.loc[:, 'sales']
    fourier = CalendarFourier(freq='M', order=4)
    dp = DeterministicProcess(
        constant=True,
        index=y.index,
        order=1,
        seasonal=True,
        drop=True,
        additional_terms=[fourier],
    )
    X_time = dp.in_sample()
    X_time['NewYearsDay'] = (X_time.index.dayofyear == 1)
    model = LinearRegression(fit_intercept=False)
    model.fit(X_time, y)
    y_deseason = y - model.predict(X_time)
    y_deseason.name = 'sales_deseasoned'
    onpromotion = average_sales.loc[:, 'onpromotion']
    X_lags = make_lags(y_deseason, lags=1)
    X_promo = pd.concat([
        make_lags(onpromotion, lags=1),
        onpromotion,
        make_leads(onpromotion, leads=1),
    ],
                        axis=1)
    X_oil = pd.DataFrame()

    _vars = ['X_lags', 'X_promo', 'X_oil']
    _expected = [X_lags, X_promo, X_oil]

    _hint = """Your solution should look like:
```python
X_lags = make_lags(y_deseason, lags=____)

X_promo = pd.concat([
    make_lags(onpromotion, lags=____),
    onpromotion,
    make_leads(onpromotion, leads=____),
], axis=1)

X_oil = ____

X = pd.concat([X_time, X_lags, X_promo, X_oil], axis=1).dropna()
y, X = y.align(X, join='inner')
```
"""
    _solution = CS("""
X_lags = make_lags(y_deseason, lags=1)

X_promo = pd.concat([
    make_lags(onpromotion, lags=1),
    onpromotion,
    make_leads(onpromotion, leads=1),
], axis=1)

X_oil = pd.DataFrame()

X = pd.concat([X_time, X_lags, X_promo, X_oil], axis=1).dropna()
y, X = y.align(X, join='inner')
""")


class Q5(EqualityCheckProblem):  # Create statistical features
    average_sales = load_store_sales().groupby(
        'date').mean().squeeze().loc['2017']
    y_lag = average_sales.loc[:, 'sales'].shift(1)
    onpromo = average_sales.loc[:, 'onpromotion']

    median_14 = y_lag.rolling(14).median()
    std_7 = y_lag.rolling(7).std()
    promo_7 = onpromo.rolling(7, center=True).sum()

    _vars = ['median_14', 'std_7', 'promo_7']
    _expected = [median_14, std_7, promo_7]

    _hint = """Your code should look like:
```python
y_lag = average_sales.loc[:, 'sales'].shift(1)
onpromo = average_sales.loc[:, 'onpromotion']

mean_7 = y_lag.rolling(7).____()
median_14 = y_lag.rolling(____).median()
std_7 = y_lag.rolling(____).____()
promo_7 = onpromo.rolling(____, center=True).____()
```
"""
    _solution = CS("""
y_lag = average_sales.loc[:, 'sales'].shift(1)
onpromo = average_sales.loc[:, 'onpromotion']

mean_7 = y_lag.rolling(7).mean()
median_14 = y_lag.rolling(14).median()
std_7 = y_lag.rolling(7).std()
promo_7 = onpromo.rolling(7, center=True).sum()
""")


qvars = bind_exercises(globals(), [Q1, Q2, Q3, Q4, Q5], var_format="q_{n}")
__all__ = list(qvars)
