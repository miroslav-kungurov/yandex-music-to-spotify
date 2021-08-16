import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import oauth2
from get_music_data import get_my_playlists, get_liked_playlists, get_albums


# функция для авторизации в Spotify
def autorisation():
    client_id = ''
    client_secret = ''
    # разрешения нашего приложения
    scope = ('user-library-read, playlist-read-private, playlist-modify-private, playlist-modify-public, user-read-private, user-library-modify, user-library-read')
    # URL, на который переадресуется браузер пользователя после получения прав доступа при получении ключа доступа
    redirect_uri = 'http://localhost:8888/callback/'
    sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope)
    code = sp_oauth.get_auth_response(open_browser=True)
    # получаем токен
    token = sp_oauth.get_access_token(code, as_dict=False)
    sp = spotipy.Spotify(auth=token)
    # id пользователя Spotify
    username = sp.current_user()['id']
    return sp, username


# функция, получающая id трека
def get_track_id(query, sp):
    # получаем данные по первому треку из поисковой выдачи Spotify
    track_id = sp.search(q=query, limit=1, type='track')
    # Теперь найдем id первого трека из поисковой выдачи.
    # метод split() сделает список из одной строчки.eя
    # Это нужно для метода playlist_add_items(), принимающего в качестве второго аргумента список.
    return track_id['tracks']['items'][0]['id'].split()


# функция, переносящая плелисты
def transfer_playlists(yandex_username, playlists_for_spotify):
    # авторизуемся в Spotify
    sp, username = autorisation()
    print('\n')
    print('Начинаю переносить плейлисты\n')
    # playlists_for_spotify – плейлисты из Яндекс Музыки (название и исполнитель)
    # плейлисты берем из функций get_liked_playlists() и get_my_playlists()
    # создадим плейлисты
    for i in range(len(playlists_for_spotify)):
        # сделаем список из ключей/названий плейлистов
        playlist_name = list(playlists_for_spotify.keys())[i]
        # создадим в Spotify плейлист с именем (playlist_name)
        create_spotify_playlist = sp.user_playlist_create(username, playlist_name)
        # получим id созданного плейлиста
        new_spotify_playlist_id = create_spotify_playlist['id']
        # number_of_tracks – количество треков в плейлисте playlist_name
        number_of_tracks = range(len(playlists_for_spotify[playlist_name]))
        new_spotify_playlist = {}
        # добавим песни в плейлист Spotify
        for j in number_of_tracks:
            try:
                # получим имя исполнителя
                artist_name = playlists_for_spotify[playlist_name][j]['artist_name']
                # получим название трека
                track_name = playlists_for_spotify[playlist_name][j]['track_name']
                # query – поисковый запрос в Spotify, состоящий из имени исполнителя (artist_name), пробела (' ') и названия трека (track_name)
                query = ' '.join([artist_name,  track_name])
                # получим id найденного трека в Spotify
                spotify_track_id = get_track_id(query, sp)
                # добавим в словарь id трека (ключ) и id плейлиста (значение)
                new_spotify_playlist[spotify_track_id[0]] = new_spotify_playlist_id
            except:
                pass

        # если плейлист пустой (треки отсутствуют в каталоге Spotify), то удалить его из Spotify
        if all(query == '' for query in new_spotify_playlist.values()):
            sp.user_playlist_unfollow(username, new_spotify_playlist_id)
            continue

        # если в каталоге есть хотя бы один трек, то добавить трек(и) в плейлист Spotify
        else:
            for new_spotify_playlist_id, track_id in new_spotify_playlist.items():
                sp.playlist_add_items(track_id, new_spotify_playlist_id.split())

        # выведем на экран перенесенный плелист
        print(
            ''.join(['[', str(i + 1), ']',
                     ' Плейлист «', playlist_name, '» перенесен'])
        )

    print('\n')
    print('Готово')
    print('\n')


# функция, получающая id альбома
def get_album_id(query, sp):
    # получим данные по альбому из поискового запроса в Spotify
    album_id = sp.search(q=query, limit=1, type='album')
    # получим id альбома
    # split() – делает список, состоящий из одной строчки для метода current_user_saved_albums_add()
    return album_id['albums']['items'][0]['id'].split()


# функция для переноса альбомов
def transfer_albums(yandex_username, albums_for_spotify):
    # авторизуемся в Spotify
    sp, username = autorisation()
    print('\n')
    print('Начинаю переносить альбомы')
    print('\n')
    # albums_for_spotify – альбомы для переноса из Яндекс.Музыки
    # содержит название трека и имя исполнитель
    for i in range(len(albums_for_spotify)):
        try:
            # получим название альбома
            album_title = albums_for_spotify[i]['album_title']
            # получим имя исполнителя
            artist_name = albums_for_spotify[i]['artist_name']
            # сформируем поисковый запрос в Spotify
            query = ' '.join([artist_name,  album_title])
            # получим id альбома в Spotify
            album_id = get_album_id(query, sp)
            # добавим альбом в свою фонотеку
            sp.current_user_saved_albums_add(album_id)

            # выведем на экран перенесенный альбомы
            print(
                ''.join(['[', str(i + 1), '/', str(len(albums_for_spotify)), ']',
                         ' Альбом «', album_title, ' — ', artist_name, '» перенесен'])
            )

        except:
            pass

    print('\n')
    print('Готово\n')
    print('\n')


def main(yandex_username):
    # перенос плейлиста «Мне нравится» и личных плейлистов
    #transfer_playlists(yandex_username, get_my_playlists(yandex_username))
    # перенос лайкнутых плейлистов
    #transfer_playlists(yandex_username, get_liked_playlists(yandex_username))
    # перенос альбомов
    transfer_albums(yandex_username, get_albums(yandex_username))



if __name__ == "__main__":
    yandex_username = 'имя пользователя Яндекс.Музыки'
    main(yandex_username)
