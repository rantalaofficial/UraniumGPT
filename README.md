# UraniumGPT
This is a minimalistic ChatGPT GUI wrapper that utilizes OpenAI API. It has all the functionality needed for basic LLM use.

## Features

- Supports text streaming from OpenAI API
- Renders responses in HTML
- Supports multiple chats
- Chats are automatically saved/loaded to/from a text file
- Selected model can be changed between messages

## How to use?

1. Make a file named "API_KEY" to the same folder as main.py and paste your OpenAI API key inside. 

2. Install Python 3 libraries:

`pip3 install --upgrade openai`

`pip3 install PyQt5`

`pip3 install mistune`

OpenAI library is needed for the API connection, PyQt5 is needed for the GUI and mistune for converting markdown syntax to HTML.

3. Launch the app!

`python3 main.py`

## Screenshot from the app:

![image](https://github.com/rantalaofficial/UraniumGPT/assets/33716618/7426c012-57db-46fb-b888-b7748cadd1ab)








