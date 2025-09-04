import pandas as pd
import numpy as np
import re
from datetime import datetime

# O DataFrame 'df' é assumido como já carregado

# 1. Padronizar o cabeçalho do DataFrame para português do Brasil
df.columns = [
    'identificador', 'nome', 'idade', 'email', 'data_registro', 'salario_bruto'
]


# 2. Remover linhas duplicadas
# Consideramos uma linha duplicada se todos os seus valores forem iguais
df.drop_duplicates(inplace=True)


# 3. Tratamento de valores nulos e correção de tipos de dados

# Coluna 'identificador' (originalmente 'id')
# Tentar converter para tipo numérico. Valores não conversíveis se tornarão NaN.
df['identificador'] = pd.to_numeric(df['identificador'], errors='coerce')
# Preencher valores nulos em 'identificador' com a mediana, se aplicável, ou 0 se a coluna for toda NaN.
# Isso é conservador para evitar a remoção de linhas.
if not df['identificador'].isnull().all():
    df['identificador'].fillna(df['identificador'].median(), inplace=True)
else:
    df['identificador'].fillna(0, inplace=True)
# Converter para int, se não houver perdas de informação (ou seja, se forem inteiros após o preenchimento)
df['identificador'] = df['identificador'].astype(int)

# Coluna 'idade'
# Tratar valores vazios como NaN para facilitar a conversão numérica
df['idade'] = df['idade'].replace('', np.nan)
# Tentar converter para tipo numérico. Valores não conversíveis se tornarão NaN.
df['idade'] = pd.to_numeric(df['idade'], errors='coerce')
# Preencher valores nulos em 'idade' com a mediana.
# Uma idade nula é preenchida com um valor razoável para a distribuição existente.
if not df['idade'].isnull().all():
    df['idade'].fillna(df['idade'].median(), inplace=True)
else:
    # Se a coluna for toda NaN após a conversão, preenche com um valor padrão, e.g., 0
    df['idade'].fillna(0, inplace=True)
# Converter para int, se não houver perdas de informação
df['idade'] = df['idade'].astype(int)


# Coluna 'email'
# Preencher valores nulos e strings vazias com uma string vazia para padronização
df['email'].fillna('', inplace=True)
df['email'] = df['email'].replace('', np.nan)
# Padronizar e-mails: converter para minúsculas e remover espaços extras
df['email'] = (
    df['email'].astype(str).str.lower().str.strip().replace('nan', np.nan)
)
# Remover e-mails inválidos (sem '@' ou '.'), substituindo por NaN
# Um regex mais robusto poderia ser usado, mas para esta tarefa, uma verificação simples é suficiente.
df['email'] = df['email'].apply(
    lambda x: x if pd.notna(x) and '@' in x and '.' in x else np.nan
)
# Para valores nulos restantes em 'email', preencher com uma string vazia para consistência
df['email'].fillna('', inplace=True)


# Coluna 'data_registro' (originalmente 'data_cadastro')
# Tratar valores vazios como NaN
df['data_registro'] = df['data_registro'].replace('', np.nan)
# Tentar converter para tipo datetime, experimentando diferentes formatos
# Usar errors='coerce' para transformar datas inválidas em NaT (Not a Time)
df['data_registro'] = pd.to_datetime(
    df['data_registro'], errors='coerce', format='%Y-%m-%d'
)
# Tentar novamente com outro formato para datas que falharam
mask_na_dates = df['data_registro'].isna()
df.loc[mask_na_dates, 'data_registro'] = pd.to_datetime(
    df.loc[mask_na_dates, 'data_registro'], errors='coerce', format='%Y/%m/%d'
)
mask_na_dates = df['data_registro'].isna()
df.loc[mask_na_dates, 'data_registro'] = pd.to_datetime(
    df.loc[mask_na_dates, 'data_registro'], errors='coerce', format='%d-%m-%Y'
)

# Preencher datas nulas usando interpolação, se houver um padrão de data
# Se não houver padrão, preenche com a data mais comum (moda) ou uma data padrão.
if not df['data_registro'].isnull().all():
    df['data_registro'].interpolate(method='time', inplace=True)
    # Após a interpolação, ainda podem existir NaT's no início ou fim.
    # Preencher com a moda (data mais frequente)
    if df['data_registro'].isnull().any():
        mode_date = df['data_registro'].mode()[0]
        df['data_registro'].fillna(mode_date, inplace=True)
