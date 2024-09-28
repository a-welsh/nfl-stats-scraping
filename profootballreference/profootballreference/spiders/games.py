import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from scrapy.selector import Selector
from selenium.webdriver.common.action_chains import ActionChains
from ..items import CsvFileItem, CsvItem, MetaItem

class GamesSpider(scrapy.Spider):
    name = 'games'
    allowed_domains = ['www.pro-football-reference.com']
    start_year = 2000
    end_year = 2024
    years = range(start_year, end_year + 1)
    start_urls = [
        f'http://www.pro-football-reference.com/years/{year}/games.htm'
        for year in years
    ]

    def parse(self, response):
        year = response.url.split('/')[-2]

        # Get week and link for all games in the season
        rows = response.xpath('//tbody/tr[not(@class="thead")]')
        for row in rows:
            week = row.xpath('.//td[@data-stat="week_num"]/text()').get()
            link = row.xpath('.//td[@data-stat="boxscore_word"]/a/@href').get()
            full_link = response.urljoin(link)

            # Use Selenium to get JavaScript content - may have to change wait_time
            yield SeleniumRequest(
                url=full_link,
                wait_time=2,
                callback=self.parse_game,
                meta={'year': year, 'week': week},
            )

    def parse_game(self, response):
        self.activate_csvs(response)
        self.parse_csvs(response)

        pass

    def activate_csvs(self, response):
        driver = response.meta['driver']

        arrows = driver.find_elements(
            By.XPATH, '//span[text()="Share & Export"]/ancestor::li[@class="hasmore"]'
        )
        buttons = driver.find_elements(
            By.XPATH,
            '//span[text()="Share & Export"]/following-sibling::div//descendant::button[text()="Get table as CSV (for Excel)"]',
        )

        previous_location = 0
        for (arrow, button) in zip(arrows, buttons):
            scroll_location = arrow.location['y'] - 50
            # For some reason it doesn't like when these are combined
            ActionChains(driver).scroll_by_amount(
                0, scroll_location - previous_location
            ).perform()

            ActionChains(driver).move_to_element(arrow).click(button).perform()

            previous_location = scroll_location

        #return response
    
    def parse_csvs(self, response):
        driver = response.meta['driver']

        s = Selector(text=driver.page_source)

        # Get scorebox info, team names
        scorebox = s.xpath('//div[@class="scorebox"]')
        away_div = s.xpath('//div[@class="scorebox"]/div[1]/descendant::strong/a')
        home_div = s.xpath('//div[@class="scorebox"]/div[2]/descendant::strong/a')
        away_code = away_div.xpath('@href').get().split('/')[1]
        home_code = home_div.xpath('@href').get().split('/')[1]
        away_full_name = away_div.xpath('text()').get()
        home_full_name = home_div.xpath('text()').get()
        away_name = away_full_name.split(' ')[-1]
        home_name = home_full_name.split(' ')[-1]
        away_coach = s.xpath('//div[@class="scorebox"]/div[1]/descendant::strong[text()="Coach"]/following-sibling::a/@href').get().split('/')[-1].split('.')[0]
        home_coach = s.xpath('//div[@class="scorebox"]/div[2]/descendant::strong[text()="Coach"]/following-sibling::a/@href').get().split('/')[-1].split('.')[0]
        # TODO: The date has no name, and the others just have <strong> tag before the text, this logic might
        # not hold for all pages 
        

        # Get non-CSV tables
        game_info_table = s.xpath("//td[text()='Game Info']/parent::tr/parent::thead/following-sibling::tbody")
        game_info_headers = game_info_table.xpath('.//th[@data-stat="info"]/text()').getall()
        game_info_values = game_info_table.xpath('.//td[@data-stat="stat"]/text()').getall()
        
        officials_table = s.xpath("//td[text()='Officials']/parent::tr/parent::thead/following-sibling::tbody")
        officials_headers = officials_table.xpath('.//th[@data-stat="ref_pos"]/text()').getall()
        officials_names = officials_table.xpath('.//td[@data-stat="name"]/@href').getall()
        officials_names = [name.split('/')[-1].split('.')[0] for name in officials_names]

        yield CsvFileItem(table_name='game_info', csv_content=[game_info_headers, game_info_values])
        yield CsvFileItem(table_name='officials', csv_content=[officials_headers, officials_names])


        table_names = s.xpath("//span[text()='Share & Export']/ancestor::div[@class='table_wrapper']/div/h2/text()").getall()
        csvs = s.xpath("//pre[starts-with(@id, 'csv')]")
        
        for table_name, csv in zip(table_names, csvs):
            # TODO: we'll see if this is brittle, it feels way too specific
            csv_content = csv.xpath('text()').getall()
            csv_content = csv_content[1].split('\n')
            csv_content = [row.split(',') for row in csv_content]
            # Most tables have this as the first row for some reason
            csv_content = [row for row in csv_content if row!=['']]

            item = CsvFileItem(table_name=table_name, csv_content=csv_content)

            yield item
        

