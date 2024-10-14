import os
import sys
import time as t
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import UnexpectedAlertPresentException, StaleElementReferenceException, NoSuchElementException, WebDriverException, NoSuchWindowException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from siqual_lite import inserir_dados_routing, inserir_registro_automacoes

"""##### LOGGER #####"""
import logging
from colorlog import ColoredFormatter

# Criar um handler que vai imprimir no terminal
console_handler = logging.StreamHandler()

# Configuração do logger com arquivo e terminal
file_handler = logging.FileHandler(R"F:\Python\Logs\atribui_tkt.log")

# Definir o formato das mensagens de logg com cores para o terminal
formatter = ColoredFormatter("%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S', log_colors={'DEBUG': 'red', 'INFO': 'bold_green', 'WARNING': 'bold_cyan', 'ERROR': 'bold_yellow', 'CRITICAL': 'bold_red', })

# Definir o formato simples para o arquivo de log
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')

# Aplicar os formatters aos handlers
console_handler.setFormatter(formatter)
file_handler.setFormatter(file_formatter)

# Configuração do logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Adicionar os handlers ao logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
"""##### LOGGER #####"""
ignored_exceptions = (UnexpectedAlertPresentException, StaleElementReferenceException, WebDriverException, NoSuchElementException, NoSuchWindowException)


def login_zendesk(driver, titulo_pagina):
    login_zendesk1 = False

    while not login_zendesk1:
        page_elements = {
            "Entrar": {"xpath": "//input[@id='i0116']", "value": "cidirclay.queiroz@aeparceiros.com.br"},
            "Insira a senha": {"xpath": "//input[@type='password']", "value": "12817374703@Ae"},
            "Mais informações necessárias": {"xpath": "//input[@id='idSubmit_ProofUp_Redirect']", "value": None},
            "Continuar conectado?": {"xpath": "//input[@id='idSIButton9']", "value": None},
            "Mantenha sua conta segura": {"xpath": "//div/a[@role='link']", "value": None}
        }

        if titulo_pagina in page_elements:
            logger.info(f'Titulo da pagina: {titulo_pagina} encontrado')
        else:
            logger.info(f'Titulo da pagina: {titulo_pagina} NÃO encontrado')

        logger.warning("Zendesk deslogado. Tentando fazer login...")

        try:
            for element, dado in page_elements.items():
                if titulo_pagina in element:
                    logger.info(f'Titulo da pagina: {titulo_pagina} encontrado')

                    xpath = dado["xpath"]
                    value = dado["value"]
                    logger.info(f'{xpath} - {value}')
                    t.sleep(3)
                    elemento_pagina = None

                    try:
                        elemento_pagina = WebDriverWait(driver, 15, ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, f'{xpath}')))
                        logger.info(f"Elemento encontrado {elemento_pagina.text} para {xpath}")
                    except:
                        logger.critical(f'Elemento NÃO ENCONTRADO: {xpath}')

                    if value:
                        driver.execute_script("arguments[0].value = '';", elemento_pagina)
                        t.sleep(1)
                        elemento_pagina.click()
                        logger.info(f"Com {value}. Elemento clicado: {value}")
                        t.sleep(1)
                        elemento_pagina.send_keys(value)
                        t.sleep(1)
                        logger.info(f"Valor enviado para o elemento: {value}")
                    else:
                        elemento_pagina.click()
                        logger.info(f"Sem value. Elemento clicado")
                    t.sleep(2)
                    ActionChains(driver).send_keys(Keys.ENTER).perform()
                    t.sleep(1)
                    break
                else:
                    logger.info(f'Titulo da pagina: {titulo_pagina} NÃO encontrado')
                    continue
            login_zendesk1 = True
        except Exception as ex:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.critical(f"Erro crítico na função BUSCA-FILA. Linha: {exc_traceback.tb_lineno}. Erro: {type(ex).__name__}")

    return login_zendesk1


