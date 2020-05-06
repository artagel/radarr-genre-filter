#! /usr/bin/env python3
import requests
import settings
import json
import logging
import argparse
import os
import sys

log = logging.getLogger("radarr-filter-logger")
log.setLevel(settings.log_level)
ch = logging.StreamHandler()
ch.setLevel(settings.log_level)
log.addHandler(ch)


def tmdb_get_genres():
    url = settings.tmdb_url + '/genre/movie/list?api_key={}'.format(settings.radarr_tmdb_api_key)
    log.info('[+] Getting list of movie genres')
    response = http_get(url)
    if response:
        try:
            genres = json.loads(response)
        except json.decoder.JSONDecodeError:
            log.error('[!] Error decoding json from response. Skipping')
            return False
        genre_list = []
        for genre in genres['genres']:
            genre_list.append(genre['name'])
        log.info('[+] Available Genres: ' + ", ".join(genre_list))
    else:
        log.error('[!] No response data found')


def tmdb_get_movie_info(tmdbid: int) -> dict:
    url = settings.tmdb_url + '/movie/{}?api_key={}'.format(tmdbid, settings.radarr_tmdb_api_key)
    response = http_get(url)
    if response:
        try:
            data = json.loads(response)
        except json.decoder.JSONDecodeError:
            log.error('[!] Error decoding json from response. Skipping')
            return {}
        return data


def radarr_get_movies() -> list:
    url = settings.radarr_url + '/movie?apikey={}'.format(settings.radarr_api_key)
    response = http_get(url)
    # Radarr doesn't chunk or paginate their response.  This request gets ALL data for all movies in your database.
    if response:
        try:
            data = json.loads(response)
        except json.decoder.JSONDecodeError:
            log.error('[!] Error decoding json from response. Skipping')
            return []
        return data


def filter_radarr(filters: list, delete: bool, deletefile: bool, exclude: bool, verify: bool, minscore: int):
    filters = [x.lower() for x in filters]
    always = False
    log.info('[+] Getting your list of movies from Radarr')
    movies = radarr_get_movies()
    movie_cnt = len(movies)
    log.info('[+] Found {} movies'.format(movie_cnt))
    count = 0
    for movie in movies:
        count += 1
        tmdb_info = tmdb_get_movie_info(movie['tmdbId'])
        if not tmdb_info:
            continue
        tmdb_genres = [x['name'] for x in tmdb_info.get('genres', [])]
        tmdb_score = tmdb_info.get('vote_average', 0) * 10
        for genre in tmdb_genres:
            if genre.lower() in filters:
                if delete or deletefile:
                    if int(tmdb_score) >= minscore:
                        log.debug(
                            '[+] Movie score {} is higher than min score {}, skipping.'.format(int(tmdb_score), minscore))
                        continue
                    if verify and not always:
                        response = input('Are you sure you want to delete {}? [y/n/a]'.format(movie['titleSlug']))
                        if response.lower() == 'a':
                            always = True
                        if response.lower() == 'n':
                            continue
                        if response.lower() == 'y' or response.lower() == 'a':
                            remove_movie(movie.get('id'), movie['titleSlug'], deletefile, exclude)
                    elif always:
                        remove_movie(movie.get('id'), movie['titleSlug'], deletefile, exclude)
                    else:
                        # No verification needed, let's delete
                        remove_movie(movie.get('id'), movie['titleSlug'], deletefile, exclude)
        if count % 10 == 0:
            log.info('[+] {}/{}'.format(count, movie_cnt))


def remove_movie(id: int, title: str, deletefile: bool, exclude: bool):
    log.info('[+] Deleting movie: {} '
             'Deleting Files: {} '
             'Adding Exclusion: {}'.format(title, deletefile, exclude))
    del_piece = ''
    exclude_piece = ''
    if deletefile:
        del_piece = '&deleteFiles=true'
    if exclude:
        exclude_piece = '&addExclusion=true'
    url = settings.radarr_url + '/movie/{}?apikey={}{}{}'.format(id, settings.radarr_api_key, del_piece, exclude_piece)
    http_delete(url)


def http_get(url: str) -> bytes:
    log.debug('[+] HTTP GET Url: {}'.format(url))
    r = requests.get(url, verify=settings.verify_ssl_certs)
    if r.status_code == 200:
        return r.content
    else:
        log.error('[!] HTTP GET request failed.  Status Code: {} Reason: {}'.format(r.status_code, r.reason))
        return b''


def http_put(url: str, data: dict) -> bytes:
    log.debug('[+] HTTP PUT Url: {}'.format(url))
    r = requests.put(url, data=json.dumps(data), verify=settings.verify_ssl_certs)
    if r.status_code == 202:
        return r.content
    else:
        log.error('[!] HTTP PUT request failed.  Status Code: {} Reason: {}'.format(r.status_code, r.reason))
        return b''


def http_delete(url: str) -> bytes:
    log.debug('[+] HTTP DELETE Url: {}'.format(url))
    r = requests.delete(url, verify=settings.verify_ssl_certs)
    if r.status_code == 200:
        return r.content
    else:
        log.error('[!] HTTP DELETE request failed.  Status Code: {} Reason: {}'.format(r.status_code, r.reason))
        return b''


if __name__ == "__main__":
    if sys.version_info < (3, 6):
        raise RuntimeError("This package requires Python 3.6+")
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", help="List the official genres available for filterings.",
                        action="store_true")
    parser.add_argument("-f", "--filter", help="Use this option for each genre you'd like to filter.",
                        action='append')
    parser.add_argument("-d", "--delete", help="Delete the movie from your wanted or downloaded list.",
                        action='store_true')
    parser.add_argument("-df", "--deletefile",
                        help="Delete the movie from your wanted or downloaded list and delete existing files, if they exist.",
                        action='store_true')
    parser.add_argument("-a", "--addexclusion",
                        help="Add the movie to the import exclusion list, effectively blacklisting it.",
                        action='store_true')
    parser.add_argument("-v", "--verify",
                        help="Verify each item to delete by asking first.",
                        action='store_true')
    parser.add_argument("-m", "--minscore",
                        help="Keep the movie if the minimum score (%%) is equal or higher than provided.",
                        action='store', type=int, default=0)
    args = parser.parse_args()
    if args.list:
        tmdb_get_genres()
    elif args.filter:
        filter_radarr(args.filter, args.delete, args.deletefile, args.addexclusion, args.verify, args.minscore)
    else:
        parser.print_help()
