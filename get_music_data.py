from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import re


# функция, запускающая браузер
def run_driver():
    # включает возможность управления опциями браузера
    chrome_options = Options()
    # аргумент '--headless' запускает браузер без всплывающего окна
    chrome_options.add_argument('--headless')
    # аргумент '--log-level=3' скрывает логирование
    chrome_options.add_argument('--log-level=3')
    # запуск браузера
    driver = webdriver.Chrome('chromedriver', options=chrome_options)
    return driver


# функция, создающая локальный html-файл
def create_local_html_page(page_filename, page_source):
    with open(page_filename + '.html', 'w', encoding='UTF-8') as file:
        # запишем в локальный html-файл содержимое интернет-страницы ЯМ (page_source)
        file.write(page_source)


# функция, открывающая локальный html-файл
def get_local_html_page(yandex_username, page_filename, url):
    # запускаем браузер
    driver = run_driver()
    # браузер переходит на страницу Яндекс.Музыки
    driver.get(url)
    # создаем локальную html-страницу с содержимым из страницы Яндекс.Музыки
    create_local_html_page(page_filename, driver.page_source)
    # путь к локальной html-странице
    path_to_local_html_page = str('file://' + os.getcwd() + '/' + page_filename + '.html')
    # браузер переходит на локальную html-страницу
    driver.get(path_to_local_html_page)
    return driver


# функция, удаляющая локальный html-файл
def delete_local_html_page(page_path):
    os.remove(page_path)


# функция, создающая словарь с названиями альбомов и именами исполнителей
def get_albums(yandex_username):
    print('Перенос альбомов\n')
    # создаем ссылку на альбом
    url = ''.join(['https://music.yandex.ru/users/', yandex_username, '/albums/'])
    print('Скачиваю данные альбомов\n')
    # создадим и перейдем на локальную страницу с альбомом из раздела «Также вам понравились эти плейлисты»
    driver = get_local_html_page(yandex_username, 'album_page', url)
    # прочтем массив с данными плейлистов
    json = driver.execute_script('return Mu')
    # создадим словарь, в который запишем название альбома и имя исполнителя
    albums_for_spotify = {}
    # получим данные альбомов
    all_albums_ids = json['pageData']['albumIds']
    # заполним словарь albums_for_spotify
    for i in range(len(all_albums_ids)):
        try:
            # перейдем на страницу альбома
            driver.get(''.join(['https://music.yandex.ru/album/', str(all_albums_ids[i])]))
            # создадим для каждого альбома вложенный словарь
            albums_for_spotify[i] = {}
            # запишем во вложенный словарь название альбома
            albums_for_spotify[i]['album_title'] = driver.find_element_by_xpath(
                "//h1[@class='deco-typo']").text
            # запишем во вложенный словарь имя исполнителя
            albums_for_spotify[i]['artist_name'] = driver.find_element_by_xpath(
                "//span[@class='d-artists']//a[@class='d-link deco-link']").text

            print(
                ''.join(['[', str(i + 1), '/', str(len(all_albums_ids)), ']',
                         ' Альбом «', albums_for_spotify[i]['album_title'],
                         ' — ', albums_for_spotify[i]['artist_name'], '» готовится к переносу'])
            )
        except:
            pass

    # удалим локальный html-файл
    delete_local_html_page('album_page.html')
    # закроем браузер
    driver.quit()

    return albums_for_spotify


# функция, создающая словарь с id лайкнутых плейлистов, их названиями
# и именами пользователя, создавших плейлист
def get_liked_playlists_data(yandex_username):
    print('Перенос избранных плейлистов\n')

    # создадим ссылку на плейлист
    url = ''.join(['https://music.yandex.ru/users/', yandex_username, '/playlists/'])
    # создадим и перейдем на локальную страницу с плейлистами из раздела «Также вам понравились эти плейлисты»
    driver = get_local_html_page(yandex_username, 'playlist_page', url)
    # получим массив с данными плейлистов

    print('Скачиваю данные плейлистов\n')

    json = driver.execute_script('return Mu')
    # создадим словарь, в который запишем имя пользователя, создавшего плейлист, id и название плейлиста
    liked_playlists_data = {}
    # получим все данные об избранных плейлистах
    bookmarked_playlists_data = json['pageData']['bookmarks']
    # заполним словарь liked_playlists_data
    for i in range(len(bookmarked_playlists_data)):
        try:
            # создадим вложенный словарь для каждого плейлиста
            liked_playlists_data[i] = {}
            # запишем во вложенный словарь id плейлиста
            liked_playlists_data[i]['id'] = bookmarked_playlists_data[i]['kind']
            # запишем во вложенный словарь имя пользователя
            liked_playlists_data[i]['yandex_username'] = bookmarked_playlists_data[i]['owner']['login']
            # запишем во вложенный словарь название плейлиста
            liked_playlists_data[i]['playlist_title'] = bookmarked_playlists_data[i]['title']
        except:
            pass

    # удалим локальный html-файл
    delete_local_html_page('playlist_page.html')

    return liked_playlists_data


