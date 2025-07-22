# %%
import numpy as np
import tensorflow as tf
import tensorflow_probability as tfp
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import arviz as az
import statsmodels.tsa.seasonal as tsas
import os

from sklearn.metrics import r2_score
from tqdm.notebook import tqdm
from IPython.display import set_matplotlib_formats, display

tfb = tfp.bijectors
tfd = tfp.distributions
tfk = tfp.math.psd_kernels

sns.set(rc={"figure.dpi":90, 'savefig.dpi':300})
sns.set_context('notebook')
sns.set_style("ticks")
set_matplotlib_formats('retina')

# %% [markdown]
# ### Helpers

# %%
def transform(mean=0., std=1., inverse=False, offset=0.01):
    bijector = tfp.bijectors.Softplus()
    def method(X):
        if inverse:
            X = (X * std) + mean
            X = bijector.forward(X) - offset
        else:
            X = bijector.inverse(X + offset)
            X = (X - mean) / std
        return X
    return method

def load_dataset(path, sheet):
    df = pd.ExcelFile(path)
    df = pd.read_excel(df, sheet, parse_dates=True, index_col=0,)
    df.dropna(how='any', inplace=True)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    return df

# %% [markdown]
# ### Load Dataset

# %%
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(BASE_DIR, 'data', 'data-updated.xlsx')
SHEET = 'Sheet4'

Dataset = load_dataset(PATH, SHEET).astype('float32')
N_train = int(0.8 * Dataset.shape[0])
Dataset_train, Dataset_test = Dataset[:N_train], Dataset[N_train:]
mean, std = Dataset.mean().values, Dataset.std().values
Dataset_train = tfp.sts.regularize_series(Dataset_train)
X_train = tf.math.round(Dataset_train.values)
X_train = transform(mean, std)(X_train)
X_train = tf.cast(tf.reshape(X_train, [-1]), tf.float32)

# %% [markdown]
# ### Plot Dataset

# %%
fig, ax = plt.subplots(figsize=(15, 5))
ax.plot(Dataset, color='teal')
ax.set_ylabel('Number of Cases')
ax.set_title(f'{Dataset.columns[0]} Weekly Cases')
ax.legend(loc='upper right')
plt.savefig(f'{Dataset.columns[0]}.svg')
plt.show()

# %% [markdown]
# ### Plot Dataset Seasonal and Residual Comppnents

# %%
dataset_series = Dataset.squeeze()

# Apply STL decomposition
stl = tsas.STL(dataset_series, period=12*4).fit().plot()
plt.savefig(f'Decomp_{Dataset.columns[0]}.svg')

# %% [markdown]
# ### Build STS Component
# 
# Note that each disease have specifically tuned components. Below is configured for the Dengue group.

# %%
def STS_components(y):
    sts_month_of_year = tfp.sts.Seasonal(
        num_seasons=12,
        num_steps_per_season=4,
        observed_time_series=y,
        allow_drift=True,
        name='sts_month_of_year')

    sts_week_of_month = tfp.sts.Seasonal(
        num_seasons=4,
        observed_time_series=y,
        allow_drift=True,
        name='sts_week_of_month')

    sts_week_of_year = tfp.sts.Seasonal(
        num_seasons=12*4,
        observed_time_series=y,
        allow_drift=True,
        name='sts_week_of_year')

    sts_semiannually = tfp.sts.Seasonal(
        num_seasons=6,
        num_steps_per_season=8,
        observed_time_series=y,
        allow_drift=True,
        name='sts_semiannually')

    sts_yearly_trend = tfp.sts.SmoothSeasonal(
        period=int(4*12*(1)),
        frequency_multipliers=[c for c in range(10)],
        allow_drift=True,
        observed_time_series=y,
        name='sts_yearly_trend')
    
    sts_long_seasonal_trend = tfp.sts.Seasonal(
        num_seasons=int(4*12*(3.25)),
        allow_drift=True,
        observed_time_series=y,
        name='sts_long_seasonal_trend')

    sts_local_trend = tfp.sts.LocalLinearTrend(
        observed_time_series=y,
        name='sts_local_trend')

    sts_residuals = tfp.sts.AutoregressiveIntegratedMovingAverage(
        ar_order=1,
        ma_order=1,
        observed_time_series=y,
        name='sts_residuals')
    
    sts_AR = tfp.sts.Autoregressive(
        order=1,
        observed_time_series=y,
        name='sts_AR'
    )

    return [
        sts_month_of_year,
        sts_yearly_trend,
        sts_residuals]

components = STS_components(X_train)
model = tfp.sts.Sum(components=components, observed_time_series=X_train) 
variational_posteriors = tfp.sts.build_factored_surrogate_posterior(model=model)

