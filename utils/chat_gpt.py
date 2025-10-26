from openai import OpenAI
import tiktoken
import json
from config import OPEN_AI_KEY, EXTRANEOUS_PROMPT, DEFAULT_PROMPT, GPT_MODEL, TOKEN_LIMIT

client = OpenAI(api_key=OPEN_AI_KEY)
filename = "data.json"
data = {}

try:
    with open(filename, 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    print("Data file does not exist, starting from scratch.")
    data = {}
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

currentPrompt = EXTRANEOUS_PROMPT + DEFAULT_PROMPT

class ChatGPTHandler:
    @staticmethod
    def self_destruct():
        global data
        data = {}
        ChatGPTHandler.save_chat()
        print("System has been cleared of all settings, history, and prompts.")
    
    @staticmethod
    def clear_history(guild_id):
        global currentPrompt
        currentPrompt = data[guild_id][0]
        ChatGPTHandler.recreate_chat_history(guild_id)
    
    @staticmethod
    def create_history(guild_id):
        print("Creating new chat log with id: '" + guild_id + "'")
        data[guild_id] = [{"role": "system", "content": EXTRANEOUS_PROMPT + DEFAULT_PROMPT}]
    
    @staticmethod
    def add_chat_history(guild_id, msg):
        if not guild_id in data:
            ChatGPTHandler.create_history(guild_id)
        data[guild_id].append({"role": "user", "content": msg})
        ChatGPTHandler.trim_history(guild_id)
        ChatGPTHandler.save_chat()
    
    @staticmethod
    def recreate_chat_history(guild_id):
        data[guild_id] = [ {"role": "system", "content": currentPrompt} ]
        ChatGPTHandler.save_chat()
        print('Cleared chat history.')

    @staticmethod
    def restore_defaults(guild_id):
        ChatGPTHandler.set_prompt(guild_id, DEFAULT_PROMPT)
        ChatGPTHandler.recreate_chat_history(guild_id)
        print('Restored default settings.')

    @staticmethod
    def generate_response(guild_id):
        print('Generating response from ChatGPT...')
        
        chat = client.chat.completions.create(model=GPT_MODEL, messages=data[guild_id])
        reply = chat.choices[0].message.content
        data[guild_id].append({"role": "assistant", "content": reply})
        ChatGPTHandler.trim_history(guild_id)
        ChatGPTHandler.save_chat()
        return reply
    
    @staticmethod
    def generate_once_off(user_msg):
        print("Generating one-off response from ChatGPT...")
        
        messages = [
            {"role": "system", "content": EXTRANEOUS_PROMPT + DEFAULT_PROMPT},
            {"role": "user", "content": user_msg}
        ]

        chat = client.chat.completions.create(
            model=GPT_MODEL,
            messages=messages
        )

        reply = chat.choices[0].message.content
        return reply
    
    @staticmethod
    def count_tokens(guild_id):
        encoding = tiktoken.encoding_for_model(GPT_MODEL)
        totalTokens = 0
        for message in data[guild_id]:
            tokens = encoding.encode(message['content'])
            totalTokens += len(tokens)
        return totalTokens
        
    @staticmethod
    def trim_history(guild_id):
        trimmedMessages = 0
        tokenCount = ChatGPTHandler.count_tokens(guild_id)
        while (tokenCount > TOKEN_LIMIT):
            data[guild_id].pop(1)
            tokenCount = ChatGPTHandler.count_tokens(guild_id)
            trimmedMessages += 1

        if (trimmedMessages > 0):
            print(f'Purged {trimmedMessages} message(s).')

    @staticmethod
    def set_prompt(guild_id, prompt):
        global currentPrompt
        currentPrompt = EXTRANEOUS_PROMPT + prompt
        ChatGPTHandler.recreate_chat_history(guild_id)
        print(f'Set new lore to: {prompt}')

    @staticmethod
    def interject(guild_id):
        data[guild_id].append({"role": "system", "content": "Please interject to the previous user messages of your own accord."})

        return ChatGPTHandler.generate_response(guild_id)
    
    @staticmethod
    def save_chat():
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
            
    # See README
    @staticmethod
    def content_notification(title, discord_role_id):
        print("Notifing discord of new channel content with title: " + title)

        contentNotificationDefault = f'''Your creator, [], has uploaded a new video with the following title: {title}.
        Please inform their discord server of this fact in a way that demonstrates your annoyance. Include '<@&{discord_role_id}>' somewhere in your response to notify the correct people if it behooves you, this is not a requirement though, in fact, if the title is particulalry annoying, you may choose NOT to notify anyone.  '''
        
        txt = [{"role": "system", "content": EXTRANEOUS_PROMPT + DEFAULT_PROMPT}, {"role": "system", "content": contentNotificationDefault}]

        print('Generating response from ChatGPT...')

        chat = client.chat.completions.create(model=GPT_MODEL, messages=txt)
        reply = chat.choices[0].message.content
        
        return reply
    
    # See README
    @staticmethod
    def stream_notification(title):
        print(f"Notifing discord of new twitch content with title: {title}")

        contentNotificationDefault = f'''Your creator, [], has started a twitch stream with the following description: {title}.
        Please inform their discord server of this fact in a way that demonstrates your annoyance. Include '<@&1335807587098169395>' somewhere in your response if it behooves you, this is not a requirement though, in fact, if the title is particulalry annoying, you may choose NOT to notify anyone. 
        
        Always include this link with your message: https://www.twitch.tv/redacted
        '''
        
        txt = [{"role": "system", "content": EXTRANEOUS_PROMPT + DEFAULT_PROMPT}, {"role": "system", "content": contentNotificationDefault}]

        print('Generating response from ChatGPT...')

        chat = client.chat.completions.create(model=GPT_MODEL, messages=txt)
        reply = chat.choices[0].message.content

        return reply