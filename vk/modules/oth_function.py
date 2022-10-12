import base64
import os
import sys

import requests

path = sys.path[0] + '/people'


def clear():
    os.system('cls')


# Преобразует фото в base64 о url
def get_as_base64(url):
    return base64.b64encode(requests.get(url).content).decode('utf-8')


# Создает файл photo_pre.html
def create_photo_pre():
    with open(f"{path}/photo_pre.html", "w") as file:
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
