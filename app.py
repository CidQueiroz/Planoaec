import os
import sys
import time
import locale
import sqlite3
import datetime
import threading
import pandas as pd
import streamlit as st
import win32com.client as win32
from atribui_tkt import processar_lista
from streamlit_option_menu import option_menu
from datetime import datetime as dtime, date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from siqual_lite import verificar_login_mysql, registrar_login, ultimo_registro
from Aegea.Midias.midias import base_midias_api

# Defina o locale para português do Brasil
locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

##### LOGGER #####
import logging
from colorlog import ColoredFormatter

# Criar um handler que vai imprimir no terminal
console_handler = logging.StreamHandler()

# Configuração do logger com arquivo e terminal
file_handler = logging.FileHandler(r"F:\Python\Logs\app_streamlit.log")

# Definir o formato das mensagens de logg com cores para o terminal
formatter = ColoredFormatter("%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S', log_colors={'DEBUG': 'red', 'INFO': 'bold_green', 'WARNING': 'bold_cyan', 'ERROR': 'bold_yellow', 'CRITICAL': 'bold_red', })

# Definir o formato simples para o arquivo de log
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')

# Aplicar os formatters aos handlers
console_handler.setFormatter(formatter)
file_handler.setFormatter(file_formatter)

# Configuração do logger
logger = logging.getLogger('app_streamlit')
logger.setLevel(logging.WARNING)

# Adicionar os handlers ao logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
##### LOGGER #####

# Pegar a data atual
dia = str(date.today().day).zfill(2)
mes = str(date.today().month).zfill(2)
ano = date.today().year
EU = int('236395')


def enviando_email_arquivo_unico(caminho_arquivo_geral, corpo_mensagem, matricula):
    # valor100 = False
    # while not valor100:
    #     try:
    st.info('********** ENVIANDO EMAIL **********')

    outlook_running = False

    hora_atual = dtime.now().strftime('%H:%M:%S')
    horaenvio = int(hora_atual.split(":")[0])

    if horaenvio < 12:
        saudacao = 'bom dia'
    elif horaenvio < 18:
        saudacao = 'boa tarde'
    else:
        saudacao = 'boa noite'

    if not outlook_running:
        outlook = win32.Dispatch('Outlook.Application')
    else:
        outlook = win32.Dispatch('Outlook.Application')

    # criar um email
    email = outlook.CreateItem(0)

    # configurar as informações do seu e-mail
    email.To = 'cidirclay.queiroz@aec.com.br'
    email.Subject = f':: Sugestão de Automação ::'
    email.HTMLBody = f"""
            <html>
            <head></head>
            <body>
            <p>Cidirclay, {saudacao}! Espero que estejam bem!</p>
            
            <p><b>{corpo_mensagem}</b>!</p>
            
            {matricula}
            
            <p><img src="cid:imagem_id"></p>
            
            </body>
            
            </html>
        """

    email.Attachments.Add(caminho_arquivo_geral)
    anexo = email.Attachments.Add(r'\\aecstrgisilon1\Fontes-Planejamento_Clientes_Premium e Gov\04_NOC\AEGEA\ROBO\Assinaturas\cidirclay.queiroz.jpg')
    anexo.PropertyAccessor.SetProperty('http://schemas.microsoft.com/mapi/proptag/0x3712001E', "imagem_id")

    email.Send()
    logger.info('Email Enviado!')

    st.success(f'********** EMAIL ENVIADO **********')

    # valor100 = True
    #
    # except Exception as excecao_email_unico:
    #     exc_type, exc_value, exc_traceback = sys.exc_info()
    #     logger.critical(f"Erro crítico na função BUSCA-FILA. Linha: {exc_traceback.tb_lineno}. Erro: {type(excecao_email_unico).__name__}")
    #     valor100 = False
    # finally:
    #     return valor100


def processar_excecao(args):
    exc_type, exc_value, exc_traceback = args
    logging.error("Ocorreu uma exceção não tratada na thread:", exc_info=(exc_type, exc_value, exc_traceback))
    # Aqui você pode adicionar lógica para notificar o usuário, enviar um email, etc.
    st.session_state.error_message = f"Ocorreu um erro inesperado: {str(exc_value)}"


# Funções para cada página
def routing(nome):
    st.title("Alteração de Routing")

    def processar_em_thread():
        try:
            result_valor_routing = processar_lista(lista_nomes, lista_atribuicoes, nome)

            # Dispara um evento para atualizar a interface
            st.session_state.resultado = result_valor_routing
        except Exception as ex:
            logging.error(f"Erro na thread: {ex}")
            # Enviar uma mensagem para a interface do usuário
            st.session_state.error_message = f"Ocorreu um erro: {str(ex)}"

    # Input para a lista de nomes
    with st.form("my_form"):
        nomes = st.text_area("Nomes", placeholder="Digite os nomes separados por vírgula")
        atribuicoes = st.selectbox("Atribuições", ["[routing]Oceano Atendimento", "[routing]Oceano Voz", "[routing]Oceano Emergencial", "[routing]Oceano BackOffice", "[routing]Oceano Backoffice Rap…"])
        submitted = st.form_submit_button("Enviar")

        if submitted:
            # Validação dos dados
            if not nomes.strip():
                st.error("A lista de nomes não pode estar vazia.")
            elif ";" not in nomes:
                st.error("Os nomes devem ser separados por ponto e vírgula.")
            elif not atribuicoes:
                st.error("Selecione pelo menos uma atribuição.")
            else:
                # Limpando e organizando as listas
                lista_nomes = [nome.strip() for nome in nomes.split(";") if nome.strip()]
                lista_atribuicoes = atribuicoes

                # Definir a função de tratamento de exceções para todas as threads
                threading.excepthook = processar_excecao(args)

                thread = threading.Thread(target=processar_em_thread)
                thread.start()

                # Mostrar mensagem de progresso ou resultado enquanto a thread executa
                st.info("Lista enviada! Favor Aguardar!")

                with st.spinner('Aguarde enquanto processamos...'):
                    while 'resultado' not in st.session_state:
                        time.sleep(0.1)

                st.success(f'Resultado: {st.session_state.resultado}')

                # progress_bar = st.progress(0)
                # for i in range(100):
                #     time.sleep(0.1)
                #     progress_bar.progress(i + 1)
    try:
        # Conectar ao banco de dados
        with sqlite3.connect(r"\\aecstrgisilon1\Mercurio-AeC_ContactCenter\Planejamento_Clientes_Premium\99\14. Códigos cid\Codigos Queiroz\Pitão\SQLite3\banco_planoaec.db") as conn:
            # Consultar os dados
            cursor = conn.cursor()
            cursor.execute("""Select data as Data,
                    nome as Nome_Operador,
                    atribuicao as Routing_Destino,
                    matricula as Matricula                 
                    from altera_routing
                    order by data desc;
                    """)
            resultados = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM altera_routing")
            count = cursor.fetchone()[0]

    except sqlite3.OperationalError as e:
        logger.error(f"Erro operacional no SQLite: {e}")
    except sqlite3.IntegrityError as e:
        logger.error(f"Violação de integridade: {e}")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")

    df = pd.DataFrame(resultados, columns=['Data', 'Nome Operador', 'Routing', 'Funcionário'])

    # Ordenando o DataFrame por data, status e operação
    df = df.sort_values(by=['Data'], ascending=[False])

    df = df.fillna('')
    df = df.astype(str)
    # logger.info(df)

    st.write(f'Total de alterações de routing: {count}')

    df = df.reset_index(drop=True)
    pd.set_option('display.max_colwidth', None)
    st.dataframe(df, use_container_width=True, hide_index=True)


def status_automacoes():
    st.title("Automações em andamento")
    CAMINHO = r'C:\Users\cidirclay.queiroz\Documents\Python'
    resultados = None

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sinalização Voz (rodar)", use_container_width=True):
            if os.path.exists(f'{CAMINHO}\\processo_voz.txt'):
                st.warning("Processo de Voz já está em execução!")
            else:
                st.info("ATIVANDO SINALIZAÇÃO DE VOZ!")
                import Aegea.GenesysAegea.GenesysAegea

    with col2:
        if st.button("Sinalização WhatsApp (rodar)", use_container_width=True):
            if os.path.exists(f'{CAMINHO}\\processo_wpp.txt'):
                st.warning("Processo de WhatsApp já está em execução!")
            else:
                st.info("ATIVANDO SINALIZAÇÃO DE WHATSAPP!")
                import Aegea.SinalizacoesWhatsApp.SinalizacoesWhatsApp

    try:
        def convert_date(date_string):
            parts = date_string.split(' ')
            date_parts = parts[0].split('/')
            return f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]} {parts[1]}"

        # Conectar ao banco de dados
        conn = sqlite3.connect(r"\\aecstrgisilon1\Mercurio-AeC_ContactCenter\Planejamento_Clientes_Premium\99\14. Códigos cid\Codigos Queiroz\Pitão\SQLite3\bd_sqlite\banco_status.db")

        # Registrar a função personalizada
        conn.create_function('convert_date', 1, convert_date)

        # Agora você pode usar a função na sua consulta SQL
        cursor = conn.cursor()
        cursor.execute("""
            WITH ResultadosOrdenados AS (
                SELECT *,
                    ROW_NUMBER() OVER (
                    PARTITION BY descricao
                    ORDER BY convert_date(data) DESC
                ) AS RowNum
            FROM automacoes
            )
            SELECT
                data as Data, tipo_automacao as Automacao, descricao as Descriçao, operacao as Operação, Status_Atual as 'Status Atual'
            FROM
                ResultadosOrdenados
            WHERE
                RowNum = 1
            ORDER BY
                datetime(convert_date(data)) DESC, Status_Atual DESC;
        """)

        resultados = cursor.fetchall()
        conn.close()
    except sqlite3.OperationalError as e:
        logger.error(f"Erro operacional no SQLite: {e}")
    except sqlite3.IntegrityError as e:
        logger.error(f"Violação de integridade: {e}")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")

    df = pd.DataFrame(resultados, columns=['Data', 'Automacao', 'Descriçao', 'Operação', 'Status_Atual'])
    df = df.drop_duplicates(subset=['Automacao', 'Descriçao', 'Operação', 'Status_Atual'])

    # Ordenando o DataFrame por data, status e operação
    # df = df.sort_values(by=['Data', 'Status_Atual'], ascending=[True, False])

    df = df.fillna('')
    df = df.astype(str)
    total_automacoes = len(df)

    st.write(f'Total de automações: {total_automacoes}')

    df = df.reset_index(drop=True)
    pd.set_option('display.max_colwidth', None)
    st.dataframe(df, use_container_width=True, hide_index=True)


