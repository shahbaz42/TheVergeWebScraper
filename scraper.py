import requests
from bs4 import BeautifulSoup
import csv
import sqlite3
import datetime
import json

class VergeScraper:
    def __init__(self):
        """
        Initialise the scraper
        """
        self.base_url = "https://www.theverge.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        }
        self.data = [] 
    
    def get_html(self):
        """
        Method to get the html
        """
        response = requests.get(self.base_url, headers=self.headers)
        html = response.content
        return html
    
    def parse_html(self, html):
        """
        Method for parsing html and getting all atricles data
        Note : This method only gets the top 5 articles because the rest of the articles are loaded using javascript
        For getting all the articles we need to use parse_json_html() and get_articles_from_json()
        """
        soup = BeautifulSoup(html, "html.parser")
        articles = soup.find_all("div", class_="max-w-content-block-standard md:w-content-block-compact md:max-w-content-block-compact lg:w-[240px] lg:max-w-[240px] lg:pr-10")
        
        for article in articles:
            headline = article.find("a", class_="group-hover:shadow-underline-franklin").text.strip()
            link = self.base_url + article.find("a", class_="group-hover:shadow-underline-franklin")["href"]
            author = article.find("a", class_="text-gray-31 hover:shadow-underline-inherit dark:text-franklin mr-8").text.strip()
            date = article.find("span", class_="text-gray-63 dark:text-gray-94").text.strip()
            print(headline, link, author, date)
            # Create a dictionary with the extracted information
            info = {
                "id": len(self.data) + 1,
                "URL": link,
                "headline": headline,
                "author": author,
                "date": date
            }
            # Append the dictionary to the list
            self.data.append(info)

    def parse_json_html(self, html):
        """
        This method gets the articles from JSON
        contained in <script id="__NEXT_DATA__"> tag
        """
        soup = BeautifulSoup(html, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")
        json_data = script.text
        json_data = json_data.replace("<!--", "")
        json_data = json_data.replace("-->", "")
        json_data = json_data.replace("window.__NEXT_DATA__ = ", "")
        json_data = json_data.replace(";", "")
        json_data = json.loads(json_data)
        self.json_article_data = json_data

    def get_articles_from_json(self):
        """
        This method scraps the articles from the parsed JSON data
        """

        # if The Verge site changes and this scrapper stops working than below line would be needed to be changed.
        placements = self.json_article_data["props"]["pageProps"]["hydration"]["responses"][0]["data"]["community"]["frontPage"]["placements"]
        for placement in placements:
            try :
                placeable = placement["placeable"]
                if placeable["type"] != "STORY":
                    continue
                headline = placeable["title"]
                id = placeable["uuid"]
                url = placeable["url"]
                author = placeable["author"]["fullName"]
                date = placeable["publishDate"]
                info = {
                    "id": id,
                    "URL": url,
                    "headline": headline,
                    "author": author,
                    "date": date
                }
                # print(info)
                self.data.append(info)
            except:
                continue
                
    def save_csv(self):
        """
        This method saves the scrapped articles in a CSV file "ddmmyyy_verge.csv"
        """
        filename = f"scrapped_data/{datetime.date.today().strftime('%d%m%Y')}_verge.csv"
        with open(filename, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "URL", "headline", "author", "date"])
            for item in self.data:
                writer.writerow([item["id"], item["URL"], item["headline"].replace(",", ""), item["author"], item["date"]]) 
    
    def save_sqlite(self):
        """
        This methods saves the data in sqlite database
        """
        conn = sqlite3.connect("verge_articles.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY,
            URL TEXT,
            headline TEXT,
            author TEXT,
            date TEXT
        )""")
        for item in self.data:
            try :
                c.execute("INSERT INTO articles ( id, URL, headline, author, date) VALUES (?, ?, ?, ?, ?)", (item["id"], item["URL"], item["headline"], item["author"], item["date"]))
            except sqlite3.IntegrityError:
                # if article is alredy present in the database then
                # do not update 
                continue
        conn.commit()
        conn.close()

    def run(self):
        """
        This method runs the scraper
        """
        html = self.get_html()
        self.parse_json_html(html)
        self.get_articles_from_json()
        self.save_csv()
        self.save_sqlite()

scraper = VergeScraper()
scraper.run()