def processar_lista(lista_nomes, atributo, matricula):
    valor_routing = False
    while not valor_routing:
        s = Service(r"F:\Python\chromedriver.exe")
        options = Options()
        options.add_argument(r'user-data-dir=F:\Python\Aegea\Profiles\PerfilRouting')

        driver = webdriver.Chrome(service=s, options=options)
        driver.maximize_window()
        logger.info('Browser conectado')

        # try:
        pagina_principal = driver.window_handles[0]
        driver.switch_to.window(pagina_principal)
        site1 = 'https://aegea.zendesk.com/admin/people/team/agents'
        driver.get(site1)
        t.sleep(5)

        try:
            try:
                driver.switch_to.frame(0)
            except:
                driver.switch_to.frame(1)

            membros_equipe = WebDriverWait(driver, 5, ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, '//h2[@id="people-search-page-title"]'))).text
            if membros_equipe == 'Membros da equipe':
                pass
            else:
                membros_equipe = WebDriverWait(driver, 1, ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, 'erro'))).text
            logger.info(f'Titulo: {membros_equipe}')
        except:
            """FAZENDO LOGIN PAGINAS AEGEA"""
            try:
                logger.info(f'entrando NO LOGIN1.')
                while True:
                    logger.info(f'entrando no while')
                    try:
                        t.sleep(2)
                        logger.info(f'entrando no try valor1')
                        valor1 = WebDriverWait(driver, 5, ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, '//div[@role="heading"]'))).text
                        logger.info(f'valor1: {valor1} encontrado')
                    except:
                        t.sleep(2)
                        logger.info(f'erro no try valor1. entrando no try valor2')
                        valor1 = WebDriverWait(driver, 5, ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//div/section[contains(.,'Mantenha sua conta segura')]"))).text
                        logger.info(f'valor1: {valor1} encontrado')
                    if not login_zendesk(driver, valor1):
                        logger.info(f'foi na função')
                        t.sleep(3)
                        logger.info(f'login_zendesk: False encontrado')
            except Exception as ex:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logger.critical(f"Erro crítico na função processar_lista. Linha: {exc_traceback.tb_lineno}. Erro: {type(ex).__name__}")
            logger.info(f'SAINDO DO LOGIN1.')
            """FAZENDO LOGIN PAGINAS AEGEA"""
        logger.info(f'LOGADO!!')

        for usuario1 in lista_nomes:
            try:
                from Aegea.busca_nome_incorreto import busca_nome_correto
                usuario = busca_nome_correto(usuario1, True)
            except:
                usuario = usuario1

            pagina_principal = driver.window_handles[0]
            driver.switch_to.window(pagina_principal)
            t.sleep(5)

            driver.get(site1)
            t.sleep(3)
            logger.info(usuario)
            usuario = usuario.rstrip(";").title()
            logger.info(f'Usuario atual: {usuario}')

            try:
                driver.switch_to.frame(0)
            except:
                driver.switch_to.frame(1)
            campo_busca = WebDriverWait(driver, 30, ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//input[@name='query']")))
            campo_busca.click()
            campo_busca.clear()
            campo_busca.send_keys(usuario)
            ActionChains(driver).send_keys(Keys.ENTER).perform()
            logger.info('Nome enviado')

            t.sleep(3)
            usuario_atual = WebDriverWait(driver, 30, ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, f"//div[@id='search-result']/div/div[2]/h1/a")))
            usuario_atual.click()
            logger.info('Usuario clicado')

            t.sleep(3)
            pagina_usuario = driver.window_handles[-1]
            driver.switch_to.window(pagina_usuario)
            t.sleep(5)
            logger.info('Assumiu PAGINA -1')

            while True:
                try:
                    aba_grupos = WebDriverWait(driver, 30, ignored_exceptions=ignored_exceptions).until(expected_conditions.element_to_be_clickable((By.XPATH, "(//div[contains(.,'Grupos')])[6]/div/div")))
                    t.sleep(5)
                    aba_grupos.click()
                    t.sleep(5)
                    logger.info('Abriu aba grupos')
                    break
                except:
                    logger.info('Erro ao abrir os grupos. Tentando novamente!')
                    pass

            # selecionando lista de rountings
            routings_selecionados = WebDriverWait(driver, 30, ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_all_elements_located((By.XPATH, '//div[@class="ember-view tile selected"]')))
            logger.info('Listando [Routings]')

            for valor in routings_selecionados:
                print(f'[Routings] ativos: {valor.text}')

            if atributo not in routings_selecionados:
                elementos = WebDriverWait(driver, 30, ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_all_elements_located((By.XPATH, '//div[@class="ember-view tile"]')))
                for elemento_a_ser_selecionado in elementos:
                    if elemento_a_ser_selecionado.text == atributo:
                        t.sleep(5)
                        # Simular um clique no elemento para selecioná-lo
                        elemento_a_ser_selecionado.click()
            t.sleep(3)

            # selecionando routing principal
            grupo_padrao = WebDriverWait(driver, 30, ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, '//div[@class ="zd-selectmenu zd-selectmenu-root zd-state-default"]')))
            logger.info(f'[Routing] padrao: {grupo_padrao.text}')
            if atributo == "[routing]Oceano Backoffice Rap…":
                atributo2 = "[routing]Oceano Backoffice Rapido"
            else:
                atributo2 = atributo

            if grupo_padrao.text == atributo2:
                st.info(f'Usuário {usuario} já está no [routing] desejado {atributo2}')
                t.sleep(2)
                driver.close()
                pass
            else:
                grupo_padrao.click()
                t.sleep(3)
                logger.info(f'Grupo padrão {grupo_padrao.text}')

                routing_lista = WebDriverWait(driver, 30, ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_all_elements_located((By.XPATH, '//div[@class="zd-menu-root zd-menu-autofit-mode"]/ul')))
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", routing_lista)

                itens_da_lista_grupo_padrao = []
                for elemento_lista in routing_lista:
                    itens_da_lista_grupo_padrao.extend(elemento_lista.find_elements(By.TAG_NAME, "li"))

                for item in itens_da_lista_grupo_padrao:
                    if item.text == atributo2:
                        logger.info(f'[Routing] selecionado: {item.text}')
                        item.click()
                        break
                t.sleep(3)

                # selecionando routings atuais
                for item in routings_selecionados:
                    elemento_a_ser_rejeitado = item.text
                    lista_routings = ["[routing]Oceano Atendimento", "[routing]Oceano Voz", "[routing]Oceano Emergencial", "[routing]Oceano BackOffice", "[routing]Oceano Backoffice Rap…"]
                    if elemento_a_ser_rejeitado != atributo and elemento_a_ser_rejeitado in lista_routings:
                        logger.info(f'[Routing] excluido: {elemento_a_ser_rejeitado}')
                        item.click()
                    t.sleep(1)
                t.sleep(3)

                # Fechando aba
                fechares = WebDriverWait(driver, 30, ignored_exceptions=ignored_exceptions).until(expected_conditions.element_to_be_clickable((By.XPATH, f"(//button[text()='Fechar'])[3]")))
                fechares.click()
                logger.info('clicou botao fechar')
                t.sleep(3)
                driver.close()

                inserir_dados_routing(usuario, atributo, matricula)
                st.success(f'{usuario} atualizado para {atributo}')
            t.sleep(2)
        valor_routing = True
        inserir_registro_automacoes('automacoes', 'Sinergia', 'ALTERAR ROUTING', 'AEGEA', 'ENVIADO')
        # except Exception as ex:
        #     exc_type, exc_value, exc_traceback = sys.exc_info()
        #     logger.critical(f"Erro crítico na função ATRIBUI_TKT. Linha: {exc_traceback.tb_lineno}. Erro: {type(ex).__name__}")
        #     inserir_registro_automacoes('automacoes', 'Sinergia', 'ALTERAR ROUTING', 'AEGEA', 'NAO ENVIADO')
        #     st.error(f'Erro! Por favor, tente novamente, {st.session_state["nome"]}!')
        #     valor_routing = False
        # finally:
        driver.quit()
        st.warning('SAINDO...')
        return valor_routing


def main():
    pass


if __name__ == "__main__":
    # lista = ['DANIEL FERREIRA DE OLIVEIRA REIMÃO', 'BRUNO OLIVEIRA DE BRITO']
    # processar_lista(lista, '[routing]Oceano Backoffice Rap…', 'Cidirclay')
    pass
