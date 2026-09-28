import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("transacoes.csv", encoding="latin1")
df["plataforma"] = "Mobile"

df["valor"] = df["valor"].fillna(df.groupby("estado_cliente")["valor"].transform("median"))

df["data_transacao"] = pd.to_datetime(df["data_transacao"]).astype("datetime64[ns]")
df["data_transacao"] = df["data_transacao"].dt.tz_localize("America/Sao_Paulo")
df["dia_semana"] = df["data_transacao"].dt.day_name()
df["mes"] = df["data_transacao"].dt.month

df = df.drop_duplicates(keep="first").reset_index(drop=True)

filtro = (df["mes"] == 9) & ((df["estado_cliente"] == "SP") | (df["estado_cliente"] == "RJ")) & (df["valor"] > 5000)
setembro_sp_rj = df[filtro]

risco_dict = {"C100": "Baixo", "C101": "Alto", "C102": "Médio", "C103": "Baixo", "C104": "Alto"}
df["nivel_risco"] = df["id_cliente"].map(risco_dict)

tabela = pd.pivot_table(df, values="valor", index="mes", columns="nivel_risco", aggfunc="sum", margins=True, margins_name="Total")


def calcular_zscore(dados):
    media = dados.groupby("estado_cliente")["valor"].transform("mean")
    desvio = dados.groupby("estado_cliente")["valor"].transform("std", ddof=0)
    return (dados["valor"] - media) / desvio


df["zscore"] = calcular_zscore(df)
anomalias = df[df["zscore"] > 2.5]

diario = df.set_index("data_transacao")["valor"].resample("D").sum()
media_movel = diario.rolling(7).mean()

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(diario.index, diario.values, label="Total diário")
ax.plot(media_movel.index, media_movel.values, label="Média móvel de 7 dias")
ax.set_ylim(bottom=0)
ax.set_title("Valor total de transações por dia")
ax.set_xlabel("Data")
ax.set_ylabel("Valor (R$)")
ax.legend()
fig.autofmt_xdate()
fig.savefig("grafico_transacoes.png", dpi=150)

print(df.head())
print(len(setembro_sp_rj), "transações em setembro (SP/RJ, acima de 5000)")
print(tabela)
print(len(anomalias), "anomalias")
print(anomalias)