def baixar_arquivos():
    # Título da página
    st.title("BAIXAR ARQUIVOS PLANEJAMENTO!")

    # Escondendo os expanders inicialmente
    # st.markdown("""
    # <style>
    # .stExpander {
    #     display: none;
    # }
    # </style>
    # """, unsafe_allow_html=True)

    with st.expander('GERAL'):
        if st.button("Estrutura Geral D0", use_container_width=True):
            from Aegea.Facilita.hierarquia_pbi import baixa_base_hierarquia_pbi
            base_est = False
            while not base_est:
                base_est = baixa_base_hierarquia_pbi()
                if base_est:
                    st.success("Base Social Midia Ride baixada com sucesso!")

    with st.expander('99'):
        if st.button("Parcial Social Mídia Ride", use_container_width=True):
            base_ride = False
            while not base_ride:
                base_ride = base_midias_api('ride')
                if base_ride:
                    st.success("Base Social Midia Ride baixada com sucesso!")

        if st.button("Parcial Social Mídia Pay", use_container_width=True):
            base_pay = False
            while not base_pay:
                base_pay = base_midias_api('pay')
                if base_pay:
                    st.success("Base Social Midia Ride baixada com sucesso!")

        if st.button("Hominum D0 - 99", use_container_width=True):
            from Aegea.EstruturaGoverno import filtra_estrutura
            est_99 = False
            while not est_99:
                est_99 = filtra_estrutura('99')
                if est_99:
                    st.success('Hominum 99 baixado com sucesso!!')
                    st.success('Local salvamento:\n\\\\aecstrgisilon1\\Mercurio-AeC_ContactCenter\\Planejamento_Clientes_Premium\\99\\1.Relatórios\\1.Intra-hora\\zBases intras fechamento')
                else:
                    st.warning('Erro ao baixar Hominum 99. Por favor, tente novamente!!')

    with st.expander('Sanofi'):
        if st.button("Hominum D0 - SANOFI", use_container_width=True):
            from Aegea.EstruturaGoverno import filtra_estrutura
            est_sf = filtra_estrutura('sanofi')
            if est_sf:
                st.success('Hominum SANOFI baixado com sucesso!!')
                mes_atual_extenso = (datetime.datetime.now().strftime('%B')).capitalize()
                st.success(fr'Local salvamento: \\aecstrgisilon1\Fontes-Planejamento_Clientes_Premium e Gov\04_NOC\SANOFI\{ano}\{mes}. {mes_atual_extenso}\01.ESTRUTURA')
            else:
                st.warning('Erro ao baixar Hominum SANOFI. Por favor, tente novamente!!')

    with st.expander('Aegea'):
        data_dia = (dtime.now() - timedelta(days=1)).strftime('%d/%m/%Y')

        if st.button("Hominum D0 - AEGEA", use_container_width=True):
            from Aegea.EstruturaGoverno import filtra_estrutura
            est_ag = False
            while not est_ag:
                est_ag = filtra_estrutura('aegea')
                if est_ag:
                    st.success('Hominum AEGEA baixado com sucesso!!')
                    mes_atual_extenso = (datetime.datetime.now().strftime('%B')).capitalize()
                    st.success(fr'Local salvamento: \\aecstrgisilon1\Fontes-Planejamento_Clientes_Premium e Gov\04_NOC\AEGEA\{ano}\{mes}. {mes_atual_extenso}\01.ESTRUTURA')
                else:
                    st.warning('Erro ao baixar Hominum AEGEA. Por favor, tente novamente!!')

        if st.button("Relatorio de Sinalizações", use_container_width=True):
            from Aegea.Graficos.graficos_sinalizacoes import separando_arquivo_graficos, imagem_sinalizacao_graficos, enviando_email_graficos
            if separando_arquivo_graficos('aegea', data_dia):
                if imagem_sinalizacao_graficos('aegea', data_dia):
                    if enviando_email_graficos('aegea', 'd', data_dia):
                        st.success('Relatório de sinalizações D-1 enviado com sucesso!!')
            else:
                st.warning('Erro ao baixar Relatório de sinalizações. Por favor, tente novamente!!')

        if st.button("Relatorio de Adoção", use_container_width=True):
            from Aegea.Facilita.facilita_adocao import baixa_base_facilita, atualiza_arquivo_facilita, separando_arquivo_facilita, enviando_email_facilita
            if baixa_base_facilita(data_dia):
                if atualiza_arquivo_facilita():
                    if separando_arquivo_facilita():
                        if enviando_email_facilita(data_dia):
                            st.success('Relatório de Adoção enviado com sucesso!!')
            else:
                st.warning('Erro ao baixar Relatório de Adoção. Por favor, tente novamente!!')

    with st.expander('Banco Pan'):
        if st.button("Hominum D0 - BANCO PAN", use_container_width=True):
            from Aegea.EstruturaGoverno import filtra_estrutura
            est_bp = False
            while not est_bp:
                est_bp = filtra_estrutura('bancopan')
                if est_bp:
                    st.success('Hominum BANCO PAN baixado com sucesso!!')
                    mes_atual_extenso = (datetime.datetime.now().strftime('%B')).capitalize()
                    st.success(fr'Local salvamento: \\aecstrgisilon1\Mercurio-AeC_ContactCenter\Planejamento_Clientes_Premium\BANCO_PAN\{ano}\{mes}.{mes_atual_extenso.upper()}\04.ESTRUTURA')
                else:
                    st.warning('Erro ao baixar Hominum BANCO PAN. Por favor, tente novamente!!')

    with st.expander('Sugestão de automação'):
        # Input para a lista de nomes
        with st.form("form_sugestao"):
            mensagem = st.text_area("Mensagem", placeholder="Em teste. Favor não usar!")
            arquivo = st.file_uploader("Escolha um arquivo", type=["csv", "xls", "xlsx", "xlsm", "xlsb"])  # Ajuste os tipos de arquivo conforme necessário
            submitted = st.form_submit_button("Enviar")

            if submitted:
                # Validação dos dados
                if not mensagem:
                    st.error("A mensagem não pode estar vazia.")
                # elif not arquivo:
                #     st.error("Você precisa selecionar um arquivo.")
                else:
                    print(arquivo.name)
                    # Obter o caminho temporário do arquivo carregado
                    caminho_arquivo_temporario = arquivo.name

                    with open(caminho_arquivo_temporario, 'wb') as f:
                        f.write(arquivo.getbuffer())

                    # Chamar a função de envio de email com o caminho do arquivo temporário e a mensagem
                    # if enviando_email_arquivo_unico(caminho_arquivo_temporario, mensagem, st.session_state['matricula']):
                    #     st.success("Email enviado com sucesso!")

    # """
    # # Lista de arquivos disponíveis (substitua por sua lista real)
    # arquivos = ['dados_2023.csv', 'dados_2022.xlsx', 'dados_2021.json']
    #
    # # Seleção do arquivo
    # arquivo_selecionado = st.selectbox('Selecione a operação:', arquivos)
    #
    # # Formato do arquivo
    # formato = st.radio('Selecione o formato:', ['CSV', 'Excel'])
    #
    # # Botão de download
    # if st.button('Baixar'):
    #     # Lógica para ler o arquivo e converter para o formato escolhido (adapte conforme sua necessidade)
    #     if formato == 'CSV':
    #         df = pd.read_csv(arquivo_selecionado)
    #         df.to_csv(f'{arquivo_selecionado[:-4]}_{formato.lower()}.csv', index=False)
    #     elif formato == 'Excel':
    #         df = pd.read_excel(arquivo_selecionado)
    #         df.to_excel(f'{arquivo_selecionado[:-5]}_{formato.lower()}.xlsx', index=False)
    #
    #     # Download do arquivo
    #     with open(f'{arquivo_selecionado[:-4]}_{formato.lower()}.{formato.lower()}', 'rb') as file:
    #         st.download_button(
    #             label="Baixar Arquivo",
    #             data=file,
    #             file_name=f'{arquivo_selecionado[:-4]}_{formato.lower()}.{formato.lower()}',
    #             mime='text/csv'  # Ajuste o mime type conforme o formato
    #         )
    # st.markdown("""
    # <script>
    #   const expanders = document.querySelectorAll('.stExpander');
    #   const buttons = document.querySelectorAll('button');
    #
    #   buttons.forEach(button => {
    #     button.addEventListener('click', () => {
    #       const expanderId = button.textContent.toLowerCase();
    #       const expander = document.querySelector(`.${expanderId}`);
    #       expander.style.display = expander.style.display === 'none' ? 'block' : 'none';
    #     });
    #   });
    # </script>
    # """, unsafe_allow_html=True)
    # """


