from opcoes_db import Opcao_db
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service  # to stop the message of path deprecated
from selenium.webdriver.common.by import By
import sys
from datetime import date, timedelta
import logging
import os

class Opcao():
    dir_path = os.path.dirname(os.path.realpath(
        __file__))  # show the full path of the class
    filename = os.path.join(dir_path, 'logging_opcoes_b3.log')
    logging.basicConfig(filename=filename, level=logging.INFO)
    driver = None

    # returns all dates from the beginning until the end
    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)


    def getting_url(self, company, date):
        try:
            date = date.strftime("%d/%m/%Y") # changing the format to match with the url
            url = f'https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/consultas/mercado-a-vista/opcoes/posicoes-em-aberto/posicoes-em-aberto-8AE490C877D179740177DEC0BF4C5BD2.htm?empresaEmissora={company}&data={date}&f=0'
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # To does not open the browser options=options
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            self.driver.implicitly_wait(10)  # Wait to load the full page
            self.driver.get(url)
            #print("Getting_url")
            return self.driver
        except Exception as e:
            logging.error(self.error_handling())

    def call_put(self, company, call_put, date):
        self.driver = self.getting_url(company, date)

        if call_put == 'CALL':
            opc_empresa = self.driver.find_elements(By.XPATH,
                                                    f"//html/body/main/div/div/div/div/div[@id='titulos-compraONN2' or @id='titulos-compraPNN2']//table//tbody/tr[1]|//div[@id='titulos-compraONN2' or @id='titulos-compraPNN2']/h5")
        else:
            opc_empresa = self.driver.find_elements(By.XPATH,
                                                    f"//html/body/main/div/div/div/div/div[@id='titulos-vendaONN2' or @id='titulos-vendaPNN2']//table//tbody/tr[1]|//div[@id='titulos-vendaONN2' or @id='titulos-vendaPNN2']/h5")

        for opcao in opc_empresa:
            try:
                opcao = opcao.text
                call_put = call_put
                if opcao[-5] == "/" and opcao[-8] == '/':  # gets the date
                    self.data_vencimento = opcao[-10:]
                else:  # gets the information and calls db class to insert
                    opcao = opcao.split(' ')
                    self.serie = opcao[0]
                    self.strike = float(opcao[1].replace(',', '.'))
                    opcoes_db.insert_data(self.serie, self.strike, self.data_vencimento, date, call_put)
            except Exception as e:
                logging.error(self.error_handling())

        # print('********************************fechando o driver********************************')
        self.driver.quit()  # precisa fechar o driver para ele poder pegar uma nova data

    def error_handling(self):
        return '{}. {}, line: {}'.format(sys.exc_info()[0],
                                                       sys.exc_info()[1],
                                                       sys.exc_info()[2].tb_lineno)


if __name__ == '__main__':
    opcao = Opcao()
    opcoes_db = Opcao_db()

    #start_date = date(2020, 7, 2)  # initial date available at b3 page. Use this one
    start_date = date(2022, 10, 10)  # initial date test.
    dt = date.today()
    end_date = date(dt.year, dt.month, dt.day)-timedelta(days=1)

    if not opcoes_db.retrieve_last_data(start_date):  # Populate de db starting from the first date available in B3
        for single_date in opcao.daterange(start_date, end_date):
            date = single_date
            #print(date)
            opcao.call_put('PETROLEO BRASILEIRO S.A. PETROBRAS', 'CALL', date)
            opcao.call_put('PETROLEO BRASILEIRO S.A. PETROBRAS', 'PUT', date)
            logging.info(f'Date: {date}')

    elif opcoes_db.retrieve_last_data(end_date):
        #print('The data already exists')
        logging.info(f'The data of the day {end_date} already exists')
    else:
        #print(end_date)
        opcao.call_put('PETROLEO BRASILEIRO S.A. PETROBRAS', 'CALL', end_date)
        opcao.call_put('PETROLEO BRASILEIRO S.A. PETROBRAS', 'PUT', end_date)
        logging.info(f'Last day available: {end_date}')


#-------------------company list if you want to change the name. It's needed to put the name equals to the list.  -----------------------------------
# https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/consultas/mercado-a-vista/opcoes/posicoes-em-aberto/posicoes-em-aberto.htm?dataConsulta=10/11/2022&f=0




