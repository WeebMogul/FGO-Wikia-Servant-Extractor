import pandas as pd 
import os
import re
import numpy as np
pd.options.mode.chained_assignment = None

keys = ['Class', 'Japanese Name', 'AKA', 'ID', 'Cost','ATK at level 1','ATK at max Servant level','HP at level 1','HP at max Servant level','Grail ATK','Grail HP','Voice Actor','Illustrator','Attribute', 'Growth Curve','Star Absorption', 
'Star Generation','NP Charge ATK','NP Charge DEF','Death Rate', 'Alignments','Gender', 'Traits', 'Card Order', 'Quick Hits', 'Arts Hits', 'Buster Hits', 'Extra Hits', 
'NP Rank', 'NP Classification','NP Damage Type','NP Hit-Count']


def update_dual_values(df):

    edit = df.loc[df['Servant Name'].isin(['Iskandar', 'Henry Jekyll & Hyde'])]
    edit = pd.DataFrame(np.repeat(edit.values, 2, axis=0))
    edit.columns = df.columns

    repr = ['Henry Jekyll & Hyde (Assassin)', 'Henry Jekyll & Hyde (Berserker)', 'Iskandar (Pre Interlude)',
            'Iskandar (Post Interlude)']

    repr_classes = ['Assassin', 'Berserker', 'Rider', 'Rider']

    edit['Servant Name'] = repr
    edit['Class'] = repr_classes

    cv = 0

    # no delete
    for edx, row in edit.iloc[:, 17:22].iterrows():
        for idx, num in enumerate(row):
            #print(type(num))
            #num = str(num)
            if type(num) is float:
                continue
            elif '/' not in num:
                continue
            else:
                num = num.split('/', 1)
                if cv > 1:
                    row[idx] = num[cv - 2]
                else:
                    row[idx] = num[cv]

        cv += 1

    df = df[~df['ID'].isin([81, 108])]
    df = df.append(edit, ignore_index=True)
    df = df.sort_values(by='ID', ascending=True)
    #df = df.drop(['index'],axis=1)
    df['Star Absorption'] = df['Star Absorption'].apply(pd.to_numeric)

    return df


def format_dataframe(stats_df,serv_df):

    stat_path_state = os.path.exists(os.path.join(os.getcwd(),'Total Servant Database.csv'))

    if stat_path_state == True:
        print('No need of formatting. Database is already updated to current time')
    else:
        # Create a copy of the dataframe 
        temp_df = stats_df.copy()

        temp_df['Throwaway_data'] = ' '
        # Get the values in the AKA column which are numeric and insert them to another column
        temp_df = temp_df[temp_df['AKA'].str.isnumeric()]       
        temp_df.insert(loc=3, column='new col1', value=['' for i in range(temp_df.shape[0])])
        temp_df['new col1'] = temp_df['AKA'] 

        # Replace the numneric values in AKA with -
        temp_df['AKA'] = temp_df['AKA'].str.isnumeric()
        temp_df['AKA'] = temp_df['AKA'].replace(True,'-')

        # Replace the original column names with the new column names.
        orig_columns = temp_df.columns[3:]
        new_columns = temp_df.columns[4:]

        # Replace the original column names with the new column names
        mod_columns = dict(zip(orig_columns,new_columns))
        temp_df = temp_df.rename(columns=mod_columns)
        

        # Drop the Throwaway_data columns
        temp_df = temp_df[temp_df.columns[:-1]]
        temp_df = temp_df.drop('Throwaway_data',axis=1)

        # Remove data where the AKA column is numeric
        stats_df = stats_df[stats_df['AKA'].str.isnumeric()!=True]

        # Append the modified dataframe with the original dataframe 
        df2 = stats_df.append(temp_df)    
        
        # Convert text numbers to numeric data and sort values by ID

        df2.update(df2.apply(pd.to_numeric,errors='coerce'))
        df2 = df2.sort_values(by='ID')
        
        
        # Split the ATK and HP data into 2 different columns (Level 1 and max level)
        df2['ATK'] = df2['ATK'].apply(lambda x: re.sub(r'  (.*)','',x))
        atk = df2['ATK'].str.split('/',n=1,expand=True)
        df2['ATK at level 1'] = atk[0]
        df2['ATK at max Servant level'] = atk[1]

        df2['HP'] = df2['HP'].apply(lambda x: re.sub(r'  (.*)','',x))
        hp = df2['HP'].str.split('/',n=1,expand=True)
        df2['HP at level 1'] = hp[0]
        df2['HP at max Servant level'] = hp[1]

        # Replace a string from the Alignments column
        df2['Alignments'] = df2['Alignments'].str.replace('・',' ')

        # DataFrame is arranged based on column order from the keys list
        df2 = df2[keys]

        serv_df.update(serv_df.apply(pd.to_numeric,errors='coerce'))

        # Merge the Servant Database and Stats Database based on ID
        # print(df2['ID'])
        new_df = pd.merge(serv_df,df2,on='ID',how='inner')
        # Drop any duplicates
        new_df = new_df.drop_duplicates(subset='Servant Name')

        # Remove Hyde from the Database (could have done this earlier but eh....) because Jekyll/Hyde already exists
        new_df = new_df[new_df['Servant Name'] != 'Hyde'].reset_index(drop=True)

        # Convert numeric text in dataframe to integer values
        numeric_lists = [
            'ATK at level 1','ATK at max Servant level','HP at level 1','HP at max Servant level',
            'Grail ATK','Grail HP']

        for i in numeric_lists:
            new_df[i] = new_df[i].apply(lambda x: x.split()[0].replace(',',''))
            new_df[i] = new_df[i].apply(pd.to_numeric)
        
        new_df = update_dual_values(new_df)

        new_df = new_df[new_df['Class'] != 'Beast II']
        new_df = new_df[new_df['Servant Name'] != 'Solomon']
        
        # Create the new dataset in .csv,.xlsx and .json
        new_df.to_csv(os.path.join(os.getcwd(),'Total Servant Database.csv'),index=False,encoding='utf-8-sig')
        new_df.to_excel(os.path.join(os.getcwd(),'Total Servant Database.xlsx'),index=False)