import datetime
import platform
import re
import subprocess
import threading

import geocoder
import requests
import random
import sys

from Functions import *
from Winter import Winter
import os
import keywords as key
import responses as res

location = geocoder.ip('me')
weather_data = None
is_next_round = False


def kelvin_to_celsius(kelvin):
    celsius = kelvin - 273.15
    return str(round(celsius, 1))


def mph_to_kph(mph):
    kph = mph * 1.60934
    return str(round(kph, 1))


def fetch_weather():
    global weather_data
    lat = location.latlng[0]
    lon = location.latlng[1]
    api_key = 'ac9c8b1df44a7385f94be73100a2b121'
    api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(api_url)
    if response.status_code == 200:
        weather_data = response.json()
        print(weather_data)

    else:
        print(f"Failed to fetch data: {response.status_code}")


def main(from_wake_word):
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    nltk.download('punkt')

    global is_next_round
    winter = Winter()
    winter.start_show_screen_thread()

    welcomeLine = winter.start()

    if not from_wake_word:
        winter.speak(welcomeLine)

    if weather_data is not None:
        questions = [
            "What can I do for you today?",
            "How may I assist you?",
            "Is there anything you need help with?",
            "How can I be of service?",
            "What do you need assistance with?",
            "How can I assist you today?",
            "What would you like help with?",
            "How can I support you?",
            "What can I help you with?",
            "Is there something I can assist you with?",
            "What do you need help with today?",
            "How can I assist you at the moment?",
            "What can I do for you right now?",
            "Do you need any help?",
            "Is there anything I can help you with?"
        ]

        temperature = weather_data['main']['temp']
        city = weather_data['name']
        weather_desc = weather_data['weather'][0]['description']
        wind_speed = mph_to_kph(weather_data['wind']['speed'])
        celsius = kelvin_to_celsius(temperature)
        winter.speak("Today's temperature is " + celsius + " degree celsius, at " + city)
        winter.speak("Wind speed is " + wind_speed + " kilometer, per hour.")
        winter.speak("There is a " + weather_desc)
        random_no = random.randint(0, len(questions) - 1)
        winter.speak(questions[random_no])
    ask_anything_else = True
    while True:

        response = winter.recognize(is_next_round, ask_anything_else)

        transcriptionFormatted = str(format_transcription(response))
        transcription = str(response)
        # winter.speak("You said: " + transcriptionFormatted)
        string_transcription = transcription.lower()
        print(string_transcription)
        if "none" in string_transcription:
            winter.sleep()
            break

        elif in_there(key.introduce_keywords, string_transcription) and in_there(key.stop_keywords,
                                                                                 string_transcription):
            winter.speak("I detected conflicting commands. Please clarify.")

        elif in_there(key.file_manager_keywords, string_transcription):
            def open_file_manager(path="."):
                # Get the absolute path
                abs_path = os.path.abspath(path)

                # Identify the platform and use the appropriate command
                system = platform.system()
                try:
                    if system == "Windows":
                        os.startfile(abs_path)
                        response = res.filemanager_successful_responses
                        random_no = random.randint(0, len(response) - 1)
                        winter.speak(response[random_no])
                    elif system == "Darwin":  # macOS
                        subprocess.run(["open", abs_path])
                        response = res.filemanager_successful_responses
                        random_no = random.randint(0, len(response) - 1)
                        winter.speak(response[random_no])
                    elif system == "Linux":
                        subprocess.run(["xdg-open", abs_path])
                        response = res.filemanager_successful_responses
                        random_no = random.randint(0, len(response) - 1)
                        winter.speak(response[random_no])
                    else:
                        response = res.filemanager_unsuccessful_responses
                        random_no = random.randint(0, len(response) - 1)
                        winter.speak(response[random_no])
                        raise NotImplementedError(f"Unsupported platform: {system}")
                except Exception as e:
                    print(f"Failed to open file manager: {e}")

            open_file_manager()
        elif in_there(key.plus_days_keywords, string_transcription):
            days = re.findall(r'\d+', string_transcription)
            if 0 < len(days) < 2:
                today = datetime.datetime.now()

                future_date = today + datetime.timedelta(days=int(days[0]))

                month_name = future_date.strftime("%B")
                month_day = future_date.strftime("%d")

                winter.speak(f"{days[0]} days from now, it will be, {month_day} of {month_name}")
            else:
                winter.speak(
                    "I am currently getting two number of days to add on from today. Could you please try again...")

        elif in_there(key.introduce_keywords, string_transcription):
            winter.speak(f"I am {winter.name}! Your assistant.")

        elif in_there(key.stop_keywords, string_transcription):
            winter.sleep()
            break
        elif in_there(key.kill_keywords, string_transcription):
            winter.speak("Killing my service.")
            winter.kill()
            sys.exit()
        elif in_there(key.asking_time_keywords, string_transcription):
            now = datetime.datetime.now()
            hour = now.strftime("%I")
            minute = now.strftime("%M")
            am_pm = now.strftime("%p").lower()

            if minute == "00":
                speakable_time = f"It's {hour} o'clock {am_pm}."
            else:
                speakable_time = f"It's {hour}:{minute} {am_pm}."

            winter.speak(speakable_time)
        elif in_there(key.asking_day_keywords, string_transcription):
            now = datetime.datetime.now()
            day = now.strftime("%A")
            winter.speak(f"Today is {day}.")

        elif in_there(key.asking_date_keywords, string_transcription):
            now = datetime.datetime.now()
            day = now.strftime("%d").lstrip('0')
            month = now.strftime("%B")
            year = now.strftime("%Y")

            speakable_date = f"Today is {month} {day}, {year}."
            winter.speak(speakable_date)
        elif in_there(key.asking_year_keywords, string_transcription):
            now = datetime.datetime.now()
            year = now.strftime("%Y")
            winter.speak(f"The current year is {year}.")

        elif in_there(key.simple_greetings_keywords, string_transcription):
            response = res.simple_greetings_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(f"{response[random_no]}")
            ask_anything_else = False
        elif in_there(key.time_based_greetings_keywords, string_transcription):
            response = res.formal_greetings_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.inquiry_greetings_keywords, string_transcription):
            response = res.formal_greetings_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.formal_greetings_keywords, string_transcription):
            response = res.formal_greetings_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.simple_thanks_keywords, string_transcription):
            response = res.simple_thanks_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.emphatic_thanks_keywords, string_transcription):
            response = res.emphatic_thanks_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.appreciation_keywords, string_transcription):
            response = res.appreciation_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.simple_apology_keywords, string_transcription):
            response = res.simple_apology_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.formal_apology_keywords, string_transcription):
            response = res.formal_apology_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.simple_confirmation_keywords, string_transcription):
            response = res.simple_confirmation_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.emphatic_confirmation_keywords, string_transcription):
            response = res.emphatic_confirmation_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.formal_confirmation_keywords, string_transcription):
            response = res.formal_confirmation_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.simple_rejection_keywords, string_transcription):
            response = res.simple_rejection_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.emphatic_rejection_keywords, string_transcription):
            response = res.emphatic_rejection_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.polite_rejection_keywords, string_transcription):
            response = res.polite_rejection_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.current_weather_keywords, string_transcription):
            fetch_weather()
            response = [
                f"The current weather is {weather_data['weather'][0]['description']} with a temperature of {kelvin_to_celsius(weather_data['main']['temp'])} degrees Celsius.",
                f"It's currently {weather_data['weather'][0]['description']} and {kelvin_to_celsius(weather_data['main']['temp'])} degrees Celsius.",
                f"The weather right now is {weather_data['weather'][0]['description']} with a temperature of {kelvin_to_celsius(weather_data['main']['temp'])} degrees Celsius.",
                f"Currently, it's {weather_data['weather'][0]['description']} and {kelvin_to_celsius(weather_data['main']['temp'])} degrees Celsius."
            ]

            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])

        elif in_there(key.simple_help_keywords, string_transcription):
            response = res.simple_help_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.request_help_keywords, string_transcription):
            response = res.request_help_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.polite_help_keywords, string_transcription):
            response = res.polite_help_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.general_feedback_keywords, string_transcription):
            response = res.general_feedback_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.criticism_keywords, string_transcription):
            response = res.criticism_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.advice_keywords, string_transcription):
            response = res.advice_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.current_location_keywords, string_transcription):
            response = res.current_location_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.find_location_keywords, string_transcription):
            response = res.find_location_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.specific_location_keywords, string_transcription):
            response = res.specific_location_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.basic_personal_info_keywords, string_transcription):
            response = res.basic_personal_info_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.origin_personal_info_keywords, string_transcription):
            response = res.origin_personal_info_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.professional_personal_info_keywords, string_transcription):
            response = res.professional_personal_info_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.interest_personal_info_keywords, string_transcription):
            response = res.interest_personal_info_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.general_jokes_keywords, string_transcription):
            response = res.general_jokes_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.specific_jokes_keywords, string_transcription):
            response = res.specific_jokes_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.general_news_keywords, string_transcription):
            response = res.general_news_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.specific_news_keywords, string_transcription):
            response = res.specific_news_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.general_music_keywords, string_transcription):
            response = res.general_music_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.specific_music_keywords, string_transcription):
            response = res.specific_music_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.music_preference_keywords, string_transcription):
            response = res.music_preference_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.general_sports_keywords, string_transcription):
            response = res.general_sports_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.sports_updates_keywords, string_transcription):
            response = res.general_sports_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.sports_entities_keywords, string_transcription):
            response = res.general_sports_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.specific_sports_keywords, string_transcription):
            response = res.general_sports_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])

        elif in_there(key.recommendation_movie_keywords, string_transcription):
            response = res.simple_greetings_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif in_there(key.file_manager_keywords, string_transcription):
            response = res.filemanager_successful_responses
            random_no = random.randint(0, len(response) - 1)
            winter.speak(response[random_no])
        elif is_question(transcription):
            answer = question_answering(transcriptionFormatted)
            winter.speak(answer)
        is_next_round = True


if __name__ == "__main__":
    assistant_thread = threading.Thread(target=main, args=(False,))
    assistant_thread.start()
