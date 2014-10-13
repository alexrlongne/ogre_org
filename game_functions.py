
import urllib2
import re
from game_classes import *
import lxml.etree as ET


###############################################################################
def get_link_found(game):
  return game.wiki_link_found
###############################################################################

###############################################################################
def sort_found_link(game_list):
  game_list.sort(key=get_link_found, reverse=True)
  return game_list
###############################################################################
  

###############################################################################
def request_url(url, headers):
  html_app_data = ""
  req = urllib2.Request(url, None, headers)
  data = []
  redirect = False
  try:
    data = urllib2.urlopen(req)
    html_app_data = data.readlines()
    if (data.geturl() != url):
      redirect =True
  except urllib2.URLError as e:
    print("URL Error, reason: {0}, code: {1}".format(e.reason, e.code))

  return html_app_data, redirect
###############################################################################


###############################################################################
def get_wiki_string(name):
  # replace name with underscored version of itself
  wiki_string = ""
  name_vec = name.split()
  for i,word in enumerate(name_vec):
    if (i==0):
      wiki_string = word
    else:
      wiki_string = "{0}_{1}".format(wiki_string, word)

  #replace apostrophes with %27, as wikipedia does
  name_vec = wiki_string.split()
  for i,word in enumerate(name_vec):
    if (i==0):
      wiki_string = word
    else:
      wiki_string = "{0}%27{1}".format(wiki_string, word)
  
  return wiki_string 
###############################################################################


###############################################################################
def scrape_details(game):
  base_wiki_api_url = 'http://en.wikipedia.org/w/index.php?action=raw&title='
  
  game_reg = re.compile('\{\{infobox video game', re.IGNORECASE) 
  game_reg_alt = re.compile('\{\{infobox vg', re.IGNORECASE) 
  redirect_reg = re.compile('#REDIRECT', re.IGNORECASE) 
  redirect_game_reg = re.compile('\[\[(.*?)\]\]', re.IGNORECASE) 

  wiki_string = get_wiki_string(game.name)

  # set up request data
  wiki_app_url = '{0}{1}'.format(base_wiki_api_url, wiki_string)
  headers = {'User-Agent' : 'Mozilla/5.0'}

  # try to get the data from the wikipedia page
  print("name: {0} , trying url: {1}".format(game.name, wiki_app_url))
  html_app_data, redirect = request_url(wiki_app_url, headers)

  #first check to see if there's game data there
  for i,line in enumerate(html_app_data):
    line = line.strip()
    if (game_reg.search(line) or game_reg_alt.search(line)):
      game.wiki_link_found = True
      game.wiki_string = wiki_string
      print("wikipedia entry found! name: {0}".format(wiki_string))
      break

  # next check to see if it needs to be redirected
  if (game.wiki_link_found == False):
    for line in html_app_data:
      if (redirect_reg.search(line)):
        new_string = redirect_game_reg.findall(line)[0]
        wiki_string = get_wiki_string(new_string)
        wiki_app_url = '{0}{1}'.format(base_wiki_api_url, wiki_string)
        html_app_data, redirect = request_url(wiki_app_url, headers)
        print("\n\nREDIRECTING..... {0} \n\n".format(wiki_string))
        for i,line in enumerate(html_app_data):
          line = line.strip()
          if (game_reg.search(line) or game_reg_alt.search(line)):
            game.wiki_link_found = True
            game.wiki_string = wiki_string
            print("wikipedia entry found! name: {0}".format(wiki_string))
            break

  # reset wiki string and try with video game appended
  wiki_string = get_wiki_string(game.name)
  if (game.wiki_link_found == False):
    #print("ERROR: Wikipedia entry not found: {0}".format(wiki_string))  
    #print("Trying name and video game")
    wiki_string = "{0}_{1}".format(wiki_string, "(video_game)")
    wiki_app_url = '{0}{1}'.format(base_wiki_api_url, wiki_string)

    print("name: {0} , trying url: {1}".format(game.name, wiki_app_url))
    html_app_data, redirect = request_url(wiki_app_url, headers)
   
    for i,line in enumerate(html_app_data):
      line = line.strip()
      #print(line)
      if (game_reg.search(line) or game_reg_alt.search(line)):
        game.wiki_link_found = True
        game.wiki_string = wiki_string
        print("Second attempt wikipedia entry found! name: {0}".format(wiki_string))
        break
