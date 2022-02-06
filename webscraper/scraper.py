# need to do this so i can use concurrent futures
import django

django.setup()
from concurrent.futures import ProcessPoolExecutor
import os
from time import sleep
from random import randint


import requests
from requests.exceptions import InvalidSchema
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    ElementClickInterceptedException,
)
from webdriver_manager.chrome import ChromeDriverManager

from .models import Webscraper


def grab_image(store, element, image_css):
    image = element.select_one(image_css)
    img_name = None
    try:
        # sainsbury's website does not have a proper alt tag for images from brand promotion search results
        if store == "sainsbury's":
            if element.find("div", class_="pt__image-wrapper"):
                image = element.select_one(image_css)
                img_name = image["alt"]
                link = image["src"]
            else:
                image = element.select_one("h3")
                img_name = image.text
                link = image.select_one("img")
                link = link["src"]
        elif store == "morrisons":
            link = "https://groceries.morrisons.com" + image["src"]
        else:
            link = image["src"]
    except KeyError as e:
        print("really should be finding the images, probably some dumb thing")
        return "N/A"

    try:
        if img_name is None:

            img_name = image["alt"]

        img_name = img_name.strip()
        img_name = img_name.replace("\r", "").replace(" ", "-").replace("/", "")
    except KeyError as e:
        print(e)
        img_name = "N/A"
    
    # one milk item from tesco has a *, i want to escape all special characters but it messes up the file search
    # pizza sizes can be written in inches as ", replace that too
    img_name = img_name.replace("*","").replace('"','')
    file_path = f"{os.getcwd()}\webscraper\static\{store}\{img_name}.jpg"
    if os.path.isfile(file_path):
        print(f"file: {img_name}.jpg already exists")
    else:
        with open(file_path, "wb") as f:
            try:
                im = requests.get(link)
                f.write(im.content)
                print("Writing: ", img_name)
            except InvalidSchema as ISE:
                print(f"trying to request image from {store} has resulted in: {ISE}")
                
    return img_name


def asda_scrape(search_term):

    option = webdriver.ChromeOptions()
    # makes chrome incognito so no cookies affect search result
    option.add_argument("incognito")
    # open chrome without displaying it to the user
    option.add_argument("--headless")
    # open website in fullscreen
    option.add_argument("--start-maximized")
    option.add_argument("log-level=3")
    # adding a user agent reduces chances of detection.
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    option.add_argument(f"user-agent={user_agent}")
    service = Service(executable_path=ChromeDriverManager().install())
    results = []
    with webdriver.Chrome(service=service, options=option) as driver:
        url = f"https://groceries.asda.com/search/{search_term}"
        driver.get(url)
        last_height = driver.execute_script("return document.body.scrollHeight")
        # scroll down the webpage, loading in images.

        sleep(1)
        while True:
            sleep(1)
            rand_y = randint(750, 1000)
            driver.execute_script(f"window.scrollBy(0, {rand_y});")
            new_height = driver.execute_script("return window.pageYOffset")
            #print(f"asda {new_height}")
            if new_height == last_height:
                break
            else:
                last_height = new_height

        html = driver.page_source
        soup = bs(html, "html.parser")
        try:
            main = soup.select_one("ul.co-product-list__main-cntr--rest-in-shelf")
        except NoSuchElementException:
            print("asda does not stock this item")
        else:

            items = main.select("li.co-item")

            for elem in items:
                img_name = grab_image("asda", elem, "img.co-item__image")

                try:
                    name = elem.select_one("a.co-product__anchor").text

                except NoSuchElementException:
                    name = "n/a"

                try:
                    url = elem.select_one("a.co-product__anchor").get("href")
                    url = f"https://groceries.asda.com{url}"
                except (NoSuchElementException, AttributeError):
                    pass

                try:
                    price = elem.select_one("strong.co-product__price").text
                    # remove formating from prices to allow them to go into database
                    price = price.replace("£", "")
                    price = price.replace("now", "")
                    price = price.strip()
                except (NoSuchElementException, AttributeError) as e:
                    price = None
                try:
                    unit_price = elem.select_one("span.co-product__price-per-uom").text
                except (NoSuchElementException, AttributeError) as e:
                    unit_price = "n/a"

                item_details = {
                    "name": name,
                    "image_name": img_name,
                    "price": price,
                    "unit_price": unit_price,
                    "url": url,
                    "store": "asda",
                }
                results.append(item_details)

    return results


