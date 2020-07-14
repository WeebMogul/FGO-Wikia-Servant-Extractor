import urllib
from urllib.request import Request
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from tqdm import tqdm 

def servant_physical_stats(soup,name):

    bio = soup.find('span',{'id':'Biography'})
    
    if bio == None:
        bio = soup.find('span',{'id':'Biography.C2.A0'}) # Nightingale
    
    bio_table = bio.find_next('table')

    bio_row = bio_table.find_all('tr')[2]

    if name == 'EMIYA':
        bio_row = bio_table.find_all('tr')[8]
    if name == 'Gilles_de_Rais_(Saber)':
        bio_row = bio_table.find_all('tr')[1]

    if len(bio_row) < 3:
        bio_row = bio_table.find_all('tr')[3] # James Moriarity
    
    bio_stats = bio_row.find_all('td')[1]
    bio_stat_texts = bio_stats.text.strip().split('\n')
    print(bio_stat_texts)
   
    for i in range(0,(len(bio_stat_texts))) :
        if '\u3000' in bio_stat_texts[i]:
            x = bio_stat_texts[i].replace('\u3000',' ')
            x = x.split('  ')
            print(x)
            bio_stat_texts.remove(bio_stat_texts[i])
            bio_stat_texts[i:i] = x

        series_indc = bio_stat_texts[i].find('Series: Fate/Grand Order')
        
        if series_indc > 0: # Artoria Lancer Alter and Jeanne Alter Santa
            continue
        elif series_indc < 0 :
            stat_text3 = re.sub(r'^(.*?):',' ',bio_stat_texts[i])
            #stat_text3 = stat_text3.split('\n')
            servant_data.append(stat_text3)
    
    
tso = []
d_link = os.path.join(os.getcwd(),'Servant Database.csv')
servant_db = pd.read_csv(d_link)

#servant_db['Servant_name'] = servant_db['Servant_name'].apply(lambda x : x.replace(' ','_'))
#name_list = servant_db.Servant_name
name_list = ['Caenis']

for i in tqdm(name_list):

    servant_data = []

    servant_name = urllib.parse.quote(i)

    url = 'https://fategrandorder.fandom.com/wiki/' + servant_name
    # print(url)

    reg = Request(url,headers={'User-Agent': 'Mozilla/5.0'})
    htm = urllib.request.urlopen(reg).read()
    soup = BeautifulSoup(htm,'lxml')

    servant_physical_stats(soup,i)
    tso.append(servant_data)


for i in range(0,len(tso)):
    if (len(tso[i]) > 6 or len(tso[i]) < 6):
        print('\n')
        print(tso[i])