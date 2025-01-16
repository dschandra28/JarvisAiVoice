import pyttsx3  # pip install pyttsx3
import speech_recognition as sr  # pip install speechRecognition
import datetime
import wikipedia  # pip install wikipedia
import webbrowser
import os
import smtplib

# Define food menu
menu = {
    'Bread': ['Plain Bread', 'Butter Bread', 'Garlic Bread'],
    'Curries': ['Paneer Butter Masala', 'Dal Tadka', 'Butter Chicken'],
    'Biryani': ['Veg Biryani', 'Chicken Biryani', 'Mutton Biryani'],
    'Drinks': ['Coke', 'Lemonade', 'Mango Lassi']
}

# Initialize speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning!")
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")

    speak("Welcome to the restaurant! I am your assistant. How may I help you with your order today?")

def takeCommand():
    # It takes microphone input from the user and returns string output
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception as e:
        print("Say that again please...")
        return "None"
    return query

def showMenu():
    speak("Here is our menu:")
    for category, items in menu.items():
        speak(f"Category: {category}")
        for item in items:
            speak(f" - {item}")
    speak("Please tell me what you'd like to order.")

def processOrder(query):
    query = query.lower()
    order = []
    
    # Search for the ordered items in the menu
    for category, items in menu.items():
        for item in items:
            if item.lower() in query:
                order.append(item)

    if len(order) > 0:
        speak(f"You've ordered: {', '.join(order)}")
        return order
    else:
        speak("Sorry, I couldn't find that on the menu. Please try again.")
        return []

def askForMore():
    speak("Would you like to add more items to your order? Please say 'yes' to add more or 'no' to proceed with your order.")

def suggestComplementary(order):
    # Suggest complementary dishes
    if 'butter chicken' in order or 'dal tadka' in order:
        speak("How about some garlic bread to go with your curry?")
    elif 'veg biryani' in order or 'chicken biryani' in order:
        speak("Would you like a drink with your biryani, perhaps a mango lassi or a coke?")
    else:
        speak("Would you like something to drink with your order? We have coke, lemonade, and mango lassi.")

def finalConfirmation(order):
    if order:
        speak(f"Your final order is: {', '.join(order)}.")
        speak("Would you like to proceed with this order or change something?")
        confirmation = takeCommand().lower()
        
        if 'proceed' in confirmation or 'place' in confirmation or 'final' in confirmation:
            speak("Thank you for your order! Your food will arrive shortly.")
            speak("Enjoy your meal!")
            return True
        elif 'change' in confirmation or 'modify' in confirmation:
            speak("No problem! Let's modify your order.")
            return False
        else:
            speak("I didn't quite understand. Would you like to proceed with your order?")
            return False
    else:
        speak("It seems you didn't order anything. Please tell me what you'd like to order.")
        return False

def sendEmail(to, content):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('youremail@gmail.com', 'your-password')
    server.sendmail('youremail@gmail.com', to, content)
    server.close()

if __name__ == "__main__":
    wishMe()

    while True:
        order_list = []
        speak("What would you like to order?")
        query = takeCommand().lower()

        if 'show me the menu' in query:
            showMenu()

        # Take first order
        order = processOrder(query)
        if order:
            order_list.extend(order)

        # Ask if they want more items
        askForMore()
        more_order = takeCommand().lower()

        while 'yes' in more_order:
            speak("Please tell me what else you'd like to order.")
            query = takeCommand().lower()
            order = processOrder(query)
            if order:
                order_list.extend(order)
            suggestComplementary(order)  # Suggest complementary items
            askForMore()
            more_order = takeCommand().lower()

        # Final confirmation
        if finalConfirmation(order_list):
            break
        else:
            order_list = []  # Reset order and restart process if user wants to change
