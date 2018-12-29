# Description
A voting bot written in python 3.x for strawpoll. It generates its proxy list from http://proxylist.hidemyass.com/
It can work on Windows, Linux and Mac.

### Features
- Easy to use command line driven program
- Ability to choose from any type of strawpoll domain
- Ability to remember which proxies have already been used
- Ability to regenerate proxies automatically

# Usage
```
Usage: Main.py [options]

Options:
  -h, --help            show this help message and exit
  -v VOTES, --votes=VOTES
                        number of times to vote
  -s SURVEY, --survey=SURVEY
                        url id of the survey
  -t TARGET, --target=TARGET
                        checkbox id to vote for
  -d DOMAIN, --domain=DOMAIN
                        domain name end
  -f, --flush           Flushes the used proxy list
  -r, --renew           Renews the proxy list
```

### Example
```
python Main.py -v  20 -s 366ggz3 -t check4963932 -f -r
```

# How to install it ?
You can either download the zip or clone it with git then install the required libraries if they are not yet installed in your operating system with:
```
pip install requests
pip install selenium
pip install beautifulsoup4
```
Remember to install the chromedriver and put it in the folder where you are running Main.py: http://chromedriver.chromium.org/downloads

# How to add proxies to the list
In order to change the proxy list through the program you can add the -r in the command line. If you want to manually add proxies
you can do so by opening the proxies.txt with a text editor (Notepad+, Textpad etc.) and add a new proxy per new line

# How do I get the survey id and the target ?
The survey id is always in the url pointing to the desired survey.If the url is https://strawpoll.com/366ggz3 then 366ggz3 would be the id
and the domain would either be left blank(automatically is set to "com") or could be manually set to "com".
To find the desired target the user must right click the checkbox you want to vote for, then go to inspect element and search for a
value with 'check' that represents the checkbox. For example: check4963932. The targeted checkbox can also be found through the page's source code. For the strawpoll.me polls instead of the name of the input, the value should be used.
