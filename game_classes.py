# game_classes.py

import urllib
import re
import lxml.etree as ET
import urllib2

class game:
  def __init__(self, name, app_ID, wiki_found=False, wiki_str="None", rd=1900, dev="Unlisted", pub="Unlisted", filled = False):
    self.name =  name
    self.app_ID = app_ID 
    self.wiki_string = wiki_str
    if (wiki_str == ""):
      wiki_string = "None"
    if (wiki_found == "False"): 
      self.wiki_link_found = False
    elif (wiki_found == "True"):
      self.wiki_link_found = True
    else:
      self.wiki_link_found = wiki_found

    if (filled == "False"): 
      self.data_filled = False
    elif (filled == "True"):
      self.data_filled = True
    else:
      self.data_filled = filled

    self.release_date = rd
    self.developer = dev
    self.publisher = pub
  def __str__(self):
    return "<name: {0}>  <app_ID: {1}> <wiki_found: {2}> <wiki_link: {3}>\n" \
              .format(self.name, self.app_ID, self.wiki_link_found, self.wiki_string)
  def __repr__(self):
    return str(self)
  def print_info(self):
    print("name: {0}   app_ID: {1}  wiki_found: {2}  wiki_link: {3}" \
              .format(self.name, self.app_ID, self.wiki_link_found, self.wiki_string))
  def full_info(self):
    print("name: {0}   app_ID: {1}  wiki_found: {2}  wiki_link: {3} dev: {4} pub:{5} rd:{6}".format(self.name, self.app_ID, self.wiki_link_found, self.wiki_string, self.developer, self.publisher, self.release_date))

  def get_data_from_steam(self):
    if(self.data_filled == True):
      print("Data already filled in, skipping {0}".format(self.name))
    else:
      #dev_reg = re.compile('Developer:<.*?><.*?>(.*?)<.*?>',re.DOTALL|re.IGNORECASE)
      dev_reg = re.compile('Developer:</b>\s*<a.*?>(.*?)</a>',re.DOTALL|re.IGNORECASE)
      pub_reg = re.compile('Publisher:</b>\s*<a.*?>(.*?)<.a>',re.DOTALL|re.IGNORECASE)
      rd_reg = re.compile('Release Date:<.*?>(.*?)<.*?>',re.DOTALL|re.IGNORECASE)
      year_reg = re.compile('([0-9]{4})', re.DOTALL)

      base_steam_url = 'http://store.steampowered.com/app/'
      steam_url = "{0}{1}".format(base_steam_url, self.app_ID)

      print("tring to scrape data for: {0} , URL: {1}".format(self.name, steam_url))
      headers = {'User-Agent' : 'Mozilla/5.0'}
      html_app_data = ""
      req = urllib2.Request(steam_url, None, headers)
      data = []
      redirect = False
      try:
        data = urllib2.urlopen(req)
        html_app_data = data.read()
        if (data.geturl() != steam_url):
          redirect =True
      except urllib2.URLError as e:
        print("URL Error, reason: {0}, code: {1}".format(e.reason, e.code))

      self.data_filled = True
      if (dev_reg.search(html_app_data)):
        dev = dev_reg.findall(html_app_data)[0]
        dev = dev.decode('unicode_escape').encode('ascii','ignore') 
        self.developer = dev
      else:
        self.data_filled = False
          
      if (pub_reg.search(html_app_data)):
        pub = pub_reg.findall(html_app_data)[0]
        pub = pub.decode('unicode_escape').encode('ascii','ignore')  
        self.publisher = pub
      else:
        self.data_filled = False

      if (rd_reg.search(html_app_data)):
        rd =rd_reg.findall(html_app_data)[0] 
        self.release_date = year_reg.findall(rd)[0]
      else:
        self.data_filled = False
