# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class CsvFileItem(scrapy.Item):
    meta = scrapy.Field()
    game_tables = scrapy.Field()
    '''
    game_id = scrapy.Field()
    year = scrapy.Field()
    week = scrapy.Field()
    home_team = scrapy.Field()
    away_team = scrapy.Field()
    home_coach = scrapy.Field()
    away_coach = scrapy.Field()
    raw_date = scrapy.Field()
    date = scrapy.Field()
    start_time = scrapy.Field()
    stadium = scrapy.Field()
    attendance = scrapy.Field()
    game_length = scrapy.Field()
    '''

class MetaItem(scrapy.Item):
    pass

class ProfootballreferenceItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
