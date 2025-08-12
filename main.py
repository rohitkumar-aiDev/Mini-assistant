import speech_recognition as sr
import webbrowser
import pyttsx3 
import musicLibrary
import difflib   # For fuzzy matching of song names
import feedparser
import requests
from openai import OpenAI


recognizer = sr.Recognizer()
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()
# This function checks if the input text contains a wake word
def is_wake_word(text):
    wake_words = ["jarvis", "jarvish", "jarvez", "jervis", "jarwish", "javis", "420"]
    words = text.lower().split()
    for word in words:
        match = difflib.get_close_matches(word, wake_words, n=1, cutoff=0.7)
        if match:
            return True
    return False
def fetch_google_news(language="en"):
    if language == "hi":
        url = "https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi"
    else:
        url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"

    feed = feedparser.parse(url)
    news_titles = [entry.title for entry in feed.entries[:5]]
    return news_titles

def aiprocess(command):
    client = OpenAI(
       api_key = "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"
    )
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages= [
            {"role": "system", "content": "You are a virtual assistant name jarvis skill in general task like alexa or google cloud"},
                {"role": "user", "content": command}
        ]
    )
    return completion.choices[0].message.content.strip()


def processCommand(c):
    if "open google" in c.lower():
        speak("opening google")
        webbrowser.open("https://www.google.com")
    elif "open youtube" in c.lower():
        speak("opening youtube")
        webbrowser.open("https://www.youtube.com")
    elif "open facebook" in c.lower():
        speak("opening facebook")
        webbrowser.open("https://www.facebook.com")
    elif "open instagram" in c.lower():
        speak("opening instagram")
        webbrowser.open("https://www.instagram.com")
    elif c.lower().startswith("play "):
        song_name = c.lower().replace("play ", "").strip()
        print(f"Song requested: {song_name}")
        # Lowercase all keys once for matching
        song_library = {k.lower(): v for k, v in musicLibrary.music.items()}
         # Use difflib to find best match
        best_match = difflib.get_close_matches(song_name, song_library.keys(), n=1, cutoff=0.4)
        if best_match:
            matched_song = best_match[0]
            print(f"Best match: {matched_song}")
            speak(f"playing {matched_song}")
            webbrowser.open(song_library[matched_song])
        else:
            speak(f"Sorry, I don't have {song_name} in my music library.")

    elif "news" in c.lower():
        # news_api = "ad5c33645a9e49f0ae2e0837f3b4add3"
        # url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api}"
        if "hindi" in c.lower():
            language = "hi"
        else:
            language = "en"
        try:
            news_titles = fetch_google_news(language)
            if news_titles:
              for title in news_titles:
                  print(title)
                  speak(title)
                  engine.runAndWait()
            else:
                speak("Failed to fetch news. Please check the API key or try again later.")
            opening_url = f"https://news.google.com/home?hl=hi&gl=IN&ceid=IN:{language}"
            webbrowser.open(opening_url)

        except requests.exceptions.RequestException as e:
            speak("An error occurred while fetching the news.")
            print(f"Request error: {e}")

    else:
        try:
            output = aiprocess(c)
            speak(output)
        except OpenAI.error.OpenAIError as e:
            if e.http_status == 429:
                speak("Sorry, I have reached my usage limit for now. Please try again later.")
            else:
                speak("An error occurred while processing your request.")
            print(f"OpenAI API error: {e}")

if __name__ == "__main__":
    speak("Intializing Jarvis...")
    while(True):
            print("Recognizing...")
            try:
                with sr.Microphone() as source:
                    print("Listening")
                    audio = recognizer.listen(source, timeout=4, phrase_time_limit=3)
                    word = recognizer.recognize_google(audio)
                    print("You said:", word)
                    if is_wake_word(word):
                        engine.say("yes Rohit, How can I assist you?")
                        with sr.Microphone() as source:
                            print("jarvish active")
                            audio = recognizer.listen(source)
                            command = recognizer.recognize_google(audio)
                            processCommand(command)
            except sr.WaitTimeoutError:
                print("Timeout: No speech detected.")
            except sr.UnknownValueError:
                print("Speech Recognition could not understand audio.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
