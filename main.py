import vk_api
import os
import json
import shutil
from datetime import datetime
from itertools import repeat
from multiprocessing import Pool
from os import cpu_count, makedirs
from os.path import join, exists

from error_log import ErrorLog

path, filename = os.path.split(os.path.abspath(__file__))
clear = lambda: os.system('cls')

error_log = ErrorLog()

def_config ={
	"dump_config": {
	  "path": "dump",
	  "download": True,
	  "download_errors": "download_errors.json",
	  "limit_photo": 1000,
	  "limit_dialog": 50
	}}

login_data={
	"token": 0,
	"login": 0,
	"password":0}



class LoginVK:
	API_VERSION = '5.92'
	def __init__(self, login_data):
		self.login_data = login_data
		self.vk = None
		self.account = None
		self.login_vks()

	def login_vks(self):
		try:
			if 'token' in self.login_data and self.login_data['token']:
				token = self.login_data['token']
				vk_session = vk_api.VkApi(token=token, auth_handler=self.auth_handler)
			elif 'login' in self.login_data and 'password' in self.login_data:
				login, password = self.login_data['login'], self.login_data['password']
				vk_session = vk_api.VkApi(login, password, captcha_handler=self.captcha_handler,
										  api_version=LoginVK.API_VERSION, auth_handler=self.auth_handler)
				vk_session.auth(token_only=True, reauth=True)
				
			else:
				raise KeyError('Введите токен или пару логин-пароль')

			self.vk = vk_session.get_api()
			self.account = self.vk.account.getProfileInfo()
			

		except Exception as e:
			raise ConnectionError(e)

	@staticmethod
	def auth_handler():
		key = input('Введите код двухфакторой аутентификации: ')
		remember_device = True
		return key, remember_device

	@staticmethod
	def captcha_handler(captcha):
		key = input(f"Введите капчу ({captcha.get_url()}): ").strip()
		return captcha.try_again(key)

def get_dump_config():
	global limit_photo
	global limit_dialog
	global dump_path
	global download
	global path_user

	limit_photo = def_config['dump_config']['limit_photo']
	limit_dialog = def_config['dump_config']['limit_dialog']
	dump_path = def_config['dump_config']['path']
	download = def_config['dump_config']['download']
	path_user= f'{path}/{dump_path}/{own_id} - {name}'

def get_stand():
	try:
		global name
		global own_id
		global photo

		name= f'{login_vk.account["first_name"]} {login_vk.account["last_name"]}'
		own_id = login_vk.account["id"]
		photo = open(f'{path}/photo_pre.html', 'r', encoding="utf8")

		get_dump_config()

		makedirs(path_user, exist_ok=True)

	except Exception as e: # Исключения ошибок
		error_log.add('get_stand', e)

