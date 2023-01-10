from time import sleep
from threading import Thread
from urllib.parse import urlparse
import bs4
import plyer
import requests
import smtplib
from datetime import datetime
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def generateDiff(oldHtml, newHtml, fileName):
    html = """<!DOCTYPE html>
            <html lang="en">
              <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="X-UA-Compatible" content="ie=edge">
              </head>
              <body>
              <h1>Old version</h1>"""
    html += oldHtml
    html +=  "<h1>New version</h1>"         
    html += newHtml                               
    html += """
              </body>
            </html>"""
    
    f = open(fileName, "w")
    f.write(html)
    f.close()
    #return html

class Tag:
    def __init__(self, header, tag, value):  
            self.header = header
            self.tag = tag
            self.value = value
class Scrapper:
    def __init__(self):  
        # creates SMTP session
        self.tags = [Tag("div", "class", "regi-list")]
        self.exceptionTags = [[Tag("span", "class", "sec-head")]]
        self.fromMail = ""
        self.password = ""
        self.toMail = self.fromMail #sending to myself
        self.url = ""
        self.tryCounter = 0
        self.sleepTimer = 60

    def show_notification(self):
        plyer.notification.notify(title='Something Changed!', message="Your URL has changed, check it out")


    def sendMail(self, message):
        self.s = smtplib.SMTP('smtp.gmail.com', 587)
        self.s.starttls()
        self.s.login(self.fromMail, self.password)
        self.s.sendmail(self.fromMail, self.toMail, message)
        self.s.quit()
        
    def sendMailWithAttachment(self, mail_content, attachment, subject):
        message = MIMEMultipart()
        message['From'] = self.fromMail
        message['To'] = self.toMail
        message['Subject'] = subject
        
        #The subject line The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        attach_file_name = attachment
        
        attach_file = open(attach_file_name, 'rb') # Open the file as binary mode
        payload = MIMEBase('application', 'octate-stream')
        payload.set_payload((attach_file).read())
        encoders.encode_base64(payload) #encode the attachment
        
        #add payload header with filename
        payload.add_header('Content-Disposition', 'attachment', filename=attach_file_name)
        message.attach(payload)
        
        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(self.fromMail, self.password) #login with mail_id and password
        text = message.as_string()
        session.sendmail(self.fromMail, self.toMail, text)
        session.quit()
        print('Mail Sent')


    def runCode(self):
        try:
            htmlContent = requests.get(url = self.url).content

            oldSoup = bs4.BeautifulSoup(htmlContent, 'html.parser')
            newSoup = bs4.BeautifulSoup(htmlContent, 'html.parser')
          
            while (True):
                htmlContent = requests.get(url = self.url).content
                webName = urlparse(self.url).netloc
                time_now = datetime.now()
                current_time = time_now.strftime("%H:%M:%S")
  
                print(webName, current_time) 
                newSoup = bs4.BeautifulSoup(htmlContent, 'html.parser')
                
                i = 0
                for entry in self.tags:              
                    oldList = oldSoup.find(entry.header,{entry.tag:entry.value})
                    newList = newSoup.find(entry.header,{entry.tag:entry.value})
                    
                    for exception in self.exceptionTags[i]:
                        for element in newList.find_all(exception.header, {exception.tag:exception.value}): 
                            element.decompose()
                        for element in oldList.find_all(exception.header, {exception.tag:exception.value}): 
                            element.decompose()
                                                                 
                    if(oldList != newList):
                        self.show_notification()
                        generateDiff(str(oldList), str(newList), webName + "_Diff.html")                       
                        self.sendMailWithAttachment("Something changed on " + webName + "!", webName + "_Diff.html",
                        webName + " Differences")
                        #os.remove(webName + "_Diff.html")
                        oldSoup = newSoup
                        break
                       
                    
                    i += 1
                    
                self.tryCounter = 0
                sleep(self.sleepTimer)
        except Exception as e:   
            print(e)
            sleep(self.sleepTimer)
            self.runCode2()

    def runCode2(self):
        self.tryCounter += 1
        if(self.tryCounter < 5):
            self.runCode()

test = Scrapper()
test.runCode()        