def aldi_scrape(search_term):

    service = Service(executable_path=ChromeDriverManager().install())
    option = webdriver.ChromeOptions()
    # makes chrome incognito so no cookies affect search result
    option.add_argument("incognito")
    # open chrome without displaying it to the user
    option.add_argument("--headless")
    # open website in fullscreen
    option.add_argument("--start-maximized")
    option.add_argument("log-level=3")
    # adding a user agent reduces chances of detection.
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    option.add_argument(f"user-agent={user_agent}")
    results = []
    with webdriver.Chrome(service=service, options=option) as driver:
        url = f"https://groceries.aldi.co.uk/en-GB/Search?keywords={search_term}"
        driver.get(url)

        sleep(3)
        try:
            WebDriverWait(driver, timeout=7).until(
                lambda d: d.find_element(By.ID, "vueSearchResults")
            )
        except TimeoutException:
            print("Aldi does not stock this item")
            item_details = {
                "name": "N/A",
                "image_name": "N/A",
                "price": 0.00,
                "unit_price": None,
                "url": url,
                "store": "aldi",
            }
            results = [item_details]
            return results

        html = driver.page_source
        soup = bs(html, "html.parser")
        main = soup.select_one("div.products-search-results")
        # why the fuck does this still catch the stuff at the bottom
        items = main.select("div.product-tile")

        for elem in items:
            img_name = grab_image("aldi", elem, "img.img-fluid")
            try:
                name = elem.select_one("a.text-default-font").text

            except NoSuchElementException:
                name = "n/a"

            try:
                url = elem.select_one("a.text-default-font").get("href")
                url = f"https://groceries.aldi.co.uk{url}"
            except (NoSuchElementException, AttributeError):
                pass

            try:
                price = elem.select_one("span.h4").text
                price = price.replace("£", "")
                price = price.replace("now", "")
                price = price.strip()
            except (NoSuchElementException, AttributeError):
                price = None
            try:
                unit_price = elem.select_one("p.m-0").text
            except (NoSuchElementException, AttributeError):
                unit_price = "n/a"

            # remove formating from prices to allow them to go into database

            item_details = {
                "name": name,
                "image_name": img_name,
                "price": price,
                "unit_price": unit_price,
                "url": url,
                "store": "aldi",
            }
            results.append(item_details)

    return results


def morrisons_scrape(search_term):

    service = Service(executable_path=ChromeDriverManager().install())
    option = webdriver.ChromeOptions()
    option.add_argument("log-level=3")
    # makes chrome incognito so no cookies affect search result
    option.add_argument("incognito")
    # open chrome without displaying it to the user
    option.add_argument("--headless")
    # open website in fullscreen
    option.add_argument("--start-maximized")
    # adding a user agent reduces chances of detection.
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    option.add_argument(f"user-agent={user_agent}")

    with webdriver.Chrome(service=service, options=option) as driver:
        url = f"https://groceries.morrisons.com/search?entry={search_term}"
        driver.get(url)
        # driver.maximize_window()
        try:
            WebDriverWait(driver, timeout=10).until(
                lambda d: d.find_element(By.CLASS_NAME, "fops-shelf")
            )
        except TimeoutException:
            # code to stop programme from breaking when morrisons doesnt have any results
            # probably better method of doing this
            print("morrisons does not stock this item")
            item_details = {
                "name": "N/A",
                "image_name": "N/A",
                "price": 0.00,
                "unit_price": None,
                "url": url,
                "store": "morrisons",
            }
            results = [item_details]
            return results

        # click the cookies button, this find method is deprecated in selenium but find_element() does not work in python

        try:
            driver.find_element_by_id("onetrust-accept-btn-handler").click()
        except ElementNotInteractableException as e:
            print("the cookies button has already been clicked")
        except NoSuchElementException:
            print("the cookies button does not exist")
        except ElementClickInterceptedException:
            # not sure whats causing this error
            print("not sure whats causing this error")
            button = driver.find_element_by_id("onetrust-accept-btn-handler")
            driver.execute_script("arguments[0].click();", button)

        # scroll the page to load images
        for _ in range(4):
            rand_y = randint(1000, 2000)
            driver.execute_script(f"window.scrollBy(0, {rand_y});")
            # above code tells selenium to scroll the window by 1080 pixels down
            # basically puts js code into the console in the developer tool tings

            # wait to load page
            sleep(0.5)

        html = driver.page_source

        soup = bs(html, "html.parser")

        mainlist = soup.find("ul", class_="fops-shelf")

        items = mainlist.find_all("div", class_="fop-contentWrapper", limit=60)

        results = []
        for elem in items:
            img_name = grab_image("morrisons", elem, "img.fop-img")
            try:
                # morrisons puts name and quantity in a single wrapper, get just the name
                name = elem.select_one("h4.fop-title").contents[0].text
            except NoSuchElementException:
                name = "n/a"

            try:
                url = elem.select_one("a").get("href")
                url = f"https://groceries.morrisons.com{url}"
            except (NoSuchElementException, AttributeError):
                url = driver.current_url
            try:
                price = elem.select_one("span.fop-price").text
                # remove formating from prices to allow them to go into database
                price = price.replace("£", "")
                if price.find("p") != -1:
                    price = price.replace("p", "")
                    price = float(price) / 100

                else:
                    price = price.strip()
            except (NoSuchElementException, AttributeError) as e:
                price = None
            try:
                unit_price = elem.select_one("span.fop-unit-price").text
            except (NoSuchElementException, AttributeError) as e:
                unit_price = "n/a"

            item_details = {
                "name": name,
                "image_name": img_name,
                "price": price,
                "unit_price": unit_price,
                "url": url,
                "store": "morrisons",
            }
            results.append(item_details)
    return results


