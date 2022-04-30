from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from dateutil.parser import parse
import pandas as pd
import time

cvs_file = "papers.csv"

df = pd.read_csv(cvs_file)

site = "IEEExplorer"

chaves = ["deep learning", "ct coronary"]

url1 = "https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&newsearch=true&matchBoolean=true&queryText="
filter = "&ranges=2012_2022_Year&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true&rowsPerPage=50&pageNumber="

cont = 0
search_term = ""
url2 = ""
for chave in chaves:

    search_term = search_term + chave

    chave = chave.replace(" ", "%20")

    url2 = url2 + "(%22All%20Metadata%22:" + chave +")"

    cont +=1
    if cont<len(chaves):
        url2 = url2 + "%20AND%20"
        search_term = search_term + ", "

page = 1

url_pg = url1 + url2 + filter + str(page)


browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
browser.get(url_pg)
time.sleep(7)

qtd_papers = browser.find_elements(By.CLASS_NAME,'strong')[1].text

paginas = int( int(qtd_papers) / 50)+1

link_erros = []

for pagina in range(0, paginas):


    url = url1 + url2 + filter + str(pagina+1)

    browser.get(url)
    time.sleep(30)

    elems = browser.find_elements(By.CLASS_NAME,'List-results-items')

    print(len(elems))

    ## get all links on this page
    links = []
    for elem in elems:
        id = elem.get_attribute('id')
        link = "https://ieeexplore.ieee.org/document/" + id
        links.append(link)

    for link in links:

        try:

            browser.get(link)
            time.sleep(7)

            titulo = browser.find_elements(By.TAG_NAME,'h1')[0].text

            doi = browser.find_element(By.CLASS_NAME, 'stats-document-abstract-doi').text
            doi = doi.replace("DOI: ", "")

            doi = str(doi)


            autores = browser.find_element(By.CLASS_NAME, "authors-info-container").text


            ano = ""
            try:
                ano = browser.find_elements(By.CLASS_NAME, "doc-abstract-pubdate")[0].text
            except:
                try:
                    ano = browser.find_elements(By.CLASS_NAME, "doc-abstract-dateadded")[0].text
                except:
                    print("erro no ano :: " + link)

                    ano = ""

            ano = parse(ano, fuzzy=True).year
            ano = str(ano)

            abstract = browser.find_elements(By.CLASS_NAME, "u-mb-1")[1].text
            abstract = abstract.replace("Abstract:","")
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

            time.sleep(7)
        except:
            link_erros.append(link)


print('NÃO FOI POSSÍVEL LER {} ARTIGOS'.format(len(link_erros)))
print('---------------------------------')
for link in link_erros:
    print(link)

