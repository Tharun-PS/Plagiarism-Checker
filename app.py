import requests
from bs4 import BeautifulSoup
import random
from flask import Flask, render_template, request
from selenium import webdriver
import os
from flask_cors import CORS, cross_origin
import json

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
CORS(app)


@app.route("/check_plagiarism", methods=["GET", "POST"])
@cross_origin()
def check():
    result = []
    text = request.form['message']
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
                    result.append({"Sentence": sample_text, "Status": "Plagiarized", "Source": links[0]})
                    break
            else:
                print("Match not found")
                result.append({"Sentence": sample_text, "Status": "Unique"})
        else:
            result.append({"Sentence": sample_text, "Status": "Unique"})
    print(result)
    return "<pre>"+json.dumps(json.loads(json.dumps(result)), indent=4)+"</pre>"


@app.route("/", methods=["GET", "POST"])
@cross_origin()
def main_page():
    return render_template("main_page.html")


if __name__ == "__main__":
    app.run(debug=True)
