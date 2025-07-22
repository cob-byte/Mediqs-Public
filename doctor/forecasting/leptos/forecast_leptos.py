import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from numpy import log
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from scipy.stats.mstats import winsorize
from sklearn.linear_model import LassoCV
from sklearn.feature_selection import RFECV
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.linear_model import LinearRegression
from sklearn.impute import IterativeImputer
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error, mean_squared_log_error, r2_score
from math import sqrt
import pmdarima as pm
from sklearn.preprocessing import RobustScaler
from statsmodels.graphics.gofplots import qqplot

exog_vars = ['tempmax', 'tempmin', 'temp', 'humidity', 'precip', 'temp_range', 'dew_point', 'rainy_days']


# Function to create new features
def create_new_features(data):
    # Add new features or transform existing ones here
    data['temp_range'] = data['tempmax'] - data['tempmin']
    return data

# Function to create rolling statistics features
def create_rolling_features(data, column, window):
    data[f"{column}_rolling_mean"] = data[column].rolling(window=window).mean()
    data[f"{column}_rolling_median"] = data[column].rolling(window=window).median()
    data[f"{column}_rolling_std"] = data[column].rolling(window=window).std()
    return data

# Function to create lag features
def create_lag_features(data, column, lag):
    data[f"{column}_lag{lag}"] = data[column].shift(lag)
    return data

# Function to create interaction features
def create_interaction_features(data, feature_pairs):
    for pair in feature_pairs:
        data[f"{pair[0]}_x_{pair[1]}"] = data[pair[0]] * data[pair[1]]
    return data

def calculate_dew_point(temp, humidity):
    a = 17.27
    b = 237.7
    alpha = ((a * temp) / (b + temp)) + np.log(humidity/100.0)
    dew_point = (b * alpha) / (a - alpha)
    return dew_point

def count_rainy_days(data, precip_col, window, threshold):
    return data[precip_col].rolling(window=window).apply(lambda x: (x > threshold).sum())    

# Function to Winsorize the target variable 'Leptospirosis'
def winsorize_target(data, target_col, limits):
    data[target_col] = winsorize(data[target_col], limits=limits)
    return data

# Perform cross-validation to ensure your model is generalizing well:
def perform_cross_validation(model, train_data, exog_vars, order, seasonal_order, n_splits=5):
    tscv = TimeSeriesSplit(n_splits=n_splits)
    sarima_cv_mape_scores = []

    for train_index, test_index in tscv.split(train_data):
        cv_train, cv_test = train_data.iloc[train_index], train_data.iloc[test_index]
        
        model_cv = model(cv_train['Leptospirosis'], exog=cv_train[exog_vars], order=order, seasonal_order=seasonal_order)
        model_cv_fit = model_cv.fit()
        
        sarima_cv_pred = model_cv_fit.forecast(steps=len(cv_test), exog=cv_test[exog_vars])
        sarima_cv_mape = mean_absolute_percentage_error(cv_test['Leptospirosis'], sarima_cv_pred)
        
        sarima_cv_mape_scores.append(sarima_cv_mape)

    return sarima_cv_mape_scores

# Function to perform Recursive Feature Elimination with Cross-Validation (RFECV)
def perform_rfecv(X, y):
    estimator = LinearRegression()
    rfecv = RFECV(estimator=estimator, step=1, cv=TimeSeriesSplit(n_splits=5), scoring='neg_mean_squared_error')
    rfecv.fit(X, y)
    return rfecv

#Function for MAPE
def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

