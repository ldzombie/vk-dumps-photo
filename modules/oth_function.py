import base64
import os
import sys
from enum import Enum

import requests

path = sys.path[0]


def clear():
    os.system('cls')


class Color(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3
    PURPLE = 4
    CYAN = 5
    GRAY = 6


# Цветные сообщения
def c_text(val1: Color, text):
    match val1:
        case Color.RED:
            color = '\033[31m'
        case Color.GREEN:
            color = '\033[32m'
        case Color.BLUE:
            color = '\033[34m'
        case Color.YELLOW:
            color = '\033[33m'
        case Color.PURPLE:
            color = '\033[35m'
        case Color.CYAN:
            color = '\033[36m'
        case Color.GRAY:
            color = '\033[37m'
        case _:
            print(f'{text}')

    ENDC = '\033[0m'
    print(f'{color}{text}{ENDC}')


# Преобразует фото в base64 о url
def get_as_base64(url):
    return base64.b64encode(requests.get(url).content).decode('utf-8')

def get_img_content(url):
    return requests.get(url).content



# Создает файл photo_pre.html
def create_photo_pre():
    with open("photo_pre.html", "w") as file:
        file.write("""<!DOCTYPE HTML>
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                <title>VK DUMP</title>
            </head>
        <body>
            <div class="full"></div>
                <div class="body">VK-Dump</div>
            """)