else:
    # Se todas as datas forem NaT, preenche com uma data padrão (e.g., hoje ou 2000-01-01)
    df['data_registro'].fillna(pd.to_datetime('2000-01-01'), inplace=True)


# Coluna 'salario_bruto' (originalmente 'salario')
# Tratar valores vazios como NaN
df['salario_bruto'] = df['salario_bruto'].replace('', np.nan)


def clean_salary(salario):
    if isinstance(salario, str):
        # Remover caracteres não numéricos, exceto ponto e vírgula
        salario = salario.replace('R$', '').replace('.', '').replace(',', '.')
        # Tentar converter para float, ignorando strings como 'quatro mil'
        try:
            return float(salario)
        except ValueError:
            return np.nan  # Se não for possível converter, retorna NaN
    return salario


# Aplicar a função de limpeza
df['salario_bruto'] = df['salario_bruto'].apply(clean_salary)

# Preencher valores nulos em 'salario_bruto' com a mediana.
# Um salário nulo é preenchido com um valor razoável para a distribuição existente.
if not df['salario_bruto'].isnull().all():
    df['salario_bruto'].fillna(df['salario_bruto'].median(), inplace=True)
else:
    # Se a coluna for toda NaN após a conversão, preenche com um valor padrão, e.g., 0
    df['salario_bruto'].fillna(0.0, inplace=True)


# Coluna 'nome'
# Preencher valores nulos ou vazios com uma string padrão para evitar erros e manter a consistência
df['nome'].fillna('Nome Desconhecido', inplace=True)
df['nome'] = df['nome'].replace('', 'Nome Desconhecido')
# Capitalizar a primeira letra de cada palavra no nome
df['nome'] = df['nome'].astype(str).str.title().str.strip()


# 4. Tratamento de gaps em sequências numéricas (identificador)
# Verificar se a coluna 'identificador' é uma sequência numérica e tem gaps.
# Assumimos que 'identificador' deveria ser uma sequência contínua de inteiros.
if pd.api.types.is_integer_dtype(df['identificador']):
    # Ordenar o DataFrame por 'identificador' para facilitar a detecção de gaps
    df.sort_values(by='identificador', inplace=True)
    # Criar uma série com a sequência esperada (começando do menor id até o maior)
    min_id = df['identificador'].min()
    max_id = df['identificador'].max()
    expected_ids = pd.Series(range(min_id, max_id + 1))

    # Identificar IDs ausentes
    missing_ids = expected_ids[~expected_ids.isin(df['identificador'])]

    if not missing_ids.empty:
        # Para cada ID ausente, adicionar uma nova linha com o ID e NaN para outras colunas
        # Preencher os NaNs nessas novas linhas com valores medianos/modais ou padrão
        new_rows = []
        for missing_id in missing_ids:
            new_row = {'identificador': missing_id}
            for col in df.columns:
                if col not in ['identificador']:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        new_row[col] = df[col].median() if not df[col].isnull().all() else 0
                    elif pd.api.types.is_datetime64_any_dtype(df[col]):
                        new_row[col] = (
                            df[col].mode()[0]
                            if not df[col].isnull().all()
                            else pd.to_datetime('2000-01-01')
                        )
                    else:
                        new_row[col] = ''  # String vazia para outros tipos
            new_rows.append(new_row)

        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        df.sort_values(by='identificador', inplace=True)
        # Re-aplicar tratamento de tipos após concatenação se necessário
        df['identificador'] = df['identificador'].astype(int)
        df['idade'] = df['idade'].astype(int)
        df['salario_bruto'] = df['salario_bruto'].astype(float)


# 5. Preencher sequências de datas incompletas (se aplicável e com lógica razoável)
# Embora 'data_registro' tenha sido interpolada, podemos refinar a lógica de preenchimento de gaps.
# Se tivéssemos múltiplas entradas para o mesmo 'identificador' com datas, poderíamos preencher
# lacunas temporais para aquele 'identificador'. Como é um registro único por 'identificador',
# a interpolação já é o método mais direto para preencher lacunas "sequenciais" no dataset como um todo.
# Não é comum ter "gaps" de datas no sentido de datas ausentes em uma série temporal contínua
# para cada linha de um dataset transacional simples como este. A interpolação global já foi feita.


# Reorganizar as colunas para garantir a ordem desejada (opcional, mas boa prática)
df = df[
    [
        'identificador',
        'nome',
        'idade',
        'email',
        'data_registro',
        'salario_bruto',
    ]
]