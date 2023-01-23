#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 16:08:55 2023

@author: aidencamilleri
"""

from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/5.3.0/bin/tesseract'

fullString = pytesseract.image_to_string(Image.open('/Users/aidencamilleri/OneDrive - College of Charleston/Personal Projects/Code Projects/CalendarMaker/ExSchedule.png'))


def getClassName(segment):
    className = segment.split('|')[0].strip()
    return className
    
def getStartDate(segment):
    startDate = segment.split('|')[2].split(':')[1].strip()
    return startDate

def getEndDate(segment):
    endDate = segment.split('|')[3].lstrip().split()[2].strip()
    return endDate

def getStartTime(segment):
    times = segment.split('AM')
    if len(times) == 1:
        times = times[0].split('PM')
    if 'PM' in segment and 'AM' not in segment:
        dayHalf = "PM"
    else:
        dayHalf = "AM"
    if len(times) != 1:
        startTime = times[0][-6:] + dayHalf
        startTime.strip()
    else:
        startTime = "NA"
    return startTime

def getEndTime(segment):
    times = segment.split('AM')
    if len(times) == 1:
        times = times[0].split('PM')
    if 'AM' in segment and 'PM' not in segment:
        dayHalf = "AM"
    else:
        dayHalf = "PM"
    if len(times) != 1:
        endTime = times[1][-6:] + dayHalf
        endTime.strip()
    else:
        endTime = "NA"
    return endTime

def getLocation(segment):
    if segment.split('Type: ')[1][:5] == "Class":
        building = segment.split("Room:")[0].split(":")[-1].strip()
        room = segment.split("Room: ")[1].split()[0][:3].strip()
        location = building + " " + room
    else:
        location = "NA"
    return location
    
def getZoom():
    zoom = pytesseract.image_to_string(Image.open('/Users/aidencamilleri/OneDrive - College of Charleston/Personal Projects/Code Projects/CalendarMaker/Zoom.png'))
    return zoom

def getDays(segment, count):
    daySplit = segment.split("y)")
    if "sM1 Mrs" in daySplit[count]:
        return "MWF"
    elif "s MEwhlris" in daySplit[count]:
        return "TR"
    else:
        return "NA"
    
def lastDay(lastDate):
    dateSplit = lastDate.split('/')
    if lastDate != "NA":
        dateTime = dateSplit[2] +  dateSplit[0] + dateSplit[1]
    return dateTime
    
def daysConverted(days):
    if days == "MWF":
        return "MO,WE,FR"
    elif days == "TR":
        return "TU,TH"
    else:
        return "NA"
    
def toDateTime(date, time):
    dateSplit = date.split('/')
    if time != "NA":
        timeMod = time[:5].split(':')
    if "PM" in time and int(timeMod[0]) != 12:
        timeMod[0] = int(timeMod[0]) + 12
        timeMod[0] = str(timeMod[0])
    dateTime = dateSplit[2] + '-' + dateSplit[0] + '-' + dateSplit[1] + 'T' + timeMod[0] + ':' + timeMod[1] + ":00-05:00"
    return dateTime


    
class Course:
    def __init__(self, courseName, startDate, endDate, startTime, endTime, location, days):
        self.courseName = courseName
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
        self.location = location
        self.days = days
        
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.app.created', 'https://www.googleapis.com/auth/calendar.events.freebusy', 'https://www.googleapis.com/auth/calendar.events.public.readonly', 'https://www.googleapis.com/auth/calendar.freebusy']


def googleAuth(creds):
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/Users/aidencamilleri/OneDrive - College of Charleston/Personal Projects/Code Projects/CalendarMaker/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def createCalendar():
    service = build('calendar', 'v3', credentials=creds)
    calendar = {'summary': 'College Classes', 'timeZone': 'America/New_York'}
    created_calendar = service.calendars().insert(body=calendar).execute()
    for i in courseList:
        if i.location != "NA":
            rrule = 'RRULE:FREQ=WEEKLY;UNTIL=' + lastDay(i.endDate) + ';BYDAY=' + daysConverted(i.days)
            startDateTime = toDateTime(i.startDate, i.startTime)
            endDateTime = toDateTime(i.startDate, i.endTime)
            event = {
                'summary': i.courseName,
      'location': i.location,
      'start': {
        'dateTime': startDateTime,
        'timeZone': 'America/New_York'
      },
      'end': {
        'dateTime': endDateTime,
        'timeZone': 'America/New_York'
      },
      'recurrence': [
        rrule
            ]
          }
            recurring_event = service.events().insert(calendarId = created_calendar['id'], body=event).execute()
            print(recurring_event['summary'] + ' added')
    




classList = fullString.split('»')
courseList = []
count = 0
for i in classList:
    if i == '':
        continue
    else:
        courseList.append(Course(getClassName(i), getStartDate(i), getEndDate(i), getStartTime(i), getEndTime(i), getLocation(i), getDays(getZoom(), count)))
        count = count + 1
        
creds = None
creds = googleAuth(creds)
createCalendar()