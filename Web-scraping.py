import pandas as pd
import numpy as np
import sqlalchemy as db
import re
import time
import itertools
from datetime import datetime as dt
from bs4 import BeautifulSoup as BSoup
from selenium import webdriver
from joblib import Parallel, delayed, parallel_backend
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

db_user = "root"
db_pass = "leo010995"
db_ip = "localhost"
db_database = "prueba_python"
conn = db.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.
                        format(db_user, db_pass, db_ip, db_database),
                        pool_recycle=3600, pool_size=5)

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

browser = webdriver.Chrome(
    executable_path="C:/chromedriver/chromedriver.exe", options=options)
browser.get("https://www.plazavea.com.pe/")
drop_not = WebDriverWait(browser, 30).until(EC.presence_of_element_located(
    (By.XPATH, "//*[contains(@id,'cancel-button')]")))
drop_not.click()

drop_opt = ["event-food", "event-nonfood"]
bases = []
for i in drop_opt:
    dropdown = browser.find_element_by_id(i)
    dropdown.click()
    subcat_boxes = browser.find_elements_by_xpath(
        "//div[@class='MainMenu__subcategory__section']//a")
    links = [x.get_attribute("href") for x in subcat_boxes]
    links_pre = [re.sub(r"^.*?pe/", "", x) for x in links]

    links_aux = [links[z] for z, x in enumerate(links_pre) if len(
        x.split("/")) - x.split("/").count("") >= 3]
    bases.append(links_aux)

bases_cons = np.unique(list(itertools.chain.from_iterable(bases)))
browser.quit()

prefs_dictionary = {'images': 2, 'popups': 2, 'geolocation': 2,
                    'notifications': 2, 'fullscreen': 2, 'mouselock': 2,
                    'mixed_script': 2, 'media_stream': 2, 'media_stream_mic': 2,
                    'media_stream_camera': 2}
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("disable-infobars")
options.add_argument("enable-automation")
options.add_argument("--disable-extensions")
options.add_argument("--disable-browser-side-navigation")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--silent")
options.add_argument("--log-level=3")
options.page_load_strategy = 'eager'
prefs = {"profile.default_content_setting_values": prefs_dictionary}
options.add_experimental_option("prefs", prefs)


def web_scrapper(links):
    browser = webdriver.Chrome(executable_path=r"C:/chromedriver/chromedriver.exe",
                               options=options,
                               port=0)
    browser.set_page_load_timeout(60)
    results = []

    for j in links:
        browser.get(j)

        try:
            wait_load = EC.visibility_of_all_elements_located(
                (By.CLASS_NAME, "Showcase__details"))
            WebDriverWait(browser, 30).until(wait_load)

            # Scroll down
            SCROLL_PAUSE_TIME = 2
            last_height = browser.execute_script(
                "return document.body.scrollHeight")

            while True:
                browser.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(SCROLL_PAUSE_TIME)
                new_height = browser.execute_script(
                    "return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            link_limpio = re.sub(
                "/", " ", re.sub(r"^.*?pe/", "", j)).split(" ")
            nivel = [re.sub("-", " ", x).strip().capitalize()
                     for x in link_limpio if x != ""]
            bs_obj = BSoup(browser.page_source, 'html.parser')
            cuadriculas = bs_obj.find_all(
                "div", {"class": "Showcase__details"})
            marcas = []
            nombres = []
            granul = []
            precio_reg = []
            precio_act = []
            precio_prom = []

            for i in cuadriculas:
                marcas.append(i.find("div", {"class": "Showcase__brand"}).text)
                link_prod = i.find(
                    "a", {"class": "Showcase__name"}).get("href")
                nombres.append(
                    re.sub("-", " ", re.sub("^.*?pe/|/p", "", link_prod)).upper())
                try:
                    precio_reg.append(
                        i.find("div", class_="Showcase__oldPrice").text)
                except:
                    precio_reg.append(None)
                try:
                    precio_act.append(i.find("div", {"class": "Showcase__salePrice"}).find(
                        "span", {"class": "price"}).get("data-price"))
                except:
                    precio_act.append(None)
                try:
                    aux = i.find("div", class_="Showcase__ohPrice")
                    if(len(aux.get("class")) > 1):
                        precio_prom.append(None)
                    else:
                        precio_prom.append(
                            aux.find("span", {"class": "price"}).get("data-price"))
                except:
                    precio_prom.append(None)

            marcas = [x.strip() for x in marcas]
            precio_reg = [re.sub("S/|,", "", x).strip()
                          if x != None else x for x in precio_reg]
            precio_act = [re.sub("S/|,", "", x).strip()
                          if x != None else x for x in precio_act]
            precio_prom = [re.sub("S/|,", "", x).strip()
                           if x != None else x for x in precio_prom]

            df_prod = pd.DataFrame({"Categoria": nivel[0],
                                    "Subcategoria": nivel[1],
                                    "Seccion": nivel[2],
                                    "Nombre": nombres,
                                    "Marca": marcas,
                                    "Precio Regular": precio_reg,
                                    "Precio Actual": precio_act,
                                    "Precio Dscto.": precio_prom})

            now = dt.now()
            df_prod["Fecha Scrap."] = now.strftime("%Y-%m-%d %H:%M:%S")
            results.append(df_prod)
            time.sleep(np.random.randint(5, 10))

        except TimeoutException:
            results.append("Error: La pagina no cargo en el tiempo limite.")
            time.sleep(np.random.randint(5, 10))
            continue

    browser.quit()
    return(results)


