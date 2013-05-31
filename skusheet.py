# -*- coding: UTF-8 -*-

##
##
##

# KNOWN ISSUES:
# (1) Some countries use more than one language and have separate links/pages
# for those languages. My mapping does not take thi sinto account yet.
# For example:
# COUNTRY: CA, Canada Français
# COUNTRY: BE, Belgique
# COUNTRY: CH, Suisse
#
# (2) some prices listed in csv without trailing ".00", but page has it, for example:
# PRICE: 1300, $ 1,300.00
#
# (3) Rubles use spaces? I don't handle that right yet.
# PRICE: 1192.5, 1 192,5 руб.

#filename = 'mindspark.csv'
#filename = 'pcd.csv'
# filename = 'ask.csv'
filename = 'all.csv'

### Sample CSV ###
# Status,Seq,URL,SKU,Product Code,IsBundle,User-pc count,SKU Type,Page to Land,Site Code,Site Language,Sku Language,Country Code,Language Code,Currency Code,Price,,,org,Channel,Promotion (Flex),Segment,Keyword Category,Email Program,Affiliate Sub Channel,Period (Time),Is Upgrade,PL Code,tppc,Batch Name,sku lang priority,Valid From,Valid To,Phased Out,Source,Vendor
# Live,20134917,http://buy.norton.com/partneroffer?ctry=US&lang=EN&selSKU=21242854&tppc=B7D37237-45A3-0AB2-EF02-F87ACFBB2435&ptype=cart,21242854,NIS_2013_12MO_PC,N,1-3,Product,cart,US_SITE,English,EN,US,en,USD,41.99,,,,,,,,,,,,ECOM_MKT_48PCTOFF,B7D37237-45A3-0AB2-EF02-F87ACFBB2435,,Current,,,,,_PC DRIVERS HQ
# Live,20134918,http://buy.norton.com/partneroffer?ctry=US&lang=EN&selSKU=21242854&tppc=16EE1066-0F9C-09DC-E1E0-F80B807BA824&ptype=cart,21242854,NIS_2013_12MO_PC,N,1-3,Product,cart,US_SITE,English,EN,US,en,USD,44.99,,,,,,,,,,,,ECOM_MKT_44PCTOFF,16EE1066-0F9C-09DC-E1E0-F80B807BA824,,Current,,,,,_PC DRIVERS HQ
###

from selenium import webdriver
from selenium.common import exceptions
from datetime import datetime
import csv
import os
import re

def get_csv_reader(file_name='sample.csv'):
	csvfile = open(file_name, 'rb')
	csvreader = csv.reader(csvfile, dialect='excel')
	# skip the header row
	for row in csvreader:
		#print row
		return csvfile,csvreader

def close_csv_reader(csvfile):
	csvfile.close()

### http://buy.norton.com/partneroffer?ctry=NL&lang=NL&selSKU=21242865&tppc=A08E7460-D6FA-E082-8E91-36882647EB0A&ptype=cart
### 1) starts with "http://buy.norton.com/partneroffer?"
### 2) country
### 3) language
### 4) sku
### 5) tppc
def validate_url(url, country, language, sku, tppc):
	if not 'ctry=' in url:
		return False
	if not country.lower() in url.lower():
		return False
	if not 'lang=' in url:
		return False
	if not language.lower() in url.lower():
		return False
	if not 'selSKU=' in url:
		return False
	if not sku in url:
		return False
	if not 'tppc=' in url:
		return False
	if not tppc in url:
		return False
	if not 'http://buy.norton.com/partneroffer?' in url:
		return False
	if not 'ptype=cart' in url:
		return False
	return True


