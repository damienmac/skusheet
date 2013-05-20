# -*- coding: UTF-8 -*-

##
##
##

### Sample CSV ###
# Status,Seq,URL,SKU,Product Code,IsBundle,User-pc count,SKU Type,Page to Land,Site Code,Site Language,Sku Language,Country Code,Language Code,Currency Code,Price,,,org,Channel,Promotion (Flex),Segment,Keyword Category,Email Program,Affiliate Sub Channel,Period (Time),Is Upgrade,PL Code,tppc,Batch Name,sku lang priority,Valid From,Valid To,Phased Out,Source,Vendor
# Live,20134917,http://buy.norton.com/partneroffer?ctry=US&lang=EN&selSKU=21242854&tppc=B7D37237-45A3-0AB2-EF02-F87ACFBB2435&ptype=cart,21242854,NIS_2013_12MO_PC,N,1-3,Product,cart,US_SITE,English,EN,US,en,USD,41.99,,,,,,,,,,,,ECOM_MKT_48PCTOFF,B7D37237-45A3-0AB2-EF02-F87ACFBB2435,,Current,,,,,_PC DRIVERS HQ
# Live,20134918,http://buy.norton.com/partneroffer?ctry=US&lang=EN&selSKU=21242854&tppc=16EE1066-0F9C-09DC-E1E0-F80B807BA824&ptype=cart,21242854,NIS_2013_12MO_PC,N,1-3,Product,cart,US_SITE,English,EN,US,en,USD,44.99,,,,,,,,,,,,ECOM_MKT_44PCTOFF,16EE1066-0F9C-09DC-E1E0-F80B807BA824,,Current,,,,,_PC DRIVERS HQ
###

from selenium import webdriver
import csv
import date

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

def get_csv_reader(file_name='sample.csv'):
		csvfile = open(file_name, 'rb')
		csvreader = csv.reader(csvfile, dialect='excel')
		# skip the header row
		for row in csvreader:
			#print row
			return csvfile,csvreader

def close_csv_reader(csvfile):
	csvfile.close()

country_mapping = {
	'US' : u'United States',
	'CA' : u'Canada',
	'BE' : u'België',
	'NL' : u'Nederland',
	'FR' : u'France',
	'LU' : u'Sélectionnez un pays', # this looks wrong. Report to estore? do we care?
	'IT' : u'Italia',
	'ES' : u'España',
	'AT' : u'Österreich',
	'DE' : u'Deutschland',
	'BR' : u'Brasil',
	'GB' : u'United Kingdom',
	'AU' : u'Australia',
}
def validate_country(csv_country, page_country):
	if page_country == country_mapping[csv_country]:
		return True
	return False

def do_work(row):

	###
	### scrape the csv row
	###
	url      = row[2]
	sku      = row[3]
	prodcode = row[4]
	country  = row[12]
	language = row[13]
	currency = row[14]
	price    = row[15]
	tppc     = row[28]
	print sku, prodcode, country, language, currency, price, tppc

	###
	### get the page and scrape the data
	###
	driver = webdriver.Firefox()
	driver.get(url)
	driver.implicitly_wait(7)

	page_url = driver.current_url
	print(page_url)

	page_country = driver.find_element_by_class_name('localizationCtryWithOutImage').text
	print(page_country.encode('utf-8'))

	page_product = driver.find_element_by_css_selector("span.spanProdTitle > a > span").text
	print(page_product.encode('utf-8'))

	page_sku_href = driver.find_element_by_css_selector("span.spanProdTitle > a").get_attribute("href")
	print(page_sku_href)

	page_price = driver.find_element_by_class_name('price').text
	print(page_price.encode('utf-8'))

	# TODO: DM: take a screenshot

	driver.close()

	###
	### compare everything for validity, massaging as necessary
	###
	if (validate_country(country, page_country)):
		print "PASS: COUNTRY: %s, %s" % (country, page_country.encode('utf-8'))
	else:
		print "FAIL: COUNTRY: %s, %s" % (country, page_country.encode('utf-8'))


def play2():
	count = 0
	print 'STARTED AT:', date.datetime.now()
	csvfile,csvreader = get_csv_reader()
	for row in csvreader:
		count += 1
		#print row
		do_work(row)
	print 'processed %d records' % count
	close_csv_reader(csvfile)

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
	#play()
	play2()