nucleos = 4

# Inicialmente, debemos barrer todos los links
enlaces = bases_cons
# Sin embargo, pueden haber errores en el transcurso
enlaces_caidos = enlaces
# Agregamos un contador limite de intentos ya que no vale la pena intentarlo muchas veces
limite = 0
# Guardamos los consolidados de cada vuelta
consolidados_finales = []

while len(enlaces_caidos) != 0:

    print(str(len(enlaces_caidos)) + " pendientes ...")

    chunks = np.array_split(enlaces_caidos, nucleos)

    a = time.time()
    results = Parallel(n_jobs=nucleos)(delayed(web_scrapper)(i)
                                       for i in chunks)
    b = time.time()

    print("Vuelta " + str(limite + 1) + " ...")
    print("Tiempo total: {:.1f} segundos".format(b - a))

    consolidado = list(itertools.chain.from_iterable(results))
    consolidados_finales.append(consolidado)
    errores = [not isinstance(x, pd.DataFrame) for x in consolidado]
    enlaces_caidos = list(itertools.compress(enlaces_caidos, errores))

    limite += 1

    if limite == 4:
        break

dfs_bbdd = list(itertools.chain.from_iterable(consolidados_finales))
base = pd.concat(list(itertools.compress(
    dfs_bbdd, [isinstance(x, pd.DataFrame) for x in dfs_bbdd])))
base["% Dscto.Reg."] = base.apply(lambda row: np.round(1 - float(row["Precio Actual"]) / float(row["Precio Regular"]), 3) * 100
                                  if row["Precio Regular"] != None and row["Precio Actual"] != None
                                  else None, axis=1)

base["% Dscto.Prom."] = base.apply(lambda row: np.round(1 - float(row["Precio Dscto."]) / float(row["Precio Actual"]), 3) * 100
                                   if row["Precio Dscto."] != None and row["Precio Actual"] != None
                                   else None, axis=1)
base["Precio Regular"] = base["Precio Regular"].astype("float")
base["Precio Actual"] = base["Precio Actual"].astype("float")
base["Precio Dscto."] = base["Precio Dscto."].astype("float")
base = base.reset_index(drop=True)

base.to_sql(name="bbdd_productos", con=conn,
            if_exists='append', index=False, chunksize=1000)