country_mapping = {
	'AE' : u'', # u'Select Country', # this is broken, should be Arab Emirates
	'AT' : u'Österreich', # Austria
	'AU' : u'Australia',
	'BE' : { 'NL': u'België', 'FR': u'Belgique', }, # Belgium
	'CA' : { 'EN': u'Canada', 'FR': u'Canada Français', },
	'CH' : { 'DE': u'Schweiz', 'FR': u'Suisse', }, # Switzerland
	'CL' : u'Chile',
	'CO' : u'Colombia',
	'DE' : u'Deutschland', # Germany
	'FR' : u'France',
	'GB' : u'United Kingdom',
	'IE' : u'Ireland',
	'IL' : u'Israel',
	'LU' : u'', #u'Sélectionnez un pays', # this looks wrong. Report to estore? do we care?
	'MX' : u'México',
	'NL' : u'Nederland',
	'NZ' : u'New Zealand',
	'PE' : u'Perú',
	'PR' : u'', # Seleccione un país # this looks wrong, there is NO 'PR' country code!
	'SE' : u'Sverige', # Sweden
	'US' : u'United States',
	'VE' : u'Venezuela',
	'ZA' : u'South Africa',
	'BR' : u'Brasil',
	'DK' : u'Danmark', # Denmark
	'ES' : u'España',
	'FI' : u'Suomi', # Finland (looks broken)
	'IT' : u'Italia',
	'PL' : u'Polska', # Poland
	'RU' : u'Россия', # Russia
	'TR' : u'Türkiye', # Turkey
	'GR' : u'Greece',
	'TH' : u'Thailand',
	'SG' : u'Singapore',
	'PT' : u'Portugal',
	'NO' : u'Norge', # Norway
	'AR' : u'Argentina',
	'ID' : u'Indonesia',
	'KH' : u'Cambodia',
	'PH' : u'Philippines',
}

def validate_country(csv_country, csv_language, page_country):
	try:
		country_map = country_mapping[csv_country.upper()]
		if type(country_map) is dict:
			country_test = country_map[csv_language.upper()].encode('utf-8')
		else:
			country_test = country_map.encode('utf-8')
		if page_country == country_test:
			return True
	except KeyError:
		return False # something not in our table, FAIL instead of crashing and examine it later
	return False

csv_product_mapping = {
	'EIS_Vx_0MO_PC'	         : 'Expert Install',
	'N360_2013_12MO_PC'      : 'N360',
	'NAV_2013_12MO_PC'       : 'NAV',
	'NAV_2013_24MO_PC'       : 'NAV',
	'NIS_2013_12MO_PC'       : 'NIS',
	'NOBU-25GB_V2.0_12MO_CC' : 'NOBU',
	'NU_V14.0_0MO_PC'        : 'Norton Utilities',
	'PCJ_Vx_0MO_PC'          : 'PC Jumpstart',
	'PCP_Vx_0MO_PC'          : 'PC Powerboost',
	'PCT_Vx_0MO_PC'          : 'PC Tune-Up',
	'SVR_Vx_0MO_PC'          : 'Spyware and Virus Removal',
}

