import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime 
date = datetime.now()


def get_url(code):

    if date.month < 4:
        semester = 1
    else:
        semester = 2
    return f'https://buscacursos.uc.cl/?cxml_semestre={date.year}-{semester}&cxml_sigla={code}#resultados'

def get_info(url, c_names):
    resource = requests.get(url).text
    souped_resource = BeautifulSoup(resource,'html.parser')

    all_rows_impar = souped_resource.find_all('tr', attrs={'class': 'resultadosRowImpar'})
    all_rows_par = souped_resource.find_all('tr', attrs={'class': 'resultadosRowPar'})

    sections = []

    # Traverse all columns in order
    for r in range(len(all_rows_par) + len(all_rows_impar)):

        if(r % 2 == 0):
            all_column = all_rows_par[r // 2].find_all('td')
        else:
            all_column = all_rows_impar[r // 2].find_all('td')

        # Save section info
        info = dict()

        for i in range(len(all_column)):
            # Erase tags
            val = all_column[i].string
            if(i < len(c_names)):
                info[c_names[i]] = val
        sections.append(info)

    return sections


def get_names(url):
    resource = requests.get(url).text
    souped_resource = BeautifulSoup(resource,'html.parser')

    all_rows = souped_resource.find_all('tr')
    c_names = []

    for row in all_rows:
        all_column = row.find_all('td')

        for i in range(len(all_column)):
            # Erase tags
            val = all_column[i].string
            
            if(i == 0 and val != 'NRC'):
                break   
            if(val == 'Vacantes'):
                c_names.append('Total')
                c_names.append('Disponibles')
                return c_names

            c_names.append(val)

def buscacursos_update():
        
    #codes = ['BIO143M', 'IIC2523']
    codes = []

    n_code = "None"
    print("Ingresar 0 para terminar")
    while(n_code):
        n_code = input("Ingresar nueva sigla de ramo: ")
        if(n_code == "0"):
            break
        elif(n_code):
            codes.append(n_code)

    c_names = get_names(get_url(codes[0]))

    pages = []
    courses = []

    for code in codes:
        page = get_url(code)      
        courses.append((get_info(page, c_names)))
        pages.append(page)

    # Starting info
    for section in courses:
        if(section):
            print(section[0]['Nombre'])
            for info in section:
                print(' Sección', info['Sec.'], 'Cupos disponibles :', info['Disponibles'])

    # Check updates
    while True:

        for i in range(len(courses)):

            sections = get_info(pages[i], c_names)
            for j in range(len(sections)):
                if(sections[j]['Disponibles'] != courses[i][j]['Disponibles']):
                    print(sections[j]['Nombre'], ' Actualización sección', sections[j]['Sec.'],':', courses[i][j]['Disponibles'], '->', sections[j]['Disponibles'], '\n')
                    courses[i][j]['Disponibles'] = sections[j]['Disponibles']

            time.sleep(1)

if __name__ == "__main__":
    buscacursos_update()