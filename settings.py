import sys
import os

# Security note: Never store api keys in files.
# We use environment keys for that.

scriptdir = os.path.dirname(os.path.realpath(sys.argv[0]))
# INFO, DEBUG, WARNING, ERROR, CRITICAL
log_level = 'INFO'
# Radarr's API Key for TMDB.  Stored because it's publicly available.
radarr_tmdb_api_key = '1a7373301961d03f97f853a876dd1212'
tmdb_url = 'https://api.themoviedb.org/3'
# Your Radarr API url. Example: http://radarr.my.server:7878/api
radarr_url = os.environ['RADARR_API_URL']
# Your Radarr API key
radarr_api_key = os.environ['RADARR_API_KEY']
# Turn this False if you really need to.
verify_ssl_certs = True