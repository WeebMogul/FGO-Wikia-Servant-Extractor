import pandas as pd 
import string 

df = pd.read_excel('Total Servant Database.xlsx')

# Convert numeric text in dataframe to integer values
numeric_lists = [
            'ATK at level 1','ATK at max Servant level','HP at level 1','HP at max Servant level',
            'Grail ATK','Grail HP',
            'NP Charge ATK','NP Charge DEF','Death Rate']

for i in numeric_lists:
    df[i] = df[i].apply(lambda x: x.split()[0].replace(',',''))
    df[i] = df[i].apply(pd.to_numeric)