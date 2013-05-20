##
##
##

from selenium import webdriver
import pprint

record = {
	# 'url':'http://buy.norton.com/partneroffer?ctry=US&lang=EN&selSKU=21242854&tppc=B7D37237-45A3-0AB2-EF02-F87ACFBB2435&ptype=cart',
	'url':'http://buy.norton.com/partneroffer?ctry=IT&lang=IT&selSKU=21242915&tppc=A08E7460-D6FA-E082-8E91-36882647EB0A&ptype=cart',
	'sku':'21242854',
	'language':'en',
	'counry': 'US',
	'currency':'USD',
	'price':'41.99',
	'vendor':'_PC DRIVERS HQ',
}

def play():
	driver = webdriver.Firefox()
	driver.get(record['url'])
	driver.implicitly_wait(7)

	new_url = driver.current_url
	print(new_url)

	country = driver.find_element_by_class_name('localizationCtryWithOutImage').text
	print(country.encode('utf-8'))

	# product = driver.find_element_by_class_name('spanProdTitle').text
	# print(product.encode('utf-8'))

	product = driver.find_element_by_css_selector("span.spanProdTitle > a > span").text
	print(product.encode('utf-8'))

	hasSKU = '21242915' in driver.find_element_by_css_selector("span.spanProdTitle > a").get_attribute("href")
	print(hasSKU)

	price = driver.find_element_by_class_name('price').text
	print(price.encode('utf-8'))

	driver.close()


if __name__ == '__main__':
	play()