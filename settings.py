import sys
import os

scriptdir = os.path.dirname(os.path.realpath(sys.argv[0]))
# INFO, DEBUG, WARNING, ERROR, CRITICAL
log_level = 'INFO'
# Radarr's API Key for TMDB
radarr_tmdb_api_key = '1a7373301961d03f97f853a876dd1212'
tmdb_url = 'https://api.themoviedb.org/3'
# Your Radarr API url
radarr_url = 'http://your_radar_url:7878/api'
# Your Radarr API key
radarr_api_key = ''
# Turn this False if you really need to.
verify_ssl_certs = True
# The file where we save the state of the genres, 
# since Radarr doesn't allow us to store it via the API properly
genre_json = os.path.join(scriptdir, 'genre_db.json')
