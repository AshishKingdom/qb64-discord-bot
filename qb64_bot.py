import os
from dotenv import load_dotenv
import discord
from datetime import datetime

#initialization 

load_dotenv()

client = discord.Client()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TEST_GUILD = os.getenv('DISCORD_GUILD_TESTING')


@client.event
async def on_ready():
	print("{} is connected to Discord!".format(client.user))

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	contents = message.content.split('\n')
	content_length = len(contents)
	if(contents[0].strip()=="%qb64"):

		print("{} has asked for running program ".format(message.author))
		#save the request done by user in a log file
		log_file = open("all-requests.log", "a")
		log_file.write("\n\n {} : {} has requested following command\n".format(datetime.now(), message.author))
		log_file.write('\n'.join(contents))
		log_file.close()

		response = ""
		execute = 0
		if(content_length>=4):
			
			code_pos = [0, 0]
			for i in range(0, len(contents)):
				if (contents[i]=="```" or contents[i]=="```vb"):
					if(code_pos[0]==0):
						code_pos[0] = i+1 # starting line of code from message
					else:
						code_pos[1] = i
						break

			if(code_pos[0]>0 and code_pos[1]>0 and code_pos[1]>code_pos[0]):
			#if(contents[1]=="```" and contents[content_length-1]=="```"):
				await message.add_reaction("⏳")
				
				f_hnd = open("source.txt", 'w')
				f_hnd.write('\n'.join(contents[code_pos[0]:code_pos[1]]))
				f_hnd.close()
				#saving output of the program in out.txt using Luke's L-Basid
				execute = os.system(".\\bin\\lbasic.exe -t source.txt>out.txt")
				f_hnd = open("out.txt", "r")
				if(execute==5): #returns 5 if the program was stuck in some kind of infinite loop
					response = f_hnd.read(1024) #in this case, we will send only 1024bytes of the output
				else:
					response = f_hnd.read()
				f_hnd.close()
				#time_taken = time.time()-start
				await message.add_reaction("✅")
				await message.clear_reaction("⏳")
				response = "_Output:-_\n```\n"+response+"\n```"
			else:
				response = "Please use proper codeblock syntax."
		else:
			response = "You are using INCORRECT syntax."
		await message.reply(response)


client.run(os.getenv('DISCORD_BOT_TOKEN'))