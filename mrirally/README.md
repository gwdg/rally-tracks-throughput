# MRI data

See <https://esrally.readthedocs.io/en/stable/adding_tracks.html>


Playground container:
```
docker run --rm -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -e "xpack.security.enabled=false" elasticsearch:8.7.1
```

For development I recommend to use the `--test-mode` that only uses the first 1k entries of the corpus.