def sainsbury_scrape(search_term):
    service = Service(executable_path=ChromeDriverManager().install())
    option = webdriver.ChromeOptions()
    option.add_argument("log-level=3")
    # makes chrome incognito so no cookies affect search result
    option.add_argument("incognito")
    # open chrome without displaying it to the user
    option.add_argument("--headless")
    # open website in fullscreen
    option.add_argument("--start-maximized")
    # adding a user agent reduces chances of detection.
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    option.add_argument(f"user-agent={user_agent}")
    results = []
    with webdriver.Chrome(service=service, options=option) as driver:
        url = f"https://www.sainsburys.co.uk/gol-ui/SearchResults/{search_term}"

        driver.get(url)

        # for branded items it seems like sainsbury's loads the non branded html first
        # account for this, might be a better way of doing this
        sleep(5)
        # if it finds the html of the brand's then do the bs4 for it
        # otherwise a timeout exception will occur and will look
        # for the non branded html
        try:
            WebDriverWait(driver, timeout=5).until(
                lambda d: d.find_element(By.CLASS_NAME, "SRF__tileList")
            )
            # driver.find_element_by_css_selector('div.')
        except TimeoutException:

            try:
                # lower timeout needed as the time taken for above wait
                # would also allow time load this element
                WebDriverWait(driver, timeout=10).until(
                    lambda d: d.find_element(By.CLASS_NAME, "gridView")
                )
            except TimeoutException:
                print("aw feck awfuck cant find either element")
            # the beautful soup for brands
            else:
                print("found branded page")

                
                try:
                    driver.find_element_by_id("onetrust-accept-btn-handler").click()
                except ElementNotInteractableException as e:
                    print("the cookies button has already been clicked")
                html = driver.page_source
                soup = bs(html, "html.parser")
                main = soup.select_one("ul.productLister.gridView")
                items = main.select("li.gridItem")

                for elem in items:
                    img_name = grab_image("sainsbury's", elem, "img")
                    try:
                        name = elem.select_one("h3").text
                    except NoSuchElementException:
                        name = "n/a"
                    try:
                        url = elem.select_one("h3").a.get("href")
                    except (NoSuchElementException, AttributeError):
                        pass
                    try:
                        price = elem.select_one("p.pricePerUnit").text
                        if price.find("p") != -1:
                            price = price.replace("p", "")
                            price = float(price) / 100

                        else:
                            price = price.replace("£", "")
                            price = price.replace("kg", "")
                            price = price.replace("/", "")
                            price = price.strip()

                    except (NoSuchElementException, AttributeError):
                        price = None
                    try:
                        unit_price = elem.select_one("p.pricePerMeasure").text
                    except (NoSuchElementException, AttributeError) as e:
                        print(e)
                        unit_price = "n/a"

                    item_details = {
                        "name": name.strip(),
                        "image_name": img_name,
                        "price": price,
                        "unit_price": unit_price,
                        "url": url,
                        "store": "sainsbury's",
                    }
                    results.append(item_details)

            return results
        # the beautiful soup stuff for non brnads
        else:

            try:
                driver.find_element_by_id("onetrust-accept-btn-handler").click()

            except ElementNotInteractableException as e:
                print("the cookies button has already been clicked")

            print("found unbranded page")
            WebDriverWait(driver, timeout=10).until(
                lambda d: d.find_element(By.CLASS_NAME, "ln-o-grid--matrix")
            )
            html = driver.page_source
            soup = bs(html, "html.parser")
            try:

                main = soup.select_one("ul.ln-o-grid--matrix")
            except NoSuchElementException:
                print("sainsburys does not stock this item")
            else:

                items = soup.select("div.pt__content")

                for elem in items:
                    img_name = grab_image("sainsbury's", elem, "img")
                    try:
                        name = elem.select_one("h2").text
                    except NoSuchElementException:
                        name = "n/a"

                    try:
                        url = elem.select_one("a.pt__link").get("href")
                    except (NoSuchElementException, AttributeError):
                        pass
                    try:
                        price = elem.select_one("div.undefined").text
                        # some veg/ fruit have / kg attached to the price
                        price = price.replace(" / kg", "")
                        if price.find("p") != -1:
                            price = price.replace("p", "")
                            price = float(price) / 100

                        else:
                            price = price.replace("£", "")
                            price = price.replace("kg", "")
                            price = price.replace("/", "")
                            price = price.strip()
                    except (NoSuchElementException, AttributeError):
                        price = None
                    try:
                        unit_price = elem.select_one("span.pt__cost__per-unit").text
                    except (NoSuchElementException, AttributeError) as e:
                        print(e)
                        unit_price = "n/a"

                    item_details = {
                        "name": name.strip(),
                        "image_name": img_name,
                        "price": price,
                        "unit_price": unit_price,
                        "url": url,
                        "store": "sainsbury's",
                    }

                    results.append(item_details)

    return results