#Фотографии из диалогов
def get_dialogs_photo(p_id):
	try:
		if download ==True:
			file = photo.read()
			photo.close()
		urls=[]
		albums=[]
		if(p_id > 0):
			test = login_vk.vk.messages.getConversationsById(peer_ids=p_id)
		else:
			if limit_dialog==0 or limit_dialog > 200:
				test = login_vk.vk.messages.getConversations(count=200) # Получаем диалоги через токен
				all_dialogs = test["items"]

				if len(all_dialogs) == 200:
					#Нужно чтобы получить все фотографии из диалога, если их больше 200
					offset=200 # сдвиг начала отсчёта
					while True: 
						fo1 = test = login_vk.vk.messages.getConversations(count=200,offset=offset)
						length = len(fo1["items"])

						if length > 0:
							all_dialogs += fo1["items"]
						else:
							break
						if length == 200:
							offset +=200
						else:
							break
			else:
				all_dialogs = login_vk.vk.messages.getConversations(count=limit_dialog)["items"]

		num = len(all_dialogs) # Количество диалогов
		print(f"Всего найдено диалогов: {num}")
		print(f"Начинаю выгрузку фотографий | {name} - vk.com/id{own_id}")

		makedirs(f'{path_user}/dialog', exist_ok=True)

		for i in all_dialogs: # Идем по списку
			if(p_id > 0):
				idd = i["peer"]["id"]
				peer_type = i['peer']['type'] # Информация о диалоге
			else:
				idd = i["conversation"]["peer"]["id"] # Вытаскиваем ID человека с  диалога
				peer_type = i['conversation']['peer']['type'] # Информация о диалоге (конференция это или человек)
			
			if peer_type == "user": # Ставим проверку конференции
				if idd > 0: # Ставим проверку на группы
					print(f"Выгрузка фотографий - {idd}")
					testtt = login_vk.vk.users.get(user_ids=idd, fields="sex") # Получаем информацию о человеке
					for b in testtt:
						pol = b["sex"]
						fio = f'{b["first_name"]} {b["last_name"]}'

						fo = login_vk.vk.messages.getHistoryAttachments(peer_id=idd, media_type='photo', start_from=0,
																count=200,
																preserve_order=1, max_forwards_level=45)
						a_photo = fo["items"]

						if len(a_photo) == 200 and limit_photo > 200 or len(a_photo) == 200 and limit_photo == 0:
							#Нужно чтобы получить все фотографии из диалога, если их больше 200
							offset=fo["next_from"] # сдвиг начала отсчёта
							while True: 
								fo1 = login_vk.vk.messages.getHistoryAttachments(peer_id=idd, media_type='photo', start_from={offset},
																	count=200,
																	preserve_order=1, max_forwards_level=45)
								length = len(fo1["items"])
								if length > 0:
									a_photo += fo1["items"]
								else:
									break
								length_all= len(a_photo)
								if length == 200 and length_all < limit_photo or length==200 and limit_photo==0: #Проверка на то нужно ли делать ещё один цикл, и не превышает ли фисло фотографий лимит
									offset = fo1["next_from"]
								else:
									break
						elif len(a_photo)==0:
							break

						

						
						for i in a_photo: # Идем по списку вложений
							for j in i["attachment"]["photo"]["sizes"]:
								if j["height"] > 500 and j["height"] < 650: # Проверка размеров
									url = j["url"] # Получаем ссылку на изображение
									urls.append(url)
									if download == True:
										file += f'<img class="photos" src="{url}" alt="Не удалось загрузить (:" title="Найдено в диалоге - vk.com/id{idd}">' # Сохраняем в переменную

						if download == True:
							if pol != 1 and pol != 2:
								save_photo = open(f'{path_user}/dialog/Не определено - id{own_id}.html', 'w+', encoding="utf8")
							else:         
								save_photo = open(f'{path_user}/dialog/id{idd} {fio}.html', 'w+', encoding="utf8") # Открываем файл
							save_photo.write(file) # Сохраняем диалог
							save_photo.close() # Закрываем
							file = open(f'{path}/photo_pre.html', 'r', encoding="utf8").read()

						albums.append({'name': '_'.join(fio),'photos': urls})
						print(f"Выгруженно {len(a_photo)} фотографий")
				else:
					print("Это группа!")
			else:
				print("Это конфа!")

		with open(join(f'{path_user}/dialog/', 'albums.json'), 'w') as alb_file:
			json.dump(albums, alb_file)

		print("Выгрузка фотографий из диалогов завершена")
		print(" ")
		print("[99] Назад")
		print(" ")
		inp = int(input("Ввод: "))
		match inp:
			case 99:
				main_menu()
			case _:
				print("Такого варианта нет")
				main_menu()

	except Exception as e: # Исключения ошибок
		error_log.add('get_dialogs_photo', e)
		main_menu()

