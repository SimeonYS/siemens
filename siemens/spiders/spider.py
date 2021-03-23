import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import SiemensItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class SiemensSpider(scrapy.Spider):
	name = 'siemens'
	start_urls = ['https://press.siemens.com/fi/fi/hakutulokset']

	def parse(self, response):
		post_links = response.xpath('//div[@class="views-field views-field-title"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//li[@class="pager__item"]/a[@class="button js-search__load-more-results"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//span[@class="Date"]/text()').get()
		title = response.xpath('//h1//text()').get()
		content = response.xpath('//div[@class="Summary hidden-xs"]/b/text()').getall() + response.xpath('//div[contains(@class,"col-md-8")]//text()').getall()[:-3]
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=SiemensItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
