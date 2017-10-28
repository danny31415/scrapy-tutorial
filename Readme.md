Running Scrapy
####

1. first set up a virtualenv (see directions elsewhere)

to run scrapy:
```scrapy runspider living_wage_spider.py -s HTTPCACHE_ENABLED=1 -o data.json```
this will create a data.json file, which has all your outputs

NOTE: if that file already exists, scrapy will append to the previous file, not overwrite it, which will cause weird issues (and an invalid json file, when trying to read it in with read_data.py)
So either use a new filename each time, or remove the previous one before you run it again.


I usually run it with the time command in front, so I can have a rough estimate of how long it takes to run each time
```time scrapy runspider living_wage_spider.py -s HTTPCACHE_ENABLED=1 -o data.json```


The HTTPCACHE_ENABLED setting will cause a .scrapy/ folder to get created, and future runs of scrapy
will avoid making a request to the server if we've already go the data in the cache. This is nice when
playing around xpaths and such in our scraper


Doing something useful with the output
####
After you have a scrapy output file, try running read_data.py on it

```python read_data.py data.json```

play around with that script to see if there are any other useful things you can do with the data.

