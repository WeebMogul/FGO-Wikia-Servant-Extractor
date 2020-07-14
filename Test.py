import pandas as pd
import numpy as np


df = pd.read_csv('Total Servant Database.csv',index_col=0)

edit = df.loc[df['Servant Name'].isin(['Iskandar', 'Henry Jekyll & Hyde'])]
edit = pd.DataFrame(np.repeat(edit.values, 2, axis=0))
edit.columns = df.columns

repr = ['Henry Jekyll & Hyde (Assassin)', 'Henry Jekyll & Hyde (Berserker)', 'Iskandar (Pre Interlude)',
        'Iskandar (Post Interlude)']

repr_classes = ['Assassin', 'Berserker', 'Rider', 'Rider']

edit['Servant Name'] = repr
edit['Class '] = repr_classes

cv = 0

# no delete
for edx, row in edit.iloc[:, 17:22].iterrows():
    # print(edit.iloc[edx])
    for idx, num in enumerate(row):
        if '/' not in num:
            continue
        else :
            num = num.split('/', 1)
            if cv > 1:
                row[idx] = num[cv-2]
            else:
                row[idx] = num[cv]

    cv += 1

df = df[~df['ID'].isin([81, 108])]
df = df.append(edit,ignore_index=True)
df = df.sort_values(by='ID',ascending=True)