def tesco_scrape(search_term):
    service = Service(executable_path=ChromeDriverManager().install())
    option = webdriver.ChromeOptions()
    # makes chrome incognito so no cookies affect search result
    option.add_argument("incognito")
    # open website in fullscreen
    option.add_argument("--start-maximized")
    # open chrome without displaying it to the user
    option.add_argument("--headless")
    option.add_argument("log-level=3")
    # adding a user agent reduces chances of detection.
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    option.add_argument(f"user-agent={user_agent}")

    results = []
    with webdriver.Chrome(service=service, options=option) as driver:
        # initialise starting url
        url = f"https://www.tesco.com/groceries/en-GB/search?query={search_term}"

        driver.get(url + "&page=1&count=48")

        # explicit wait using a lambda (anonymous) function, waits until the function returns true
        # explicit wait doesnt seem to work for tesco's website
        # WebDriverWait(driver,timeout=10).until(lambda d: d.find_element(By.CLASS_NAME,'product-lists-wrapper'))

        # WebDriverWait(driver,timeout=10).until(lambda d: d.execute_script("return document.readyState") == "complete")
        sleep(3)
        # images do not load if they are out of view, bring them into view while simulating human scrolling
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            sleep(1)
            rand_y = randint(750, 1000)
            driver.execute_script(f"window.scrollBy(0, {rand_y});")
            new_height = driver.execute_script("return window.pageYOffset;")

            print(f"tesco + {new_height}")
            if new_height == last_height:
                # is_the_image_loaded_yet = driver.execute_script("return document.images[49].srcset;")
                # WebDriverWait(driver,timeout=2).until(lambda d: d.execute_script("return document.images[49].srcset;") != "")
                # this is the recommended tile that loads at the bottom of tesco's page and only loads when you scroll down there
                # make sure the last image is loaded
                try:
                    WebDriverWait(driver, timeout=2).until(
                        lambda d: d.execute_script('''
                            let page_body = document.getElementsByClassName('product-list grid')[0];
                            img_arr = page_body.getElementsByTagName('img');
                            last_img = img_arr[img_arr.length-1].src;
                            
                            return last_img;
                        '''
                        ).find(".com") != -1
                                                        )
                    break
                except Exception as e:
                    print(f"lets see what error waiting for last image to load caused: {e.args}")
                    break
                # print(is_the_image_loaded_yet)
                
            else:
                last_height = new_height
                
        
        html = driver.page_source
        soup = bs(html, "html.parser")
        # since i could not find a valid element for tesco webdriverwait, this is how i will handle empty results
        if soup.select("div.results-page.no-results"):
            print("Tesco does not have this item")
            item_details = {
                "name": "N/A",
                "image_name": "N/A",
                "price": 0.00,
                "unit_price": None,
                "url": url,
                "store": "tesco",
            }
            results = [item_details]
            return results
        main = soup.select_one("ul.product-list.grid")

        items = main.select("li.product-list--list-item")

        for elem in items:
            img_name = grab_image("tesco", elem, "img.product-image")
            try:
                name = elem.select_one("h3").text
            except NoSuchElementException:
                name = "n/a"

            try:
                url = elem.select_one("a.ui__StyledLink-sc-18aswmp-0").get("href")
                url = f"https://www.tesco.com{url}"
            except (NoSuchElementException, AttributeError):
                pass
            try:
                price = elem.select_one("span.value").text
                price = price.replace("£", "")
                price = price.strip()
            except (NoSuchElementException, AttributeError):
                price = None
            try:
                unit_price = elem.select_one("div.price-per-quantity-weight").text
            except (NoSuchElementException, AttributeError):
                unit_price = "n/a"

            # remove formating from prices to allow them to go into database

            item_details = {
                "name": name,
                "image_name": img_name,
                "price": price,
                "unit_price": unit_price,
                "url": url,
                "store": "tesco",
            }
            results.append(item_details)

    return results


