import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from pathlib import Path
import sys

# ======== AJUSTE SEUS CAMINHOS AQUI ========
FILE_RECEITA = Path("./data/atv2_receita.csv")
FILE_SALDO   = Path("./data/atv2_saldo.csv")
# ===========================================

# ---------- Funções utilitárias ----------
def ler_csv(path: Path, sep=";") -> pd.DataFrame:
    "Lê, converte vírgula decimal, parseia data e devolve ordenado."
    df = pd.read_csv(path, delimiter=sep)
    df["valor"] = (df["valor"].astype(str)
                   .str.replace(",", ".", regex=False)
                   .astype(float))
    df["data"] = pd.to_datetime(df["data"], dayfirst=True)
    return df.sort_values("data").reset_index(drop=True)

def tendencia(series: pd.Series, thr_rel: float = 0.001):
    "Classifica a série como crescente/estável/decrescente."
    x = np.arange(len(series))
    slope, intercept, r, p, stderr = linregress(x, series)
    thr_abs = thr_rel * series.abs().mean()
    if slope > thr_abs:
        tag = "crescente"
    elif slope < -thr_abs:
        tag = "decrescente"
    else:
        tag = "estável"
    return tag, slope, intercept, r**2

def plota(ax, datas, valores, slope, intercept, titulo):
    ax.plot(datas, valores, label="Série")
    ax.plot(datas, intercept + slope*np.arange(len(valores)),
            "--", label="Tendência")
    ax.set_title(titulo, fontsize=11)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Valor")
    ax.legend()

# ---------- Leitura ----------
if not (FILE_RECEITA.exists() and FILE_SALDO.exists()):
    sys.exit("Arquivos não encontrados. Verifique FILE_RECEITA e FILE_SALDO.")

df_rec = ler_csv(FILE_RECEITA)
df_sal = ler_csv(FILE_SALDO)

# ---------- Tendências ----------
tag_rec, slope_rec, int_rec, r2_rec = tendencia(df_rec["valor"])
tag_sal, slope_sal, int_sal, r2_sal = tendencia(df_sal["valor"])

print("\n==== Tendências Calculadas ====")
print(f"Receita: {tag_rec.capitalize()}  |  Inclinação = {slope_rec:.2f}  |  R² = {r2_rec:.2f}")
print(f"Saldo  : {tag_sal.capitalize()}  |  Inclinação = {slope_sal:.2f}  |  R² = {r2_sal:.2f}")

# ---------- Gráficos individuais ----------
plt.style.use("seaborn-v0_8-whitegrid")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

plota(
    ax1, df_rec["data"], df_rec["valor"],
    slope_rec, int_rec,
    f"Receita (jan/1995 – {df_rec['data'].max():%b/%Y})\nTendência: {tag_rec.capitalize()}"
)
plota(
    ax2, df_sal["data"], df_sal["valor"],
    slope_sal, int_sal,
    f"Saldo (jan/1995 – {df_sal['data'].max():%b/%Y})\nTendência: {tag_sal.capitalize()}"
)
plt.tight_layout()

fig2, ax3 = plt.subplots(figsize=(10, 5))
ax3.plot(df_rec["data"], df_rec["valor"], label="Receita", linewidth=1.5)
ax3.plot(df_sal["data"], df_sal["valor"], label="Saldo", linewidth=1.2)
ax3.set_title("Receita vs. Saldo – Evolução Comparativa")
ax3.set_xlabel("Ano")
ax3.set_ylabel("Valor")
ax3.legend()
plt.tight_layout()

plt.show()
