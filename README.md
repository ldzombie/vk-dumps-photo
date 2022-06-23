# vk-dumps-photo

[![Python: 3.7](https://img.shields.io/badge/python-3.7-green "python 3.7")](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/vk_api.svg "Vk_api")]([https://www.python.org/](https://pypi.org/project/vk-api/))

## Установка

```pip install -r requirements.txt  ```

## Использование

### 1 способ

```python main.py```

#### Авторизация
[Img 1](https://github.com/ldzombie/vk-dumps-photo/img/img 1.jpg)

#### Главное меню
[Img 2](https://github.com/ldzombie/vk-dumps-photo/img/img 2.jpg)

#### Настройки
[Img 3](https://github.com/ldzombie/vk-dumps-photo/img/img 3.jpg)

### 2 способ
```$ main.py -h
usage: main.py [-h] [-t [TOKEN]] [-l [LOGIN]] [-p [PASSWORD]] [-sp [SETPATH]] [-sd [{txt,offline,online}]]
               [-slp [SETLIMITPHOTO]] [-sld [SETLIMITDIALOG]] [-st] [-m METHOD [METHOD ...]] [-u [USER]]

--------------------------------------------------------------------------
https://github.com/ldzombie/vk-dumps-photo/

options:
  -h, --help            show this help message and exit
  
  -t, --token           Токен
  
  -l , --login          Логин 
  
  -p , --password       Пароль писать в ""
  
  -sp, --setpath        Название папки для сохранения
  
  -sd, --setdumpmethod  Метод сохранения данных {txt,offline,online}
  
  -slp, --setlimitphoto Лимит фотографий
  
  -sld,--setlimitdialog Лимит диалогов
  
  -st, --savetoken      Сохранить токен  
  
  -m, --method          1-фотографии из всех диалогов 2-фотографии из опр. диалога 3-фото из плейлистов 4-плейлисты
                        опр. пользователя 5-сохры всех друзей у которых открыты  
                        
  -u , --user           id пользователя для методов 2,4
  ```
