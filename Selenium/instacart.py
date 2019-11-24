from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv

BASE_URL = "https://www.instacart.com"
ZIPCODE = "02452"
STORE = "Wegmans"
CATEGORY = "Produce"

try:
    driver = webdriver.Firefox()
    time.sleep(13)
    driver.get(BASE_URL)

    #Locate login button
    loginbutton = driver.find_element(By.XPATH, "//a/span[contains(text(), 'Log in')]/parent::a")
    loginbutton.send_keys(Keys.RETURN)

    #Enter values into email and password textfields
    email = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//input[@type='email']")))
    email.send_keys("suman4283@gmail.com")
    passwd = driver.find_element(By.XPATH, "//input[@type='password']")
    passwd.send_keys("sageof6paths")
    print("Entered login info")

    #Submit and transfer to profile
    submit = driver.find_element(By.XPATH, "//button[@type = 'submit']")
    submit.send_keys(Keys.RETURN)
    print("Pressed submit, waiting for page to load, sleep for 30s")

    #Click profile link and wait for render
    producelink = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.LINK_TEXT, CATEGORY)))
    producelink.send_keys(Keys.RETURN)
    time.sleep(20)

    #Loop over links in produce unordered list
    producepage = BeautifulSoup(driver.page_source, "html.parser")
    li_links = producepage.find_all("li", attrs={"data-testid":"navigate-web"})
    relative_links = [link.a['href'] for link in li_links]
    aisle_links = [driver.current_url+href[href.rindex("/", 0, -8):] for href in relative_links]
    csvfile = open("instacart_data.csv", "w")
    print("Here are the aisle_links", aisle_links)
    print("Writing header row")
    writer = csv.writer(csvfile)
    writer.writerow(["Product_ID", "Product_Name", "Product_Category", "Price", "Image_URL", "Details", "Ingredients", "Nutrition_Dict", "Zip_Code", "Store", "Category"])
    for link in aisle_links:
        print("In aisle page")
        driver.get(link)
        time.sleep(15)
        aisle_page = BeautifulSoup(driver.page_source, "html.parser")
        items = aisle_page.find_all("li", attrs = {"class": "item-card"})
        print("Here are raw li links", items)
        itempagelinks = [BASE_URL+link.a['href'] for link in items]
        print("These are formatted item page links", itempagelinks)
        product_category = driver.title.split("-")[-1]
        for itemlink in itempagelinks:
            nutrition_dict = {}
            driver.get(itemlink)
            time.sleep(13)
            try:
                itemsource = BeautifulSoup(driver.page_source, "html.parser")
                #Data collection
                title = itemsource.find("h2").string
                price = driver.find_element(By.XPATH, "//span[contains(text(), 'price')]//following-sibling::span").text
                image_url = itemsource.find("div", {"class": "ic-image-zoomer"}).img['src']
                product_id = driver.current_url.split("_")[-1]
                h3_tags = itemsource.find_all("h3")
                stronglinks = itemsource.find_all("strong")
                details = "NA"
                ingredients = "NA"
                #Find details and ingredients
                for tag in h3_tags:
                    if tag.string == "Details":
                        details = tag.next_sibling.string
                    elif tag.string == "Ingredients":
                        ingredients = tag.next_sibling.string
                #Find nutrition dict
                if stronglinks:
                    for strong in stronglinks:
                        nutrition_dict[strong.text] = strong.next_sibling
                else:
                    nutrition_dict = "NA"
                writer.writerow([product_id, title, product_category, price, image_url, details, ingredients, nutrition_dict, ZIPCODE, STORE, CATEGORY])
            except Exception as e:
                continue


except Exception as e:
    print(type(e))
    print(e)

finally:
    csvfile.close()
    driver.close()