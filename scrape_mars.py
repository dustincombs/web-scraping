from splinter import Browser
from bs4 import BeautifulSoup
import requests
import pandas as pd
import pymongo

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=True)

def get_soup(url):
    # use chromedriver to retrieve html
    browser = init_browser()
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    browser.quit()
    # return beautiful soup object
    return soup

def get_headline():
	# get headline and teaser
	print('getting headline')
	url = 'https://mars.nasa.gov/news/'
	soup = get_soup(url)
	# get most recent article
	li = soup.find('li', class_="slide")
	headline = li.find('h3').text
	teaser = li.find('div',class_="article_teaser_body").text
	return headline, teaser


def get_feature_pic():
	# get pic of the day
	print('getting picture of the day')
	url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars#submit'
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	image = soup.find('div', class_="img")
	# get path to image
	source = image.find('img')['src']
	base = 'https://www.jpl.nasa.gov/spaceimages/images/largesize/'
	# get file name
	file_name = source.split('/')[-1]
	# construct path to full size image
	featured_image_url = base + file_name.split('-')[0] + '_hires.jpg'
	return featured_image_url

def get_table():
	# get table
	print('getting table')
	tables = pd.read_html('https://space-facts.com/mars/')
	df = tables[0]
	df.columns = ['Object','Value']
	html_table = df.to_html(index=False)
	html_table = html_table.replace('\n', '')
	return html_table

def get_hemi_data():
	# get hemisphere images
	print('getting hemisphere images')
	url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
	soup = get_soup(url)
	anchors = soup.find_all('a',class_='itemLink product-item')
	hemi_list = []

	# iterate over anchor tags
	for a in anchors:
		# if tag contains h3 get image and text
		if a.h3:
		    base_url = 'https://astrogeology.usgs.gov'
		    page_url = base_url + a['href']
		    hemi_text = a.find('h3').text
		    print(f'getting data for {hemi_text}')

		    soup = get_soup(page_url)
		    dl = soup.find('div',class_='downloads')
		    link = dl.find('li')
		    hemi_img_url = link.find('a')['href']
		    hemi_list.append({'name':hemi_text,'url':hemi_img_url})
	return hemi_list

def scrape():
	# get data and create dict
	headline, teaser = get_headline()
	mars_dict = {'mars_news_headline':headline,'mars_news_teaser':teaser}

	featured_image_url = get_feature_pic()
	mars_dict.update({'mars_image_url':featured_image_url})

	html_table = get_table()
	mars_dict.update({'mars_table_data':html_table})

	hemi_list = get_hemi_data()
	mars_dict.update({'mars_hemi_data':hemi_list})

	# connect to mongo
	client = pymongo.MongoClient('mongodb://localhost:27017')
	db = client.mars_db
	# drop the table to remove duplicates
	db.mars.drop()
	# insert record
	db.mars.insert_one(mars_dict)


	return(mars_dict)