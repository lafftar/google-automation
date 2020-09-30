import requests
import bs4

URL = "https://www.scribblehub.com/read/14190-the-novels-redemption/chapter/14194/"

chapter = requests.get(URL)
chphtml = bs4.BeautifulSoup(chapter.content, 'html.parser')

#Finds element for the read button then finds the hyperlink url.
nextchpurl = chphtml.find(class_='btn-wi btn-next')
print("\n", nextchpurl , "\n")
nextchpurl = nextchpurl['href']
print(nextchpurl)
exit()