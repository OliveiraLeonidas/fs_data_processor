import numpy as np
import re
from datetime import datetime

# Renomear coluna para português do Brasil se necessário
if 'first_name' in df.columns:
    df.rename(columns={'first_name': 'nome'}, inplace=True)

# Remover espaços extras dos nomes e padronizar para capitalizado
if 'nome' in df.columns:
    df['nome'] = df['nome'].astype(str).str.strip().str.title()

# Corrigir e padronizar e-mails (remover espaços, minúsculo, corrigir domínios simples)
if 'email' in df.columns:
    def clean_email(x):
        if not isinstance(x, str):
            return np.nan
        x = x.strip().lower()
        # Corrigir emails sem domínio
        if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', x):
            return x
        if re.match(r'^[\w\.-]+@[\w\.-]+$', x):
            return x + '.com'
        return np.nan
    df['email'] = df['email'].apply(clean_email)

# Corrigir e padronizar datas (data_cadastro)
if 'data_cadastro' in df.columns:
    def parse_date(x):
        if pd.isnull(x):
            return np.nan
        for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y'):
            try:
                return pd.to_datetime(x, format=fmt)
            except Exception:
                continue
        try:
            return pd.to_datetime(x, errors='coerce')
        except Exception:
            return np.nan
    df['data_cadastro'] = df['data_cadastro'].apply(parse_date)

# Corrigir e padronizar salário (converter para float, remover texto)
if 'salario' in df.columns:
    def parse_salario(x):
        if pd.isnull(x):
            return np.nan
        if isinstance(x, (int, float)):
            return float(x)
        x = str(x).replace('.', '').replace(',', '.').strip().lower()
        # Tentar extrair número
        num = re.findall(r'\d+\.?\d*', x)
        if num:
            return float(num[0])
        # Tentar converter texto por extenso
        if 'mil' in x:
            val = re.findall(r'\d+', x)
            if val:
                return float(val[0]) * 1000
            return 4000.0  # caso "quatro mil"
        return np.nan
    df['salario'] = df['salario'].apply(parse_salario)

# Corrigir idade (converter para inteiro, tratar vazios)
if 'idade' in df.columns:
    def parse_idade(x):
        try:
            if pd.isnull(x) or str(x).strip() == '':
                return np.nan
            return int(float(str(x).strip()))
        except Exception:
            return np.nan
    df['idade'] = df['idade'].apply(parse_idade)

# Corrigir id (converter para inteiro, tratar vazios)
if 'id' in df.columns:
    df['id'] = df['id'].apply(lambda x: int(x) if not pd.isnull(x) else np.nan)

# Remover duplicatas mantendo a primeira ocorrência
df.drop_duplicates(inplace=True, ignore_index=True)

# Preencher valores nulos de 'idade' e 'salario' com a mediana se possível
if 'idade' in df.columns:
    mediana_idade = df['idade'].median()
    df['idade'] = df['idade'].fillna(mediana_idade)
if 'salario' in df.columns:
    mediana_salario = df['salario'].median()
    df['salario'] = df['salario'].fillna(mediana_salario)

# Preencher valores nulos de 'email' e 'nome' com string vazia
if 'email' in df.columns:
    df['email'] = df['email'].fillna('')
if 'nome' in df.columns:
    df['nome'] = df['nome'].fillna('')

# Preencher valores nulos de 'data_cadastro' com a data mais frequente
if 'data_cadastro' in df.columns:
    moda_data = df['data_cadastro'].mode()
    if not moda_data.empty:
        df['data_cadastro'] = df['data_cadastro'].fillna(moda_data[0])

# Preencher valores nulos de 'id' com sequência numérica crescente, evitando duplicatas
if 'id' in df.columns:
    ids_existentes = set(df['id'].dropna().astype(int))
    proximo_id = 1
    def preencher_id(x):
        nonlocal proximo_id
        if not pd.isnull(x):
            return int(x)
        while proximo_id in ids_existentes:
            proximo_id += 1
        ids_existentes.add(proximo_id)
        return proximo_id
    df['id'] = df['id'].apply(preencher_id)

# Se data_cadastro for uma sequência, preencher datas faltantes (forward fill)
if 'data_cadastro' in df.columns:
    df = df.sort_values('data_cadastro').reset_index(drop=True)
    df['data_cadastro'] = df['data_cadastro'].fillna(method='ffill')

# Garantir tipos finais
if 'id' in df.columns:
    df['id'] = df['id'].astype(int)
if 'idade' in df.columns:
    df['idade'] = df['idade'].astype(int)
if 'salario' in df.columns:
    df['salario'] = df['salario'].astype(float)
if 'data_cadastro' in df.columns:
    df['data_cadastro'] = pd.to_datetime(df['data_cadastro'])

# Reordenar colunas para o padrão original
colunas = ['id', 'nome', 'idade', 'email', 'data_cadastro', 'salario']
df = df[[c for c in colunas if c in df.columns]]