def scraper(search_term):
    # get this through a form
    search_term = search_term.replace("%20", " ")

    # !r means get the official representation of the string i.e. it gives the quotation marks as well 'scraperesults' in this case
    # similar to calling repr(string), using this because this statement is looking for the table name as a string.
    # try:
    #     cursor.execute(cursor.execute(f"SELECT * FROM {table_name} WHERE search_term = {search_term!r} AND date_searched={todays_date!r}"))
    #     if cursor.fetchone() != None:
    #         print('item has been searched for today')
    #         already_searched = cursor.fetchall()
    #         for item in already_searched:
    #             print(item)
    #         do_search = False
    # # this error means i've either messed up the sql being executed or the table doesnt exist
    # except mysql.connector.ProgrammingError as sql_err:
    #     print("Table does not exist, creating Table")
    #     cursor.execute(f"CREATE TABLE {table_name} (store VARCHAR(11), item_name VARCHAR(255), price DECIMAL(6,2), unit_price VARCHAR(20), search_term VARCHAR(255), url VARCHAR(255))")

    # cursor.close()

    # tasks = [ asda_scrape, aldi_scrape, morrisons_scrape, sainsbury_scrape, tesco_scrape]
    # so i can easily disable/enable different functions
    tasks = []
    tasks += [asda_scrape]
    tasks += [aldi_scrape]
    tasks += [morrisons_scrape]
    tasks += [sainsbury_scrape]
    tasks += [tesco_scrape]
    with ProcessPoolExecutor(max_workers=5) as ex:
        # using list comprehension creates a list of the running tasks based on above tasks list
        # and then calls each function in the order of the list feeding search_term to each function
        running_tasks = [ex.submit(task, search_term) for task in tasks]

        for running_task in running_tasks:
            try:

                for count, value in enumerate(running_task.result()):
                    #print(count, value["store"], value["name"])
                    Webscraper.objects.create(
                        store=value["store"],
                        item_name=value["name"],
                        item_image=f'{value["store"]}/{value["image_name"]}',
                        item_price=value["price"],
                        unit_price=value["unit_price"],
                        item_searched=search_term.replace("%20", " "),
                        item_url=value["url"],
                    )
            except AttributeError as AE:
                print(AE)
                print("likely, item not available at store")
    print("script ended")


if __name__ == "__main__":
    webscraper()
