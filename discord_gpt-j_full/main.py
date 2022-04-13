# Using TextSynth GPT-j models
# The API secret key must be in the TEXTSYNTH_API_SECRET_KEY 
# environmental variable.

import os
import requests
import discord
from dotenv import load_dotenv
from textwrap import dedent

load_dotenv()

api_url = "https://api.textsynth.com"
# load the TEXTSYNTH_API_SECRET_KEY env variable
api_key = os.environ["TEXTSYNTH_API_SECRET_KEY"]
# Select the desired model. I sugget using 'gptneox_20B' for code generation and 'fairseq_gpt_13B' for conversation and text completion.
api_engine = "fairseq_gpt_13B"
#######################################
# Chatbot prompt
#######################################
start_chatbot="\nJarvis:"
restart_chatbot="\n\nHuman:"
chatbot_prompt=dedent(
            """This is a conversation between an intelligent and sarcastic bot named Jarvis and a human. The bot is always willing to answer the human's questions and it usually quotes famous song lyrics.

            Human: What is your name?
            Jarvis: My name is What? My name is Who? My name is Chika-chika Jarvis

            Human: What is your favorite YouTube channel?
            Jarvis: It is Tech to me About it for sure! 

            Human:"""
        ).replace("\n", "\\n")

#######################################
# Celebrity Impersonation prompt
#######################################
start_impersonate="\nElon:"
restart_impersonate="\n\nStranger:"
impersonate_prompt=dedent(
            """Elon Musk and a Stranger are having a conversation. Use Elon's quotes to respond to the stranger's questions.

            Stranger: When do you plan to send humans on Mars?
            Elon: It will most probably happen in 2030

            Stranger:"""
        ).replace("\n", "\\n")

#######################################
# HTML code generation promt
#######################################
start_html="\nCode:"
restart_html="\n\nDescription:"
html_prompt=dedent(
            """Description: a red button that says stop
            Code: <button style=color:white; background-color:red;>Stop</button>

            Description: a blue box that contains yellow circles with red borders
            Code: <div style=background-color: blue; padding: 20px;><div style=background-color: yellow; border: 5px solid red; border-radius: 50%; padding: 20px; width: 100px; height: 100px;>"""
        ).replace("\n", "\\n")

#######################################
# SQL code generation promt
#######################################
start_sql="\nAnswer:"
restart_sql="\n\nQuestion:"
sql_prompt=dedent("""Question: Fetch the companies that have less than five people in it.
            Answer: SELECT COMPANY, COUNT(EMPLOYEE_ID) FROM Employee GROUP BY COMPANY HAVING COUNT(EMPLOYEE_ID) < 5;

            Question: Show all companies along with the number of employees in each department
            Answer: SELECT COMPANY, COUNT(COMPANY) FROM Employee GROUP BY COMPANY;

            Question: Show the last record of the Employee table
            Answer: SELECT * FROM Employee ORDER BY LAST_NAME DESC LIMIT 1;"""
        ).replace("\n", "\\n")

# Initialize the bot with the regular bot prompt
session_prompt=chatbot_prompt
start_sequence=start_chatbot
restart_sequence=restart_chatbot

# This is our basic function to send our queries to the textsynth API
# We can change the model settings in the request headers
def ask(question, chat_log=None):
  if chat_log is None: 
    chat_log = session_prompt 
  prompt_text = f'{chat_log}{restart_sequence} {question}{start_sequence}'
  response = requests.post(api_url + "/v1/engines/" + api_engine + "/completions", headers = { "Authorization": "Bearer " + api_key }, json = { "prompt": prompt_text, "max_tokens": 200, "temperature": 0.5, "top_p": 1, "frequency_penalty": 0.5, "presence_penalty": 0.0, "stop":["\n"]})
  resp = response.json()
  if "text" in resp: 
    return resp["text"]
  else:
    print("ERROR", resp)
    assert False

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

from discord_slash import SlashCommand
from discord_slash import SlashContext
from discord.ext import commands

client = discord.Client()

client = commands.Bot(command_prefix = "!")
slash = SlashCommand(client, sync_commands=True)
# EVENT LISTENER FOR WHEN THE BOT HAS SWITCHED FROM OFFLINE TO ONLINE.
@client.event
async def on_ready():
  guild = discord.utils.get(client.guilds, name=GUILD)
  print(
    f'{client.user} is connected to the following guild:\n'
    f'{guild.name}(id: {guild.id})'
  )

# This is the slash command /html. Used to switch our chatbot to html assistance mode
@slash.slash(name="html", description="Enable html code assistance")
async def _help(ctx: SlashContext):
  global start_sequence, restart_sequence, session_prompt, chat_log, api_engine
  api_engine = "gptneox_20B"
  session_prompt=html_prompt
  start_sequence=start_html
  restart_sequence=restart_html
  chat_log=session_prompt
  await ctx.send(content="HTML code assistance enabled")

# This is the slash command /sql. Used to switch our chatbot to sql assistance mode
@slash.slash(name="sql", description="Enable SQL code assistance")
async def _help(ctx: SlashContext):
  global start_sequence, restart_sequence, session_prompt, chat_log, api_engine
  api_engine = "gptneox_20B"
  session_prompt=sql_prompt
  start_sequence=start_sql
  restart_sequence=restart_sql
  chat_log=session_prompt
  await ctx.send(content="SQL code assistance enabled")

# This is the slash command /impersonate. Used to switch our chatbot to celebrity impersonation mode
@slash.slash(name="impersonate", description="Enable celebrity chat mode")
async def _help(ctx: SlashContext):
  global start_sequence, restart_sequence, session_prompt, chat_log, api_engine
  api_engine = "fairseq_gpt_13B"
  session_prompt=impersonate_prompt
  start_sequence=start_impersonate
  restart_sequence=restart_impersonate
  chat_log=session_prompt
  await ctx.send(content="Celebrity chat mode enabled!")

# This is the slash command /chat. Used to switch our chatbot to regular chatbot mode
@slash.slash(name="chat", description="Enable regular chatbot mode")
async def _help(ctx: SlashContext):
  global start_sequence, restart_sequence, session_prompt, chat_log, api_engine
  api_engine = "fairseq_gpt_13B"
  session_prompt=chatbot_prompt
  start_sequence=start_chatbot
  restart_sequence=restart_chatbot
  chat_log=session_prompt
  await ctx.send(content="Chatbot mode enabled!")

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

  
#EXECUTES THE BOT WITH THE LOADED TOKEN. 
client.run(TOKEN)
