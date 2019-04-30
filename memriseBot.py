from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys, time
import unicodedata
import thread

print("Enter URL")
url = raw_input("-> ")

level = 1
prog = 2
links = ["/garden/", "practise/", "learn/", "review_level"]

num = 0
words = [[]]

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')


def runner(tNum):
   d = webdriver.Firefox()
   d.get("http://memrise.com/login/")
   e = d.find_element_by_name("username") #Find username box
   e.send_keys("<username>")
   e = d.find_element_by_name("password") #Find password box
   e.send_keys("<password>"+Keys.ENTER)
   # try:
   #    e = d.find_element_by_class_name("courses-filter-container") #Check for element on home page (succesful login?)
   # except Exception as e:
   #    print(e)
   #    sys.exit(1)
   time.sleep(2)

   get_words(d)
   print("Learning!")
   answerQuestions(d)

def get_words(d):
   global words
   d.get(url+str(prog)) #Go to the course
   ees = d.find_elements_by_class_name("text-text") #Find the list of words and translations
   for i in range(len(ees)): #Add words to list (each item is a list with word/translation)
       words.append(strip_accents(ees[i].text).encode("utf8").replace("\xc2\xbf", "").split("\n"))

   del words[0] #Delete the first element, empty for some reason
   if len(words[0]) > 2: #Delete the text with the time left until next review
      for i in range(len(words)):
         del words[i][0]
   print(words) #Print the words

def check_type(d): #Checks the type of question
        try:
            e = d.find_element_by_xpath('//*[@id="boxes"]/div/div[4]/input') #If there is a next button then it's a text question
            return "TEXT"
        except Exception:
            return "MULTICHOICE" #It's a multiple choice question

def answerQuestions(d):
   global prog, num
   while True: #Answer questions - go to the learning page
      d.get(url+str(level)+links[0]+links[prog]) #Start learning
      time.sleep(1)
      while True: #Answer questions
         if(prog > 1):
            try:
               e = d.find_element_by_xpath('//*[@id="content"]/div/div/div[1]/div[2]')
            except Exception:
               print("Already learnt, reviewing...")
               prog = 1
               get_words(d)
               break
         try:
            while True: #Click next when it tells you the words
               e = d.find_element_by_xpath('//*[@id="boxes"]/div/div[3]/div[2]/a') #Check for element specific to that page
               e = d.find_element_by_xpath('//*[@id="boxes"]/div/button') #Select nex button
               e.click() #Click next page
               time.sleep(0.8)
         except Exception:
            a = 1
         try:
            e = d.find_element_by_xpath('//*[@id="boxes"]/div/div[1]/div/div[1]/span[2]') #Check for element?
            break
         except Exception:
            a = 1
         try:
            e = d.find_element_by_xpath('//*[@id="content"]/div/a/span') #Check if learning session has finished
            #url = url[:-15]+"3/garden/learn/"
            break
         except Exception:
            a = 1
         #Get the word/phrase to translate
         translation = strip_accents(d.find_element_by_xpath('//*[@id="boxes"]/div/div[1]/div[2]').text).encode("utf8").replace("\xc2\xbf", "")
         for j in range(len(words)): #Find the answer
            while True:
               try:
                  num = words[j].index(translation) #Try to index translation for each pair
                  loc = j
                  break
               except Exception: #Found the answer
                  break
         if(check_type(d) == "MULTICHOICE"): #If it's a multichoice question
            options = []
            try:
               ops = d.find_elements_by_xpath('//*[@id="boxes"]/div/ol/li') #Get the elements for the answers
            except Exception:
               a = 1
            for i in range(1,len(ops)+1): #Get the text for each option
                options.append(strip_accents(d.find_element_by_xpath('//*[@id="boxes"]/div/ol/li['+str(i)+']/span[2]').text).encode("utf8").replace("\xc2\xbf", ""))
            if num == 1:
                ans = options.index(words[loc][0])+1
            else:
                ans = options.index(words[loc][1])+1
            e = d.find_element_by_xpath('//*[@id="boxes"]/div/ol/li['+str(ans)+']') #find the right option
            e.click() #Click the option
            e = d.find_element_by_xpath('//*[@id="boxes"]/div/button') #Click next
            e.click()
            time.sleep(0.5) #Wait for next question to load (AJAX)
         else:
            e = d.find_element_by_xpath('//*[@id="boxes"]/div/div[4]/input') #If it's a text question
            if num == 1:
                ans = words[loc][0]
            else:
                ans = words[loc][1]
            e.send_keys(ans) #Type the answer
            e = d.find_element_by_xpath('//*[@id="boxes"]/div/button') #Find the next button
            e.click() #Click next
            time.sleep(0.5) #Wait for next question (AJAX)

runner(1)