def conect_ips():
    st.title("Login IP's AeC")

    if int(st.session_state['matricula']) != 265132:
        st.write(f'{st.session_state["nome"]}, ainda estamos em etapa de finalização! Por favor, aguarde!')
    else:
        # Opções do radio button
        opcoes = ['113_33_JN1', '127_56_RJO', '155_218_CPV', '156_98_CPV', 'Rhinos']

        # Radio button para seleção
        opcao_selecionada = st.radio("Escolha uma opção:", opcoes)

        # Botão de envio
        if st.button("Enviar"):
            st.write(f"Você será conectado ao IP {opcao_selecionada}")
            from Avulsos.forticlient_automacao import abrir_ip
            enviado = abrir_ip(str(opcao_selecionada))
            st.write(f'Enviado: {enviado}')


def construcao():
    st.title("ESPERA, P...")
    st.write("")


def login_page():
    # Interface do Streamlit
    st.title("Login")

    st.session_state['authenticated'] = False
    st.session_state['matricula'] = st.text_input("Informe sua matrícula:")
    cpf = st.text_input("Informe seu CPF:")
    st.session_state['nome'] = None
    st.session_state['cargo'] = None
    # cpf = "fiofonaroda"

    if st.button("Login"):
        resultado_mysql, st.session_state['nome'], st.session_state['cargo'] = verificar_login_mysql(st.session_state['matricula'], cpf)
        st.session_state['nome'] = st.session_state['nome'].capitalize()
        st.session_state['cargo'] = st.session_state['cargo'].capitalize()

        if not st.session_state['matricula'] or not cpf:
            st.error("Por favor, preencha todos os campos.")
            registrar_login(st.session_state['matricula'], 'login', False)
        elif not resultado_mysql:
            # elif cpf != 'fiofonaroda':
            st.error("Matrícula ou CPF inválidos")
            registrar_login(st.session_state['matricula'], 'login', False)
        else:
            st.success(f"Login bem-sucedido, {st.session_state['nome']}! (Clique em login novamente, por favor)")
            registrar_login(st.session_state['matricula'], 'login', True)
            st.session_state['authenticated'] = True