page_product_mapping = {
	'Expert Installation'         : 'Expert Install',
	'Instalação especializada'    : 'Expert Install', # Portuguese
	'PC-Installationshilfe'       : 'Expert Install', # Austrian, and others
	'Installatie door experts'    : 'Expert Install', # Belgian
	'Service Installation'        : 'Expert Install', # Switzerland and others?

	'Norton 360™'                 : 'N360',
	'Norton AntiVirus™'           : 'NAV', # nice inconsistency!
	'Norton™ AntiVirus'           : 'NAV', # nice! inconsistency
	'Norton™ Internet Security'   : 'NIS',

	'Norton™ Online Backup 25GB'    : 'NOBU', # nice inconsistency!
	'Norton™ Online Backup 25 GB'   : 'NOBU', # nice inconsistency !
	'Norton™ Online Backup (25 GB)' : 'NOBU', # nice inconsistency (!)
	'Norton™ Online Backup 25 Go'   : 'NOBU', # French
	'Norton™ Online Backup 25 Gt'   : 'NOBU', # Finland
	'Norton™ Online Backup 25 ГБ'   : 'NOBU', # Russia

	''                    : 'Norton Utilities', # all these pages are broken?

	'PC Jump Start'                        : 'PC Jumpstart',
	'Service Installation et Optimisation' : 'PC Jumpstart', # French
	'PC-Starthilfe'                        : 'PC Jumpstart', # German
	'Pc-opstarthulp'                       : 'PC Jumpstart', # Dutch

	'PC Power Boost'      : 'PC Powerboost',

	'PC Tune-Up'          : 'PC Tune-Up',
	'PC TuneUp'           : 'PC Tune-Up',
	'Pc-afstelling'       : 'PC Tune-Up', # Dutch
	'PC-Optimierung'      : 'PC Tune-Up', # German
	'Optimisation du PC'  : 'PC Tune-Up', # French
	'Datoroptimering'     : 'PC Tune-Up', # Swedish
	'Optimização do PC'   : 'PC Tune-Up', # Portuguese

	'NortonLive™ Spyware and Virus Removal'                   : 'Spyware and Virus Removal',
	'Rimozione di spyware e virus NortonLive™'                : 'Spyware and Virus Removal', # Italian
	'Eliminación de virus y spyware de NortonLive™'           : 'Spyware and Virus Removal', # Spanish
	'NortonLive™ Remoção de Vírus e Spyware'                  : 'Spyware and Virus Removal', # Portuguese
	'Service NortonLive™ de suppression de spywares et virus' : 'Spyware and Virus Removal', # French
	'NortonLive™ Spyware- und Virenentfernung'                : 'Spyware and Virus Removal', # German
	'Spyware- en virusverwijdering van NortonLive™'           : 'Spyware and Virus Removal', # Dutch
	'NortonLive™ spyware- og virusfjernelse'                  : 'Spyware and Virus Removal', # Danish
	'NortonLive™ spionprogram- og virusfjerning'              : 'Spyware and Virus Removal', # Norsk?
}

def validate_product(csv_product, page_product, country):
	try:
		if csv_product_mapping[csv_product] \
			and page_product_mapping[page_product] \
			and csv_product_mapping[csv_product] == page_product_mapping[page_product]:
			return True
	except KeyError:
		return False # something not in our table, FAIL instead of crashing and examine it later
	return False

def validate_sku(sku, page_sku_href):
	return sku in page_sku_href

def validate_price(price, page_price, country):
	comma_price = price.replace('.', ',')
	return price in page_price or comma_price in page_price

currency_mapping = {
	'ARS'	: '$'    , # Argentina Peso
	'AUD'	: '$'    , # Australia Dollar
	'BRL'	: 'R$'   , # Brazil Real
	'CAD'	: '$'    , # Canadian Dollars
	'CHF'	: 'SFr'  , # "SFr." Switzerland Franc
	'CLP'	: 'Ch$'  , # Chile Peso
	'COP'	: '$'    , # Columbian Peso
	'DKK'	: 'kr'   , # Denmark Krone
	'EUR'	: '€'    , # Euros
	'GBP'	: '£'    , # United Kingdom Pound
	'MXN'	: '$'    , # Mexico Peso
	'NOK'	: 'kr'   , # Norway Krone
	'NZD'	: '$'    , # New Zealand Dollar
	'PLN'	: 'zł'   , # Poland Zloty (at the END like "116,99 zl")
	'RUB'	: 'руб'  , # "руб." Russia Ruble (no commas, and at end, with period! like "1 881 ???.")
	'SEK'	: 'kr'   , # Sweden Krona
	'SGD'	: '$'    , # Singapore Dollar
	'TRY'	: 'TL'   , # Turkey Lira (at end like "79,99 TL") 
	'USD'	: '$'    , # US Dollars
	'ZAR'	: 'R'    , # South Africa Rand (R 191.99)
}

def validate_currency(currency, page_price):
	# find the currency symbol. Note: sometimes it is on the end and other times at the front (grrr!)
	# try stripping out whitespace, commas, periods, numbers - and see what's left
	page_currency = re.sub(r'[\s\d\,\.]+', '', page_price)
	#print '### after strip found "%s"' % page_currency
	try:
		if currency_mapping[currency] == page_currency:
			return True
	except KeyError:
		return False
	return False


