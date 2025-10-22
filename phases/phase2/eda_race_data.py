# %% [markdown]
# # Professional EDA Notebook for Race Data
# This notebook explores the cleaned race data. We analyze distributions, correlations, top riders, and point-based metrics. Each plot is accompanied by descriptive statistics and observations.

# %%
# Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set plot style
plt.rcParams['figure.figsize'] = (10,6)
sns.set_style("whitegrid")

# %%
# Load data
data_path = "../../Joel/processed_data/race_data_processed_v3.csv"
df = pd.read_csv(data_path, parse_dates=['Date','birthdate'])
print(f"Data shape: {df.shape}")
df.head()

# %% [markdown]
# ## Overview and Missing Values

# %%
display(df.info())

missing_pct = (df.isnull().sum()/len(df)*100).sort_values(ascending=False)
print("Missing values (% of dataset):")
display(missing_pct[missing_pct>0])

# %% [markdown]
# Observations:
# - Most columns are complete.
# - `birthdate` and `country` have ~23% missing.
# - Rolling metrics and ranks are precomputed.
# - Missing birthdates may affect `age_at_race`.

# %% [markdown]
# ## Target Variable Analysis (`is_top_10`)

# %%
sns.countplot(x='is_top_10', data=df)
plt.title("Distribution of Top-10 Finishes")
plt.xlabel("Is Top 10")
plt.ylabel("Count")
plt.show()

counts = df['is_top_10'].value_counts()
percentages = df['is_top_10'].value_counts(normalize=True)*100
print("Counts:")
print(counts)
print("\nPercentages:")
print(percentages)

# %% [markdown]
# Observations:
# - Only ~6% of entries are top-10 finishes.
# - The target is highly imbalanced, which may affect modeling.

# %% [markdown]
# ## Numeric Features Summary

# %%
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
display(df[numeric_cols].describe().T)

# %% [markdown]
# Observations:
# - `Rnk_clean`, `Length_km`, `Time_sec`, `Timelag_sec` have wide ranges and some outliers.
# - `age_at_race` mostly ranges between 18–40.
# - Rolling metrics are precomputed and ready for analysis.

# %% [markdown]
# ## Numeric Features Plots with Descriptions

# %%
plot_cols = ['Age','age_at_race','Length_km','Time_sec','Timelag_sec','Rnk_clean',
             'rolling_avg_rank_5','rolling_avg_rank_10','recent_top10_count','recent_top10_rate',
             'UCI_total','UCI_avg','UCI_max','Pnt_total','Pnt_avg','Pnt_max']

for col in plot_cols:
    plt.figure()
    sns.histplot(df[col], bins=50, kde=True)
    plt.title(f"Distribution of {col}")
    plt.xlabel(col)
    plt.ylabel("Count")
    plt.show()
    
    desc = df[col].describe()
    print(f"{col} statistics:")
    print(f"Mean: {desc['mean']:.2f}, Median: {desc['50%']:.2f}, Min: {desc['min']}, Max: {desc['max']}, Std: {desc['std']:.2f}")
    
    # Observations in words
    if col in ['Age','age_at_race']:
        print(f"Most riders are between 18 and 40 years old.\n")
    elif col == 'Length_km':
        print(f"Stage lengths vary widely, from {desc['min']} km to {desc['max']} km, mean {desc['mean']:.1f} km.\n")
    elif col in ['Time_sec','Timelag_sec']:
        print(f"Time distributions have long tails; median is {desc['50%']:.0f} sec, mean {desc['mean']:.0f} sec.\n")
    elif col == 'Rnk_clean':
        print(f"Ranking shows a heavy right tail; most riders are below {desc['50%']:.0f}.\n")
    elif 'rolling_avg_rank' in col:
        print(f"{col} ranges widely and indicates recent performance trends.\n")
    elif 'recent_top10' in col:
        print(f"{col} is skewed towards 0, reflecting few top-10 finishes recently.\n")
    elif 'UCI' in col or 'Pnt' in col:
        print(f"{col} shows point accumulation; some riders have very high max values indicating elite performance.\n")
    else:
        print("\n")

# %% [markdown]
# ## Correlation Heatmap

# %%
plt.figure(figsize=(14,10))
corr = df[numeric_cols].corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Correlation Heatmap of Numeric Features")
plt.show()

# %% [markdown]
# Observations:
# - `Rnk_clean` correlates strongly with rolling average ranks.
# - `Time_sec` and `Timelag_sec` correlate moderately with ranking.
# - UCI points and race points correlate with each other and with rank metrics.

# %% [markdown]
# ## Categorical Features Analysis

# %%
cat_cols = ['Team','Race_Name','country','Stage_Type','race_tier']

for col in cat_cols:
    plt.figure(figsize=(12,4))
    top10 = df[col].value_counts().index[:10]
    sns.countplot(y=col, data=df, order=top10)
    plt.title(f"Top 10 Categories in {col}")
    plt.xlabel("Count")
    plt.ylabel(col)
    plt.show()
    
    top_counts = df[col].value_counts().head(10)
    print(f"Top 10 {col} counts:")
    display(top_counts)
    print("\n")

# %% [markdown]
# Observations:
# - Teams: most common teams dominate the dataset.
# - Races: Tour de France, Vuelta a España, and Giro d’Italia are the most frequent.
# - Countries: Italy, France, Spain, and Belgium dominate.
# - Stage types: majority are road races (`RR`), few time trials or sprints.
# - Race tiers: mostly Tier 2 events.

# %% [markdown]
# ## Next Steps
# - Feature engineering: age groups, normalized metrics.
# - Explore top riders' historical performance.
# - Prepare data for modeling: handle imbalance, scale features.
# - Consider advanced visualization: top riders by UCI points over time, performance trends.
