import requests
import os
import argparse
import requests_mock


class SpotifyClientException(Exception):
    ''' Custom exception class for Spotify client '''

    def __init__(self, message):
        self.message = message


class SpotifyClient:
    ''' Simple Spotify REST api client '''

    def __init__(self):
        self._main_api_path = 'https://api.spotify.com/v1/artists'

    def get_artist_data(self, artist_id):
        '''
        Returns json data about single artist from Spotify
        :param artist_id: string, artist id from Spotify
        :return: json data about single artist
        '''

        url = self._main_api_path + '/' + artist_id
        res = requests.get(url)

        if res.status_code != 200:
            raise SpotifyClientException('Improper client id or service unavailable')
        return res.json()

    def get_multiple_artists_data(self, ids, sort_by='default'):
        '''
        Returns list of json object about artists
        :param ids: list or tuple of Spotify artist ids
        :param sort_by: string, normally 'default' value, then data is
        returned as received from sever, other possibilities are 'name' and
        'popularity', that sort data before return respectively
        :return: list of json objects about artists from Spotify
        '''
        payload = {'ids': ','.join(ids)}
        res = requests.get(self._main_api_path, params=payload)
        if res.status_code != 200:
            raise SpotifyClientException('Improper client id or service unavailable')

        if sort_by == 'default':
            results = res.json()['artists']
        elif sort_by == 'name':
            artist_list = res.json()['artists']
            if artist_list:
                results = sorted(artist_list, key=lambda item: item['name'])
        elif sort_by == 'popularity':
            artist_list = res.json()['artists']
            if artist_list:
                results = sorted(artist_list, key=lambda item: item['popularity'], reversed=True)
        else:
            raise SpotifyClientException('Improper value of sort_by')

        return results

    def get_artist_albums_titles(self, artist_id, quantity=10):
        '''
        Returns list of artist albums titles
        :param artist_id: string, Spotify artist id
        :param quantity: number of albums titles returned
        :return: list
        '''
        url = self._main_api_path + '/{}/albums'.format(artist_id)
        payload = {'limit': quantity}

        res = requests.get(url, params=payload)
        if res.status_code != 200:
            raise SpotifyClientException('Improper client id or service unavailable')

        response_json = res.json()
        titles = [item['name'] for item in response_json['items']]
        return titles

    def get_best_songs(self, artist_id, country='PL'):
        '''
        Returns list of most popular songs of particular artist
        :param artist_id: string, Spotify artist id
        :param country: two letter country code, specifies from which
        country popularity should be returned
        :return: list of list in form [song_title, popularity]
        '''

        url = self._main_api_path + '/{}/top-tracks'.format(artist_id)
        payload = {'country': country}

        res = requests.get(url, params=payload)
        if res.status_code != 200:
            raise SpotifyClientException('Improper client id or country code or service unavailable')

        response_json = res.json()
        tracks = [[item['name'], item['popularity']] for item in response_json['tracks']]

        # no need to sort, they are by default returned ordered by popularity
        return tracks


def unit_tests():
    '''
    Some basic tests
    :return: None, raise exception if some of tests failed
    '''
    session = requests.Session()
    adapter = requests_mock.Adapter()
    session.mount('mock', adapter)

    adapter.register_uri('GET', 'mock://test.com', text='data')
    resp = session.get('https://api.spotify.com/v1/artists/3qm84nBOXUEQ2vnTfUTTFC')
    try:
        resp.raise_for_status()
    except Exception:
        raise Exception('Tests failed')

    if not resp.json() or resp.json()['name'] != "Guns N' Roses":
        raise Exception('Tests failed')


def main():
    '''
    Just a basic demonstration of client functionalities
    :return: None
    '''

    unit_tests()

    ap = argparse.ArgumentParser()
    ap.add_argument('-a', '--artist_id', required=True, help='Spotify artist id')
    args = vars(ap.parse_args())

    test_artist_id = args['artist_id']
    sc = SpotifyClient()

    artist_info = sc.get_artist_data(test_artist_id)
    first_10_album_titles = sc.get_artist_albums_titles(test_artist_id)
    most_popular_songs = sc.get_best_songs(test_artist_id)

    print('Artist:', artist_info['name'])
    print('First 10 album titles:', first_10_album_titles)
    print('Most popular songs:', most_popular_songs)

if __name__ == '__main__':
    main()