def page1():
    # Interface principal
    st.title(f"Bem-vindo, {st.session_state['nome']}!!")
    st.title("Planejamento - AeC! Equipe Dhiego Sarmento!")
    st.write("")

    # Lista com os 10 tópicos
    topicos = [
        "Princípios Inegociáveis!!",
        "1. Estamos aqui para fazer melhor que todos.",
        "2. Focamos a inovação constantemente.",
        "3. Só acreditamos no simples.",
        "4. Somente entramos no mercado em que podemos fazer uma contribuição significativa.",
        "5. Temos foco.",
        "6. Acreditamos na colaboração mútua dos nossos grupos.",
        "7. Não aceitamos nada que seja abaixo do nível de excelência.",
        "8. Somos humildes e honestos para admitir nossos erros.",
        "9. Somos corajosos o suficiente para mudarmos quando necessário.",
        "10. Somos felizes com o que fazemos."]

    # Exibir os tópicos
    for topico in topicos:
        st.write(topico)

    # Criando um container para centralizar a imagem
    st.markdown("""
    <style>
    .center {
      display: block;
      margin-left: auto;
      margin-right: auto;
      width: 80%;  # Ajuste a largura conforme necessário
    }
    </style>
    """, unsafe_allow_html=True)

    st.image(r"F:\Python\PlanoAeC\grupo_plan2.jpg", width=700)


