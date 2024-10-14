import sqlite3
import pandas as pd
from datetime import datetime as dtime
import datetime as datetime

"""##### LOGGER #####"""
import logging
from colorlog import ColoredFormatter

# Criar um handler que vai imprimir no terminal
console_handler = logging.StreamHandler()

# Configuração do logger com arquivo e terminal
file_handler = logging.FileHandler(R"C:\Users\cidirclay.queiroz\Documents\Python\Logs\salva_sinalizacao_bd.log")

# Definir o formato das mensagens de logg com cores para o terminal
formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'red',
        'INFO': 'bold_green',
        'WARNING': 'bold_cyan',
        'ERROR': 'bold_yellow',
        'CRITICAL': 'bold_red',
    })

# Definir o formato simples para o arquivo de log
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')

# Aplicar os formatters aos handlers
console_handler.setFormatter(formatter)
file_handler.setFormatter(file_formatter)

# Configuração do logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Adicionar os handlers ao logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
"""##### LOGGER #####"""


def salvar_dados_sqlite(nome_operador, estado, tempo_format, ns_do_dia, clientes, agentes):
    salvar_dados_sqlite1 = False
    while not salvar_dados_sqlite1:
        try:
            # Conectar ao banco de dados (ajuste o caminho e nome do banco)
            conn = sqlite3.connect(r"\\aecstrgisilon1\Mercurio-AeC_ContactCenter\Planejamento_Clientes_Premium\99\5. Escala Nice\Codigos Queiroz\Pitão\SQLite3\banco_teste.db")
            cursor = conn.cursor()
            dia = dtime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute('''
                SELECT * FROM registros
                WHERE nome = ? AND status = ?
                ORDER BY data DESC
                LIMIT 1
            ''', (nome_operador, estado))
            ultimo_registro = cursor.fetchone()

            logger.info(f'ultimo_registro: {ultimo_registro}')

            if ultimo_registro:
                # Calcular a diferença de tempo e data
                ultimo_datetime = datetime.datetime.strptime(f"{ultimo_registro[0]}", '%Y-%m-%d %H:%M:%S.%f')  # Assumindo que a coluna 'data' está no formato YYYY-MM-DD HH:MM:SS
                logger.info(ultimo_datetime)
                novo_datetime = datetime.datetime.strptime(f"{dia}", '%Y-%m-%d %H:%M:%S')
                logger.info(novo_datetime)
                diferenca = novo_datetime - ultimo_datetime

                # Verificar se a diferença está dentro de 10 minutos e se a data está dentro do intervalo
                dez_minutos = datetime.timedelta(minutes=10)
                if abs(diferenca) >= dez_minutos:
                    # Inserir novo registro e enviar mensagem
                    logger.warning(f"Último registro para {nome_operador} e {estado} há mais de 10 minutos. Inserindo novo registro.")
                    cursor.execute('''
                                INSERT INTO registros (data, nome, status, tempo, ns, clientesfila, agentesdisponiveis)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (dia, nome_operador, estado, tempo_format, ns_do_dia, clientes, agentes))
                    conn.commit()
                    salvar_dados_sqlite1 = True
                else:
                    logger.info(f"Último registro para {nome_operador} e {estado} há menos de 10 minutos.")
                    salvar_dados_sqlite1 = False
            else:
                # Inserir novo registro se não houver registros anteriores
                logger.info(f"Não há registros anteriores para {nome_operador} e {estado}. Inserindo novo registro.")
                # ... (inserir novo registro)
                salvar_dados_sqlite1 = True
        except Exception as e:
            salvar_dados_sqlite1 = True
            logger.error(f"Erro na consultas: {e}")
        finally:
            conn.close()
            return salvar_dados_sqlite1
