import urllib
from urllib.request import Request
from bs4 import BeautifulSoup
from collections import defaultdict
import pandas as pd
import os
from tqdm import tqdm

pd.options.mode.chained_assignment = None
# Range of Servant IDs
id_count = ['1-100','101-200','201-300']
#id_count = ['201-300']

class ServantDB:
    
    # Lists to store the mentioned data
    names = []
    ids = []
    rarities = []
    
    def create_ServantDB_file(self):

        print('Collecting Servant name, ID and Rarity')
        for count in tqdm(id_count) : 

            # Create a url, send request and get data, use Beautifulsoup to transcribe the HTML data
            url = 'https://fategrandorder.fandom.com/wiki/Sub:Servant_List_by_ID/'+ count

            req = Request(url,headers={'User-Agent': 'Mozilla/5.0'})
            htm = urllib.request.urlopen(req).read()
            soup = BeautifulSoup(htm,'lxml')

            # Targeting the table rows
            first = soup.find('div',{'id':'mw-content-text'})
            f_rows = first.find_all('tr')[1:]
    
            # Storing the name,rarity,id in their lists
            for i in f_rows:

                data = i.find_all('td')
                self.names.append(data[1].text.strip())
                self.ids.append(data[3].text.strip())
                self.rarities.append(data[2].text.strip())
        
        corr_rarity = {'★ ★ ★':'3-Star','★ ★ ★ ★ ★':'5-Star','★ ★ ★ ★':'4-Star','★ ★':'2-Star','★':'1-Star','—':'2-Star'}
        
        # Create the dataframe and store the data in it.
        data = {'Servant Name' : self.names, 'ID' : self.ids, 'Rarity' : self.rarities}
        df = pd.DataFrame(data)
        
        # Remove the non-playable servants from the dataframe 
        df = df.query("ID not in ['151','152','168','240']")

        # Replace the emoji-text in the Rarity column with the corr_rarity dict.
        temp_rarity = df['Rarity'].replace(corr_rarity)
        df.loc[:,'Rarity'] = temp_rarity
        df.reset_index()

        # Create the .csv file
        d_link = os.path.join(os.getcwd(),'Total Servant Database.csv')
        new_len  = len(df)

        
        if (os.path.exists(d_link) == True):
            # File already exists ? Get the length and compare it with the newly retrieved dataframe
            check_df = pd.read_csv(d_link,encoding='utf-8-sig')
            old_len = len(check_df['ID'].unique()) + 3                            #Hyde is a duplicate of Jekyll and Hyde,so Hyde is removed in the existing dataset file
        else :
            # Create the servant database as the file does not exist
            print('Created Servant Database\n')
            return False,df
        
        if new_len == old_len :
            # If the size of the old and new dataframe are same, no need to update it
            print('Servant Database is already updated')
            return True,df
        elif ((new_len > old_len)|(new_len < old_len)) :
            # Delete the old file and make a new one
            print('Created an updated Servant Database')
            os.remove(os.path.join(os.getcwd(),'Total Servant Database.csv'))
            os.remove(os.path.join(os.getcwd(),'Total Servant Database.xlsx'))
            return False,df
        
    
