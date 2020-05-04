# radarr-genre-filter
Clean specific Genres from your Radar wanted/downloaded library.

## Install
`pip3 install -r requirements.txt`

## Syntax
```angular2
usage: run_radarr_filter.py [-h] [-l] [-f FILTER] [-d] [-df] [-a] [-v]
                            [-m MINSCORE]

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            List the official genres available for filterings.
  -f FILTER, --filter FILTER
                        Use this option for each genre you'd like to filter.
  -d, --delete          Delete the movie from your wanted or downloaded list.
  -df, --deletefile     Delete the movie from your wanted or downloaded list
                        and delete existing files, if they exist.
  -a, --addexclusion    Add the movie to the import exclusion list,
                        effectively blacklisting it.
  -v, --verify          Verify each item to delete by asking first.
  -m MINSCORE, --minscore MINSCORE
                        Keep the movie if the minimum score (%) is equal or
                        higher than provided.
```

## Example
Want to delete all Horror flicks that don't have a minimum score of 70%, and ask you to verify before deleting?  Use the following syntax:  
`run_radarr_filter.py --filter Horror --deletefile --addexclusion --verify --minscore 70`

## Radarr Issues
Unfortunately, Radarr doesn't seem to have a way to store the genre using the API, even though the documentation says it can. 
When you PUT to the movies api endpoint, the data isn't updated, and from the issue comments, it seems like it simply isn't implemented.

It would be much more efficient to simply update that info in Radarr for subsequent calls, instead, I chose to keep the data locally in a JSON file.