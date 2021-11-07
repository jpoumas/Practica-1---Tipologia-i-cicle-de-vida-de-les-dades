from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import csv
import re 
import os

#-------------------------------------------------------------------------------------------------
#                            Definició de les funcions
#-------------------------------------------------------------------------------------------------

#Funció encarregada d'obtenir les dades dels jugadors dels diferents equips de la lliga
def downloadData(url):
    # DataFrame on afegirem les dades dels porters
    df_goalkeepers =  pd.DataFrame(columns=["NOM","POS","EDAD","EST","PESO","NAC","AP","SUB","G",
                                            "A","GA","TT","TM","FC","FS","TA","TR"])
    
    # Dataframe on afegirem les dades dels jugadors
    df_players =  pd.DataFrame(columns=["NOM","POS","EDAD","EST","PESO","NAC","AP","SUB","G",
                                           "A","GA","TT","TM","FC","FS","TA","TR"])
    url_teams = [] 
    
    # Obtenim la pàgina web i l'objecte BeautifulSoup
    html_lliga = get_html(url)
    soup_lliga = get_object_soup(html_lliga)
    
    # Obtenim els elements del dom que forman part del div del llistat dels clubs
    div_equips = soup_lliga.find('div', class_ = "layout is-split")
    content_list = div_equips.find_all('div', class_ = "ContentList__Item")
    
    url_teams = get_links_url_id_teams(content_list)
    
    # seleccionem de totes les url de cada equip de la lliga les que
    # tenen el seu identificador 
    selected_url_teams =  select_main_url_teams(url_teams)
    
    # Recorrem totes url obtingudes dels clubs
    for item in selected_url_teams:
        # Obtenim l'url on apareixen els jugadors de l'equip
        url_player_team = build_url_players(item)
        html_players = get_html(url_player_team)
        soup_teams = BeautifulSoup(html_players, "lxml")
            
        # Obtenim les dades dels porters
        df_goalkeepers = get_goalkeepers(soup_teams, df_goalkeepers)
        
        # Obtenim les dades dels jugadors
        df_players = get_players(soup_teams, df_players)
        

    result = pd.concat([df_goalkeepers, df_players])
    return result
   

# Funció que descarrega la pàgina web 
def get_html(url):
    try:
        html = urlopen(url).read()
    except urllib2.URLError as e:
        print('Download error:', e.reason)
        html = None
    return html


# Funció que retorna l'objecte de BeautifulSoup
def get_object_soup(html): 
    try:
        soup = BeautifulSoup(html, 'lxml')
    except AttributeError as e:
        return None  
    return soup

# Funció que obté tots els links dels equips del tag href
def get_links_url_id_teams(content_list):
    result = []
    
    for i in content_list:
        links = i.find_all("a")
        for link in links:
            link_url = link["href"]
            result.append(link_url)
    
    return result

# Funció que selecciona les url dels equips on apareix el
# seu identificador
def select_main_url_teams(url_teams):
    result = []
    
    # construim una array a les posicions de les url que volem obtenir
    ind_pos = [0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,68,72,76]
    
    # Obtenim les url de les posicions 
    for index in ind_pos:
        result.append(url_teams[index])
    return result


# Funció que construeix i retorna l'url que accedeix als jugadors d'un equip
def build_url_players(item):
    # Obtenim la subcadena on apareix l'identificador i en nom de l'equip
    substring = item[17:]
    #construim l'adreça l'url on apareixen els jugadors de l'equip
    result = "http://espndeportes.espn.com/futbol/equipo/plantel/_/" + substring
    return result


#Funció que retorna les dades dels portes
def get_goalkeepers(soup, df_goalkeepers):
    # busquem el tag de la taula on apareixen els jugadors
    table = soup.find('table')
    
    for row in table.find_all('tr'):
        table_data = row.find_all('td')
        if table_data:
            nom = table_data[0].text.strip()
            posicio = table_data[1].text.strip()   
            edat = table_data[2].text.strip()
            estatura = table_data[3].text.strip()
            pes = table_data[4].text.strip()
            nac = table_data[5].text.strip()
            ap = table_data[6].text.strip()
            sub = table_data[7].text.strip()
            a = table_data[8].text.strip()
            goles_concedidos = table_data[9].text.strip()
            faltas_cometidas = table_data[11].text.strip()
            faltas_sufridas = table_data[12].text.strip()
            tarjeta_amarilla = table_data[13].text.strip()
            tarjeta_roja = table_data[14].text.strip()
        
            df_goalkeepers = df_goalkeepers.append({'NOM': nom, 
                                                    'POS': posicio, 
                                                    'EDAD': edat, 
                                                    'EST': estatura, 
                                                    'PESO': pes, 
                                                    'NAC': nac,
                                                    'AP': ap, 
                                                    'SUB': sub,
                                                    'G': "0",
                                                    'A': a,
                                                    'GA': goles_concedidos,
                                                    'TT': "0",
                                                    'TM': "0",     
                                                    'FC': faltas_cometidas,
                                                    'FS': faltas_sufridas,
                                                    'TA': tarjeta_amarilla,
                                                    'TR': tarjeta_roja}, ignore_index=True)
     
    return df_goalkeepers  
      
            
#Funció que retorna les dades dels jugadors
def get_players(soup, df_players):
    table_Body = soup.find('tbody', class_ = "Table__TBODY").find_next('tbody', class_ = "Table__TBODY")
    
    for row in table_Body.find_all('tr'):
        table_data_body = row.find_all('td')
    
        if table_data_body:
            nom = table_data_body[0].text.strip()
            posicio = table_data_body[1].text.strip()   
            edat = table_data_body[2].text.strip()
            estatura = table_data_body[3].text.strip()
            pes = table_data_body[4].text.strip()
            nac = table_data_body[5].text.strip()
            ap = table_data_body[6].text.strip()
            sub = table_data_body[7].text.strip()
            gols = table_data_body[8].text.strip()
            a = table_data_body[9].text.strip()
            tiros = table_data_body[10].text.strip()
            tiros_a_meta = table_data_body[11].text.strip()
            faltas_cometidas = table_data_body[12].text.strip()
            faltas_sufridas = table_data_body[13].text.strip()
            tarjeta_amarilla = table_data_body[14].text.strip()
            tarjeta_roja = table_data_body[14].text.strip()
        
            df_players = df_players.append({'NOM': nom, 
                                            'POS': posicio, 
                                            'EDAD': edat, 
                                            'EST': estatura, 
                                            'PESO': pes, 
                                            'NAC': nac,
                                            'AP': ap,
                                            'SUB': sub,
                                            'G': gols,
                                            'A': a,
                                            'GA': "0",
                                            'TT': tiros,
                                            'TM': tiros_a_meta,     
                                            'FC': faltas_cometidas,
                                            'FS': faltas_sufridas,
                                            'TA': tarjeta_amarilla,
                                            'TR': tarjeta_roja}, ignore_index=True)
    return df_players

#---------------------------------------------------------------------------------------------
#                                       Main
#---------------------------------------------------------------------------------------------

# Cridem la funció encarregade de fer el scrapin
response = downloadData('https://espndeportes.espn.com/futbol/equipos/_/liga/ESP.1/primera-divisi%C3%B3n-de-espa%C3%B1a')

if response.empty:
    print("Title could not be found")
else:
    out_name_file = 'dataset.csv'
    out_dir = './Practica1'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
    fullname = os.path.join(out_dir, out_name_file)   
    response.to_csv(fullname, index = False, sep=';', encoding='ansi', header = True)

