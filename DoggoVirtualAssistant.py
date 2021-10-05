from __future__ import print_function
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import time
import playsound
import speech_recognition as sr
import pyaudio
import dateutil.parser
import pyttsx3
import pytz
import subprocess
import requests
import json

Wake = "hey doggo"
Wake2 = "hey doug"
Wake3 = "hey dog"
Wake4 = "hey dugge"

Sleep = "goodbye dock"
Sleep2 = "goodbye doug"
Sleep3 = "goodbye dog"
Sleep4 = "goodbye dugge"

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday", "sunday"]
DAY_EXT = ["rd", "th", "st", "nd"]
GET_EVENTS = ["what do i have", "do i have plans", "am i busy", "what events do i have",
              "do i have anything", "what events do i have", "do i have any events"]
NOTE = ["make a note", "create a note",
        "write a note", "open notes", "notes"]
HRU = ["how are you?", "how are you", "how are you doing",
       "how is everything", "how's everything"]
COVID = ["how is covid", "covid in"]
WEATHER = ["how's the weather", "how is the weather",
           "is it hot today", "is it cold today"]
TIME = ["What time is it", "what is the time", "what's the time"]
COUNTRIES = ["Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua &amp; Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahamas",
             "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia", "Bosnia &amp; Herzegovina", "Botswana", "Brazil",
             "British Virgin Islands", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Cape Verde", "Cayman Islands", "Chad", "Chile", "China", "Colombia", "Congo",
             "Cook Islands", "Costa Rica", "Cote D Ivoire", "Croatia", "Cruise Ship", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador",
             "Egypt", "El Salvador", "Equatorial Guinea", "Estonia", "Ethiopia", "Falkland Islands", "Faroe Islands", "Fiji", "Finland", "France", "French Polynesia", "French West Indies",
             "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Gibraltar", "Greece", "Greenland", "Grenada", "Guam", "Guatemala", "Guernsey", "Guinea", "Guinea Bissau", "Guyana", "Haiti", "Honduras",
             "Hong Kong", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Isle of Man", "Israel", "Italy", "Jamaica", "Japan", "Jersey", "Jordan", "Kazakhstan", "Kenya", "Kuwait",
             "Kyrgyz Republic", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Macau", "Macedonia", "Madagascar", "Malawi", "Malaysia",
             "Maldives", "Mali", "Malta", "Mauritania", "Mauritius", "Mexico", "Moldova", "Monaco", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Namibia", "Nepal", "Netherlands",
             "Netherlands Antilles", "New Caledonia", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Norway", "Oman", "Pakistan", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru",
             "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Reunion", "Romania", "Russia", "Rwanda", "Saint Pierre &amp; Miquelon", "Samoa", "San Marino", "Satellite", "Saudi Arabia",
             "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "South Africa", "South Korea", "Spain", "Sri Lanka", "St Kitts &amp; Nevis", "St Lucia", "St Vincent",
             "St. Lucia", "Sudan", "Suriname", "Swaziland", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor L'Este", "Togo", "Tonga", "Trinidad &amp; Tobago", "Tunisia",
             "Turkey", "Turkmenistan", "Turks &amp; Caicos", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "Uruguay", "Uzbekistan", "Venezuela", "Vietnam", "Virgin Islands (US)", "Yemen",
             "Zambia", "Zimbabwe"]
SALUTES = ["hi", "hello", "hola", "what's up", "what is up", "sup"]


# speaks the the input text
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    print(text)


# convert audio to text
def get_audio():
    r = sr.Recognizer()
    with sr.Microphone(device_index=0) as source:
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
        said = " "
    try:
        said = r.recognize_google(audio)
        print(said)
    except Exception as e:
        pass
    return said


# gets a specific date out of a a line of text
def get_date(text):
    text = text.lower()
    today = datetime.date.today()
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    # look for the mention of today, yesterday, tomorrow
    if text.count("today") > 0:
        return today
    elif text.count("tomorrow") > 0:
        return tomorrow
    elif text.count("yesterday") > 0:
        return yesterday

    day = -1
    day_w = -1
    month = -1
    year = today.year  # by default the year will the current year

    # look for the mention of a day, day_ext, day_w, and/or month
    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_w = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXT:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[: found])
                    except:
                        pass

    # jumps to next year in case month already passed this year
    if month < today.month and month != -1:
        year = year + 1

    # if only found a day
    if month == -1 and day != -1:
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    # if only found a day of the week
    if month == -1 and day == -1 and day_w != -1:
        cday_w = today.weekday()
        diff = day_w - cday_w

        if diff < 0:
            diff += 7
            if text.count("next") > 1:
                diff += 7

        return today + datetime.timedelta(diff)

        if diff > 0:
            i = text.count("next")
            while i > 0:
                diff += 7
                i -= 1
        return today + date.timedelta(diff)

    # checks that we at least know the day after checking all conditions
    if day != -1:
        return datetime.date(month=month, day=day, year=year)


# Verify the credential files of your google account to use Google API
def authenticate_google():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service