def sinalizacao():
    st.title("Sinalizações realizadas")

    try:
        # Conectar ao banco de dados
        with sqlite3.connect(r"\\aecstrgisilon1\Mercurio-AeC_ContactCenter\Planejamento_Clientes_Premium\99\14. Códigos cid\Codigos Queiroz\Pitão\SQLite3\banco_teste.db") as conn:
            # Consultar os dados
            cursor = conn.cursor()
            cursor.execute("SELECT data as Data, "
                           "nome as Operador,"
                           "status as Status, "
                           "tempo as Tempo "
                           "FROM "
                           "registros "
                           "ORDER BY "
                           "Data DESC, Operador asc")
            resultados = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) FROM registros WHERE strftime('%Y-%m-%d', data) = strftime('%Y-%m-%d', datetime());")
            count = cursor.fetchone()[0]
    except sqlite3.OperationalError as e:
        logger.error(f"Erro operacional no SQLite: {e}")
    except sqlite3.IntegrityError as e:
        logger.error(f"Violação de integridade: {e}")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        # logger.info(resultados)

    resultado = ultimo_registro(r"\\aecstrgisilon1\Mercurio-AeC_ContactCenter\Planejamento_Clientes_Premium\99\14. Códigos cid\Codigos Queiroz\Pitão\SQLite3\banco_teste.db")

    data_hora1 = resultado[0]
    data_hora1 = pd.to_datetime(data_hora1, format='%Y-%m-%d %H:%M:%S')
    data_hora = data_hora1.strftime('%d/%m/%Y %H:%M:%S')
    data = str(data_hora).split()[0]
    hora = str(data_hora).split()[1]

    st.write(f'Total de sinalizações enviadas: {count}')
    st.write(f'Última atualização: {data} às {hora}')
    df = pd.DataFrame(resultados, columns=['Data', 'Operador', 'Status', 'Tempo'])
    df = df.drop_duplicates(subset=['Data', 'Operador', 'Status', 'Tempo'])

    # Ordenando o DataFrame por data, status e operação
    df = df.sort_values(by=['Data'], ascending=[False])

    df = df.fillna('')
    df = df.astype(str)

    # Inicialmente, o DataFrame filtrado é igual ao DataFrame original
    df_filtrado = df.copy()
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    # # Adicionando filtros
    # data_inicio = st.date_input("Data inicial")
    # data_fim = st.date_input("Data final")
    # operadores = st.multiselect("Selecione os operadores", df['Operador'].unique())
    #
    # if not pd.api.types.is_datetime64_dtype(df['Data']):
    #     df['Data'] = pd.to_datetime(df['Data'])
    #
    # # Aplicando os filtros apenas se os valores forem válidos
    # if data_inicio and data_fim and operadores:
    #     df_filtrado = df[(df['Data'] >= pd.to_datetime(data_inicio)) &
    #                      (df['Data'] <= pd.to_datetime(data_fim)) &
    #                      df['Operador'].isin(operadores)]
    # if data_inicio and data_fim and not operadores:
    #     df_filtrado = df[(df['Data'] >= pd.to_datetime(data_inicio)) &
    #                      (df['Data'] <= pd.to_datetime(data_fim))]
    # if operadores:
    #     df_filtrado = df_filtrado[df['Operador'].isin(operadores)]
    #
    # df = df_filtrado.reset_index(drop=True)
    # pd.set_option('display.max_colwidth', None)
    #
    # # Exibindo o DataFrame filtrado
    # st.dataframe(df, use_container_width=True, hide_index=True)


