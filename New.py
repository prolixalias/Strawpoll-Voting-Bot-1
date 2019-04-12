
# Usage: Main.py [options]
#
# Options:
#   -h, --help                       | show this help message and exit
#   -e, --electorate=filename.json   | list of voters (accepts only json)
#   -s SURVEY, --survey=SURVEY       | id of the survey
#   -t TARGET, --target=TARGET       | checkbox to vote for
#   -f, --flush                      | deletes skipping proxy list
#
#  Example:
#    python3 Main.py -e electorate.json -s 5c8fe5b2415047923ca8bb63 -t 5c8fe63f6072beaf0cb05040 -f -r
#



####
#
# (0) Populate list of proxies
# (1) Read list of all voters
# (2) Read list of all proxies
# (3) Read list of polls
# (4) Loop - while true
# (5)   Set timestamp for now
# (6)   Loop - over all voters
# (6.1)   If voter not in polls OR if in polls AND timestamp - lastVote > 24 hours
# (6.2)     add to line at polls
# (6.3)   Else skip this voter
# (6.4) End loop 6 
# (7) Loop - over line at polls
# (7.1)   dd
####



try:
    from optparse import OptionParser
    import sys
    import os
    import re
    from bs4 import BeautifulSoup
    import urllib.request
    import random
    import requests
    import html5lib
    import json
    from datetime import datetime, timezone
    from pprint import pprint
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError as msg:
    print("[!] Library not installed: " + str(msg))
    exit()



