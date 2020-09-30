from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from time import sleep, time
from bs4 import BeautifulSoup
from pandas import DataFrame, read_excel
import os


NUM = 0


def init_chrome():
    options = webdriver.ChromeOptions()
    options.add_argument('--proxy-server=socks5://154.21.232.12:11077')
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-port=8000")
    options.add_argument("user-data-dir=profile1")
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options,
                              executable_path=rf'chromedriver_win32\chromedriver.exe')
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
      """
    })
    driver.set_window_size(1200, 8000)
    return driver


def search_past_24_hours(input_kw):
    global NUM
    driver.get("https://google.com")
    search_box = driver.find_element_by_xpath('//*[@id="tsf"]/div[2]/div[1]/div[1]/div/div[2]/input')
    search_box.send_keys(f"{input_kw}")
    search_box.send_keys(Keys.RETURN)
    driver.find_element_by_xpath('//*[@id="hdtb-tls"]').click()  # tools btn
    sleep(0.3)
    driver.find_element_by_xpath('//*[@id="hdtbMenus"]/div/div[2]/div').click()  # any time
    sleep(0.3)
    driver.find_element_by_xpath('//*[@id="qdr_d"]/a').click()  # past 24 hours
    sleep(0.3)
    # 2nd page (if there is one)
    check_if_end_of_page() # I know how to build my own links now, might not be needed


def check_if_end_of_page():
    try:
        driver.find_element_by_xpath('//*[@id="xjs"]/div/table/tbody/tr/td[3]/a').click()
    except NoSuchElementException:
        pass


def selenium_scrape_return_xlsx(input_kw):
    global NUM
    driver.get(f"https://www.google.com/search?q={input_kw}&tbs=qdr:d&start={NUM}0")
    end_text = "In order to show you the most relevant results, " \
               "we have omitted some entries very similar to the"
    no_match_text = "It looks like there aren't any great matches for your search"
    output = []
    while True:  # build results for one keyword, go through all pages.
        print(f"On Page Number: {(NUM + 1)}")
        # print(f"https://www.google.com/search?q={input_kw}&tbs=qdr:d&start={NUM}0")
        driver.get(f"https://www.google.com/search?q={input_kw}&tbs=qdr:d&start={NUM}0")
        take_screenshot(input_kw)
        # parsing logic, to do: clean.
        html = driver.page_source
        html = BeautifulSoup(html, 'html.parser')
        results = html.find_all("div", attrs={"class": "rc"})
        for result in results:
            title = result.div.a.h3.text
            link = result.div.a['href']
            # dealing with different types of results
            try:  # regular
                time_posted = result.find("span", attrs={"class": "f"}).text.split()[0:2]
            except AttributeError as e:  # video
                # print("Failed at first, likely video.")
                # print(title, link, e)
                # print(result)
                try:  # jesus :'(
                    time_posted = result.select("span.st")[-1].next_sibling.text.split()[0:2]
                except AttributeError:
                    # print("Failed at second")
                    # print(title, link, e)
                    continue
                except TypeError:
                    # print("Failed at second")
                    # print(title, link, e)
                    continue
            time_posted = " ".join(time_posted)
            output.append(
                {
                    "Title": title,
                    "Link": link,
                    "Time": time_posted
                }
            )
        NUM += 1
        if NUM >= 25:  # hard stop at page 25
            break
        if end_text in html.text:
            print("End Type Text Found, Ending Run")
            break
        if no_match_text in html.text:
            print("Match Type Text Found, Ending Run")
            break
    print(f"Creating Output .xlsx for Page {NUM + 1} of {input_kw}")
    DataFrame(output).to_excel(f"output/{input_kw}.xlsx")


def requests_input_keyword():
    # read input from .xlsx
    data_frame = read_excel("input.xlsx", sheet_name="Sheet1", engine="openpyxl")
    input_kws = data_frame['Keywords'].tolist()
    return input_kws


def prep_file_output(input_kw):
    # take screenshots option checked.
    if not os.path.exists(f'images/{input_kw}/'):
        os.makedirs(f'images/{input_kw}/')
    if not os.path.exists(f'output/'):
        os.makedirs(f'output/')


def take_screenshot(input_kw):
    output_file = f"images/{input_kw}/{NUM + 1}.png"



# t1 = time()
# driver = init_chrome()
# input_kws = requests_input_keyword()
# for input_kw in input_kws:
#     print("-----------------------------------------------------------------------------")
#     print(f"Scraping {input_kw}")
#     prep_file_output(input_kw)
#     selenium_scrape_return_xlsx(input_kw)
#     t2 = time()
#     NUM = 0
#     print(f"Took {t2 - t1} seconds.")
#     print("-----------------------------------------------------------------------------")
# driver.close()
# driver.quit()

#todo: better screenshots of whole page.
#todo: visit each link we scraped.
#todo: use multiprocessing to scrape all result pages + website pages.