from datetime import datetime, timezone, timedelta
from timezonefinder import TimezoneFinder
import pytz
import pygame
from stateful.config import Config
from modules.scanline import Scanline
from modules.globemap import Globemap
from modules.ui import Circular, Text

class PolarisClock:
    def __init__(self):
        db = Config(db_name="config.db")
        if db.check():
            tz = "UTC"
            self.lon = 0
            self.lat = 0
        else:
            db.get()
            tz = db.tz
            self.lon = float(db.lon)
            self.lat = float(db.lat)

        global lon_center, lat_center, center_x, center_y, radius, geojson_data, country_border_data, width, height
        pygame.init()
        width = 800
        height = 800
        center_x = width // 2
        center_y = height // 2
        self.tz = pytz.timezone(str(tz))
        self.radius = 400
        self.lst_angle = self.get_lst_angle(self.lon)
        self.screen = pygame.display.set_mode((width, height), pygame.SCALED | pygame.FULLSCREEN )
        self.clock = pygame.time.Clock()
        self.running = False
        self.font = pygame.font.Font(None, 62)
        self.color = pygame.Color('blue')
        self.color2 = pygame.Color('blue')
        self.color3 = pygame.Color('blue')
        self.color4 = pygame.Color('white')
        self.center = self.screen.get_rect().center

        #Class init
        self.scanline_manager = Scanline(self.screen, width, height, speed=10)
        self.globemap = Globemap()
        self.circular = Circular( self.screen, self.center, self.radius, self.color, self.color2, self.color4, self.font )
        self.text = Text(self.screen, self.font, self.color4)

    def get_cr(self):
        return datetime.now(self.tz).strftime('%H:%M')

    def check_dst(self):
        aware_dt = self.tz.localize(datetime.now(), is_dst=None)
        dst_offset = aware_dt.tzinfo.dst(aware_dt)
        return dst_offset != timedelta(0)

    def circular_time_adj(self):
        days_diff = (datetime.now() - datetime(datetime.now().year, 3, 6)).days
        minutes_per_day = days_diff * 3.56
        sidereal_time_angle = minutes_per_day * 0.25
        # Add daylight saving time if required
        if self.check_dst() is True:
            sidereal_time_angle -= 15

        return sidereal_time_angle

    def convert_angle_to_time(self, lst_angle):
        hours = lst_angle / 15
        h = int(hours)
        minutes = (hours - h) * 60
        m = int(minutes)
        seconds = (minutes - m) * 60
        s = round(seconds, 2)
        return f"{h}:{m}"

    def get_dubhe_lha_angle(self, lst_angle):
        dubhe_ra = 165.932 #165.932° is the accurate J2000 Right Ascension (RA) for Dubhe
        dubhe_lha_angle = (lst_angle - dubhe_ra) # Compute Local Hour Angle for Dubhe (LHA)
        return dubhe_lha_angle

    def get_lst_angle(self, long):
        utc_time = datetime.now(timezone.utc).strftime("%m%d%y %H%M")
        self.long = long

        # # Parse values
        MM = int(utc_time[0:2])
        DD = int(utc_time[2:4])
        YY = int(utc_time[4:6]) + 2000
        hh = int(utc_time[7:9])
        mm = int(utc_time[9:11])
        mm = mm / 60
        UT = hh + mm

        # Julian date
        JD = (367 * YY) - int((7 * (YY + int((MM + 9) / 12))) / 4) + int((275 * MM) / 9) + DD + 1721013.5 + (UT / 24)

        # Greenwhich mean sidereal time
        GMST = 18.697374558 + 24.06570982441908 * (JD - 2451545)
        GMST = GMST % 24

        # Convert to the local sidereal time
        self.long = self.long / 15
        LST = GMST + self.long
        if LST < 0:
            LST = LST + 24
        LSTmm = (LST - int(LST)) * 60
        LSThh = int(LST)
        LSTmm = int(LSTmm)

        lst_angle = (LSThh * 15) + (LSTmm / 4)

        return lst_angle

    def screen_main(self):
        angle=float('30')
        self.screen.fill((0, 0, 0))
        self.globemap.draw_geojson_coastlines(self.lon, self.lat, self.color3)
        self.globemap.draw_geojson_country_borders(self.lon, self.lat, self.color3)
        self.text.draw((300, 450), f"{self.tz.zone}")
        self.text.draw((350, 500), self.get_cr())
        self.scanline_manager.update()
        self.scanline_manager.draw()
        self.circular.draw_border()
        self.circular.draw_hour_ticks(self.circular_time_adj())
        self.circular.draw_clock_hand(self.get_dubhe_lha_angle(self.get_lst_angle(self.lon)))
        pygame.display.flip()

    def get_size(self):
        return width, height

    def get_rect(self):
        return pygame.Rect(0, 0, width, height)

    def loop(self):
        self.running = True
        lon_center = self.lon
        lat_center = self.lat
        prev_mouse_pos = None
        left_button = False
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        left_button = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        tf = TimezoneFinder()
                        tz = tf.timezone_at(lat=lat_center, lng=lon_center)
                        db = Config(db_name='config.db')
                        db.save(tz, lon_center, lat_center)
                        self.__init__()
                        self.running = False
                        self.loop()
                        left_button = False
                if event.type == pygame.MOUSEMOTION:
                    if left_button:
                        current_mouse_pos = event.pos
                        if prev_mouse_pos is None:
                            prev_mouse_pos = current_mouse_pos
                        else:

                            dx = prev_mouse_pos[0] - current_mouse_pos[0]
                            dy = prev_mouse_pos[1] - current_mouse_pos[1]

                            if -180 <= lon_center <= 180:
                                lon_center += 0.5 if dx > 0 else -0.5 if dx < 0 else 0
                            lon_center = max(-180, min(lon_center, 180))
                            if 5 <= lat_center <= 75:
                                lat_center += 0.5 if dy < 0 else -0.5 if dy > 0 else 0
                            lat_center = max(5, min(lat_center, 75))

                        prev_mouse_pos = current_mouse_pos
            self.lon = lon_center
            self.lat = lat_center
            self.screen_main()

if __name__ == '__main__':
    screen = PolarisClock()
    screen.loop()