def forecast_leptos_cases_weekly(leptos_data_path, weather_data_path):
    # Load the leptospirosis dataset
    leptospirosis_data = pd.read_excel(leptos_data_path)

    # Load the weather dataset
    weather_data = pd.read_excel(weather_data_path)

    # convert the datetime column to a datetime object
    leptospirosis_data['datetime'] = pd.to_datetime(leptospirosis_data['datetime'])
    weather_data['datetime'] = pd.to_datetime(weather_data['datetime'])

    # set the datetime column as the index and keep only the 'Leptospirosis' column
    leptospirosis_data = leptospirosis_data.set_index('datetime')[['Leptospirosis']]
    weather_data = weather_data.set_index('datetime')

    # Create an IterativeImputer object
    imputer = IterativeImputer(random_state=0, max_iter = 100)

    # Create new features before resampling
    weather_data = create_new_features(weather_data)
    weather_data['dew_point'] = calculate_dew_point(weather_data['temp'], weather_data['humidity'])

    #the window size is set to 7 (corresponding to a 7-day rolling window) and the threshold is set to 10 mm 
    #(i.e., any day with precipitation greater than 10 mm is counted as a rainy day).
    weather_data['rainy_days'] = count_rainy_days(weather_data, 'precip', window=7, threshold=10)

    # Resample the data to weekly frequency using the mean
    weather_data_weekly = weather_data.resample('W').mean()

    # Merge leptospirosis and weather datasets
    merged_data = pd.merge(leptospirosis_data, weather_data_weekly, left_index=True, right_index=True, how='inner')

    # Impute missing values using the IterativeImputer object
    merged_data = pd.DataFrame(imputer.fit_transform(merged_data), columns=merged_data.columns, index=merged_data.index)

    # Apply Winsorization to the target variable 'Leptospirosis'
    limits = (0.01, 0.01)
    merged_data = winsorize_target(merged_data, 'Leptospirosis', limits)

    #ADF test  less than 0.05, which suggests that we should reject the null hypothesis for each of the variables.
    result = adfuller(merged_data.Leptospirosis.dropna())
    print('ADF Statistic: %f' % result[0])
    print('p-value: %f' % result[1])

    plt.rcParams.update({'figure.figsize':(12,7), 'figure.dpi':250})

    # Original Series
    fig, axes = plt.subplots(4, 1)

    # Plotting the original series
    merged_data.Leptospirosis.plot(ax=axes[0])
    axes[0].set_title('Original Series')

    # ACF plot
    plot_acf(merged_data.Leptospirosis, ax=axes[1])

    # PACF plot (AR)
    plot_pacf(merged_data.Leptospirosis.dropna(), ax=axes[2])

    # ACF plot (MA)
    plot_acf(merged_data.Leptospirosis.dropna(), ax=axes[3])

    plt.subplots_adjust(hspace=0.75)  # Adjust the vertical spacing between subplots

    plt.savefig('static/forecasting/leptos_original_series.png')

    # Create rolling features
    rolling_columns = ['Leptospirosis', 'tempmax', 'tempmin', 'temp', 'humidity', 'precip', 'temp_range', 'dew_point', 'rainy_days']  # added 'temp_range', 'dew_point', and 'rainy_days_count'
    for col in rolling_columns:
        merged_data = create_rolling_features(merged_data, col, window=7)

    # Create lag features
    lag_columns = ['Leptospirosis', 'tempmax', 'tempmin', 'temp', 'humidity', 'precip', 'temp_range', 'dew_point', 'rainy_days']
    for col in lag_columns:
        merged_data = create_lag_features(merged_data, col, lag=3)

    # Create interaction features
    feature_pairs = [('tempmax', 'humidity'), ('tempmin', 'humidity'), ('temp', 'humidity'), ('temp', 'precip')]
    merged_data = create_interaction_features(merged_data, feature_pairs)

    # Create a list of all exogenous variables
    exog_vars.extend([f"{col}_rolling_{stat}" for col in rolling_columns for stat in ['mean', 'median', 'std']])
    exog_vars.extend([f"{col}_lag3" for col in lag_columns])
    exog_vars.extend([f"{pair[0]}_x_{pair[1]}" for pair in feature_pairs])

    # Fill NaN values with mean
    merged_data = merged_data.apply(lambda x: x.fillna(x.mean()),axis=0)

    # Now apply imputation
    merged_data[exog_vars] = imputer.fit_transform(merged_data[exog_vars])

    # split the dataset into training and testing sets
    train_size = int(len(merged_data) * 0.8)
    train_data, test_data = merged_data[:train_size], merged_data[train_size:]

    #Outliers and Noise: Apply robust scaling to the exogenous variables
    robust_scaler = RobustScaler()
    merged_data[exog_vars] = robust_scaler.fit_transform(merged_data[exog_vars])

    for var in exog_vars:
        result = adfuller(merged_data[var].dropna())
        print('ADF Statistic for {}: {}'.format(var, result[0]))
        print('p-value: {}'.format(result[1]))

    # Perform feature selection using LassoCV
    lasso_cv = LassoCV(cv=TimeSeriesSplit(n_splits=10), random_state=0)
    lasso_cv.fit(train_data[exog_vars], train_data['Leptospirosis'])
    selected_features = [exog_var for coef, exog_var in zip(lasso_cv.coef_, exog_vars) if coef != 0]

    # Perform Recursive Feature Elimination with Cross-Validation (RFECV)
    rfecv = perform_rfecv(train_data[selected_features], train_data['Leptospirosis'])
    selected_features = train_data[selected_features].columns[rfecv.get_support()]

    # Find the best ARIMA model
    best_model = pm.auto_arima(train_data['Leptospirosis'],
                            seasonal=True, m=12, stepwise=True,
                            suppress_warnings=True, trace=True)

    # Get the order, seasonal_order, and exogenous variables from the best model
    order = best_model.order
    seasonal_order = best_model.seasonal_order

    # Fit your model
    model = SARIMAX(train_data['Leptospirosis'], exog=train_data[selected_features],
                    order=order, seasonal_order=seasonal_order)
    model_fit = model.fit()

    # Call the perform_cross_validation function
    sarima_cv_mape_scores = perform_cross_validation(SARIMAX, train_data, selected_features, order, seasonal_order)

    # Calculate standard deviation of cross-validation scores
    std_sarima_cv_mape = np.std(sarima_cv_mape_scores)
    print('Standard Deviation of SARIMA CV MAPE scores:', std_sarima_cv_mape)

    # Predict using the SARIMA model with the selected exogenous variables
    forecast_horizon = len(test_data)
    exog_test_data = test_data[selected_features].iloc[:forecast_horizon]
    sarima_pred = model_fit.get_prediction(start=test_data.index[0], end=test_data.index[-1], exog=exog_test_data)

    # Residual analysis
    residuals = test_data['Leptospirosis'] - sarima_pred.predicted_mean

    # Evaluate the SARIMA model using multiple metrics
    sarima_rmse = sqrt(mean_squared_error(test_data['Leptospirosis'], sarima_pred.predicted_mean))
    sarima_mae = mean_absolute_error(test_data['Leptospirosis'], sarima_pred.predicted_mean)
    sarima_mape = mean_absolute_percentage_error(test_data['Leptospirosis'], sarima_pred.predicted_mean)
    sarima_r2 = r2_score(test_data['Leptospirosis'], sarima_pred.predicted_mean)

    print('RMSE of SARIMA model:', sarima_rmse)
    print('MAE of SARIMA model:', sarima_mae)
    print('MAPE of SARIMA model:', sarima_mape)
    print('R-squared of SARIMA model:', sarima_r2)

    # Plot residuals
    plt.figure(figsize=(10,6))
    plt.plot(residuals)
    plt.title('Residuals from SARIMA Model')
    plt.ylabel('Error')
    plt.xlabel('Date')
    plt.savefig('static/forecasting/leptos_plot_residuals.png')

    # Plot ACF of residuals
    plt.figure(figsize=(10,6))
    plot_acf(residuals, lags=50, zero=False)
    plt.title('Autocorrelation Function of Residuals from SARIMA Model')
    plt.savefig('static/forecasting/leptos_acf_residuals.png')

    # Plot histogram of residuals
    plt.figure(figsize=(10,6))
    residuals.hist(bins=20)
    plt.title('Histogram of Residuals from SARIMA Model')
    plt.savefig('static/forecasting/leptos_histogram_residuals.png')

    # Plot QQ plot of residuals
    plt.figure(figsize=(10,6))
    qqplot(residuals, line='s')
    plt.title('QQ Plot of Residuals from SARIMA Model')
    plt.savefig('static/forecasting/leptos_qqplot_residuals.png')

    # Plot the forecast along with the actual values
    plt.figure(figsize=(20, 6))
    plt.plot(train_data.index, train_data['Leptospirosis'], label='Training Data')
    plt.plot(test_data.index, test_data['Leptospirosis'], label='Testing Data')
    plt.plot(test_data.index, sarima_pred.predicted_mean, label='SARIMA Predictions')
    plt.xlabel('Date')
    plt.ylabel('Number of Leptospirosis Cases')
    plt.title('Weekly Leptospirosis Cases Forecast in the Philippines')
    plt.savefig('static/forecasting/weekly_leptos_forecast.png')

