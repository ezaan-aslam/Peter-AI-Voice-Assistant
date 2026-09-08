"""
Peter - Voice Assistant (Full Version)
----------------------------------------
Install these first:
    pip install SpeechRecognition pyttsx3 pyaudio pyautogui screen-brightness-control requests pygetwindow

Run:
    python peter.py

Say things like:
    "Peter open youtube"
    "Peter play Believer"
    "Peter search AI"
    "Peter open notepad"
    "Peter close notepad"     (closes any open window with "notepad" in its title)
    "Peter calculate 25 plus 50"
    "Peter what's the weather in Rawalpindi"
    "Peter tell me a joke"
    "Peter increase volume"
    "Peter take screenshot"
    "Peter stop"

NOTES ON SOME COMMANDS (read before using):
    - Shutdown / Restart / Lock: These affect your real computer.
      Shutdown and Restart commands here ask for confirmation before acting.
    - App paths (VS Code, Word, PowerPoint) assume they are installed normally
      on Windows and registered in PATH. If they don't open, see the comments
      near OPEN_APP_COMMANDS below to fix the path for your PC.
    - Weather uses the free wttr.in service - no API key needed, but needs
      internet.
"""

import speech_recognition as sr
import pyttsx3
import webbrowser
import subprocess
import datetime
import random
import re
import requests
import pygetwindow as gw
import pyautogui
import screen_brightness_control as sbc
import os
import ctypes
import winsound

engine = pyttsx3.init()
engine.setProperty('rate', 175)

OPEN_APP_COMMANDS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "vs code": "code",
    "word": "winword.exe",
    "powerpoint": "powerpnt.exe",
}

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "Why did the computer go to therapy? It had too many unresolved issues.",
    "Why do Java developers wear glasses? Because they can't C sharp.",
    "I told my computer I needed a break, and it said no problem, it'll go to sleep too.",
]


def speak(text):
    print(f"Peter: {text}")
    engine.say(text)
    engine.runAndWait()


def acknowledge():
    """Plays the Windows default notification sound, then says 'On it, sir.'"""
    try:
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception:
        pass
    speak("On it, sir.")


def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
        except sr.WaitTimeoutError:
            return ""

    try:
        text = recognizer.recognize_google(audio, language="en-US")
        print(f"You: {text}")
        return text.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("Please check your internet connection.")
        return ""


def close_window(keyword):
    """Finds any open window whose title contains the keyword and closes it."""
    try:
        matches = [w for w in gw.getAllWindows() if keyword.lower() in w.title.lower() and w.title.strip() != ""]
        if matches:
            matches[0].close()
            return matches[0].title
        return None
    except Exception:
        return None


def get_first_youtube_result(query):
    """Searches YouTube and returns the URL of the first video result."""
    try:
        search_url = f"https://www.youtube.com/results?search_query={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers, timeout=6)
        video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
        if video_ids:
            return f"https://www.youtube.com/watch?v={video_ids[0]}"
        return None
    except Exception:
        return None


def get_weather(city):
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3", timeout=5)
        return response.text
    except Exception:
        return None


def calculate(expression):
    expression = expression.replace("plus", "+")
    expression = expression.replace("minus", "-")
    expression = expression.replace("times", "*")
    expression = expression.replace("multiplied by", "*")
    expression = expression.replace("divided by", "/")
    expression = expression.replace("x", "*")

    try:
        allowed = set("0123456789+-*/(). ")
        if not set(expression) <= allowed:
            return None
        result = eval(expression)
        return result
    except Exception:
        return None


