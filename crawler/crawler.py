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

    def handle_data(self, data):
        # print("Encountered some data  :", data)
        found_team = False
        for team in teams:
            if team in data:
                found_team = True
        if found_team and len(data) < 100:
            found_team = False
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

def main():
    parser = MyHTMLParser()

    response = urllib.request.urlopen("http://www.nfl.com/player/tombrady/2504211/gamelogs?season=2001")
    page_source = response.read()
    #print(page_source)
    lol = page_source.decode("utf-8") 
    parser.feed(lol)
    print(opponents_out)
    print(opponents_home)
    print(type(lol))


if __name__ == "__main__":
    main()