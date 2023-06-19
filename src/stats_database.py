import urllib
from urllib.request import Request
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from tqdm import tqdm 
pd.options.mode.chained_assignment = None

# Columns for the Servant Stats
keys = ['Class', 'Japanese Name', 'AKA', 'ID', 'Cost','ATK','HP','Lvl 100 Grail ATK','Lvl 100 Grail HP','Lvl 120 Grail ATK','Lvl 120 Grail HP', 'Voice Actor','Illustrator','Attribute', 'Growth Curve','Star Absorption','Star Generation','NP Charge ATK','NP Charge DEF','Death Rate', 'Alignments','Gender', 'Traits', 'Card Order', 'Quick Hits', 'Arts Hits', 'Buster Hits', 'Extra Hits','NP Damage Type','NP Rank', 'NP Classification','NP Hit-Count']

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

 for i in range(len(stat_table_row)):
    stats = stat_table_row[i].find_all('td')

    if stat_table_row[i].find('th'):
        img_link = stat_table_row[i].find('th')
        card_order = img_link.find('img')['alt']
        servant_data.append(card_order)
    else :
        for i in stats:

            if i.find_all('span',{'class':'InumMobileDisplay'}):

                tsd = i.text
                tsd = re.sub('\([^().]*\)|Hits:|  |  | ','',tsd).strip()
                tsd = tsd.split('|')
                tsd = [int(int(num)/11) for num in tsd]

                #print(tsd)
                for j in range(0,4):
                    servant_data.append(tsd[j])
            
            else :
                spx  = i.find_all('span',{'title':"Servant's minimum and maximum attack stat."})
                spx2  = i.find_all('span',{'title':"Servant's minimum and maximum HP (Health)."})
                
                if (len(spx)>0):
                    stat_text = spx[0].next_sibling
                elif (len(spx2)>0):
                    stat_text = spx2[0].next_sibling
                # Mash has both stats for lvl 80 and 90 so we remove the 90 for her
                elif (i.text.strip().find('★ ')!=-1):
                    stat_text = i.text.strip()
                    stat_text = stat_text[0:stat_text.find('★ ')]
                else :
                    # Process all of the other stats
                    stat_text = i.text.strip()

                # Some pages list 'Base' in front of ATK stat so remove it
                if(stat_text and stat_text.find('Base')!= -1):
                    stat_text = stat_text.replace('Base: ', '')

                # Some servants have additional traits specific to a stage
                # This messes up the data model so for now remove them
                remove = False
                if (stat_text.find('┗')!=-1):
                    remove = True

                # Add the stat to the servant data
                if (not remove):
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
   #print("\n")
   #print(np_values_rows)

   np_atk_type = servant_np_table.find_all('img',alt=True)[0]
   servant_data.append(np_atk_type['alt'])

   if len(np_values_rows) == 4:

       np_values_rows_2 = servant_np_table.find_all('tr')[3]
       np_values_row = str(np_values_rows) + str(np_values_rows_2)

       np_values_row_html = BeautifulSoup(np_values_row,'html.parser')

       #print(np_values_row_html)

       for i in range(0,3):

           values = np_values_row_html.find_all('td')[i].text
           #print(values)
           servant_data.append(values.strip())
   
   elif len(np_values_rows) == 6:

       np_values_rows_4 = servant_np_table.find_all('tr')[3]
       np_values_row_2 = str(np_values_rows) + str(np_values_rows_4)

       np_values_row_html_2 = BeautifulSoup(np_values_row_2,'html.parser')

       for i in range(0,3):

           values = np_values_row_html_2.find_all('td')[i].text
           # print(values)
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

                # Skip Beast_IV because it's an enemy servant only and gives errors
                if name != 'Beast_IV:_L':
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
                    #servant_card_trait(soup,servant_data)
                    servant_np_stats(soup,servant_data)

                    # Append the given servant data to another list (reshaping is another option but eh....this also works too)
                    total_servant_data.append(servant_data)
                    # print('servant: ', servant_name)
                    # print('servant data: ', servant_data)

                    # Create the servant stats dataframe and strip whitespace fromt 

            df = pd.DataFrame(total_servant_data,columns=keys)
            df = df.astype(str).apply(lambda x : x.str.strip()) 
            # df.to_csv(os.path.join(os.getcwd(),'Servant Stats.csv'),encoding='utf-8')
            return df
            #print(df)
           