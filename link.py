import requests
from parsel import Selector
import pandas as pd
import time
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
}

def fetch_url(url, headers, retries=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Request failed {response.status_code}")
        except Exception as e:
            print(f"Request failed",e)


url = 'https://stores.dominos.co.in/location/delhi/new-delhi'

html_text = fetch_url(url, headers)
selector = Selector(text=html_text)

locality_options = selector.xpath('//*[@name="locality"]/option/text()').getall()

data = []
for loc in locality_options:
    locality_url = f'https://stores.dominos.co.in/location/delhi/new-delhi/{loc.replace(" ", "-")}'
    data.append({'Locality': loc, 'URL': locality_url})


df = pd.DataFrame(data)
output_path = r'links.xlsx'
df.to_excel(output_path, index=False)