def diario_bordo():
    # Título da página
    st.title('Atualizar Diário de Bordo')

    if 'Auxiliar' in st.session_state['cargo']:
        st.write(f'{st.session_state["nome"]}, ainda estamos em etapa de finalização! Por favor, aguarde!')
    else:
        from Aegea.Supervisao.diario_bordo import atualizar_diario_bordo

        # Campos para coleta de dados
        hoje = date.today()
        matricula = st.text_input('Matrícula do Agente')
        data_inicio = st.date_input('Data Início', format='DD/MM/YYYY', min_value=hoje)
        hora_inicio = st.time_input('Hora Início')
        tratativa = st.text_input('Tratativa')
        tratativa_2 = st.text_input('Tratativa 2')
        data_final = st.date_input('Data Final', format='DD/MM/YYYY', min_value=data_inicio)
        hora_final = st.time_input('Hora Final')
        atingimento = st.text_input('Atingimento')
        sistema = st.text_input('Sistema')
        impacto = st.text_input('Impacto')

        # Botão para enviar os dados
        if st.button('Enviar para o Diário de Bordo'):
            dados_obtidos = {
                'Matricula': matricula,
                'Data Inicio': data_inicio,
                'Hora Inicio': hora_inicio,
                'Tratativa': tratativa,
                'Tratativa 2': tratativa_2,
                'Data Final': data_final,
                'Hora Final': hora_final,
                'Atingimento': atingimento,
                'Sistema': sistema,
                'Impacto': impacto
            }
            print(dados_obtidos)

            st.info('Dados sendo enviados. Por favor!')
            atualizar_diario_bordo(dados_obtidos)
            st.success('Dados enviados com sucesso!')