def process_row(row, passed, failed):

	###
	### early exit?
	###
	if not row[0] == 'Live':
		return passed,failed

	###
	### scrape the csv row
	###
	url      = row[2]
	sku      = row[3]
	product  = row[4]
	country  = row[12]
	language = row[13]
	currency = row[14]
	price    = row[15]
	tppc     = row[28]
	partner  = row[35]
	print "\n", partner, sku, product, country, language, currency, price, tppc
	#print url

	###
	### Make sure the URL we are about to fetch has the params that match other fields in the spreadsheet
	###
	### http://buy.norton.com/partneroffer?ctry=NL&lang=NL&selSKU=21242865&tppc=A08E7460-D6FA-E082-8E91-36882647EB0A&ptype=cart
	### 1) starts with "http://buy.norton.com/partneroffer?"
	### 2) country
	### 3) language
	### 4) sku
	### 5) tppc

	if validate_url(url, country, language, sku, tppc):
		passed += 1
		print "PASS: URL: %s" % url
	else:
		failed += 1
		print "FAIL: URL: %s" % url

	###
	### get the page and scrape the data
	###
	driver = webdriver.Firefox()
	driver.get(url)
	driver.implicitly_wait(7)

	page_url = driver.current_url
	#print page_url

	page_country  = 'NOT FOUND'
	page_product  = 'NOT FOUND'
	page_sku_href = 'NOT FOUND'
	page_price    = 'NOT FOUND'

	try:
		page_country = driver.find_element_by_class_name('localizationCtryWithOutImage').text
		page_country = page_country.encode('utf-8')
		#print 'Page Country: "%s"' % page_country

		page_product = driver.find_element_by_css_selector("span.spanProdTitle > a > span").text
		page_product = page_product.encode('utf-8')
		#print 'Page Product: "%s"' % page_product

		page_sku_href = driver.find_element_by_css_selector("span.spanProdTitle > a").get_attribute("href")
		#print page_sku_href

		page_price = driver.find_element_by_class_name('price').text
		page_price = page_price.encode('utf-8')
		#print page_price
	except exceptions.NoSuchElementException:
		# let the validation code fail on default empty strings that might still exist
		print "ERROR: finding an element on this page did not work!"
		pass

	if (False):
		image_filename = os.getcwd() + "\\" + partner + '-' + sku + '-' + language + '-' + country + '-' + price + '.png'
		#print "Saving screenshot to ", image_filename
		driver.get_screenshot_as_file(image_filename)


	driver.close()

	###
	### compare everything for validity, massaging as necessary
	###
	if validate_country(country, language, page_country):
		passed += 1
		print "PASS: COUNTRY: %s, %s" % (country, page_country)
	else:
		failed += 1
		print "FAIL: COUNTRY: %s, %s" % (country, page_country)

	if validate_product(product, page_product, country):
		passed += 1
		print "PASS: PRODUCT: %s, %s" % (product, page_product)
	else:
		failed += 1
		print "FAIL: PRODUCT: %s, %s" % (product, page_product)

	if validate_sku(sku, page_sku_href):
		passed += 1
		print "PASS: SKU: %s" % sku
	else:
		failed += 1
		print "FAIL: SKU: %s not in %s" % (sku, page_sku_href)

	if validate_price(price, page_price, country):
		passed += 1
		print "PASS: PRICE: %s, %s" % (price, page_price)
	else:
		failed += 1
		print "FAIL: PRICE: %s, %s" % (price, page_price)

	if validate_currency(currency, page_price):
		passed += 1
		print "PASS: CURRENCY: %s, %s" % (currency, page_price)
	else:
		failed += 1
		print "FAIL: CURRENCY: %s, %s" % (currency, page_price)

	return passed,failed


def validate_skus():
	count = 0
	passed = 0
	failed = 0

	start_time = datetime.now()
	print 'STARTED AT: %s' % start_time

	csvfile,csvreader = get_csv_reader(filename)
	for row in csvreader:
		if not row: break
		count += 1
		passed,failed = process_row(row, passed, failed)
	close_csv_reader(csvfile)

	print '\nprocessed %d records (%d tests passed; %d tests failed)' % (count, passed, failed)
	end_time = datetime.now()
	print 'ENDED AT: %s' % end_time
	print 'DURATION: %s' % (end_time - start_time)


if __name__ == '__main__':
	validate_skus()