# %% [markdown]
# ### Fit STS using Variational Inference
# 
# Increase number of steps if the loss is still decreasing

# %%
num_steps = 80
lr_schedule = tf.keras.optimizers.schedules.CosineDecay(0.1, num_steps, alpha=0.0000001)
optimizer = tf.optimizers.Adam(learning_rate=lr_schedule)

@tf.function
def fit():
    ELBO_loss = tfp.vi.fit_surrogate_posterior(
        target_log_prob_fn=model.joint_log_prob(observed_time_series=X_train),
        surrogate_posterior=variational_posteriors,
        optimizer=optimizer,
        num_steps=num_steps)
    return ELBO_loss

ELBO_loss = fit()
plt.plot(ELBO_loss)
plt.ylabel('-ELBO'); 
plt.xlabel('Iteration')
plt.title(f'Training ELBO Loss - {Dataset.columns[0]}')
plt.savefig(f'Loss_{Dataset.columns[0]}.svg')
plt.show()

# %% [markdown]
# ### Plot Forecasts

# %%
inverse_transform = transform(mean, std, inverse=True)
parameter_samples = variational_posteriors.sample(100)

forecast_distribution = tfp.sts.forecast(
    model,
    observed_time_series=X_train,
    parameter_samples=parameter_samples,
    num_steps_forecast=len(Dataset_test))

forecast = (
    forecast_distribution.mean().numpy()[..., 0],
    forecast_distribution.stddev().numpy()[..., 0])

forecast_mean = tf.math.round(inverse_transform(forecast[0]))
forecast_scale = transform(0., std, inverse=True)(forecast[1])
forecast_samples = forecast_distribution.sample(250) 

Dataset_test = Dataset[N_train:]
Dataset_test.insert(
    loc=0,
    column='pred',
    value=forecast_mean)

HDI = inverse_transform(az.hdi(forecast_samples[None, ...].numpy(), hdi_prob=0.95))
MSLE = tf.keras.losses.MeanSquaredLogarithmicError()(
    Dataset_test[Dataset.columns[0]].values, forecast_mean)

offset = tf.reduce_mean(Dataset_test[Dataset.columns[0]])
test = Dataset_test[Dataset.columns[0]] + offset
pred = Dataset_test['pred'] + offset

MAPE = np.mean(np.abs((test- pred) / test)) * 100


fig, ax = plt.subplots(figsize=(12, 5))
t = np.array(Dataset_test.index.to_pydatetime(), dtype=np.datetime64)
plt.fill_between(t, 
                 HDI[..., 0, 0], 
                 HDI[..., 0, 1], 
                 color='orange', alpha=0.25, label='95% HDI')
ax.plot(Dataset_train, color='teal', linewidth=1.5, label='Train')
sns.scatterplot(Dataset_test[Dataset.columns[0]], color='red', label='Test', s=50)
ax.plot(Dataset_test['pred'], color='blue', linewidth=2, label='Forecast')
ax.set_ylabel('Number of Cases'); ax.set_xlabel('Date')
ax.set_title(f'MSLE:  {MSLE :3.2f}%     MAPE:  {MAPE :3.2f}%                       Model: STS - Variational Inference Fit')
fig.suptitle(f'{Dataset.columns[0]} Weekly Cases')
ax.legend(loc='upper left')
ax.set_ylim([-50, Dataset.max().values + 0.05 * Dataset.max().values]);
plt.savefig(f'Forecast_{Dataset.columns[0]}.svg')
plt.show()

# %% [markdown]
# ### Visualize Posterior Samples and Seasonal Effects

# %%
parameter_samples = variational_posteriors.sample(80)
component_dists = tfp.sts.decompose_by_component(
    model=model,
    observed_time_series=X_train,
    parameter_samples=parameter_samples)
component_means, component_stddevs = (
    {k.name: c.mean() for k, c in component_dists.items()},
    {k.name: c.stddev() for k, c in component_dists.items()})
num_components = len(component_means)
fig, ax = plt.subplots(num_components, 1, figsize= (12, 12))
for i, component_name in enumerate(component_means.keys()):
    component_mean = component_means[component_name]
    component_stddev = component_stddevs[component_name]
    
    ax[i].plot(Dataset_train.index.values, component_mean)
    
    ax[i].fill_between(
        x=Dataset_train.index.values,
        y1=component_mean - 2*component_stddev,
        y2=component_mean + 2*component_stddev,
        alpha=0.4
    )
    ax[i].set(title=component_name)
plt.savefig(f'STS_{Dataset.columns[0]}.svg')
plt.tight_layout()
plt.show()