def handle_command(command):
    if "close" in command:
        acknowledge()
        target = command.replace("close", "").strip()
        closed_title = close_window(target)
        if closed_title:
            speak(f"Closed {closed_title}.")
        else:
            speak(f"I couldn't find an open window matching '{target}'.")

    elif "play" in command:
        song = command.replace("play", "").strip()
        acknowledge()
        video_url = get_first_youtube_result(song)
        if video_url:
            speak(f"Playing {song} now.")
            webbrowser.open(video_url)
        else:
            speak("I couldn't find that on YouTube, opening search results instead.")
            webbrowser.open(f"https://www.youtube.com/results?search_query={song}")

    elif "search" in command:
        query = command.replace("search", "").strip()
        acknowledge()
        webbrowser.open(f"https://www.google.com/search?q={query}")

    elif "youtube" in command:
        acknowledge()
        webbrowser.open("https://www.youtube.com")

    elif "chatgpt" in command:
        acknowledge()
        webbrowser.open("https://chat.openai.com")

    elif "gmail" in command:
        acknowledge()
        webbrowser.open("https://mail.google.com")

    elif "facebook" in command:
        acknowledge()
        webbrowser.open("https://www.facebook.com")

    elif "instagram" in command:
        acknowledge()
        webbrowser.open("https://www.instagram.com")

    elif "google" in command:
        acknowledge()
        webbrowser.open("https://www.google.com")

    elif "whatsapp" in command:
        acknowledge()
        webbrowser.open("https://web.whatsapp.com")

    elif "open notepad" in command:
        acknowledge()
        subprocess.Popen(OPEN_APP_COMMANDS["notepad"])

    elif "open calculator" in command:
        acknowledge()
        subprocess.Popen(OPEN_APP_COMMANDS["calculator"])

    elif "vs code" in command or "visual studio code" in command:
        acknowledge()
        subprocess.Popen(OPEN_APP_COMMANDS["vs code"], shell=True)

    elif "open word" in command:
        acknowledge()
        subprocess.Popen(OPEN_APP_COMMANDS["word"])

    elif "powerpoint" in command:
        acknowledge()
        subprocess.Popen(OPEN_APP_COMMANDS["powerpoint"])

    elif "open folder" in command:
        folder_name = command.replace("open folder", "").strip()
        path = os.path.join(os.path.expanduser("~"), folder_name.capitalize())
        if os.path.exists(path):
            acknowledge()
            os.startfile(path)
        else:
            speak(f"I couldn't find a folder called {folder_name}.")

    elif "joke" in command:
        speak(random.choice(JOKES))

    elif "weather" in command:
        city = command.replace("what's the weather in", "") \
                       .replace("whats the weather in", "") \
                       .replace("weather in", "") \
                       .replace("what's the weather", "") \
                       .replace("weather", "").strip()
        if not city:
            city = "Rawalpindi"
        result = get_weather(city)
        if result:
            speak(f"Here's the weather: {result}")
        else:
            speak("Sorry, I couldn't fetch the weather right now.")

    elif "calculate" in command:
        expression = command.replace("calculate", "").strip()
        result = calculate(expression)
        if result is not None:
            speak(f"The answer is {result}")
        else:
            speak("Sorry, I couldn't calculate that.")

    elif "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {now}")

    elif "increase volume" in command or "volume up" in command:
        acknowledge()
        pyautogui.press("volumeup", presses=5)

    elif "decrease volume" in command or "volume down" in command:
        acknowledge()
        pyautogui.press("volumedown", presses=5)

    elif "mute" in command:
        acknowledge()
        pyautogui.press("volumemute")

    elif "increase brightness" in command:
        acknowledge()
        current = sbc.get_brightness()[0]
        sbc.set_brightness(min(current + 20, 100))

    elif "decrease brightness" in command:
        acknowledge()
        current = sbc.get_brightness()[0]
        sbc.set_brightness(max(current - 20, 0))

    elif "screenshot" in command:
        filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = os.path.join(os.path.expanduser("~"), "Desktop", filename)
        pyautogui.screenshot(path)
        speak(f"Screenshot saved as {filename} on your Desktop.")

    elif "lock" in command:
        acknowledge()
        ctypes.windll.user32.LockWorkStation()

    elif "shutdown" in command:
        speak("Are you sure you want to shut down? Say 'yes shutdown' to confirm.")

    elif "yes shutdown" in command:
        speak("Shutting down the computer.")
        os.system("shutdown /s /t 5")

    elif "restart" in command:
        speak("Are you sure you want to restart? Say 'yes restart' to confirm.")

    elif "yes restart" in command:
        speak("Restarting the computer.")
        os.system("shutdown /r /t 5")

    elif "stop" in command or "shut down peter" in command or "exit" in command:
        speak("Goodbye!")
        return False

    else:
        speak("Sorry, I didn't understand that command.")

    return True


def main():
    speak("Good day Sir Ezaan, how you doing.")

    running = True
    while running:
        command = listen_command()

        if "peter" in command:
            actual_command = command.replace("peter", "").strip()
            if actual_command:
                running = handle_command(actual_command)
            else:
                speak("Yes? What can I do for you?")


if __name__ == "__main__":
    main()
