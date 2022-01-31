import scrapy
import json
from dog_products.items import DogProductsItem

class ChewySpider(scrapy.Spider):
    name = 'chewy'
    allowed_domains = ['chewy.com']
    start_urls = ['https://www.chewy.com/b/dog-288']

    def parse(self, response):

        '''Main Listing Page'''
        
        blocks = response.xpath("//header/h2/a")

        for block in blocks:
            category_url = block.xpath("./@href").get()
            
            if '/b/dog-tech-smart-home-1897' in category_url:
                yield response.follow(category_url, callback=self.product_links)

    def product_links(self, response):

        '''Each Category Listing Page'''

        Categories = response.xpath("//h1[contains(@class,'product-header')]//text()").get()

        product_links = response.xpath("//div/div[@class='kib-product-card__canvas']/a/@href").getall()

        meta = {}
        meta['Categories'] = Categories

        for product_link in product_links:

            yield response.follow(product_link, callback=self.product_details, meta=meta)

            next_page_url = response.xpath("//a[contains(.,'Next')]/@href").get()

            if next_page_url:
                yield response.follow(next_page_url, callback=self.product_links)

    def product_details(self, response):

        '''Each Product Detail Page'''

        Categories = response.meta['Categories']

        ProductName = response.xpath(
            "//div[@id='product-title']/h1//text()").get()
        ProductName = ProductName.strip()

        Brand = response.xpath(
            "//div[@id='product-subtitle']//span//text()").get()

        Price = response.xpath(
            "//div[@id='pricing']//p[preceding-sibling::p[@class='title'][contains(.,'Price')]]//text()[contains(.,'$')]").get()
        Price = Price.strip()

        Images = response.xpath("//div[@id='media-selector']//a/@href").getall()
        Images = ', '.join(['https:'+''+n for n in Images if '#' not in n])    

        Description = response.xpath(
            "//article[@id='descriptions']//section[preceding-sibling::span[contains(.,'Description')]]/span/p//text()").getall()

        KeyBenefits = response.xpath(
            "//article[@id='descriptions']//ul[preceding-sibling::span[contains(.,'Key Benefits')]]//text()").getall()
        KeyBenefits = [i.strip() for i in KeyBenefits]
        KeyBenefits = ' '.join(KeyBenefits)
        
        Ingredients = response.xpath(
            "//article[@id='Nutritional-Info']//section/p[preceding-sibling::span[contains(.,'Ingredients')]][following-sibling::span[contains(.,'Caloric Content')]]//text()").getall()
        Ingredients = [i.strip() for i in Ingredients]
        Ingredients = ' '.join(Ingredients)

        item = DogProductsItem()
        item['Categories'] = Categories
        item['ProductName'] = ProductName
        item['Brand'] = Brand
        item['Price'] = Price
        item['Images'] = Images
        item['Description'] = Description
        item['KeyBenefits'] = KeyBenefits
        item['Ingredients'] = Ingredients
        item['ProductUrl'] = response.url
        yield item
      
        


