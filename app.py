from gtts import gTTS
import os
import speech_recognition as sr
from datetime import datetime
import gradio as gr
from flask import Flask, render_template_string, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Initialize an empty list to store orders
orders = []
user_preferences = {"diet": None}  # Default to None for explicit user selection

# Define the menu directly in the script (no external JSON file needed)
menu = {
    "main_course": {
        "vegetarian": {
            "paneer butter masala": {"type": "vegetarian"},
            "dal makhani": {"type": "vegetarian"},
            "masala dosa": {"type": "vegetarian"},
            "idli sambhar": {"type": "vegetarian"},
            "fried rice": {"type": "vegetarian"},
            "hakka noodles": {"type": "vegetarian"}
        },
        "halal": {
            "butter chicken": {"type": "halal"},
            "hyderabadi biryani": {"type": "halal"},
            "chilli chicken": {"type": "halal"},
            "fish curry": {"type": "halal"},
            "tandoori chicken": {"type": "halal"},
            "prawns masala": {"type": "halal"}
        },
        "all": {
            "masala chai": {"type": "all"},
            "lassi": {"type": "all"},
            "cold coffee": {"type": "all"},
            "fresh lime soda": {"type": "all"}
        },
        "biryani": {
            "vegetarian biryani": {"type": "vegetarian"},
            "paneer biryani": {"type": "vegetarian"},
            "chicken biryani": {"type": "halal"},
            "mutton biryani": {"type": "halal"}
        }
    },
    "starters": {
        "vegetarian": {
            "veg pakora": {"type": "vegetarian"},
            "paneer tikka": {"type": "vegetarian"}
        },
        "halal": {
            "chicken wings": {"type": "halal"},
            "fish fry": {"type": "halal"}
        }
    },
    "drinks": {
        "all": {
            "masala chai": {"type": "all"},
            "lassi": {"type": "all"},
            "cold coffee": {"type": "all"},
            "fresh lime soda": {"type": "all"}
        }
    },
    "desserts": {
        "all": {
            "gulab jamun": {"type": "all"},
            "rasgulla": {"type": "all"}
        }
    }
}

# Function to speak text using gTTS
def speak_text(text):
    tts = gTTS(text=text, lang='en')
    tts.save("output.mp3")
    os.system("mpg321 output.mp3")  # Play the generated audio

# Function to get greeting
def get_greeting():
    current_hour = datetime.now().hour
    if current_hour < 12:
        return "Good morning!"
    elif 12 <= current_hour < 18:
        return "Good afternoon!"
    else:
        return "Good evening!"

# Function to filter menu based on user preferences
def filter_menu(menu):
    filtered_menu = {}
    if user_preferences["diet"] == "all":
        for category in menu.values():
            for subcategory, items in category.items():
                for dish, details in items.items():
                    filtered_menu[dish] = details
    else:
        for category in menu.values():
            for subcategory, items in category.items():
                for dish, details in items.items():
                    if "type" not in details:
                        continue
                    if user_preferences["diet"] == details["type"] or details["type"] == "all":
                        filtered_menu[dish] = details
    return filtered_menu

# Function to process commands
def process_command(command):
    global orders, user_preferences
    command = command.lower()

    if "vegetarian" in command:
        user_preferences["diet"] = "vegetarian"
        speak_text("Vegetarian preference set.")
        return "Vegetarian preference set."
    elif "halal" in command:
        user_preferences["diet"] = "halal"
        speak_text("Halal preference set.")
        return "Halal preference set."
    elif "all" in command:
        user_preferences["diet"] = "all"
        speak_text("Mixed preference set.")
        return "Mixed preference set."
    
    if "reset" in command:
        user_preferences["diet"] = None
        speak_text("Diet preference has been reset.")
        return "Diet preference has been reset."

    if user_preferences["diet"] is None:
        speak_text("Please set your dietary preference (vegetarian, halal, or mix) before proceeding.")
        return "Please set your dietary preference (vegetarian, halal, or mix) before proceeding."

    filtered_menu = filter_menu(menu)

    if "menu" in command or "show me the menu" in command:
        if filtered_menu:
            menu_list = ", ".join(filtered_menu.keys())
            speak_text(f"Our menu includes: {menu_list}")
            return f"Our menu includes: {menu_list}"
        else:
            speak_text("No items match your preferences.")
            return "No items match your preferences."

@app.route('/')
def home():
    greeting = get_greeting()
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Voice Assistant</title>
    </head>
    <body>
        <h1>{{ greeting }}</h1>
        <p>Welcome to the Restaurant. Please type your dietary preference or command!</p>
        <form id="userInputForm">
            <label for="user_input">Say Something:</label><br><br>
            <input type="text" id="user_input" name="user_input" required>
            <button type="submit">Submit</button>
        </form>
        <p id="response"></p>
        <script>
            document.getElementById("userInputForm").addEventListener("submit", function(event){
                event.preventDefault();
                const userInput = document.getElementById("user_input").value;
                fetch("/process", {
                    method: "POST",
                    body: new URLSearchParams({
                        "user_input": userInput
                    }),
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById("response").innerText = "Response: " + data.response;
                });
            });
        </script>
    </body>
    </html>
    ''', greeting=greeting)

@app.route('/process', methods=['POST'])
def process():
    user_input = request.form['user_input']
    response = process_command(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)