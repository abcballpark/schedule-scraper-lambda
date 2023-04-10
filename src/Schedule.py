import attr
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from Game import Game
import httpx
from icalendar import Calendar, Event
from uuid import uuid4


@attr.s(auto_attribs=True)
class Schedule:
    kid: str
    sport: str
    division: int = 1
    team: str = ""
    games: list = None

    def save(self, filename: str = None):
        self.fetch()
        self.parse_games()
        ics = self.to_ical()
        if filename is None:
            filename = self.kid
        with open(f"{filename}.ics", "wb") as f:
            f.write(ics)

    def fetch(self):
        req = httpx.post(
            url="http://www.abcballpark.com/eventschedule/index.php",
            data={
                "srch_divn": self.division,
                "srch_team": self.team,
            }
        )
        self._text = req.text
        self._soup = BeautifulSoup(self._text, "html.parser")
        return self
    
    def parse_games(self):
        table = self._soup.table
        games = [g for g in table.find_all("tr")][1:-1] # Exclude the <th>s at the end
        self.games = [self._parse_game(g) for g in games]
        return self

    def to_ical(self):
        cal = Calendar()
        for game in self.games:
            title = f"{self.sport} - {self.kid} {game.location}"
            if "ABC" in game.location:
                game.location = "ABC Ballpark, 10500 Livingston Ave, St Ann, MO 63074, USA"
            elif "BMAC" in game.location:
                game.location = "BMAC, 13161 Taussig Rd, Bridgeton, MO 63044, USA"
            startstr = game.time.strftime("%Y%m%dT%H%M%S")
            endstr = (game.time + timedelta(hours=1)).strftime("%Y%m%dT%H%M%S")
            new_game = Event(
                uid=uuid4(),
                dtstamp=startstr,
                dtstart=startstr,
                dtend=endstr,
                location=game.location,
                summary=title,
                description=f"{game.division}: {game.away} @ {game.home}"
            )
            cal.add_component(new_game)
        cal.add('prodid', '-//abcballpark.com//Game Schedule 1.0//EN')
        cal.add('version', '2.0')
        return cal.to_ical()

    def _parse_team(self, game):
        game.find_all("br")[0].replace_with(" ")
        return game.text.replace(u"\xa0", u"")

    def _parse_game(self, game, year=date.today().year):
        cells = [c for c in game.find_all("td")]
        game_date, game_time, game_field, game_division, _, home, _, away, _ = cells
        # Parse date
        game_date_obj = datetime.strptime(f"{game_date.text} {year} {game_time.text}", "%a %b %d %Y %I:%M %p")
        # Parse field string
        game_field.find_all("br")[0].replace_with(" ")
        home = self._parse_team(home)
        away = self._parse_team(away)
        new_game = Game(
            time=game_date_obj,
            division=game_division.text,
            location=game_field.text,
            home=home,
            away=away,
        )
        return new_game