###############################################################################


###############################################################################
# build list of games from XML file
def get_game_list_from_XML(filename):
  game_list = []

  r_tree = ET.parse(filename)
  r_root = r_tree.getroot()
  r_info = r_root[0]
  ngames = int(r_info[1].text)
  r_game_list = r_root[1]
  for game_itr in r_game_list.findall('game'):
    name = game_itr.get("name")
    app_ID = int(game_itr.find("app_ID").text)
    found_l = game_itr.find("wiki_link_found").text
    wiki_l = game_itr.find("wiki_string").text
    dev = game_itr.find("developer").text
    release_date = game_itr.find("publisher").text
    pub = int(game_itr.find("release_date").text)
    game_list.append(game(name, app_ID, found_l,wiki_l,release_date, dev, pub))
  return game_list, ngames 
###############################################################################

###############################################################################
# write game list to XML file
def write_new_game_list(game_list, steam_user_id, filename):
  print("Writing game data to XML file")
  ngames = len(game_list)
  root = ET.Element("root")
  info = ET.SubElement(root, "info")
  user = ET.SubElement(info, "user_ID")
  user.text = steam_user_id
  ngame_elem = ET.SubElement(info, "num_games")
  ngame_elem.text = "{0}".format(ngames)

  games = ET.SubElement(root, "game_list")

  for g_itr in game_list:
    game_elem = ET.SubElement(games, "game")
    game_elem.set("name", g_itr.name)
    #elements of game item
    app_elem = ET.SubElement(game_elem, "app_ID")
    found_elem = ET.SubElement(game_elem, "wiki_link_found")
    wiki_elem = ET.SubElement(game_elem, "wiki_string")
    rd_elem = ET.SubElement(game_elem, "release_date")
    dev_elem = ET.SubElement(game_elem, "developer")
    pub_elem = ET.SubElement(game_elem, "publisher")
    app_elem.text = str(g_itr.app_ID)
    found_elem.text = str(g_itr.wiki_link_found)
    wiki_elem.text = g_itr.wiki_string
    rd_elem.text = str(g_itr.release_date)
    dev_elem.text = g_itr.developer
    pub_elem.text = g_itr.publisher

  tree = ET.ElementTree(root)
  tree.write(filename, pretty_print=True )

###############################################################################

###############################################################################
def get_steam_game_list(steam_user_id):

  print("Getting game list for Steam user {0}".format(steam_user_id))
  steam_user_url = 'http://steamcommunity.com/id/{0}'.format(steam_user_id)
  all_games_url = '{0}/games/?tab=all'.format(steam_user_url)

  steam_url_obj = urllib.urlopen(all_games_url)
  html_all_games = steam_url_obj.readlines()

  ###############################################################################
  # find the long string of games and data from raw HTML
  ###############################################################################
  raw_games_str = ""

  for i,line in enumerate(html_all_games):
    lvec = line.split()
    if (len(lvec) > 2 ):
      if (lvec[1] =='rgGames'):
        raw_game_str = line

  ###############################################################################
  # parse games and app ID from raw string
  # (this string is defining a java class)
  ###############################################################################

  #regular expressions
  g_reg = re.compile('\{\"appid\".*?\}')
  app_reg = re.compile('\"appid\":(.*?),')
  name_reg = re.compile('\"name\":\"(.*?)\"') 
   
  g_str_list = g_reg.findall(raw_game_str)

  steam_game_list = []
  for g_s in g_str_list:
    app_ID = app_reg.findall(g_s)[0]
    name = name_reg.findall(g_s)[0]
    steam_game_list.append(game(name, app_ID))

  ngames = len(steam_game_list)

  return steam_game_list, ngames
###############################################################################

###############################################################################

def print_percent_found(game_list):
  num_found = 0
  ngames = len(game_list)
  for game_itr in game_list:
    if (game_itr.wiki_link_found):
      num_found = num_found + 1

  print("Found: {0} , percent: {1}".format(num_found, float(num_found)/ngames*100))
