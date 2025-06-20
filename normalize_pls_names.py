import pandas as pd

df = pd.read_json('pls_full_2.json')

nomes_originais_sf = df[
    (df["casa_origem"] == "Senado Federal") &
    (df["nome_original"].notna()) &
    (df["nome_original"].astype(str).str.strip() != "")
]["nome_original"].astype(str).str.strip()

df = df[~((df["nome"].isin(nomes_originais_sf)) & (df["casa_origem"] == "Câmara dos Deputados"))].reset_index(drop=True)
df.to_json('pls_full_2_norm.json')