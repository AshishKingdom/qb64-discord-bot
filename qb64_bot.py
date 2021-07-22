# @Author : AshishKingdom (Ashish Kushwaha)

import os
from dotenv import load_dotenv
import discord
import qb64_help_parser

#initialization 

load_dotenv()

client = discord.Client()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TEST_GUILD = os.getenv('DISCORD_GUILD_TESTING')


#load all qb64/qbasic keywords
keywords_known = []
f = open('keywords.txt', 'r')
keywords_known = f.read().split('\n')
f.close()

@client.event
async def on_ready():
    print("{} is connected to Discord!".format(client.user))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    contents = message.content.split('\n')
    # %qb64 command
    if(contents[0].strip()=="%qb64"):
        response = ""
        execute = 0
        debug = False
        if(len(contents)>=4):
            
            code_pos = [0, 0]
            for i in range(0, len(contents)):
                if (contents[i]=="```" or contents[i]=="```vb"):
                    if(code_pos[0]==0):
                        code_pos[0] = i+1 # starting line of code from message
                    else:
                        code_pos[1] = i
                        break
                #for debuging
                if(contents[i]=="'$debug-bot-cloud"):
                    debug = True
            if(debug):response+="[QB64_BOT_DEBUG_MODE]\n"


            if(code_pos[0]>0 and code_pos[1]>0 and code_pos[1]>code_pos[0]):
            #if(contents[1]=="```" and contents[content_length-1]=="```"):
                await message.add_reaction("⏳")

                if(debug):response+="[QB64_BOT: attemtping to save the code in '/tmp/source.txt']\n"

                try:
                    f_hnd = open("/tmp/source.txt", 'w')
                    f_hnd.write('\n'.join(contents[code_pos[0]:code_pos[1]]))
                    f_hnd.close()
                    if(debug):response+="[QB64-BOT: code saved in 'tmp/source.txt' successfully.]\n"
                except OSError:
                    response+="[QB64_BOT: Failed to write code in '/tmp/source.txt']\n"
                    await message.add_reaction("❗")
                    await message.clear_reaction("⏳")
                    await message.reply("```\n{}\n```".format(response))
                    return
                #saving output of the program in out.txt using Luke's L-Basid

                if(debug):response+="[QB64_BOT: running './bin/lbasic -t /tmp/source.txt>/tmp/out.txt']\n"

                execute = os.system("./bin/lbasic -t /tmp/source.txt>/tmp/out.txt")

                if(execute==1):
                    if(debug):response+="[QB64_BOT: Some error occured. lbasic ended with 1.]\n"

                if(debug): response+="[QB64_BOT: attemtping to read '/tmp/out.txt']\n"

                try:
                    f_hnd = open("/tmp/out.txt", "r")
                    if(execute==5): #returns 5 if the program was stuck in some kind of infinite loop
                        if(debug): response+="[QB64_BOT: Program execution exceeded more than 2 seconds]\n"
                        response+= f_hnd.read(1500) + "\n" #in this case, we will send only 1024bytes of the output
                    else:
                        response+= f_hnd.read(1500) + "\n"
                    f_hnd.close()
                except OSError:
                    response+="[QB64_BOT: Failed to read '/tmp/out.txt']\n"
                    await message.add_reaction("❗")
                    await message.clear_reaction("⏳")
                    await message.reply("```\n{}\n```".format(response))
                    return
                #time_taken = time.time()-start
                await message.add_reaction("✅")
                await message.clear_reaction("⏳")
                response = ">>> **Output :-**\n```\n"+response+"\n```"
            else:
                await message.add_reaction("❌") 
                response = "> {} Please use proper codeblock syntax.".format(message.author.mention)
        else:
            await message.add_reaction("❌")
            response = "> {} You are using incorrect syntax.".format(message.author.mention)
        await message.channel.send(response)
        return
    else:
        # %wiki KEYWORD command
        if(message.content[:6]=="%wiki "):
            help_word = message.content[5:].strip().upper()
            response = ""
            if(help_word in keywords_known):
                await message.add_reaction("✅")
                response = "> {} : http://qb64.org/wiki/".format(message.author.mention)+help_word
            else:
                await message.add_reaction("❌")
                response = "> {} : keyword not found. Try again. 🤷‍".format(message.author.mention)
            await message.channel.send(response)
            return
        # %help KEYWORD command
        if(message.content[:6]=="%help "):
            doc_word = message.content[5:].strip().upper()
            response = ""
            if(doc_word in keywords_known):
                await message.add_reaction("✅")
                doc = qb64_help_parser.getDocumentation(doc_word)
                response = ">>> **{}** \n {}\n\n".format(doc["title"], doc["use"])
                response += "**Syntax :-**\n{}\n\n".format(doc["syntax"])
                if(doc["parameters"]!=''): response += "**Parameters :-**\n {}\n\n".format(doc["parameters"])
                if(doc["description"]!=''): response += "**Description :-**\n {}\n\n".format(doc["description"])
                if(doc["availability"]!=''): response += "**Availability :-**\n {}\n".format(doc["availability"])
                if(len(response)>1800):
                    response = "**{}** description exceed 2000 chars. 🤷‍ \n Use wiki - http://qb64.org/wiki/{}".format(doc_word, doc_word)
            else:
                await message.add_reaction("❌")
                response = "> {} keyword not found. Try again. 🤷‍".format(message.author.mention)
            
            await message.channel.send(response)
            return
        # %example command
        if(message.content[:9]=="%example "):
            doc_word = message.content[9:].strip().upper()
            response = ""
            if(doc_word in keywords_known):
                await message.add_reaction("✅")
                response = qb64_help_parser.getExample(doc_word)
                if(len(response)>1800):
                    response = ">>> **{}** example code exceed 2000 chars. 🤷‍ \n Use wiki - http://qb64.org/wiki/{}".format(doc_word, doc_word)
            else:
                await message.add_reaction("❌")
                response = "> {} : keyword not found. Try again. :(".format(message.author.mention)
            
            await message.channel.send(response)
            return
        # %bot-help command
        if(message.content.strip()=="%bot-help"):
            response = ">>> **QB64 BOT Help -** \n\n"
            response += "_To run code using Luke's L-BASIC, use the following syntax :-_ \n%qb64\n\`\`\`\n'your code\n\`\`\`\n_OR_"
            response += "\n%qb64\n\`\`\`vb\n'your code\n\`\`\`\n"
            response += "_To get full documentation for a keyword, use the following syntax :-_\n`%help keyword_name`\n"
            response += "_To get example for a keyword, use the following syntax :-_\n`%example keyword_name`\n"
            response += "_To get wiki link for a keyword, use the following syntax :-_\n`%wiki keyword_name`\n"
            response += "_To get this help message use the following syntax :-_\n`%bot-help`"
            await message.channel.send(response)
            return


client.run(os.getenv('DISCORD_BOT_TOKEN'))
