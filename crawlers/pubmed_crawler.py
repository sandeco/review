from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from dateutil.parser import parse
import pandas as pd
import time

chaves = ["deep learning", "ct coronary"]


cvs_file = "papers.csv"
df = pd.read_csv(cvs_file)


site = "PUBMED"

url1 = "https://pubmed.ncbi.nlm.nih.gov/?term="
filter = "&filter=years.2011-2021&page="

cont = 0
search_term = ""
url2 = ""
for chave in chaves:

    search_term = search_term + chave

    chave = chave.replace(" ", "%20")

    url2 = url2 + "(" + chave +")"

    cont +=1
    if cont<len(chaves):
        url2 = url2 + "%20AND%20"
        search_term = search_term + ", "

page = 1

url_pg = url1 + url2 + filter + str(page)


browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
browser.get(url_pg)
time.sleep(10)

qtd_papers = browser.find_elements(By.CLASS_NAME,"value")[0].text.replace(",","")

paginas = int(int(qtd_papers) / 10)+1

link_erros = []

for pagina in range(1, paginas):

    #url = url1 + search_term + filter + str(pagina)
    url = url1 + url2 + filter + str(pagina)
    browser.get(url)
    time.sleep(10)

    elems = browser.find_elements(By.CLASS_NAME,"docsum-title")
    links = [elem.get_attribute('href') for elem in elems]

    for link in links:

        try:
            browser.get(link)
            time.sleep(10)

            doi = browser.find_elements(By.CLASS_NAME,"id-link")[1].text

            titulo = browser.find_elements(By.CLASS_NAME,"heading-title")[0].text

            auths = browser.find_elements(By.CLASS_NAME,"authors-list-item ")
            autores = ""

            aux=0
            for aut in auths:
                autor = aut.text
                if autor!="":
                    autores = autores + autor
                    cont+=1
                    if aux<=len(auths):
                        autores = autores + ", "

            autores = autores.replace(" , , ", "; ")

            autores = ''.join(i for i in autores if not i.isdigit())


            ano = browser.find_elements(By.CLASS_NAME,"cit")[0].text
            ano = ano.split(";")[0]
            ano = parse(ano, fuzzy=True).year
            ano = str(ano)

            abstract = str(browser.find_elements(By.CLASS_NAME,"abstract-content")[0].text)
            abstract = abstract.replace("Abstract", "")
            abstract = abstract.replace("\n", " ")


            dados = {'artigo': titulo,
                         'autores': autores,
                         'doi': doi,
                         'ano': ano,
                         'link': link,
                         'abstract': abstract,
                         'site': site,
                         'search_term': search_term}

            new_line = pd.DataFrame(data=dados, index=[0])

            df = df.append(new_line, ignore_index=True)

            df.to_csv(cvs_file, index=False)

            time.sleep(3)
        except:
            link_erros.append(link)


print('NÃO FOI POSSÍVEL LER {} ARTIGOS'.format(len(link_erros)))
print('---------------------------------')
for link in link_erros:
    print(link)
