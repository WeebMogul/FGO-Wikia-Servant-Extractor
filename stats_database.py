import urllib
from urllib.request import Request
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from tqdm import tqdm 
pd.options.mode.chained_assignment = None

# Columns for the Servant Stats
keys = ['Class ', 'Japanese Name', 'AKA', 'ID', 'Cost','ATK','HP','Grail ATK','Grail HP','Voice Actor','Illustrator','Attribute', 'Growth Curve','Star Absorption', 
'Star Generation','NP Charge ATK','NP Charge DEF','Death Rate', 'Alignments','Gender', 'Traits', 'Card Order', 'Quick Hits ', 'Arts Hits ', 'Buster Hits ', 'Extra Hits ', 
'Rank ', 'Classification ', 'Type ', 'Hit-Count ',]

'''
Functions such as servant_stats(),servant_card_trait(),servant_np_stats() have similar functionality :

Extract data from given tags and tables next to those tags. 
There are some tags that have a different id for the tag. 

'''

# Get the data for the main stats of all the servants 
def servant_stats(soup,servant_data):
 
 servant_class = soup.find('div',{'class':'ServantInfoClass'})
 s_class = servant_class.find('a')['title']
 servant_data.append(s_class)

 servant_stats = soup.find('div',{'class':"ServantInfoStatsWrapper"})
 stat_table = servant_stats.find_all('table',{'class':'closetable'})[0]

 stat_table_row = stat_table.find_all('tr')

 for row in stat_table_row:
    stats = row.find_all('td')

    for i in stats:
        stat_text = i.text.strip()
        servant_data.append(re.sub(r'^(.*?):',' ',stat_text))

# Get the data for the Card order, traits and the number of hits for each card
def servant_card_trait(soup,servant_data):

    servant_stats_2 = soup.find('div',{'class':"ServantInfoStatsWrapper"})

    stat_table2 = servant_stats_2.find_all('table',{'class':'closetable'})[1]
    stat_table_row2 = stat_table2.find_all('tr')

    # Table Data
    stats2 = stat_table_row2[0].find('td')
    stat_text2 = stats2.text.strip()
    servant_data.append(re.sub(r'^(.*?):',' ',stat_text2))

    # Card Order
    card_ori = stat_table_row2[1].find('img')['alt']
    servant_data.append(card_ori)

    card_hits_row = stat_table_row2[2].find('th')

    for i in range(0,4):

        card_hits = card_hits_row.find_all('div',{'class':'InumWrapper hidden'})[i]

        # Card name 
        card_name_loc = card_hits.find('div',{'class':'InumIcon hidden'})
        card_name = card_name_loc.find('a')['title']
    
        # Number of hits
        card_hitcount_loc = card_hits.find('div',{'class':'InumNum hidden'})
        card_hitcount = card_hitcount_loc.text
    
        servant_data.append('{hitcount}'.format(name=card_name,hitcount = card_hitcount))

# Get the data for the Noble Phantasm 
def servant_np_stats(soup,servant_data):

   servant_np = soup.find('span',{'id':'Noble_Phantasm'})

   if servant_np is None :
       servant_np = soup.find('span',{'id':'.E2.80.8B.E2.80.8BNoble_Phantasm'}) # Tawara Touta
   
   servant_np_table = servant_np.find_next('table')
   
   np_values_rows = servant_np_table.find_all('tr')[1]

   for i in range(0,4):

       values = np_values_rows.find_all('td')[i].text
       servant_data.append(values.strip())

class StatsDB:
    
    def create_StatsDB_file(self,state,servant_df):
        # Read data from the Servant Database .csv file
        # d_link = os.path.join(os.getcwd(),'Servant Database.csv')

        if state == True:
            print('Stat Database is already updated')
       # elif os.path.exists(d_link) == False:
           # print('Servant Database file does not exist. Reload the program again')
        else :

            print('Creating Servant Stats Database')
            # servant_db = pd.read_csv(d_link)
            servant_db = servant_df.copy()

            # Gather the names of all the Servants and replace spaces with _ 
            servant_db['Servant Name'] = servant_db['Servant Name'].apply(lambda x : x.replace(' ','_'))
            name_list = servant_db['Servant Name']

            total_servant_data = []

            for name in tqdm(name_list):
                servant_data = []

                # Parse name and create url
                servant_name= urllib.parse.quote(name)
                url = 'https://fategrandorder.fandom.com/wiki/' + servant_name

                # Send link and gather the data
                reg = Request(url,headers={'User-Agent': 'Mozilla/5.0'})
                htm = urllib.request.urlopen(reg).read()
                soup = BeautifulSoup(htm,'lxml')

                # Called functions
                servant_stats(soup,servant_data)
                servant_card_trait(soup,servant_data)
                servant_np_stats(soup,servant_data)

                # Append the given servant data to another list (reshaping is another option but eh....this also works too)
                total_servant_data.append(servant_data)

                # Create the servant stats dataframe and strip whitespace fromt 
            df = pd.DataFrame(total_servant_data,columns=keys)
            df = df.apply(lambda x : x.str.strip())
            return df
            #df.to_csv(os.path.join(os.getcwd(),'Servant Stats.csv'),encoding='utf-8')








