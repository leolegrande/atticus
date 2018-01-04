##### Atticus the Cactus Twitterbot Class #####

from twython import Twython
from gpiozero import LightSensor
from time import sleep, strftime, localtime
from datetime import datetime
from picamera import PiCamera
import forecastio

class Atticus:

    #fields
    #date and time
    date = {
            'month' : '',
            'day' : '',
            'year' : '',
            'weekday' : ''
            }
    time = {
            'hour' : '',
            'minutes' : '',
            'seconds' : ''
            }

    # light shit
    sun_has_risen = True
    sunrise_threshold = 0.6

    # twitter shit
    weekday_tweets = {
            'Monday' : [0, []],
            'Tuesday' : [0, []],
            'Wednesday' : [0, []],
            'Thursday' : [0, []],
            'Friday' : [0, []],
            'Saturday' : [0, []],
            'Sunday' : [0, []],
            'Sadday' : [0, []]
            }

    #keys
    from auth.twit_auth import (
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret
            )

    from auth.weather_auth import weather_key

    twitter = Twython(
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret
            )

    # emojis
    weather_emojis = {
            'clear-day' : '\u2600',
            'clear-night' : '\u2600',
            'rain' : '\U0001F327',
            'snow' : '\U0001F328',
            'sleet' : '\U0001F328',
            'wind' : '\U0001F32C',
            'cloudy' : '\u2601',
            'partly-cloudly-day' : '\u26C5',
            'thunderstorm' : '\u26C8'
            }

    # peripherals
    ldr = LightSensor(4)
    camera = PiCamera()
    lat = 38.88
    lng = -77.19

    # constructor
    def __init__(self):
        self.update_time()
        self.get_data()

    #methods

    def update_time(self):
        self.date['month'] = strftime('%m', localtime())
        self.date['day'] = strftime('%d', localtime())
        self.date['year'] = strftime('%y', localtime())
        self.time['hour'] = strftime('%H', localtime())
        self.time['minutes'] = strftime('%M', localtime())
        self.time['seconds'] = strftime('%S', localtime())
        wkdy = strftime('%A', localtime())
        # also checks if day has passed, and if so, sun hasn't risen yet today
        if (wkdy != self.date['weekday'] and self.date['weekday'] != ''):
            self.sun_has_risen = False
        self.date['weekday'] = wkdy

    # not sure how correct this is, but updates index in .txt files
    # i use .txt files to store this data so i can easily write new tweets
    # while also not having to worry about the index resetting if power goes out
    def increase_index(self, day):
         with open('tweet_data/%s.txt' % day, 'r+') as f:
             lines = f.read().splitlines()
             index = int(lines[0])
             index += 1
             self.weekday_tweets[day][0] = index
             lines[0] = str(index)
             f.seek(0)
             for line in lines:
                 f.write(line + "\n")
         f.close()

    # for some reason, weather data is 4 hours ahead
    # even though i'm inputting the correct timezone, possibly a bug with the forecast api?
    # gets weather, returns tuple of string representation of weather and temperature data
    def get_weather(self):
        cur_time = datetime.now()
        forecast = forecastio.load_forecast(self.weather_key, self.lat, self.lng, time=cur_time)
        current = forecast.currently()
        weather = str(current.icon)
        temperature = str(current.temperature)
        return (weather, temperature)

    # reads data from txt files
    def get_data(self):
        for day, tup in self.weekday_tweets.items():
            with open('tweet_data/%s.txt' % day, 'r+') as f:
                tweets = f.read().splitlines()
                tup[0] = int(tweets[0])
                tup[1] = tweets[1:]

    # returns true if sun hasn't risen yet and it's lit af
    # returns True if the sun hasn't risen yet and it's now sunny af
    def check_sunrise(self):
        sunlight = ldr.value
        if (sunlight > self.sunrise_threshold and self.sun_has_risen == False):
            sun_has_risen = True
            return True
        else:
            return False

    # takes photo from rpi
    # returns filepath of photo
    def take_photo(self):
        self.camera.start_preview()
        sleep (5)
        date = strftime("%m-%d-%y_%H:%M:%S", localtime())
        filename = 'photos/%s_atticus.jpg' % date
        self.camera.capture(filename)
        self.camera.stop_preview()
        return filename

    # creates message based off weather
    # returns string representation of weather, something along the lines of:
    # Good morning! [weather emoji]
    # [weekday tweet?]
    def create_message(self):
        message = "Good morning! "
        weather, temperature = self.get_weather()
        message += self.weather_emojis[weather] + "\n"
        sub_message = ""
        message_array = []
        if (weather == 'rain'):
            message_array = self.weekday_tweets['Sadday']
        else:
            message_array = self.weekday_tweets[self.date['weekday']]
        index = message_array[0]
        array_length = len(message_array[1]) 
        # going to % index so there's no out-of-index-range errors
        sub_message = message_array[1][index%array_length]
        message += sub_message
        return message

    # creates a message, takes a photo, posts to twitter
    def post_to_twitter(self):
        message = self.create_message()
        photo_path = self.take_photo()
        photo = open(photo_path, 'rb')
        response = self.twitter.upload_media(media=photo)
        self.twitter.update_status(status=message, media_ids=[response['media_id']])
        print("Tweeted: %s" % message)

    def main(self):
        get_data()
        while True():
            update_time()
            if check_sunrise():
                post_to_twitter(message, photo_path)
                print("Updated Status: %s" % message)
            sleep(60)