class Strawpoll_Multivote:

    # Initialization
    maxVotes = 1
    voteFor = ""
    surveyId = ""
    proxyListFile = "proxies.txt"
    saveStateFile = "usedProxies.txt"
    voterPolls = "voterPolls.json"
    proxyTimeout = 10 # in seconds
    currentProxyPointer = 0
    successfulVotes = 0



    def __init__(self):
        try:

            # Parse Arguments
            parser = OptionParser()
            parser.add_option("-e", "--electorate", action="store", type="string", dest="electorate", help="list of voters") 
            parser.add_option("-s", "--survey",     action="store", type="string", dest="survey",     help="url id of the survey")
            parser.add_option("-t", "--target",     action="store", type="string", dest="target",     help="checkbox id to vote for")
            parser.add_option("-f", "--flush",      action="store_true", dest="flush", help="Flushes the used proxy list")
            parser.add_option("-r", "--renew",      action="store_true", dest="renew", help="Renews the proxy list")

            (options, args) = parser.parse_args()

            if len(sys.argv) > 2:
                    if options.electorate is None:                                  
                        print("[-] List of voters is not defined with: -e") 
                        exit(1) 
                    if options.survey is None:
                        print("[!] Url id of the survey defined with: -s")
                        exit(1)
                    if options.target is None:
                        print("[!] Target checkbox to vote for is not defined with: -t")
                        exit(1)

                    # Save arguments into global variable
                    self.votes = 1
                    self.electorate = options.electorate
                    self.voteFor = options.target
                    self.surveyId = options.survey
                    #self.fqdn = 'campaigns.socialnewsdesk.com'
                    self.fqdn = 'localhost'

                    # Flush usedProxies.txt
                    if options.flush == True:
                        print("[#] Flushing usedProxies.txt file...")
                        os.remove(self.saveStateFile)
                        open(self.saveStateFile, 'w+')
                    if options.renew == True:
                        renewlist=self.renewProxyList();
                        os.remove(self.proxyListFile)
                        with open(self.proxyListFile, "a") as myfile:
                            for i in renewlist:
                                myfile.write(i)

            # Print help
            else:
                print("[!] Not enough arguments given")
                print()
                parser.print_help()
                exit()



            timeStamp = datetime.now(timezone.utc).astimezone().isoformat()
            pprint("Now: " + timeStamp)

            with open(self.electorate) as file:
              voters = json.load(file)

            pprint(range(len(voters)))

            store_list = []

            for voter in voters:
              store_details = {'id':None, 'attributes':None}
              store_details['id'] = voter['id']
              #print(voter['id'])
              #pprint(voter['attributes']['personalInfo']['dob'])
              #pprint(voter['attributes']['address']['address'])
              store_details['attributes'] = voter['attributes']
              store_list.append(store_details)

            #pprint(store_list)

            randomVoter = random.choice(store_list)
            
            print("random:")
            pprint(randomVoter["id"])

            store_list.pop(randomVoter["id"])

            print("new list:")
            pprint(store_list)















            # Read proxy list file
            alreadyUsedProxy = False
            proxyList = open(self.proxyListFile).read().split('\n')

            proxyList2 = None

            # Check if saveState.xml exists and read file
            if os.path.isfile(self.saveStateFile):
                proxyList2 = open(self.saveStateFile).read().split('\n')

            # Print remaining proxies
            if proxyList2 is not None:
                print("[#] Number of proxies remaining in old list: " + str(len(proxyList) - len(proxyList2)))
                print()
            else:
                print("[#] Number of proxies in new list: " + str(len(proxyList)))
                print()

            # Go through proxy list
            for proxy in proxyList:

                # Check if max votes has been reached
                if self.successfulVotes >= self.maxVotes:
                    break

                # Increase number of used proxy integer
                self.currentProxyPointer += 1



                # Read in saveState.xml if this proxy has already been used
                if proxyList2 is not None:
                    for proxy2 in proxyList2:
                        if proxy == proxy2:
                            alreadyUsedProxy = True
                            break

                # If it has been used print message and continue to next proxy
                if alreadyUsedProxy == True:
                    print("["+ str(self.currentProxyPointer) +"] Skipping proxy: " + proxy)
                    alreadyUsedProxy = False
                    continue

                # Print current proxy information
                print("["+ str(self.currentProxyPointer) +"] New proxy: " + proxy)
                print("[#] Connecting... ")

                # Connect to strawpoll and send vote
                # self.sendToWeb('http://' + proxy,'https://' + proxy)
                self.webdriverManipulation(proxy);
                # Write used proxy into saveState.xml
                self.writeUsedProxy(proxy)
                print()

            # Check if max votes has been reached
            if self.successfulVotes >= self.maxVotes:
                print("[*] Finished voting: " + str(self.successfulVotes) + ' times.')
            else:
                print("[*] Finished every proxy in the list.")

            exit()
        except IOError as ex:
            print("[!] " + ex.strerror + ": " + ex.filename)

        except KeyboardInterrupt as ex:
            print("[#] Ending procedure...")
            print("[#] Programm aborted")
            exit()



    def writeUsedProxy(self, proxyIp):
        if os.path.isfile(self.saveStateFile):
            with open(self.saveStateFile, "a") as myfile:
                myfile.write(proxyIp+"\n")



    def getIp(self, httpProxy):
        proxyDictionary = {"https": httpProxy}
        request = requests.get("https://api.ipify.org/", proxies=proxyDictionary)
        requestString = str(request.text)
        return requestString



	# Using selenium and chromedriver to run the voting process on the background
    def webdriverManipulation(self,Proxy):
        try:
            WINDOW_SIZE = "1920,1080"

            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
            chrome_options.add_argument('--proxy-server=%s' % Proxy)
            prefs = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", prefs)
            chrome = webdriver.Chrome(options=chrome_options)

            if self.fqdn == "localhost":
                chrome.get('https://' + self.fqdn + '/' + self.surveyId)
                element = chrome.find_element_by_xpath('//*[@value="'+ self.voteFor +'"]')
                webdriver.ActionChains(chrome).move_to_element(element).click(element).perform()
                submit_button = chrome.find_elements_by_xpath('//*[@type="submit"]')[0]
                submit_button.click()
            else:
                chrome.get('https://' + self.fqdn + '/' + self.surveyId)
                element = chrome.find_element_by_xpath('//*[@name="'+ self.voteFor +'"]')
                webdriver.ActionChains(chrome).move_to_element(element).click(element).perform()
                submit_button = chrome.find_elements_by_xpath('//*[@id="votebutton"]')[0]
                submit_button.click()

            chrome.quit()
            print("[*] Successfully voted.")
            self.successfulVotes += 1
            return True
        except Exception as exception:
            print("[!] Voting failed for the specific proxy.")
            chrome.quit()
            return False



        # Original headers:
        #
        #            'Host': self.fqdn,
        #            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0',
        #            'Accept': '*/*',
        #            'Accept-Language': 'en - us, en; q = 0.5',
        #            'Accept-Encoding': 'gzip, deflate',
        #            'Accept-Charset': 'ISO - 8859 - 1, utf - 8; = 0.7, *;q = 0.7',
        #            'Referer': 'https://'+ self.fqdn +'/' + self.surveyId,
        #            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        #            'X-Requested-With': 'XMLHttpRequest',
        #            'Content-Length': '29',
        #            'Cookie': 'lang=en',
        #            'DNT': '1',
        #            'Connection': 'close'



    # Posting through requests (previous version)
    def sendToWeb(self, httpProxy, httpsProxy):
        try:
            headers = \
                {
                    'Host': 'campaigns-api-public.socialnewsdesk.com',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Referer': 'https://' + self.fqdn + '/',
                    'Content-Type': 'application/json;charset=utf-8',
                    'Content-Length': '361',
                    'Origin': 'https://' + self.fqdn,
                    'Connection': 'keep-alive'
                }
            #payload = {'pid': self.surveyId, 'oids': self.voteFor}
            payload = {"entry":{"data":{"customCheckboxes":{"5c8fe63f6072beaf0cb05040":true},"personalInfo":{"dob":"1974-10-30T05:00:00.000Z","firstName":"Mike","lastName":"Honcho","emailAddress":"mhoncho@rybamarine.com","phone":"231-420-9427"},"address":{"address":"6800 Hughston Drive","city":"Harbor Springs","state":"MI","zip":"49721"}},"promotionId":"5c8fe5b2415047923ca8bb63"}}
            proxyDictionary = {"http": httpProxy, "https": httpsProxy}

            pprint("httpProxy: " + httpProxy)
            pprint("httpsProxy: " + httpsProxy)
            pprint(self.fqdn)
            pprint(self.surveyId)
            pprint(self.voteFor)
            pprint(headers)
            pprint(payload)

            # Connect to server
            r = requests.post('https://' + self.fqdn + '/api/promotions/' + self.surveyId + '/entrant', data=payload, headers=headers)
            json = r.json()

            # Check if the vote was successful
            if(bool(json['success'])):
                print("[*] Successfully voted.")
                self.successfulVotes += 1
                return True
            else:
                print("[!] Voting failed.")
                return False
        except requests.exceptions.Timeout:
            print("[!] Timeout")
            return False
        except requests.exceptions.ConnectionError:
            print("[!] Couldn't connect to proxy")
            return False
        except Exception as exception:
            print(str(exception))
            return False

    # Renew Proxy List
    def renewProxyList(self):
        final_list=[]
        url = "http://proxy-daily.com/"
        content = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(content,features="html5lib")
        center = soup.find_all("center")[0]
        div = center.findChildren("div", recursive=False)[0].getText()
        children= div.splitlines()
        for child in children:
            final_list.append(child+"\n")
        return (final_list)
# Execute strawpoll_multivote
Strawpoll_Multivote()