def forecast_leptos_cases_monthly(leptos_data_path, weather_data_path):
    # Load the leptospirosis dataset
    leptos_data = pd.read_excel(leptos_data_path)

    # Load the weather dataset
    weather_data = pd.read_excel(weather_data_path)

    # convert the datetime column to a datetime object
    leptos_data['datetime'] = pd.to_datetime(leptos_data['datetime'])
    weather_data['datetime'] = pd.to_datetime(weather_data['datetime'])

    # set the datetime column as the index and keep only the 'Leptospirosis' column
    leptos_data = leptos_data.set_index('datetime')[['Leptospirosis']]
    weather_data = weather_data.set_index('datetime')

    # Create an IterativeImputer object
    imputer = IterativeImputer(random_state=0, max_iter = 100)

    # Create new features before resampling
    weather_data = create_new_features(weather_data)
    weather_data['dew_point'] = calculate_dew_point(weather_data['temp'], weather_data['humidity'])

    #the window size is set to 7 (corresponding to a 7-day rolling window) and the threshold is set to 10 mm 
    #(i.e., any day with precipitation greater than 10 mm is counted as a rainy day).
    weather_data['rainy_days'] = count_rainy_days(weather_data, 'precip', window=7, threshold=10)

    # Resample the data to monthly frequency using the mean
    leptos_data_monthly = leptos_data.resample('M').mean()
    weather_data_monthly = weather_data.resample('M').mean()

    # Merge leptos and weather datasets
    merged_data = pd.merge(leptos_data_monthly, weather_data_monthly, left_index=True, right_index=True, how='inner')

    # Impute missing values using the IterativeImputer object
    merged_data = pd.DataFrame(imputer.fit_transform(merged_data), columns=merged_data.columns, index=merged_data.index)

    # Apply Winsorization to the target variable 'Leptospirosis'
    limits = (0.01, 0.01)
    merged_data = winsorize_target(merged_data, 'Leptospirosis', limits)

    # Create rolling features
    rolling_columns = ['Leptospirosis', 'tempmax', 'tempmin', 'temp', 'humidity', 'precip', 'temp_range', 'dew_point', 'rainy_days']  # added 'temp_range', 'dew_point', and 'rainy_days_count'
    for col in rolling_columns:
        merged_data = create_rolling_features(merged_data, col, window=2)

    # Create lag features
    lag_columns = ['Leptospirosis', 'tempmax', 'tempmin', 'temp', 'humidity', 'precip', 'temp_range', 'dew_point', 'rainy_days']
    for col in lag_columns:
        merged_data = create_lag_features(merged_data, col, lag=3)

    # Create interaction features
    feature_pairs = [('tempmax', 'humidity'), ('tempmin', 'humidity'), ('temp', 'humidity'), ('temp', 'precip')]
    merged_data = create_interaction_features(merged_data, feature_pairs)

    # Create a list of all exogenous variables
    exog_vars.extend([f"{col}_rolling_{stat}" for col in rolling_columns for stat in ['mean', 'median', 'std']])
    exog_vars.extend([f"{col}_lag3" for col in lag_columns])
    exog_vars.extend([f"{pair[0]}_x_{pair[1]}" for pair in feature_pairs])

    # Fill NaN values with mean
    merged_data = merged_data.apply(lambda x: x.fillna(x.mean()),axis=0)

    # Impute missing values using the IterativeImputer object
    merged_data[exog_vars] = imputer.fit_transform(merged_data[exog_vars])

    # split the dataset into training and testing sets
    train_size = int(len(merged_data) * 0.8)
    train_data, test_data = merged_data[:train_size], merged_data[train_size:]

    # Perform feature selection using LassoCV
    lasso_cv = LassoCV(cv=TimeSeriesSplit(n_splits=5), random_state=0)
    lasso_cv.fit(train_data[exog_vars], train_data['Leptospirosis'])
    selected_features = [exog_var for coef, exog_var in zip(lasso_cv.coef_, exog_vars) if coef != 0]

    # Perform Recursive Feature Elimination with Cross-Validation (RFECV)
    rfecv = perform_rfecv(train_data[selected_features], train_data['Leptospirosis'])
    selected_features = train_data[selected_features].columns[rfecv.get_support()]

    # Find the best ARIMA model
    best_model = pm.auto_arima(train_data['Leptospirosis'],
                            seasonal=True, m=12, stepwise=True,
                            suppress_warnings=True, trace=True)

    # Get the order, seasonal_order, and exogenous variables from the best model
    order = best_model.order
    seasonal_order = best_model.seasonal_order

    # train and fit the SARIMA model with the selected exogenous variables
    model = SARIMAX(train_data['Leptospirosis'], exog=train_data[selected_features],
                    order=order, seasonal_order=seasonal_order)
    model_fit = model.fit()

    # Predict using the SARIMA model with the selected exogenous variables
    forecast_horizon = len(test_data)
    exog_test_data = test_data[selected_features].iloc[:forecast_horizon]
    sarima_pred = model_fit.get_prediction(start=test_data.index[0], end=test_data.index[-1], exog=exog_test_data)

    # Evaluate the SARIMA model using multiple metrics
    sarima_rmse = sqrt(mean_squared_error(test_data['Leptospirosis'], sarima_pred.predicted_mean))
    sarima_mae = mean_absolute_error(test_data['Leptospirosis'], sarima_pred.predicted_mean)
    sarima_mape = mean_absolute_percentage_error(test_data['Leptospirosis'], sarima_pred.predicted_mean)
    sarima_r2 = r2_score(test_data['Leptospirosis'], sarima_pred.predicted_mean)

    print('RMSE of SARIMA model:', sarima_rmse)
    print('MAE of SARIMA model:', sarima_mae)
    print('MAPE of SARIMA model:', sarima_mape)
    print('R-squared of SARIMA model:', sarima_r2)

    # Plot the forecast along with the actual values
    plt.figure(figsize=(12, 6))
    plt.plot(train_data.index, train_data['Leptospirosis'], label='Training Data')
    plt.plot(test_data.index, test_data['Leptospirosis'], label='Testing Data')
    plt.plot(test_data.index, sarima_pred.predicted_mean, label='SARIMA Predictions')
    plt.xlabel('Date')
    plt.ylabel('Number of Leptospirosis Cases')
    plt.title('Monthly Leptospirosis Cases Forecast in the Philippines')
    plt.savefig('static/forecasting/monthly_leptos_forecast.png')