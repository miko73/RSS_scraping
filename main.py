# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import xml.etree.ElementTree as ET
import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin  # Importujeme funkci pro vytvoření úplné URL
import datetime

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

log_filename='log.txt'
stored_couneter = 0

def my_print(*args, **kwargs):
    # Získání původního sys.stdout
    original_stdout = sys.stdout
    global log_filename
    # Otevření souboru pro zápis
    # log_filename = 'log.txt'
    print(f'log_filename : {log_filename}')
    print(*args, **kwargs)

    with open(log_filename, 'a', encoding="utf-8") as log_file:
        # Přesměrování sys.stdout na log_file
        sys.stdout = log_file

        # Použití původního print se všemi argumenty
        print(*args, **kwargs)

        # Vrácení původního sys.stdout
        sys.stdout = original_stdout

def process_links(base_url, url, deska_name):
    # Stáhneme stránku
    text_pro_ulozeni=''
    # response = requests.get(url)
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))

    try:
        response = session.get(url)
        response.raise_for_status()  # Check for HTTP status code
        # Process the response here
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return



    # Zkontrolujeme, zda byla stránka úspěšně stažena
    if response.status_code == 200:
        # Vytvoříme objekt BeautifulSoup pro parsování HTML
        # soup = BeautifulSoup(response.text, 'html.parser')

        soup = BeautifulSoup(response.text, 'html.parser')

        # Najdeme všechny elementy <tr> s class "even"
        tr_elements = soup.find_all('tr', class_='even')

        for tr_element in tr_elements:
            # Zkontrolujeme, zda obsahuje element <th> s textem "Název"
            th_element = tr_element.find('th', text='Název')
            if th_element:
                # Najdeme odpovídající <td> element
                td_element = tr_element.find('td')
                if td_element:
                    # Získáme text z <td> elementu a uložíme ho do proměnné
                    obsha = td_element.text.strip()[:160]
                    special_characters = "/\|\"<>:*?\t"
                    obsha = ''.join(['_' if char in special_characters else char for char in obsha])

                    # my_print(f'url: {url}')
                    # my_print(f'Obsah proměnné "obsha": {obsha}')
                    my_print(f'<a href="{url}">{obsha}</a> <br>')

                    text_pro_ulozeni = text_pro_ulozeni + "\n" + url
                    text_pro_ulozeni = text_pro_ulozeni + "\n" + f'Obsah proměnné "obsha": {obsha}'
                    # Můžeme ukončit smyčku, protože jsme našli požadovaný prvek
                    break
            else:
                print('Nepodařilo se najít <tr> element s class "even" obsahující <th>Název</th>.')

        # Najdeme element <h1>Obsah vyvěšení</h1>
        h1_element = soup.find('h1', text='Obsah vyvěšení')

        if h1_element:
            # Najdeme tabulku uvnitř elementu <h1>
            table_element = h1_element.find_next('table', style='width: 100%; table-layout:fixed')

            if table_element:
                # Vytvoříme adresář pro uložení souborů

                directory_name = os.path.join('vyvesky_archiv', deska_name, obsha)
                os.makedirs(directory_name, exist_ok=True)


                # Projdeme řádky tabulky
                for tr_element in table_element.find_all('tr'):
                    # Najdeme odkaz v prvku <a>
                    a_element = tr_element.find('a')

                    if a_element:
                        # Získáme odkaz na soubor a vytvoříme úplnou URL
                        file_url = urljoin(base_url, a_element.get('href'))

                        # Získáme název souboru z odkazu
                        file_name = os.path.basename(file_url)

                        # Stažení souboru a uložení do adresáře
                        try:
                            with open(os.path.join(directory_name, file_name), 'wb') as file:
                                file_response = requests.get(file_url)
                                file.write(file_response.content)
                                my_print(f'<a href="file:///C:/Users/miko/PycharmProjects/RSS_scraping/{directory_name}/{file_name}"> ../{file_name} </a>')
                        except:
                         print(f'Chybné jméno souboru : {file_name}')
            else:
                print('Nepodařilo se najít tabulku uvnitř elementu <h1>.')
        else:
            print('Nepodařilo se najít element <h1>Obsah vyvěšení</h1>.')







        # Najdeme element <h1>Stav vyvěšení</h1>
        h1_element = soup.find('h1', text='Stav vyvěšení')

        if h1_element:
            # Najdeme tabulku uvnitř elementu <h1>
            table_element = h1_element.find_next('table', style='width:100%; table-layout:fixed')

            if table_element:
                # Projdeme řádky tabulky
                for tr_element in table_element.find_all('tr'):
                    # Najdeme odkaz v prvku <a>
                    # print(f'stav {tr_element.text}')
                    th=tr_element.find("th")
                    td=tr_element.find("td")
                    my_print(f'<p> {th.text} {td.text} </p>')
                    # a_element = tr_element.find('th')
                    # if a_element:
                    #     a_element.get
                    #     # Získáme název souboru z odkazu
                    #     file_name = os.path.basename(file_url)
                    #
                    #     # Stažení souboru a uložení do adresáře
                    #     try:
                    #         with open(os.path.join(directory_name, file_name), 'wb') as file:
                    #             file_response = requests.get(file_url)
                    #             file.write(file_response.content)
                    #             my_print(f'<a href="file:///C:/Users/miko/PycharmProjects/RSS_scraping/{directory_name}/{file_name}"> ../{file_name} </a>')
                    #     except:
                    #       print(f'Chybné jméno souboru : {file_name}')
            else:
                print('Nepodařilo se najít tabulku uvnitř elementu <h1>.')
        else:
            print('Nepodařilo se najít element <h1>Stav vyvěšení</h1>.')








    else:
        print(f'Chyba při stahování stránky. Kód chyby: {response.status_code}')
        # my_print(f'<p>soubor protokolu: {protokol}</p>')

