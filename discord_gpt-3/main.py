import discord
import os
from dotenv import load_dotenv
from textwrap import dedent
import openai 

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
completion = openai.Completion()
#######################################
# Chatbot prompt
#######################################
start_sequence="\nElon:"
restart_sequence="\n\nStranger:"
session_prompt=dedent(
             """Elon Musk and a Stranger are having a conversation. Use Elon's quotes to respond to the stranger's questions.

            Stranger: When do you plan to send humans on Mars?
            Elon: It will most probably happen in 2030
  
            Stranger:"""
        ).replace("\n", "\\n")
print(session_prompt)

# This is our basic function to send our queries to the textsynth API
# We can change the model settings in the request headers
def ask(question, chat_log=None):
  if chat_log is None: 
    chat_log = session_prompt 
  prompt_text = f'{chat_log}{restart_sequence}: {question}{start_sequence}:'
  response = openai.Completion.create(
  engine="text-davinci-001",
  prompt=prompt_text,
  temperature=0.8,
  max_tokens=150,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0.3,
  stop=["\n"],
  )
  story = response['choices'][0]['text']
  return str(story)
 
# This is a helper function that appends our chat history to every request
# This is needed in order to add some memory and consistency to our chatbot
def append_interaction_to_chat_log(question, answer, chat_log=None):
  if chat_log is None: 
    chat_log = session_prompt 
  return f'{chat_log}{restart_sequence} {question}{start_sequence}{answer}'

#########################
# DISCORD SETTINGS
#########################
# Loading our discord env variables
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

# EVENT LISTENER FOR WHEN THE BOT HAS SWITCHED FROM OFFLINE TO ONLINE.
@client.event
async def on_ready():
  guild = discord.utils.get(client.guilds, name=GUILD)
  print(
    f'{client.user} is connected to the following guild:\n'
    f'{guild.name}(id: {guild.id})'
  )

# EVENT LISTENER FOR WHEN A NEW MESSAGE IS SENT TO A CHANNEL.
@client.event
async def on_message(message):

  global chat_log
  
  if message.author == client.user:
    return

  #if client.user.mentioned_in(message):
  incoming_msg = message.content
  print(message.content)
  try:
    chat_log
  except NameError:
    chat_log=""
    print("empty")
  answer = ask(incoming_msg, chat_log)
  chat_log = append_interaction_to_chat_log(incoming_msg, answer, chat_log)
  #print(answer)
  print("log:"+chat_log)
  await message.channel.send(answer)

async def shutdown(context):
    exit()

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. 
client.run(TOKEN)