class VirtualAssistant():
    # Verify the credential files of your google account to use Google API
    def authenticate_google(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('calendar', 'v3', credentials=creds)
        return service

    # Gets the events assigned to a day in the google calendar API
    def get_events(self, day, service):
        # Crates the start and end of the day and format to utc timezone so it is compatible with google calender API
        dayStart = datetime.datetime.combine(day, datetime.datetime.min.time())
        dayEnd = datetime.datetime.combine(day, datetime.datetime.max.time())
        utc = pytz.UTC
        dayStart = dayStart.astimezone(utc)
        dayEnd = dayEnd.astimezone(utc)

        # Accessess the Google Calender API and stores all the events and their info
        events_result = service.events().list(calendarId='primary', timeMin=dayStart.isoformat(),
                                              timeMax=dayEnd.isoformat(), singleEvents=True,
                                              orderBy='startTime').execute()
        # creates a list cointaing the events of the day.
        events = events_result.get('items', [])

        # checks the amount of events in input day.
        if not events:
            speak("No upcoming events found.")
        else:
            if len(events) == int(1):
                speak("You have one event this day.")
            else:
                speak(f"You have {len(events)} events this day.")

            for event in events:
                # stores the event's date and time.
                event_stime = event['start'].get(
                    'dateTime', event['start'].get('date'))
                print(event_stime, event['summary'])

                # chacks for time of event and if there is a time it stores only the hour in startingTime.
                if 'T' in event_stime:
                    dateutil.parser.parse(event_stime)
                    dt = dateutil.parser.parse(event_stime)
                    startingTime = dt.strftime('%I:%M')
                    # formats the starting time more by adding pm or am
                    if int(startingTime.split(":")[0]) < 12:
                        startingTime = startingTime + 'am'
                    else:
                        startingTime = str(int(startingTime.split(":")[0]))
                        startingTime = startingTime + 'pm'
                    speak(event['summary'] + ' at ' + startingTime)
                else:
                    speak(event['summary'])

    # writes a note
    def note(self, text):
        from pathlib import Path
        date = datetime.datetime.now()
        filename = Path(str(date) + '.txt')
        # will create file, if it exists will do nothing
        filename.touch(exist_ok=True)
        file = open(filename)
        with open(filename, "w") as f:
            f.write(text)
        subprocess.Popen(
            ["/System/Applications/TextEdit.app/Contents/MacOS/TextEdit", filename])

    # gets the weather of the city mentioned
    def get_weather(self, city, weatherAPIkey):
        BASE_URL = "https://api.openweathermap.org/data/2.5/weather?q="
        URL = Base_URL + city + "&appid=" + weatherAPIkey
        response = requests.get(URL)
        if response.status_code == 200:
             # getting data in the json format
            data = response.json()
            # getting the main dict block
            main = data['main']
            # getting temperature
            temperature = main['temp']
            # getting the humidity
            humidity = main['humidity']
            # getting the pressure
            pressure = main['pressure']
            # weather report
            report = data['weather']
            speak("Weather Report: {report[0]['description']}")


service = authenticate_google()
# weatherAPIkey = cf95b20fb67c15e89702ed289866ab30
Doggo = VirtualAssistant()

while True:
    print('Listening...')
    text = get_audio().lower()

    # looks for the wake up call
    if text.count(Wake) > 0 or text.count(Wake2) > 0 or text.count(Wake3) > 0 or text.count(Wake4) > 0:
        speak('What is up?')
        pass

    # looks for event funtion calling
    for phrase in GET_EVENTS:
        if phrase in text.lower():
            date = get_date(text)
            if date:
                Doggo.get_events(date, service)
            else:
                speak('Come again?' or 'Can you say that again please?')

    # looks for note function calling
    for phrase in NOTE:
        if phrase in text:
            speak("What do you want to write? ")
            print("Listening...")
            content = get_audio()
            Doggo.note(content)
            speak("Done! I've created a note for you.")

    for phrase in TIME:
        if phrase in text:
            time = time.asctime(time.localtime(time.time()))
            speak(time)

    for phrase in WEATHER:
        if phrase in text:
            speak("What is the name of your city?")
            print("Listening")
            city = get_audio()
            get_weather(city, weatherAPIkey)

    for phrase in HRU:
        if phrase in text:
            speak("Good, how about you?")
            break
        else:
            pass

    for word in SALUTES:
        if word == text:
            speak("Hello friend, how can I help?")
            break
        else:
            pass

    if text == "you stupid":
        speak("No I am not")
        print('Listening...')
        text = get_audio().lower()
        if text == "what's 9 + 10" or "what is 9 + 10":
            speak("21")
        else:
            pass

    if text == 'thank you':
        speak("You are welcome, I am here to help my friend")

    if text == "goodbye":
        speak("Goodbye")
        break

# Youtube Channel TechWithTim -- https://www.youtube.com/channel/UC4JX40jDee_tINbkjycV4Sg
# Youtube Channel Corey Schafer -- https://www.youtube.com/user/schafer5
# Stackoverflow Community -- https://stackoverflow.com/questions
# Google Calendar API Algorithm & Credentials -- https://console.cloud.google.com/marketplace/product/google/calendar-json.googleapis.com?q=search&referrer=search&project=quickstart-316602
