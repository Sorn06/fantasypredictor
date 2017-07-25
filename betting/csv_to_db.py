import sqlite3
import collections

conn = sqlite3.connect('e0.db')
c = conn.cursor()

def get_db_column_name(requested_coloumn):
    columns = {'Div': 'div',
               'Date': 'match_date',
               'HomeTeam': 'home_team',
               'AwayTeam': 'away_team',
               'FTHG': 'fthg',
               'FTAG': 'ftag',
               'FTR': 'ftr',
               'HTHG': 'hthg',
               'HTAG': 'htag',
               'HTR': 'htr',
               'HS': 'hs',
               'AS': 'as_',
               'HST': 'hst',
               'AST': 'ast',
               'HF': 'hf',
               'AF': 'af',
               'HC': 'hc',
               'AC': 'ac',
               'HY': 'hy',
               'AY': 'ay',
               'HR': 'hr',
               'AR': 'ar' 
               }

    return columns.get(requested_coloumn)

def create_team_name(team_name):
    c.execute("SELECT rowid FROM team WHERE name = ?", (team_name,))
    data = c.fetchall()
    if len(data) == 0:
        print(team_name + " does not exist, adding it")
        c.execute("INSERT INTO team (name) VALUES (?)", (team_name,))
        conn.commit()

    else:
        print(team_name + " does exist, skipping")

def load_file(files):
    primary_id = 0
    for file in files:
        with open (file, "r") as myfile:
            matches = myfile.readlines()
            save_tags = True
            tags = []
            row = collections.OrderedDict()
            for match in matches:
                content = match.split(',')
                if save_tags:
                    tags = content
                    save_tags = False
                else:
                    count = 0
                    for t, v in zip(tags, content):
                        row[t] = v

                    # Get div
                    c.execute('''SELECT rowid
                                    FROM division
                                    WHERE name LIKE ''' 
                                        + "'" 
                                        + row['Div']
                                        + "'")
                    div = c.fetchone()

                    ht = row['HomeTeam']
                    at = row['AwayTeam']

                    create_team_name(ht)
                    create_team_name(at)

                    # Get home team
                    c.execute('''SELECT rowid
                                    FROM team
                                    WHERE name LIKE ?''', (ht,))
                    HomeTeam = c.fetchone()
                    print("HomeTeam")
                    print(HomeTeam)

                    # Get away team
                    c.execute('''SELECT rowid
                                    FROM team
                                    WHERE name LIKE '''
                                    + "'"
                                    + at
                                    + "'")
                    AwayTeam = c.fetchone()

                    c.execute('''INSERT INTO match (match_id, home_team, away_team)
                                    VALUES (?, ?, ?)''', (primary_id, HomeTeam[0], AwayTeam[0]))

                    c.execute('''UPDATE match 
                                 SET div = ?
                                 WHERE rowid = ?''', (div[0], primary_id))

                    for k, v in row.items():
                        column = get_db_column_name(k)
                        print(column, k, v)
                        if column and (column != 'away_team' and column != 'home_team' and column != 'div'):
                            print("LOLLOLOLOL")
                            print(column, v)
                            c.execute('''UPDATE match
                                        SET ''' + column + ''' = ?
                                        WHERE rowid = ?''', (v, primary_id))
                    conn.commit()
                    c.execute('''SELECT * FROM match''')
                    
                    primary_id += 1

def main():
    files = ['E0.csv']
    load_file(files)

    conn.close()

if __name__ == "__main__":
    main()