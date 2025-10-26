# DiscordGPT

A Discord Bot integrated with ChatGPT to chat and also stream YouTube urls. 

## Features

 - Responds to user messages in Discord channels using !chat.
 - Keeps a log of previous conversation history local to each channel.
 - Ability to join discord calls and stream YouTube urls for playback.

## Installation

Clone the repository:

```bash
https://github.com/csummerson/DiscordGPT.git
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install [FFMPEG](https://ffmpeg.org/download.html)

## Settings

In settings.toml, input your

- Discord Token
- OpenAI API Key
- Owner ID (to limit use of /destroy)

Also make sure to give the bot

- A status
- Personality prompt

## Running

```bash
py bot.py
```

# History

This was a project originally started in around 2022, when I wanted to try and create something to integrate with AI. After originally trying to make it with C# (my most comfortable language), I later shifted over to python due to better libraries and ease of use. 
I also use a different version of this bot to watch my YouTube and Twitch channels and send notifications to specific channels in discord servers, though this functionality has been cut since it is unlikely to be useful to someone wanting a Discord bot.