#Фотографии из плейлистов
def get_photos_profile():
	try:
		path_albums= f'{path_user}/albums'
		json_albums = []
		urls=[]
		if download == True:
				file = open(f'{path}/photo_pre.html', 'r', encoding="utf8").read()
		albums = login_vk.vk.photos.getAlbums(need_system=1)
		num = albums["count"]# Количество альбомов
		print(f"Всего найдено альбомов: {num}")
		print(f"Начинаю выгрузку фотографий")

		makedirs(f'{path_user}/albums', exist_ok=True)

		for i in albums["items"]:
			idd = i["id"]
			title = i["title"]
			count = i["size"]
			if count ==0:
				continue
			print(f"{title} - Фото: {count}")
			
			a_photos = login_vk.vk.photos.get(album_id=idd, photo_sizes=1, rev=1, count=1000, offset=0)["items"]
			if count > 1000 and a_photos < limit_photo or count > 1000 and limit_photo==0:
				offset=1000 # сдвиг начала отсчёта
				while True: #получаем все фотографии если их больше 1000
					a_photos +=login_vk.vk.photos.get(album_id=idd, photo_sizes=1, rev=1, count=1000, offset=offset)["items"]

					if len(a_photos) >= limit_photo or count == len(a_photos):
						break
					else:
						offset += 1000

			for i in a_photos: # Идем по списку вложений
				for j in i["sizes"]:
					if j["height"] > 500 and j["height"] < 650: # Проверка размеров
						url = j["url"] # Получаем ссылку на изображение
						urls.append(url)
						if download == True:
							
							file += f'<img class="photos" src="{url}" alt="Не удалось загрузить (:" title="Найдено в альбоме - {idd}">' # Сохраняем в переменную
						break #чтобы не добавляло одинаковых фото

			json_albums.append({'name': "_".join(title.split(' ')),'photos': urls})

			print(f"Выгруженно {len(a_photos)} фотографий")
			if download == True:
				save_photo = open(f'{path_albums}/{title}.html', 'w+', encoding="utf8") # Открываем файл
				save_photo.write(file) # Сохраняем диалог
				save_photo.close() # Закрываем
				file = open(f'{path}/photo_pre.html', 'r', encoding="utf8").read()
			
		with open(join(f'{path_albums}/', 'albums.json'), 'w') as alb_file:
			json.dump(json_albums, alb_file)
		print("Выгрузка фотографий из альбомов завершена")
		print(" ")
		print("[99] Назад")
		print(" ")
		inp = int(input("Ввод: "))
		match inp:
			case 99:
				main_menu()
			case _:
				print("Такого варианта нет")
				main_menu()
	except Exception as e: # Исключения ошибок
		error_log.add('get_photos_profile', e)
		main_menu()
		
#Фотографии из плейлистов пользователя
def get_photos_friend(owner_id):
	try:
		user = login_vk.vk.users.get(user_ids=owner_id)
		fio = f'{user["first_name"]} {user["last_name"]}'
		json_albums = []
		urls=[]
		if download == True:
				file = open(f'{path}/photo_pre.html', 'r', encoding="utf8").read()
		albums = login_vk.vk.photos.getAlbums(need_system=1)
		num = albums["count"]# Количество альбомов
		print(f"Всего найдено альбомов: {num}")
		print(f"Начинаю выгрузку фотографий")

		path_user_friend=f'{path}/dump/{owner_id} - {fio}'
		path_albums= f'{path_user_friend}/albums'

		makedirs(f'{path_user_friend}/albums', exist_ok=True)

		for i in albums["items"]:
			idd = i["id"]
			title = i["title"]
			count = i["size"]
			if count ==0:
				continue
			print(f"{title} - Фото: {count}")
			
			a_photos = login_vk.vk.photos.get(album_id=idd, photo_sizes=1, rev=1, count=1000, offset=0)["items"]
			if count > 1000 and a_photos < limit_photo or count > 1000 and limit_photo==0:
				offset=1000 # сдвиг начала отсчёта
				while True: #получаем все фотографии если их больше 1000
					a_photos +=login_vk.vk.photos.get(album_id=idd, photo_sizes=1, rev=1, count=1000, offset=offset)["items"]

					if len(a_photos) >= limit_photo or count == len(a_photos):
						break
					else:
						offset += 1000

			for i in a_photos: # Идем по списку вложений
				for j in i["sizes"]:
					if j["height"] > 500 and j["height"] < 650: # Проверка размеров
						url = j["url"] # Получаем ссылку на изображение
						urls.append(url)
						if download == True:
							
							file += f'<img class="photos" src="{url}" alt="Не удалось загрузить (:" title="Найдено в альбоме - {idd}">' # Сохраняем в переменную
						break #чтобы не добавляло одинаковых фото

			json_albums.append({'name': "_".join(title.split(' ')),'photos': urls})

			print(f"Выгруженно {len(a_photos)} фотографий")
			if download == True:
				save_photo = open(f'{path_albums}/{title}.html', 'w+', encoding="utf8") # Открываем файл
				save_photo.write(file) # Сохраняем диалог
				save_photo.close() # Закрываем
				file = open(f'{path}/photo_pre.html', 'r', encoding="utf8").read()
			
		with open(join(f'{path_albums}/', 'albums.json'), 'w') as alb_file:
			json.dump(json_albums, alb_file)
		print("Выгрузка фотографий из альбомов завершена")
		print(" ")
		print("[99] Назад")
		print(" ")
		inp = int(input("Ввод: "))
		match inp:
			case 99:
				main_menu()
			case _:
				print("Такого варианта нет")
				main_menu()
	except Exception as e: # Исключения ошибок
		error_log.add('get_photos_profile', e)
		main_menu()