# def print_log(protokol, ):

def get_rss(deska, url):

    # Get the current date
    current_date = datetime.date.today()

    # Format the date as "yyyy_mm_dd"
    formatted_date = current_date.strftime("%Y_%m_%d")
    xml_file_name = formatted_date + '_' + deska + '.xml'

    # Define the directory path
    directory_name = os.path.join('vyvesky_archiv', deska, 'XMLs')

    # Check if the directory exists
    if not os.path.exists(directory_name):
        # Create the directory if it doesn't exist
        os.makedirs(directory_name)
        print(f"The directory '{directory_name}' has been created.")
    else:
        print(f"The directory '{directory_name}' already exists.")

    # Create the full path to the file
    xml_file_name = os.path.join(directory_name, xml_file_name)

    # Check if the file does not exist
    if not os.path.exists(xml_file_name):
        print(f"The file '{xml_file_name}' does not exist in the directory '{directory_name}'.")

        # Print the formatted date
        print(f'xml_file_name : {xml_file_name}')

        # Stáhnutí dat z URL
        response = requests.get(url)

        # Zkontrolujte, zda bylo stahování úspěšné
        if response.status_code == 200:
            xml_data = response.text.replace("#", "%23")  # Získání textového obsahu z odpovědi

            # Uložení XML dat do souboru
            with open(xml_file_name, "w", encoding="utf-8") as xml_file:
                xml_file.write(xml_data)
            print(f"XML data byla uložena do souboru {xml_file_name}.")
        else:
            print(f"Chyba při stahování dat: {response.status_code}")
        return True, xml_file_name
    else:
        print(f"The file '{xml_file_name}' exists in the directory '{directory_name}'.")
        return False, xml_file_name


def scrap_rss(base_url, url, deska_name):
    global log_filename
    new_xml, rss_file_name = get_rss(deska_name, url)
    if not new_xml:
        print(f'RSS file exists {rss_file_name}')
        # return False

    tree = ET.parse(rss_file_name)

    # Get the root element
    root = tree.getroot()

    # Iterate through the first 5 <link> elements
    # for link_element in root.findall('.//link')[:10]:  # Limit to the first 5 elements
    for link_element in root.findall('.//link'):  # Limit to the first 5 elements
        link_value = link_element.text  # Get the text value of the <link> element
        # link_value = link_value.replace('#', '%23')
        global stored_couneter
        url = link_value
        stored_couneter = stored_couneter + 1


        log_filename = deska_name
        log_filename = log_filename + '.html'
        # with open(protokol, "a", encoding="utf-8") as soubor_objekt:
        # soubor_objekt.write(text_pro_ulozeni)
        # with open(protokol, 'a', encoding="utf-8") as log_file:
        my_print(f'<p>Počet uložených : {stored_couneter}</p>')
        # my_print(f'url: {url}')
        # Uložení původního sys.stdout
        # original_stdout = sys.stdout

        # Přesměrování sys.stdout na log_file
        # sys.stdout = log_file

        # Zde můžete používat print a výstup bude zapisován do log_file
        # print("Toto je zpráva, která bude uložena do souboru.")
        process_links(base_url, url, deska_name)
        # Vrácení původního sys.stdout
        # sys.stdout = original_stdout





def scrap_hmp():
    base_url = "https://eud.praha.eu"
    url = 'http://eud.praha.eu/pub/rss/6000004/4/?nazev=&cislo_jednaci=&datum_od=&datum_do=&text=&pozice=0&pocet=25&trideni='
    deska_name = 'HMP'
    scrap_rss(base_url, url, deska_name)

def scrap_p5():
    base_url = "https://eud.praha5.cz"
    deska_name = 'MCP5'
    # URL, ze kterého chceme stáhnout XML data
    url = "https://eud.praha5.cz/pub/rss/13000002/MC05AWO0A02N/?nazev=&cislo_jednaci=&datum_od=&datum_do=&text=&pozice=0&pocet=100&trideni="
    scrap_rss(base_url, url, deska_name)

def scrap_p10():
    base_url = "http://edeska.praha10.cz"
    deska_name = 'MCP10'
    # URL, ze kterého chceme stáhnout XML data
    url = "https://edeska.praha10.cz/rss.jsp"
    scrap_rss(base_url, url, deska_name)




# Po skončení tohoto bloku kódů se výstup opět vrátí na standardní výstup (obvykle konzoli)
print("Toto se vypíše na standardní výstup.")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    scrap_p5()
    scrap_hmp()
    # scrap_p10()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