def main():
    st.set_page_config(
        page_title="Planejamento - AeC",
        page_icon=r"C:\Users\cidirclay.queiroz\Documents\Python\PlanoAeC\img_title_aec.png",
    )

    menus1 = {
        1: {'titulo': 'Início', 'icon': 'house'},
        2: {'titulo': 'Alteração de Routing', 'icon': 'gear'},
        3: {'titulo': 'Status Automações', 'icon': 'heart'},
        4: {'titulo': 'Sinalizações', 'icon': 'book'},
        5: {'titulo': 'Conectar IP', 'icon': 'play'},
        6: {'titulo': 'Baixar Arquivos', 'icon': 'book'},
        7: {'titulo': 'Diário de Bordo', 'icon': 'gear'},
        8: {'titulo': 'Em Construção', 'icon': 'gear'},
    }

    st.markdown("""
    <style>
        /* Estilo para botões na sidebar */
        [data-test-id=stSidebar] .stButton > button {
            background-color: #0000FF;
            color: white;
        }

        /* Estilo para botões do menu na sidebar */
        [data-test-id=stSidebar] [data-testid=stVerticalBlock] {
            gap: 0;
        }

        /* Estilo para sliders na sidebar */
        [data-test-id=stSidebar] .stSlider .st-bu {
            background-color: #0000FF;
        }

        /* Estilo para caixas de seleção na sidebar */
        [data-testid=stSidebar] .stCheckbox > label > div[role="checkbox"] {
            background-color: #0000FF !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Verifica se o usuário está autenticado
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if st.session_state['authenticated']:
        st.sidebar.title("Menu")
        # Criando um menu com opções
        with st.sidebar:
            selected = option_menu(
                menu_title="Plano AeC",
                options=["Início", "Alteração de Routing", "Status Automações", "Sinalizações", "Conectar IP", "Baixar Arquivos", "Diário de Bordo", "Em Construção"],
                icons=["house", "gear", "heart", "book", "play", "book", "gear", "gear"],
                default_index=0
            )

        # Chamando a função da página escolhida
        if selected == "Alteração de Routing":
            routing(st.session_state['nome'])
        elif selected == "Status Automações":
            status_automacoes()
        elif selected == "Sinalizações":
            sinalizacao()
        elif selected == "Conectar IP":
            conect_ips()
        elif selected == "Baixar Arquivos":
            baixar_arquivos()
        elif selected == "Em construção":
            construcao()
        elif selected == "Diário de Bordo":
            diario_bordo()
        else:
            page1()

        # Botão de logout no sidebar
        if st.sidebar.button("Logout"):
            st.session_state['authenticated'] = False
            registrar_login(st.session_state['matricula'], 'logout', True)
    else:
        login_page()


if __name__ == "__main__":
    main()
