# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv
import os
import json

# TODO: Throw all of this out and save everything to a DB
class CsvFilePipeline:
    def process_item(self, item, spider):
        game_id = item['game_id']
        table_name = item['table_name']
        csv_content = item['csv_content']

        # Create a directory to store the CSV files if it doesn't exist
        output_dir = f'csv_files/game_id'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Define the CSV file path
        csv_file_path = os.path.join(output_dir, f'{table_name}.csv')

        # Write the CSV content to the file
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for row in csv_content:
                writer.writerow(row)

        return item


class MetaPipeline:
    def process_item(self, item, spider):
        pass


class ProfootballreferencePipeline:
    def process_item(self, item, spider):
        return item
