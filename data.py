import os
import re
import json
import pandas as pd
import requests
from parsel import Selector

input_path = r'Stores_Dominos_Delhi_Links.xlsx'
output_json_path = r'Stores_Dominos_Delhi.json'
Html_dir = r'stores_dominos_pages'

df = pd.read_excel(input_path)

if 'URL' not in df.columns:
    raise ValueError("The Excel file must contain a 'URL' column.")

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
}


def fetch_data(url, retries=5):
    Html_path = os.path.join(Html_dir, re.sub(r'[^\w\s]', '_', url) + '.html')

    if os.path.exists(Html_path):
        print(f"Reading from Pagesave: {Html_path}")
        with open(Html_path, 'r', encoding='utf-8') as file:
            return file.read()

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                html_text = response.text
                os.makedirs(Html_dir, exist_ok=True)
                with open(Html_path, 'w', encoding='utf-8') as file:
                    file.write(html_text)
                return html_text
            else:
                print(f"Request failed {response.status_code}")
        except requests.RequestException as e:
            print(f"Request failed", e)


data_list = []
data_list_unique = set()

for index, row in df.iterrows():
    url = row['URL']
    html_text = fetch_data(url)
    selector = Selector(text=html_text)
    store_info_boxes = selector.xpath('//*[@class="store-info-box"]')

    for di in store_info_boxes:
        store_data = {}
        try:
            store_data['website'] = di.xpath('.//li[@class="outlet-name"]/div[@class="info-text"]//a/@href').get()
        except Exception as e:
            print(e)
            store_data['website'] = ''

        try:
            map_url = di.xpath('.//li[@class="outlet-name"]/div[@class="info-text"]//a/@href').get()
            store_data['map'] = map_url.replace("/Home", "/Map") if map_url else ''
        except Exception as e:
            print(e)
            store_data['map'] = ''

        try:
            name = di.xpath(
                './/li[@class="outlet-name"]/div[@class="info-text"]//a/@data-track-event-click').get()
            if name:
                store_data['name'] = name.strip()
        except:
            store_data['name'] = ''

        try:
            store_data['locality'] = di.xpath(
                './/li[@class="outlet-name"]/div[@class="info-text"]//a/@data-track-event-business-alternate-name').get()
        except:
            store_data['locality'] = ''

        try:
            fullname = di.xpath('.//li[@class="outlet-name"]/div[@class="info-text"]//a/@title').get()
            if fullname:
                store_data['fullname'] = fullname.strip()
        except:
            store_data['fullname'] = ''

        try:
            store_data['state'] = di.xpath(
                './/li[@class="outlet-name"]/div[@class="info-text"]//a/@data-track-event-state').get()
        except:
            store_data['state'] = ''

        try:
            store_data['city'] = di.xpath(
                './/li[@class="outlet-name"]/div[@class="info-text"]//a/@data-track-event-city').get()
        except:
            store_data['city'] = ''

        try:
            address_parts = di.xpath(
                './/li[@class="outlet-address"]//div[@class="info-text"]/span/text() | '
                './/li[@class="outlet-address"]//div[@class="info-text"]/span/span/text()'
            ).getall()

            if address_parts:
                store_data['address'] = ' '.join(part.strip() for part in address_parts).strip()
            else:
                store_data['address'] = ''
        except Exception as e:
            store_data['address'] = ''
            print("Address error", e)

        try:
            store_data['phone'] = di.xpath('.//li[@class="outlet-phone"]/div[@class="info-text"]/a/text()').get()
        except:
            store_data['phone'] = ''

        try:
            store_data['open_at'] = di.xpath('.//li[@class="outlet-timings"]/div[@class="info-text"]/span/text()').get()
        except:
            store_data['open_at'] = ''

        store_data['link'] = url  

        unique_id = (store_data['website'], store_data['address'], store_data['phone'])
        if unique_id not in data_list_unique:
            data_list_unique.add(unique_id)
            data_list.append(store_data)

with open(output_json_path, 'w') as json_file:
    json.dump(data_list, json_file, indent=4)

print(f"Json file {output_json_path}.")
