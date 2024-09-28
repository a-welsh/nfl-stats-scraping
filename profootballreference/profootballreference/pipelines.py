# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv
import os
import json

class CsvFilePipeline:
    def process_item(self, item, spider):
        table_name = item['table_name']
        csv_content = item['csv_content']

        # Create a directory to store the CSV files if it doesn't exist
        if not os.path.exists('csv_files'):
            os.makedirs('csv_files')

        # Define the CSV file path
        csv_file_path = os.path.join('csv_files', f'{table_name}.csv')

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
