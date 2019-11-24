# -*- coding: utf-8 -*-
import scrapy
from scrapy import FormRequest
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from scrapy.http import HtmlResponse


def authentication_failed(response):
    return "Invalid" in response.text

class InstadataSpider(scrapy.Spider):
    name = 'instadata'
    allowed_domains = ['instacart.com']
    start_urls = ['https://instacart.com/']

    def parse(self, response):
        try:
            driver = webdriver.Firefox()
            driver.get("https://instacart.com")
            loginbutton = driver.find_element(By.XPATH, "//a/span[contains(text(), 'Log in')]/parent::a")
            loginbutton.send_keys(Keys.RETURN)
            self.logger.info("Made it till here after identifying the login button")
            self.logger.info("Type of page_source: ", type(driver.page_source))
            return FormRequest.from_response(
                Response(
                    url = self.start_requests[0],
                    body = driver.page_source
                ),
                formdata = {"nextgen-authenticate.all.log_in_email": "suman4283@gmail.com", "nextgen-authenticate.all.log_in_password": "sageof6paths"},
                callback = self.after_login
            )
        except Exception as e:
            self.logger.error(type(e))
            self.logger.error(e)
        finally:
            driver.close()
    
    def after_login(self, response):
        if authentication_failed(response):
            self.logger.error("Login failed")
            return
        self.logger.info("Made it to products page successfully!")

        a_links = response.xpath("//a").extract()
        yield {"a_links": a_links}