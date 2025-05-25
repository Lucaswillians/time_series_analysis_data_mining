import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import sys
from pathlib import Path

file_path = Path("./data/atividade_1.csv")
if not file_path.exists():
    sys.exit(f"Arquivo não encontrado: {file_path}")

df = pd.read_csv(file_path, delimiter=';')

df["valor"] = (df["valor"]
               .astype(str)
               .str.replace(",", ".", regex=False)
               .astype(float))
# converte a coluna de datas
df["data"] = pd.to_datetime(df["data"], dayfirst=True)

df = df.sort_values("data").reset_index(drop=True)

def calc_trend(series: pd.Series, threshold: float = 0.01) -> str:
    x = np.arange(len(series))
    slope, *_ = linregress(x, series)
    if slope > threshold:
        return "crescente", slope
    elif slope < -threshold:
        return "decrescente", slope
    else:
        return "estável", slope

def plot_series(ax, dates, values, slope, intercept, title):
    ax.plot(dates, values, label="Endividamento (%)")
    ax.plot(dates, intercept + slope*np.arange(len(values)),
            "--", label="Linha de tendência")
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("Ano")
    ax.set_ylabel("% da renda comprometida")
    ax.legend()

trend_full, slope_full = calc_trend(df["valor"])
intercept_full = df["valor"].iloc[0]

jan_ult_5anos = df["data"].max() - pd.DateOffset(years=5)
recent = df[df["data"] >= jan_ult_5anos].reset_index(drop=True)
trend_recent, slope_recent = calc_trend(recent["valor"])
intercept_recent = recent["valor"].iloc[0]

print("\n==== Tendências calculadas ====")
print(f"Tendência geral (2005-2025): {trend_full.capitalize()}  "
      f"|  Inclinação ≈ {slope_full:.3f} ponto percentual/mês")
print(f"Tendência últimos 5 anos:      {trend_recent.capitalize()}  "
      f"|  Inclinação ≈ {slope_recent:.3f} ponto percentual/mês")

plt.style.use("seaborn-v0_8-whitegrid")

fig1, ax1 = plt.subplots(figsize=(10, 5))
plot_series(
    ax1,
    df["data"],
    df["valor"],
    slope_full,
    intercept_full,
    f"Endividamento das famílias brasileiras (jan/2005 – {df['data'].max().strftime('%b/%Y')})\n"
    f"Tendência geral: {trend_full.capitalize()}"
)

fig2, ax2 = plt.subplots(figsize=(10, 5))
plot_series(
    ax2,
    recent["data"],
    recent["valor"],
    slope_recent,
    intercept_recent,
    f"Endividamento – últimos 5 anos ({recent['data'].min():%b/%Y} – {recent['data'].max():%b/%Y})\n"
    f"Tendência: {trend_recent.capitalize()}"
)

plt.tight_layout()
plt.show()
