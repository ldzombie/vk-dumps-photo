# vk-dumps-photo

[![Python: 3.7](https://img.shields.io/badge/python-3.10.4-green "python 3.7")](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/vk_api.svg "Vk_api")]([https://www.python.org/](https://pypi.org/project/vk-api/))

## Установка

```pip install -r requirements.txt  ```

## Использование

### 1 способ

```python main.py```   

#### Авторизация
![Img 1](https://github.com/ldzombie/vk-dumps-photo/blob/main/img/img_1.jpg?raw=true)

#### Главное меню
![Img 2](https://github.com/ldzombie/vk-dumps-photo/blob/main/img/img_2.jpg?raw=true)

#### Настройки
![Img 3](https://github.com/ldzombie/vk-dumps-photo/blob/main/img/img_3.jpg?raw=true)

### 2 способ
```$ main.py -h
usage: main.py [-h] [-t [TOKEN]] [-l [LOGIN]] [-p [PASSWORD]] [-sp [SETPATH]] [-sd [{txt,offline,online}]]
               [-slp [SETLIMITPHOTO]] [-sld [SETLIMITDIALOG]] [-su] [-ru] [-m METHOD [METHOD ...]] [-u [USER]] [-os]

--------------------------------------------------------------------------
https://github.com/ldzombie/vk-dumps-photo/

options:
  -h, --help            show this help message and exit
  
  -t, --token           Токен
  
  -l , --login          Логин 
  
  -p , --password       Пароль писать в ""
  
  -sp, --setpath        Название папки для сохранения
  
  -sd, --setdumpmethod  Метод сохранения данных {txt,offline,online} Метод сохранения данных, offline-фотографии доступны без интернета(самый долгий метод "Я предупредил")
  
  -slp, --setlimitphoto Лимит фотографий
  
  -sld,--setlimitdialog Лимит диалогов
  
  -si, --setinterval 	Добавляет интервалы между запросами, default=True
  
  -siv, --setinvalue 	Время интервала выбирается рандомно из диапозона чисел default=[1, 10]
  
  -shw, --sethw 	Устанавливает размеры фото default=[500, 650] (height and width)
  
  -srod, --setrod 	Как часто файл фотографий альбома будет делиться на части default=2(каждые 2000 фотографий)
  
  -su, --saveuser       Сохранить пользователя  
  
  -ru, --removeuser     Удалить пользователя 
  
  -m, --method          1-фотографии из всех диалогов 2-фотографии из опр. диалога 3-фото из плейлистов 4-плейлисты
                        опр. пользователя 5-сохры всех друзей у которых открыты  
                        
  -u , --user           id пользователя для методов 2,4
  
  -os , --onlysaved     (default:True) в методах 3-5, берется только альбом с сохрами
  ```
Пример   
```python main.py -t token -sp dump -slp 500 -sld 50 -shw 650 1280 -su -m 1 4 -u 123456786 ```
