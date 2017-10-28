import scrapy
from scrapy.linkextractors import LinkExtractor

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.httpcache.HttpCacheMiddleware': 300,
}

class LivingWageSpider(scrapy.Spider):
    name = 'livingwagespider'

    custom_settings = {
        # throttle the requests by putting a .25 second delay between, so we don't hit their server too hard
        'DOWNLOAD_DELAY': .25,
        # cache the results, so successive runs of the scraper while we are developing will be much faster. 
        # This also avoids the download delay as well
        'HTTPCACHE_ENABLED': True,
    }

    # start_urls are where the spider starts crawling (the seed)
    start_urls = [
        # use just this line if you want to test on a single county page, and see what gets extracted from the wage table
        # 'http://livingwage.mit.edu/counties/48001'

        # use just this line to try a single state (HI), which will grab all the county and metro links off that page
        # then traverse into those pages to extract wage tables from each
        'http://livingwage.mit.edu/states/15/locations',

        # Use this line if you want to grab all the data
        # it'll parse the main page, which has links to all the states,
        # which will in turn have all the counties and metros,
        # and we'll end up getting all 30k+ total county+metro pages and outputing their wage tables
        # 'http://livingwage.mit.edu/',
    ]

    # this method gets called on all the pages
    def parse(self, response):
        
        # /html/body/div/div[2]/div[1]/table
        # the wages table has class attribute 'wages_table', so we just search the entire page for that class
        for wages_table in response.xpath("//*[contains(@class, 'wages_table')]"):
            # since we found a wages table, then the title is relevant to us
            # grab the title of the page. Something like 'Living Wage Calculation for Anderson County, Texas'
            title = response.xpath('/html/body/div/div[2]/h1/text()').extract_first()

            # xpath I got from google chrome for the header row /html/body/div/div[2]/div[1]/table/thead/tr/th
            # but here we will use a relative path from the wages table 
            header_row_sel = './thead/tr/th/text()'

            # full xpath from chrome /html/body/div/div[2]/div[1]/table/tbody
            # note the tbody vs thead on the header row, and that tr is an array here, since there is only one row in the header
            # and multiple rows in the body
            living_wage_sel = './tbody/tr[1]/td/text()'
            poverty_wage_sel = './tbody/tr[2]/td/text()'
            minimum_wage_sel = './tbody/tr[3]/td/text()'

            # use these arrays to store the data from the table, so we can stick it all in the json object for this page at the bottom
            header_row_data = []
            living_wage_data = []
            poverty_wage_data = []
            minimum_wage_data = []
            # string = string.replace("\u00A0","");
            # /html/body/div/div[2]/div[1]/table/tbody/tr[1]/td[2]

            # get rid of leading and trailing whitespace.
            # also remove the annoying non-breaking-spaces by replacing it with a normal space
            for cell in wages_table.xpath(header_row_sel):
                header_row_data.append(cell.extract().strip().replace("\u00A0"," "))
            for cell in wages_table.xpath(living_wage_sel):
                living_wage_data.append(cell.extract().strip().replace("\u00A0"," "))
            for cell in wages_table.xpath(poverty_wage_sel):
                poverty_wage_data.append(cell.extract().strip().replace("\u00A0"," "))
            for cell in wages_table.xpath(minimum_wage_sel):
                minimum_wage_data.append(cell.extract().strip().replace("\u00A0"," "))

            # this is the actual data that we want to return.
            # the URL and title are going to be useful later for knowing which fips code this data is referring to
            # yeilding a raw dictionary causes the result to be in the output (when you pass -o data.json on the command line for instance)
            # and to the output in your terminal when you run it
            yield {
                'url': response.url,
                'title': title,
                'header_row_data': header_row_data,
                'living_wage_data': living_wage_data,
                'poverty_wage_data': poverty_wage_data,
                'minimum_wage_data': minimum_wage_data,
            }

        
        # find all links on the page, looking for state, county, or metro links
        for link in response.xpath("//a/@href"):
            link_extract = link.extract()

            # on the state pages, we want to traverse into the /metros/* and /counties/* pages. for example
            # http://livingwage.mit.edu/counties/48001
            # http://livingwage.mit.edu/metros/10180
            if link_extract.startswith('/metros/') or link_extract.startswith('/counties/'):
                # yielding a scrapy.Request causes that url to be added to the list of pages to scrape
                yield scrapy.Request(
                    response.urljoin(link_extract),
                    callback=self.parse
                )
            # from the main page, we want to traverse into the state pages 
            # http://livingwage.mit.edu/states/48/locations
            # so they begin with /states/ and end with /locations
            # this isn't super robust against them changing the layout of the page, but it's good enough to get
            # the job done for now
            elif link_extract.startswith('/states/') and link_extract.endswith('/locations'):
                # yielding a scrapy.Request causes that url to be added to the list of pages to scrape
                yield scrapy.Request(
                    response.urljoin(link_extract),
                    callback=self.parse
                )
            else:
                # dummy code for debugging links
                pass
                # yield {
                #     'dead_link': link_extract,
                # }
