from datetime import datetime
from bs4 import BeautifulSoup
import base64, os, time
import requests
import pandas as pd
from twilio.rest import Client 

disciplina_desejada = "Dinâmica de Gases"   # <-- COLOCAR DISCIPLINA DESEJADA AQUI
celular_notificar = "+5511912341234"        # <-- COLOCAR CELULAR A RECEBER O ALERTA SMS AQUI

num_itens_verificar = 50

# Abaixo deve ser incluído o link da planilha com a atualização das disciplinas liberadas:
url_planilha="https://docs.google.com/spreadsheets/d/1oOxnkl8lmP0JiByw9Ksfz4alzw_S8GrUj7pZODQCtMw/htmlview"


# Chaves do Twilio (criar conta em twilio.com):
account_sid = 'ABCccc18c3641a4cad396f7ae4f602d5f5'      # <-- COLOCAR AQUI SID GERADO NO TWILIO 
auth_token = '9813246418ef92057d53905e9de67f9e'         # <-- COLOCAR AQUI AUTH TOKEN GERADO NO TWILIO
messaging_service_id='SP241dd48cd1c128670e7099e80776218d'   # <-- COLOCAR AQUI MESSAGING SERVICE ID GERADO NO TWILIO


def send_sms_twilio():
    client = Client(account_sid, auth_token) 
    
    message = client.messages.create(  
                                messaging_service_sid=messaging_service_id, 
                                body='DISCIPLINA LIBERADA!! DISCIPLINA LIBERADA!! DISCIPLINA LIBERADA!!',      
                                to=celular_notificar
                            ) 
    
    print(message.sid)


def process_file():
    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(url_planilha).text

    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    #print(soup.prettify()) # print the parsed data of html

    gdp_table = soup.find("table", attrs={"class": "waffle"})
    gdp_table_data = gdp_table.tbody.find_all("tr")  # contains 2 rows

    # para cada linha, se primeira coluna tiver informação adiciona pra dataframe
    l = []
    for tr in gdp_table_data:
        td = tr.find_all('td')
        row = [tr.text for tr in td]
        l.append(row)
    df = pd.DataFrame(l, columns=["Materia", "Vagas", "Requisicoes", "Liberada em", "E", "F", "G"])
    df = df.iloc[1: , :]


    liberada = False
    for seq in range(num_itens_verificar):
        value = df["Materia"].iloc[seq]
        liberada = str(value).startswith(disciplina_desejada)
        if liberada: break

    if liberada:
        print("LIBERADA RECENTEMENTE!")        
        return True
    else:
        print("ainda não...")
        return False


while True:
    print(f"Verificando disponibilidade de '{disciplina_desejada}' - {str(datetime.now())}")
    status = process_file()
    if status:
        send_sms_twilio()
        break
    time.sleep(120)     #aguarda 120 segundos (2 minutos) antes de tentar novamente
    
print("FIM!")
