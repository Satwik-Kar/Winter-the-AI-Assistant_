import datetime

import geocoder
import requests
import random
import sys
from Winter import Winter
import os

location = geocoder.ip('me')
weather_data = None
is_next_round = False
from transformers import pipeline


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

    def question_answering(question):
        try:

            # Load the pipeline with the text2text-generation task
            pipe = pipeline("text2text-generation", model="google/flan-t5-large", device=0)
            with open("intelligence/intelligence.txt", 'r') as file:
                # Step 2: Read the entire content of the file
                file_content = file.read()
            input_text = f"question={question} context={file_content}"

            # Get the answer
            result = pipe(input_text, max_length=128, num_return_sequences=1)
            # Print the result
            return result[0]['generated_text']
        except Exception as e:
            print(f"Error loading model or generating text: {e}")

    def is_question(prompt):
        words = word_tokenize(prompt.lower())
        questions_words = ["what", "when", "where", "why", "how", "who", "whom", "is", "are", "do", "does", "can"]
        question_patterns = ["are you", "can you", "what is", "how are"]
        for pattern in question_patterns:
            if pattern in prompt.lower():
                return True
        if words[0] in questions_words:
            return True

        return False

    def format_transcription(transcription):
        # Tokenize to get sentences
        try:
            sentences = sent_tokenize(transcription)

            # Process each sentence
            formatted_sentences = []
            for sentence in sentences:

                isQuestion = is_question(sentence)

                # Add punctuation and capitalize
                if isQuestion:
                    formatted_sentence = sentence.strip() + " ?"
                else:
                    formatted_sentence = sentence.strip() + " ."

                # Capitalize first letter
                formatted_sentence = formatted_sentence.capitalize()

                # Append to formatted sentences list
                formatted_sentences.append(formatted_sentence)

            # Join sentences back into a single string
            formatted_transcription = " ".join(formatted_sentences)
            return formatted_transcription
        except Exception as e:
            print(f"Error formatting transcription: {e}")

    def in_there(smaller_chunks, large_string):
        found = False
        for chunk in smaller_chunks:
            if chunk in large_string:
                found = True
                print(chunk)
                break

        if found:
            return True
        else:
            return False

    global is_next_round
    winter = Winter()
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
    introduce_keywords = {
        "name", "who are", "call", "introduce", "yourself", "ai"
    }
    stop_keywords = {
        "stop", "exit", "quit", "end", "terminate", "close", "bye",
        "goodbye", "shutdown", "cancel", "halt", "pause", "dismiss",
        "leave", "log out", "shut down", "turn off", "see you"
    }
    kill_keywords = {
        'kill', 'service'
    }
    asking_time_keywords = {
        "what time", "when", "at what time", "time is it", "current time",
        "now", "right now", "exact time", "clock", "o'clock",
        "am", "pm", "midnight", "noon", "early", "late"
    }
    asking_date_keywords = {
        "what date", "which date", "today's date", "current date",
        "date is it", "date today", "on which date"
    }
    asking_day_keywords = {"what day", "which day", "day is it", "today", "tomorrow", "yesterday",
                           "day of the week", "day today", "weekday", "weekend"
                           }
    asking_month_keywords = {
        "what month", "which month", "month is it", "current month",
        "month today", "month are we in"
    }
    asking_year_keywords = {
        "what year", "which year", "year is it", "current year",
        "year today", "year are we in"
    }

    while True:

        response = winter.recognize(is_next_round)

        if response["success"]:
            transcriptionFormatted = str(format_transcription(response["transcription"]))
            transcription = str(response["transcription"])
            winter.speak("You said: " + transcriptionFormatted)
            words = transcription.lower()
            print(words)
            if "none" in words:
                winter.sleep()
                break

            elif in_there(introduce_keywords, words) and in_there(stop_keywords, words):
                winter.speak("I detected conflicting commands. Please clarify.")

            elif in_there(introduce_keywords, words):
                winter.speak(f"I am {winter.name}! Your assistant.")

            elif in_there(stop_keywords, words):
                winter.sleep()
                break
            elif in_there(kill_keywords, words):
                winter.speak("Killing my service.")
                winter.kill()
                sys.exit()
            elif in_there(asking_time_keywords, words):
                now = datetime.datetime.now()
                hour = now.strftime("%I")
                minute = now.strftime("%M")
                am_pm = now.strftime("%p").lower()

                if minute == "00":
                    speakable_time = f"It's {hour} o'clock {am_pm}."
                else:
                    speakable_time = f"It's {hour}:{minute} {am_pm}."

                winter.speak(speakable_time)
            elif asking_day_keywords.intersection(words):
                now = datetime.datetime.now()
                day = now.strftime("%A")
                winter.speak(f"Today is {day}.")

            elif asking_date_keywords.intersection(words):
                now = datetime.datetime.now()
                day = now.strftime("%d").lstrip('0')
                month = now.strftime("%B")
                year = now.strftime("%Y")

                speakable_date = f"Today is {month} {day}, {year}."
                winter.speak(speakable_date)
            elif asking_year_keywords.intersection(words):
                now = datetime.datetime.now()
                year = now.strftime("%Y")
                winter.speak(f"The current year is {year}.")
            elif asking_month_keywords.intersection(words):
                now = datetime.datetime.now()
                month = now.strftime("%B")
                winter.speak(f"The current month is {month}.")
            elif is_question(transcription):

                answer = question_answering(transcriptionFormatted)
                winter.speak(answer)
            is_next_round = True
        elif response["error"]:
            print("ERROR: " + response["error"])
            winter.speak("I couldn't understand what you said. Please try again.")


if __name__ == "__main__":
    # fetch_weather()
    main(from_wake_word=False)
