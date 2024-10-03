import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from scrapy.selector import Selector
from selenium.webdriver.common.action_chains import ActionChains
from ..items import CsvFileItem
from datetime import datetime


# TODO: add logic here to check file system for game CSVs and skip if they exist
# This will require some thought around folder structure... if there's one folder per game that would help,
# but might make parsing downstream more difficult

# 10/3/2024 update: I was able to finally get the item pipeline to work...
#   but only with setting callback=parse_scorebox and moving some things around.  But, 
#   it seems like I need to simplify things.  Once something is yielded from a callback method,
#   it seems like the spider stops and sends it to the pipeline.  So I need to store everything
#   until I'm ready to be done with that page and then I can yield the item.
#   This obviously uses more memory, but I'm not sure how else to do it.

class GamesSpider(scrapy.Spider):
    name = 'games'
    allowed_domains = ['www.pro-football-reference.com']
    start_year = 2000
    end_year = 2024
    years = range(start_year, end_year + 1)
    start_urls = [
        f'http://www.pro-football-reference.com/years/{year}/games.htm'
        for year in years
    ][-1:]

    def parse(self, response):
        year = response.url.split('/')[-2]

        # Get week and link for all games in the season, bypassing header rows
        rows = response.xpath('//table[@id="games"]/tbody/tr[not(@class="thead") and not(td/strong[contains(text(), "Playoffs")])]')
        for row in rows:
            week = row.xpath('./th[@data-stat="week_num"]/text()').get()
            link = row.xpath('./td[@data-stat="boxscore_word"]/a/@href').get()
            full_link = response.urljoin(link)

            # Use Selenium to get JavaScript content - may have to change wait_time
            yield SeleniumRequest(
                url=full_link,
                wait_time=2,
                callback=self.parse_game,
                #callback=self.parse_scorebox,
                meta={'year': year, 'week': week},
                screenshot=True,
            )
            break

    def parse_game(self, sel_response):
        meta = self.parse_scorebox(sel_response)
        self.activate_csvs(sel_response)
        item = self.parse_csvs(sel_response, meta)
        yield item

    def parse_scorebox(self, sel_response):
        driver = sel_response.meta['driver']
        s = Selector(text=driver.page_source)

        #with open(r'C:\Users\Austin\nfl-stats-scraping\profootballreference\profootballreference\test.html', 'w') as f:
        #    f.write(driver.page_source)

        # Get scorebox info, team names
        scorebox = s.xpath('//div[@class="scorebox"]')
        away_div = s.xpath('//div[@class="scorebox"]/div[1]/descendant::strong/a')
        home_div = s.xpath('//div[@class="scorebox"]/div[2]/descendant::strong/a')
        away_code = away_div.xpath('./@href').get().split('/')[-2]
        home_code = home_div.xpath('./@href').get().split('/')[-2]
        away_full_name = away_div.xpath('./text()').get()
        home_full_name = home_div.xpath('./text()').get()
        away_name = away_full_name.split(' ')[-1]
        home_name = home_full_name.split(' ')[-1]
        away_coach = scorebox.xpath('./div[1]/descendant::strong[text()="Coach"]/following-sibling::a/@href').get().split('/')[-1].split('.')[0]
        home_coach = scorebox.xpath('./div[2]/descendant::strong[text()="Coach"]/following-sibling::a/@href').get().split('/')[-1].split('.')[0]
        
        # TODO: Most don't have descriptors, this logic might not hold for all pages
        other_info = s.xpath('//div[@class="scorebox"]/div[@class="scorebox_meta"]')
        raw_date = other_info.xpath('./descendant::div[1]/text()').get()
        parsed_date = datetime.strptime(raw_date, '%A %b %d, %Y').strftime('%Y-%m-%d')
        game_id = f'{parsed_date}_{away_code}_{home_code}'
        start_time = other_info.xpath('./descendant::div[2]/text()').get().strip(': ')
        stadium = other_info.xpath('./descendant::div[3]/a/@href').get().split('/')[-1].split('.')[0]
        attendance = other_info.xpath('./descendant::div[4]/a/text()').get()
        game_length = other_info.xpath('./descendant::div[5]/text()').get().strip(': ')

        # This is one way to do it, or I could just add these attributes to the meta in the response
        return {
            'game_id': game_id,
            'year': sel_response.meta['year'],
            'week': sel_response.meta['week'],
            'home_team': home_name,
            'away_team': away_name,
            'home_coach': home_coach,
            'away_coach': away_coach,
            'raw_date': raw_date,
            'date': parsed_date,
            'start_time': start_time,
            'stadium': stadium,
            'attendance': attendance,
            'game_length': game_length,
        }

    def activate_csvs(self, sel_response):
        driver = sel_response.meta['driver']

        arrows = driver.find_elements(
            By.XPATH, '//span[text()="Share & Export"]/ancestor::li[@class="hasmore"]'
        )
        buttons = driver.find_elements(
            By.XPATH,
            '//span[text()="Share & Export"]/following-sibling::div//descendant::button[text()="Get table as CSV (for Excel)"]',
        )

        previous_location = 0
        for i, (arrow, button) in enumerate(zip(arrows, buttons)):
            scroll_location = arrow.location['y'] - 50
            # For some reason it doesn't like when these are combined
            ActionChains(driver).scroll_by_amount(
                0, scroll_location - previous_location
            ).perform()

            driver.save_screenshot(f'screenshot_scroll_{i}.png')

            ActionChains(driver).move_to_element(arrow).click(button).perform()

            previous_location = scroll_location
    
    def parse_csvs(self, sel_response, meta):
        output_dict = {}
        driver = sel_response.meta['driver']
        s = Selector(text=driver.page_source)
        #with open('debug.txt', 'w') as f:
        #    f.write(driver.page_source)

        # Get non-CSV tables
        # TODO: Add "Scoring" table too
        game_info_table = s.xpath('//td[text()="Game Info"]/parent::tr/parent::thead/following-sibling::tbody')
        # TODO: see if this matters, these used to have .//th instead of /tr/th - I think they are equivalent
        game_info_headers = game_info_table.xpath('./tr/th[@data-stat="info"]/text()').getall()
        game_info_values = game_info_table.xpath('./tr/td[@data-stat="stat"]/text()').getall()
        
        officials_table = s.xpath('//td[text()="Officials"]/parent::tr/parent::thead/following-sibling::tbody')
        officials_headers = officials_table.xpath('./tr/th[@data-stat="ref_pos"]/text()').getall()
        officials_names = officials_table.xpath('./tr/td[@data-stat="name"]/@href').getall()
        officials_names = [name.split('/')[-1].split('.')[0] for name in officials_names]

        output_dict['game_info'] = [game_info_headers, game_info_values]
        output_dict['officials'] = [officials_headers, officials_names]

        table_names = s.xpath('//span[text()="Share & Export"]/ancestor::div[@class="table_wrapper"]/div/h2/text()').getall()
        table_names = [i.replace(meta['away_team'], 'away').replace(meta['home_team'], 'home') for i in table_names]
        table_names = [i.lower().replace('/', '').replace(' ', '_').replace(',', '').replace('& ', '') for i in table_names]
        csvs = s.xpath('//pre[starts-with(@id, "csv")]')
        
        for table_name, csv in zip(table_names, csvs):
            # TODO: we'll see if this is brittle, it feels way too specific
            csv_content = csv.xpath('text()').getall()
            csv_content = csv_content[1].split('\n')
            csv_content = [row.split(',') for row in csv_content]
            # Most tables have this as the first row for some reason
            csv_content = [row for row in csv_content if row!=['']]

            output_dict[table_name] = csv_content

        item = CsvFileItem(meta=meta, game_tables=output_dict)

        return item
        

