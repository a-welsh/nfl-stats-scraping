# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv
import os
import json
from pathlib import Path

BASE_DIR = Path('./csv_files')

# TODO: Throw all of this out and save everything to a DB
# From what I've seen online, it seems like the Pipeline has to just return one item,
# so that's why I've put all of the tables in a list.  This seems clunky though.
class CsvFilePipeline:
    def process_item(self, item, spider):
        with open('debug_csv.txt', 'a') as f:
            f.write(f'Processing item: {item}\n')
        
        meta = item['meta']
        game_tables = item['game_tables']
        
        game_id = meta['game_id']

        # Create a directory to store the CSV files if it doesn't exist
        output_dir: Path = BASE_DIR / game_id
        print(f'Creating directory {output_dir}')
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write the CSV contents to files
        for table_name, csv_content in game_tables.items():
            csv_file_path = output_dir / f'{table_name}.csv'
            with open(csv_file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                for row in csv_content:
                    writer.writerow(row)

        # Write the meta info to a file
        meta_file_path = output_dir / 'meta.json'
        if not meta_file_path.exists():
            with open(meta_file_path, 'w') as f:
                json.dump(meta, f)

        #return item

class MetaPipeline:  
    pass
    '''
    def process_item(self, item, spider):
        with open('debug_meta.txt', 'a') as f:
            f.write(f'Processing item: {item}\n')
        game_id = item['game_id']
        output_dir = BASE_DIR / game_id
        print(f'Creating directory {output_dir}')
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / 'meta.json'
        with open(output_path, 'w') as f:
            json.dump(dict(item), f)
    '''


class ProfootballreferencePipeline:
    def process_item(self, item, spider):
        return item