def main_menu():
	clear()
	get_stand()
	print(f'{name} -  Авторизован')
	print(" ")
	print("[1] Дамп фотографий из всех диалогов")
	print("[2] Дамп фотографий диалога с опр. пользователем")
	print("[3] Дамп фотографий (сохры. и т.д.)")
	#print("[5] Дамп фотографий всех друзей у которых открыты(сохры. и т.д)")
	print("[4] Дамп фотографий друга(сохры. и т.д)")
	print(" ")
	print("[111] Настройки")
	print("[0] Выйти из аккаунта")
	print(" ")

	try:
		inp = int(input("Ввод: "))
		match inp:
			case 1:
				get_dialogs_photo(0)
			case 2:
				try:
					i = int(input("Введите id пользователя: "))
					get_dialogs_photo(i)
				except Exception as e:
					main_menu()
			case 3:
				get_photos_profile()
			case 4:
				try:
					i = int(input("Введите id пользователя: "))
					get_photos_friend()
				except Exception as e:
					main_menu()
				
			case 111:
				settings()
			case 0:
				exit()
			case _:
				print("Такого варианта нет")
				main_menu()
	except Exception as e:
		error_log.add('main_menu', e)
		main_menu()

def settings():
	clear()
	print(f'{name} -  Авторизован')

	print(" ")

	print(f'Папка сохранения - {dump_path}')
	print(f'download - {download}')

	if limit_photo == 0:
		print(f'Лимит фотографий - нет')
	else:
		print(f'Лимит фотографий - {limit_photo}')

	if limit_dialog == 0:
		print(f'Лимит диалогов - нет')
	else:
		print(f'Лимит диалогов - {limit_dialog}')

	print(" ")

	print("[1] Изменить папку сохранения")
	print("[2] Изменить download")
	print("[3] Изменить лимит фотографий")
	print("[4] Изменить лимит диалогов")
	
	print(" ")
	print("[99] Назад")
	print(" ")	
	try:
		inp = int(input("Ввод: "))
		match inp:
			case 1:
				l = input("Введите название папки: ")
				def_config['dump_config']['path'] = l
				dump_defconfig()

				get_dump_config()

				settings()
			case 2:
				if def_config['dump_config']['download'] == False:
					def_config['dump_config']['download'] = True
				else:
					def_config['dump_config']['download'] = False
				dump_defconfig()

				get_dump_config()

				settings()
			case 3:
				l = int(input("Введите число: "))
				def_config['dump_config']['limit_photo'] = l
				dump_defconfig()

				get_dump_config()

				settings()
			case 4:
				l = int(input("Введите число: "))
				def_config['dump_config']['limit_dialog'] = l
				dump_defconfig()

				get_dump_config()

				settings()
			case 99:
				main_menu()
			case _:
				print("Такого варианта нет")
				settings()
	except Exception as e:
		error_log.add('settings', e)
		settings()

def exit():
	login_vk=None
	auth_menu()

def auth_menu():
	clear()
	print("Авторизоваться через ")
	print("[1] Токен")
	print("[2] Логин и пароль")

	inp = 1#int(input("Выберите способ входа: "))
	try:
		match inp:
			case 1:
				login_data['token'] = input("Введите токен: ")
				
				collect(login_data)
			case 2:
				login_data['login'] = input("Введите логин: ")
				login_data['password'] = input("Введите пароль: ")
				collect(login_data)
			case _:
				print("Такого варианта нет")
				auth_menu()
	except Exception as e:
		error_log.add('auth_menu', e)

def dump_manager(config):
	#dump_config = config['dump_config']
	auth_menu()

def dump_defconfig():
	with open('config.json', 'w') as config_file:
		json.dump(def_config, config_file)

def collect(config): #
	global login_vk
	login_vk = LoginVK(config)
	if login_vk.account["id"] > 0:
		main_menu()
	#return MethodsVK(login_vk.vk, login_vk.vk_tools, login_vk.account) 

if __name__ == '__main__':
	try:
		with open('config.json', 'r') as config_file:
			def_config = json.load(config_file)
		dump_manager(def_config)
	except Exception as e:
		error_log.add(__name__, e)
	error_log.save_log('error.log')