import requests
from bs4 import BeautifulSoup
import random
import pandas as pd
from flask import Flask
from selenium import webdriver
import os

A = ("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 "
     "Safari/537.36",
     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
     )

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def check():
    result = pd.DataFrame()
    text = "As we all know by now, Russia has declared war against Ukraine. " \
           "Russian troops had started surrounding Ukraine nearly 2 months ago and they finally " \
           "declared war yesterday. Ukraine has seen multiple blasts on the border and there has been " \
           "observed a major loss of life and destruction of property. " \
           "The tension between Russia and Ukraine has always been evident since Putin, " \
           "the Russian president has always been clear about he wants to reclaim Ukraine as his own," \
           " and as to how it was part of the USSR. Putin recently announced that Russia " \
           "will recognize the independence of 2 breakaway republics – Luhansk and Donetsk – which are " \
           "closely bordering Ukraine and are arguably within Ukrainian territory.Hello Everyone," \
           " Naa madan Gowricarvradrv"

    if text[-1] == ".":
        text = text[:-1]
    text = text.replace("\t", ".")
    text = text.replace("\n", ".")
    text_arr = text.split(".")
    for sample_text in text_arr:
        if len(sample_text) <= 5:
            continue
        url = 'https://google.com/search?q=' + '"' + sample_text + '"'
        agent = A[random.randrange(len(A))]
        headers = {'user-agent': agent}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        link_cards = soup.find_all("div", {"class": "ZINbbc luh4tb xpd O9g5cc uUPGi"})

        print()
        if link_cards:
            links = []
            for i in link_cards:
                x = i.div.a
                furl = x['href']
                links.append(furl[furl.index("url=") + 4:].split("&")[0])

            if len(links) > 2:
                links = links[:2]

            for link in links:
                print(
                    "=================================================================================================="
                    "===")
                print("Sample Text :", sample_text)
                deep_url = link
                print("Source Link :", deep_url)
                driver.get(deep_url)
                html_source = driver.page_source
                deep_page = BeautifulSoup(html_source, "html.parser")
                for data in deep_page(['style', 'script']):
                    data.decompose()
                print(' '.join(deep_page.stripped_strings).replace("\xa0", " "))
                print()
                if sample_text in ' '.join(deep_page.stripped_strings).replace("\xa0", " "):
                    print("Match Found")
                    result = result.append({"Sentence": sample_text, "Status": "Plagiarized", "Source": links[0]},
                                           ignore_index=True)
                    break
            else:
                print("Match not found")
                result = result.append({"Sentence": sample_text, "Status": "Unique"}, ignore_index=True)
        else:
            result = result.append({"Sentence": sample_text, "Status": "Unique"}, ignore_index=True)
    print(result)
    return result.to_dict()


if __name__ == "__main__":
    app.run(debug=True)
