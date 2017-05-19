from html.parser import HTMLParser
import urllib.request
import re

opponents_home = []
opponents_out = []

# TODO: LÆS OP PÅ REGEX
# TODO ADD ALL TEAMS
teams = ['CIN', 'NYJ', 'IND', 'SEA', 'MIA', 'SD', 'DEN', 'ATL', 'BUF']

class MyHTMLParser(HTMLParser):
    game_logs = False
    regular_season = True
    def handle_starttag(self, tag, attrs):
        #print("Encountered a start tag:", tag)
        tag_text = self.get_starttag_text()
        if "Game Logs For" in tag_text:
            print(self.get_starttag_text())
            game_logs = True
            # Her kan jeg få navnet på spilleren og sæsonen

    #def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)

    found_team = False
    get_score = False
    def handle_data(self, data):
        # print("Encountered some data  :", data)
        #print(data)
        set_trace = False
        
        result = re.match("^([0-9]+-[0-9]+)+$", data)
        if self.get_score and len(data.strip()) > 1:
            print("get score")
            if '-' in data:
                print("- in data")
                print(data.strip())
                exit()
            self.get_score = False

            print(data) 

        if self.found_team and len(data) < 100:
            self.found_team = False
            self.get_score = True

            print("new data")
            print(data)
            data = re.sub('\s+',' ', data)
            if "@" in data:
                opponents_out.append(data)
                print(data)
            else:
                opponents_home.append(data)
                print(data)
            #exit() 
            #set_trace = True
        if set_trace:
            import pdb; pdb.set_trace()

        if "Regular Season" in data:
            self.regular_season = True
            print(data)

        elif "Postseason" in data:
            self.regular_season = False
            print(data)

        elif "Pro Bowl" in data:
            self.regular_season = False
            print(data)
        if data == 'Tom Brady':
            print(data)

        if self.regular_season:
            i = 1
def parse_html(html):
    found_season = False
    new_week = True
    found_team = False
    current_team = ''
    dict_matches = {}
    current_week = 0
    for h in html:
        if '<tbody>' in h:
            found_season = True

        if found_season:
            if '<td>' in h:
                if new_week:
                    new_week = False
                    current_week = re.findall(r'\d+', h)
            if found_team:
                if '@' in h or current_team in h:
                    current_team, away = get_team(h)
                    print(current_team)
                    found_team = False
                    exit()


            for team in teams:
                if '/teams/profile?team=' + team in h:
                    found_team = True
                    current_team = team

def get_team(string):
    for team in teams:
        if '@' in string:
            return '@' + team, True
        if team in string:
            return team, False

def main():
    parser = MyHTMLParser()
    # http://www.pro-football-reference.com/players/B/BradTo00/gamelog/2006/
    # THIS RIGHT HERE!!!
    response = urllib.request.urlopen("http://www.nfl.com/player/tombrady/2504211/gamelogs?season=2001")
    page_source = str(response.read())
    split = page_source.split()
    parse_html(split)
    exit()
    lol = page_source.decode("utf-8") 
    parser.feed(lol)
    print(opponents_out)
    print(opponents_home)
    print(type(lol))


if __name__ == "__main__":
    main()