# функция, которая переходит на страничку лайкнутых плейлистов и получает названия треков и исполнителей
def get_liked_playlists(yandex_username):
    # получим id плейлистов, их названия и имя пользователя, создавшего плейлист
    liked_playlists_data = get_liked_playlists_data(yandex_username)
    # создадим словарь, в который запишем название плейлиста, треков и имя исполнителя
    liked_playlists_for_spotify = {}

    counter = 0
    for key, value in liked_playlists_data.items():
        # ключ – порядковый номер плейлиста в словаре liked_playlists_data, а значения – имя пользователя и id плейлиста
        # создадим ссылку на плейлист пользователя
        url = ''.join(['https://music.yandex.ru/users/',
                      str(value['yandex_username']), '/playlists/', str(value['id'])])
        # создадим и перейдем на локальную html-страницу плейлиста
        driver = get_local_html_page(yandex_username, str(key), url)
        # получим массив с данными плейлистов
        json = driver.execute_script('return Mu')
        # создадим словарь, в который запишем треки и имя исполнителей
        liked_playlists = {}
        # получим из json значение id трека и id альбома в формате track_id:album_id
        all_track_ids = json['pageData']['playlist']['trackIds']
        # получим название плейлиста
        playlist_name = json['pageData']['playlist']['title']

        counter += 1
        print(''.join(['[', str(counter), '/', str(len(liked_playlists_data)), ']',
                       ' Плейлист «', playlist_name, '» готовится к переносу']))

        # запишем в словарь треки и имена исполнителей
        for i in range(len(all_track_ids)):
            try:
                # отфильтруем только id трека
                track_id = re.findall(r'\d+(?=:)', all_track_ids[i])[0]
                # перейдем на страницу трека
                driver.get(''.join(['https://music.yandex.ru/track/', track_id]))
                # создадим вложенный словарь для каждого плейлиста
                liked_playlists[i] = {}

                # получим название трека из боковой панели
                try:
                    liked_playlists[i]['track_name'] = driver.find_elements_by_xpath("//span[@class='']//a[@class='d-link deco-link']")[0].text
                except:
                    liked_playlists[i]['track_name'] = ['']

                # получим имя исполнителя из боковой панели
                try:
                    liked_playlists[i]['artist_name'] = driver.find_elements_by_xpath(
                        "//span[@class='d-artists']//a[@class='d-link deco-link']")[0].text
                except:
                    liked_playlists[i]['artist_name'] = ['']

                print(''.join(['[', str(i + 1), '/',
                               str(len(all_track_ids)), ']' ' трек готовится к переносу']))
            except:
                pass

        # запишем в словарь название плейлиста, его треки и имена исполнителей
        liked_playlists_for_spotify[playlist_name] = liked_playlists
        # удалим локальный html-файл
        delete_local_html_page(str(key) + '.html')

        print('\n')

        # закроем браузер
        driver.quit()

    return liked_playlists_for_spotify


# функция, получающая id плейлистов
def get_my_playlists_id(yandex_username):
    # создадим ссылку на плейлист
    url = ''.join(['https://music.yandex.ru/users/', yandex_username, '/playlists/'])
    # создадим и перейдем на локальную страницу плейлиста
    driver = get_local_html_page(yandex_username, 'playlist_page', url)
    # получим массив с данными плейлистов
    json = driver.execute_script('return Mu')
    # получим id плейлистов
    my_playlists_id = json['pageData']['playlistIds']

    return my_playlists_id


# функция, создающая словарь с названиями личных плейлистов, треков и именами исполнителей
def get_my_playlists(yandex_username):
    print('Перенос личных плейлистов пользователя', yandex_username, '\n')
    # получим id плейлистов
    my_playlists_id = get_my_playlists_id(yandex_username)
    # создадим словарь, в который запишем название плейлистов, треков и имена исполнителей
    my_playlists_for_spotify = {}
    print('Скачиваю данные плейлистов\n')
    # заполним словарь my_playlists_for_spotify
    for i in range(len(my_playlists_id)):
        # создадим ссылку на плейлист
        my_playlist_url = ''.join(['https://music.yandex.ru/users/',
                                  yandex_username, '/playlists/', str(my_playlists_id[i])])
        # создадим и перейдем на локальную страницу плейлиста
        driver = get_local_html_page(yandex_username, 'my_playlist', my_playlist_url)
        # получим массив с данными плейлистов
        json = driver.execute_script('return Mu')

        # создадим словарь, в который запишем название трека и имя исполнителя
        my_playlists = {}
        # получим из json значение id трека и id плейлиста в формате track_id:playlist_id
        all_track_ids = json['pageData']['playlist']['trackIds']
        # получим название плейлиста
        playlist_name = json['pageData']['playlist']['title']

        print(''.join(['[', str(i + 1), '/', str(len(my_playlists_id)), ']',
                       ' Плейлист «', playlist_name, '» готовится к переносу']))


        # заполним словарь my_playlists
        for j in range(len(all_track_ids)):
            # получим id трека
            track_id = re.findall(r'\d+(?=:)', all_track_ids[j])[0]
            # перейдем на страницу трека
            driver.get(''.join(['https://music.yandex.ru/track/', track_id]))
            # создадим вложенный словарь для каждого плейлиста
            my_playlists[j] = {}
            # запишем в словарь название трека
            try:
                my_playlists[j]['track_name'] = driver.find_elements_by_xpath("//span[@class='']//a[@class='d-link deco-link']")[0].text
            except:
                my_playlists[j]['track_name'] = ['']
            # запишем в словарь имя исполнителя
            try:
                my_playlists[j]['artist_name'] = driver.find_elements_by_xpath(
                "//span[@class='d-artists']//a[@class='d-link deco-link']")[0].text
            except:
                my_playlists[j]['track_name'] = ['']

            print(''.join(['[', str(j + 1), '/',
                           str(len(all_track_ids)), ']' ' трек готовится к переносу']))


        # запишем в словарь название плейлиста, его треки и имена исполнителей
        my_playlists_for_spotify[playlist_name] = my_playlists

        # удалим локальный html-файл
        delete_local_html_page('my_playlist.html')
        print('\n')

    # закроем браузер
    driver.quit()

    return my_playlists_for_spotify

