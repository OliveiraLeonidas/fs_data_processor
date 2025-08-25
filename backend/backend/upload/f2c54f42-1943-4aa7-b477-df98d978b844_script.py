import pandas as pd
import numpy as np
import re
from datetime import datetime

# O DataFrame 'df' já existe e contém os dados.

# 1. Tratar valores nulos
# Para 'id': É um identificador único. Se faltar, pode ser problemático.
# Dado que é um float e faltam 1, podemos tentar preencher com um valor único ou remover a linha.
# Dada a pequena amostra, vamos preencher com um valor sentinela negativo temporário e depois converter para int.
# Se a coluna 'id' fosse crucial para relações, a remoção da linha seria mais segura.
try:
    df['id'] = df['id'].fillna(-1) # Preenche com um valor sentinela para permitir conversão para int
except Exception as e:
    print(f"Erro ao tratar nulos na coluna 'id': {e}")

# Para 'nome': Deixar como nulo ou uma string vazia parece razoável. Vamos preencher com string vazia.
try:
    df['nome'] = df['nome'].fillna('')
except Exception as e:
    print(f"Erro ao tratar nulos na coluna 'nome': {e}")

# Para 'idade': É um valor numérico. Nulos podem ser preenchidos com a mediana/média ou removidos.
# Dado que 'idade' é object e pode ter strings vazias, vamos converter para numérico primeiro.
# Se houver valores inválidos após a limpeza, podemos preenchê-los.
try:
    # Substituir strings vazias por NaN para facilitar a conversão
    df['idade'] = df['idade'].replace('', np.nan)
    # Tentar converter para numérico, valores não convertíveis se tornarão NaN
    df['idade'] = pd.to_numeric(df['idade'], errors='coerce')
    # Preencher NaN resultantes (originalmente nulos ou strings vazias/inválidas) com a mediana
    # Usar mediana é mais robusto a outliers do que a média.
    if df['idade'].isnull().any():
        mediana_idade = df['idade'].median()
        df['idade'] = df['idade'].fillna(mediana_idade)
    # Converter para int, já que idade geralmente não tem casas decimais
    df['idade'] = df['idade'].astype(int)
except Exception as e:
    print(f"Erro ao tratar nulos e converter tipo na coluna 'idade': {e}")


# Para 'email': É uma string. Nulos podem ser preenchidos com string vazia.
try:
    df['email'] = df['email'].fillna('')
except Exception as e:
    print(f"Erro ao tratar nulos na coluna 'email': {e}")

# Para 'data_cadastro': É uma data. Nulos podem ser preenchidos com uma data padrão (e.g., 1900-01-01) ou a mediana/moda.
# Vamos preencher com uma data padrão para manter a consistência do tipo.
try:
    df['data_cadastro'] = df['data_cadastro'].fillna('1900-01-01') # Preenche com uma data sentinela
except Exception as e:
    print(f"Erro ao tratar nulos na coluna 'data_cadastro': {e}")


# Para 'salario': É um valor numérico. Nulos podem ser preenchidos com a mediana/média.
# Assim como idade, primeiro tratar strings vazias e converter para numérico.
try:
    df['salario'] = df['salario'].replace('', np.nan)
    # Tentar converter para numérico, tratando 'quatro mil' e outros textos como NaN.
    # Podemos tentar uma substituição mais inteligente, mas para 'quatro mil', é melhor converter para NaN.
    df['salario'] = pd.to_numeric(df['salario'], errors='coerce')
    # Preencher NaN resultantes (originalmente nulos, strings vazias ou textos inválidos) com a mediana
    if df['salario'].isnull().any():
        mediana_salario = df['salario'].median()
        df['salario'] = df['salario'].fillna(mediana_salario)
except Exception as e:
    print(f"Erro ao tratar nulos e converter tipo na coluna 'salario': {e}")


# 2. Remover duplicatas
# O dataset reporta 0 linhas duplicadas, mas é uma boa prática manter o código para garantir.
try:
    df.drop_duplicates(inplace=True)
except Exception as e:
    print(f"Erro ao remover duplicatas: {e}")

# 3. Corrigir tipos de dados e padronizar formatação

# Coluna 'id': Converter para int. O -1 será um ID inválido, que pode ser tratado posteriormente.
try:
    df['id'] = df['id'].astype(int)
except Exception as e:
    print(f"Erro ao converter 'id' para int: {e}")

# Coluna 'nome': Já é string (object). Nenhuma alteração necessária, a menos que queiramos capitalizar, etc.
# Por enquanto, sem formatação específica.

# Coluna 'idade': Já tratada e convertida para int no passo 1.

# Coluna 'email': Padronizar e validar.
# Remover espaços em branco e converter para minúsculas.
try:
    df['email'] = df['email'].astype(str).str.strip().str.lower()
    # Validar formato de email. Emails inválidos (e.g., 'bruno@email') podem ser marcados ou limpos.
    # Vamos substituir emails que não parecem válidos (sem '@' ou '.') por np.nan ou string vazia.
    # O regex verifica um formato básico: texto@texto.texto
    df['email'] = df['email'].apply(lambda x: x if re.match(r'[^@]+@[^@]+\.[^@]+', x) else '')
except Exception as e:
    print(f"Erro ao limpar e validar 'email': {e}")

# Coluna 'data_cadastro': Converter para datetime e padronizar formato.
try:
    # Definir uma função de parsing robusta para diferentes formatos
    def parse_date(date_str):
        if pd.isna(date_str) or date_str == '1900-01-01': # Trata o sentinela e NaN
            return pd.NaT # Not a Time, valor padrão para datas inválidas
        for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y'):
            try:
                return datetime.strptime(str(date_str), fmt)
            except ValueError:
                continue
        return pd.NaT # Retorna NaT se nenhum formato for compatível

    df['data_cadastro'] = df['data_cadastro'].apply(parse_date)
    # Preencher quaisquer NaT restantes (originalmente nulos ou formatos inválidos)
    # com a data sentinela ou a moda, dependendo da política.
    # Usaremos o valor sentinela que definimos para manter a lógica.
    df['data_cadastro'] = df['data_cadastro'].fillna(datetime(1900, 1, 1))
except Exception as e:
    print(f"Erro ao converter e padronizar 'data_cadastro': {e}")


# Coluna 'salario': Já tratada e convertida para float no passo 1.

# 4. Remover linhas/colunas inválidas se necessário
# Dada a abordagem conservadora e o preenchimento de nulos, nenhuma remoção de linha ou coluna é explicitamente necessária no momento.
# Se tivéssemos muitos IDs inválidos (-1), poderíamos remover essas linhas.
# Por exemplo, para remover IDs inválidos:
# df = df[df['id'] != -1]

# O DataFrame 'df' agora está limpo e tratado.