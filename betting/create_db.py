import sqlite3
conn = sqlite3.connect('e0.db')
c = conn.cursor()

def create_team():
    c.execute('''DROP TABLE IF EXISTS team''')

    c.execute('''CREATE TABLE team(
                    name text)''')

    conn.commit()

    #conn.close()

def create_division():
    c.execute('''DROP TABLE IF EXISTS division''')
    c.execute('''CREATE TABLE division(
                    name text)''')
    c.execute('''INSERT INTO division VALUES ('E0')''')
    c.execute('''SELECT * FROM division''')
    print(c.fetchone())
    conn.commit()

def create_match():
    c.execute('''DROP TABLE IF EXISTS match''')
    c.execute('''CREATE TABLE match(
                    match_id integer PRIMARY KEY,
                    div integer,
                    match_date text,
                    home_team integer,
                    away_team integer,
                    fthg integer,
                    ftag integer,
                    ftr text,
                    hthg integer,
                    htag integer,
                    htr text,
                    attendance integer,
                    hs integer, 
                    as_ integer, 
                    hst integer, 
                    ast integer, 
                    hhw integer, 
                    hf integer, 
                    af integer, 
                    hc integer, 
                    ac integer, 
                    ho integer, 
                    ao integer, 
                    hy integer, 
                    ay integer, 
                    hr integer, 
                    ar integer,
                    temperature integer,
                    weather integer,
                    FOREIGN KEY(div) REFERENCES division (rowid),
                    FOREIGN KEY(home_team) REFERENCES team(rowid),
                    FOREIGN KEY(away_team) REFERENCES team(rowid))''')
    conn.commit()

def test():
    create_team()
    create_match()
    create_division()
    conn.commit()
    

def main():
    test()

    conn.close()

if __name__ == "__main__":
    main()