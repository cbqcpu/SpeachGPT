import sounddevice as sd
import openai
from scipy.io.wavfile import write

# Make sure to set your OpenAI API key
openai.api_key = 'You API KEY'

# Set the sample rate and duration for recording
samplerate = 16000  # Hertz
duration = 10  # seconds

# Create a callback function to record audio
def record_audio(filename):
    myrecording = sd.rec(int(samplerate * duration), samplerate=samplerate,
                         channels=1, blocking=True)
    write(filename, samplerate, myrecording)  # Save as WAV file

# Function to convert speech to text using Whisper
def speech_to_text(filename):
	audio_file= open(filename, "rb")
	response = openai.Audio.transcribe("whisper-1", audio_file)
	return response['text']

# Function to get a response from GPT-3.5-turbo
def chat_with_gpt(text):
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text}
        ]
    )
    return response['choices'][0]['message']['content']


import tkinter as tk
from threading import Thread
from datetime import datetime
import os
import time
# Keep track of the chat history
chat_history = []
filename = ''  # Initialize filename
recording_in_progress = False

def start_recording():
    global filename, recording_in_progress
    # Disable the 'Send' button
    send_button.config(state=tk.DISABLED)
    # Use a timestamp to give the file a unique name
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f'output_{timestamp}.wav'
    recording_in_progress = True
    Thread(target=record_audio, args=(filename,)).start()

def check_file_exists(filename):
    # Continually check if the file exists
    while not os.path.isfile(filename):
        time.sleep(1)  # Wait for a short period of time before checking again
    # Once the file exists, enable the 'Send' button
    send_button.config(state=tk.NORMAL)

def stop_recording():
    global recording_in_progress
    # Set recording_in_progress to False when the recording is done
    recording_in_progress = False
    # Start a new thread to check if the file exists
    Thread(target=check_file_exists, args=(filename,)).start()
def send_recording():
    if not recording_in_progress:
        text = speech_to_text(filename)
        chat_history.append(("You", text))
        update_chat_history()

        response = chat_with_gpt(text)
        chat_history.append(("GPT-3.5-turbo", response))
        update_chat_history()

def update_chat_history():
    chat_text.delete(1.0, tk.END)  # Clear the chat history
    for role, text in chat_history:
        chat_text.insert(tk.END, f"{role}: {text}\n")

root = tk.Tk()

record_button = tk.Button(root, text="Start Recording", command=start_recording)
record_button.pack()

stop_button = tk.Button(root, text="Stop Recording", command=stop_recording)
stop_button.pack()

send_button = tk.Button(root, text="Send", command=send_recording, state=tk.DISABLED)
send_button.pack()

chat_text = tk.Text(root)
chat_text.pack()

root.mainloop()
