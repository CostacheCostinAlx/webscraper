from curl_cffi import requests
from bs4 import BeautifulSoup
import lxml
import re 

url = "https://altex.ro/robots.txt"

# headers similar to browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
}

# curl_cffi requests impersonates a browser and handles anti-bot measures
response = requests.get(url, headers=headers, impersonate="chrome110")

print(response.status_code)
# print(response.text)

sitemaps = []
for line in response.text.splitlines():
    if line.startswith("Sitemap:"):
        sitemap_url = line.split(":", 1)[1].strip()
        sitemaps.append(sitemap_url)

# print(sitemaps)

sitemap = sitemaps[0] if sitemaps else None
sitemap_urls = []
if sitemap:
    response = requests.get(sitemap, headers=headers, impersonate="chrome110")
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "lxml")
        for loc in soup.find_all("loc"):
            sitemap_urls.append(loc.text)

print(sitemap_urls)


# collect data from the sitemap URLs
data = []
for url in sitemap_urls:
    response = requests.get(url, headers=headers, impersonate="chrome110")
    print("Fetching URL:", url, "Status Code:", response.status_code)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "lxml")
        # Extract relevant data from the page
        title = soup.find("title").text if soup.find("title") else "No title"
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag["content"] if description_tag else "No description"
        data.append({"url": url, "title": title, "description": description})
        # write to file 
        with open("data/altex_data.jsonl", "a", encoding="utf-8") as f:
            f.write(f'{{"url": "{url}", "title": "{title}", "description": "{description}"}}\n')