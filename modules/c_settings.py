import json
import time
from random import randint


# Класс всех настроек
class Settings:
    def_config = {
        "setting": {
            "path": "dump",
            "dump_txt": False,
            "dump_html": True,
            "dump_html_offline": False,
            "a_interval": True,
            "album_only_saved": True,
            "interval_values": [1, 10],
            "s_height_width": [500, 650],
            "s_rod": 2,
            "limit_photo": 200,
            "limit_dialog": 20

        }}

    def __init__(self):
        self.show_off = False

        self.dump_path = "dump"
        self.dump_html_offline = None
        self.dump_html = None
        self.dump_txt = None
        self.limit_dialog = None
        self.limit_photo = None
        self.album_only_saved = None

        self.s_rod = None
        self.s_height_width = None

        self.a_interval = None
        self.interval_values = None

        try:
            with open('config.json', 'r') as config_file:
                self.def_config = json.load(config_file)
            self.get_dump_config()
        # auth_menu()
        except Exception as e:
            if "No such file or directory" in str(e):
                self.dump_config()

    def dump_config(self):
        if self.def_config is not None:
            with open('config.json', 'w+') as config_file:
                json.dump(self.def_config, config_file)

    def get_dump_config(self):
        self.dump_path = str(self.def_config['setting']['path'])

        self.limit_photo = int(self.def_config['setting']['limit_photo'])
        self.limit_dialog = int(self.def_config['setting']['limit_dialog'])
        self.dump_txt = bool(self.def_config['setting']['dump_txt'])
        self.dump_html = bool(self.def_config['setting']['dump_html'])
        self.dump_html_offline = bool(self.def_config['setting']['dump_html_offline'])
        self.album_only_saved = bool(self.def_config['setting']["album_only_saved"])

        self.a_interval = bool(self.def_config['setting']['a_interval'])
        self.interval_values = list(self.def_config['setting']['interval_values'])

        self.s_height_width = list(self.def_config['setting']['s_height_width'])
        self.s_rod = int(self.def_config['setting']['s_rod'])

    def update_settings(self):
        try:
            self.dump_config()
            self.get_dump_config()
        except Exception:
            self.check_err()
            self.dump_config()
            self.get_dump_config()

    def check_err(self):
        if not self.dump_txt and not self.dump_html and not self.dump_html_offline:  # and not download
            self.def_config['setting']['dump_html'] = True
        if not self.dump_path:
            self.def_config['setting']['path'] = "dump"

        if self.interval_values[0] < 0 or self.interval_values[1] > 100:
            self.def_config['setting']['interval_value'] = [1, 10]

        if self.s_rod <= 1 or self.s_rod > 5:
            self.def_config['setting']['s_rod'] = 2

        if self.s_height_width[0] < 0 or self.s_height_width[1] > 3000:
            self.def_config['setting']['s_height_width'] = [500, 650]

        self.update_settings()


    def set_dump(self, key: str, b: bool):
        self.def_config['setting'][key] = b
        self.update_settings()

    def set_limit_photo(self, b: int):
        self.def_config['setting']['limit_photo'] = b
        self.update_settings()

    def set_limit_dialog(self, b: int):
        self.def_config['setting']['limit_dialog'] = b
        self.update_settings()

    def set_dump_path(self, b: str):
        self.def_config['setting']['path'] = b
        self.update_settings()

    def set_interval_values(self, b: list):
        self.def_config['setting']['interval_values'] = b if b[0] > 0 and b[1] < 100 else [1, 10]
        self.update_settings()

    def set_height_width(self, val1: int, val2: int):
        self.def_config['setting']['s_height_width'] = [val1, val2] if val1 > 1 and val2 < 3000 else [500, 650]
        self.update_settings()

    def set_rod(self, val1: int):
        self.def_config['setting']['s_rod'] = val1 if val1 > 1 else 2
        self.update_settings()

    def set_change_show(self, val: bool):
        self.show_off = val

    def set_album_only_saved(self, val: bool):
        self.album_only_saved = val

    def intervals(self):
        if self.a_interval:
            time.sleep(randint(self.interval_values[0], self.interval_values[1]))

    def check_sizes(self, val1: int) -> bool:
        return bool(self.s_height_width[0] < val1 < self.s_height_width[1])
