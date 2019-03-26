__author__ = 'Kfir'

import log

with log.DatabaseConnection('levels') as table:
    df = table.read()

data = df.loc[[2]].to_dict(orient='records')
print(data)
print(df)