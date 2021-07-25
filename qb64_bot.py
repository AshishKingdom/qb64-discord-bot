# @Author: AshishKingodm (Ashish Kushwaha)

import os
from dotenv import load_dotenv
import discord
import qb64_help_parser

#initialization 

load_dotenv()

client = discord.Client()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')


#load all qb64/qbasic keywords
keywords_known = []
f = open('keywords.txt', 'r')
keywords_known = f.read().split('\n')
f.close()

@client.event
async def on_ready():
    print("{} is connected to Discord!".format(client.user))
    game = discord.Game("%bot-help")
    await client.change_presence(activity=game)
    return

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # %qb64 command
    if(message.content[:5]=="%qb64"):
        response = ""
        execute = 0
        debug = False

        code_data = ""
        vb_mentioned = False
        # lets first look for ```vb in message (if user has used codeblocks)
        code_block_pos = message.content.find("```vb")
        if(code_block_pos == -1):
            # ```vb not found.. so maybe user might have used simply ```
            code_block_pos = message.content.find("```")
        else:
            # since vb was mentioned in ```vb, vb_mentioned will be set to true
            vb_mentioned = True

        if(code_block_pos == -1):
            # ah.. so ``` is also not present in a message.
            # now there are 2 possibilities, either user have just sent %qb64 which is wrong
            # or user have sent the code without using codeblocks.
            if(message.content[5:].strip()==''):
                # only %qb64 was used by the user.
                await message.add_reaction("❌")
                await message.channel.send("> {} : No code found. Use %bot-help".format(message.author.mention))
                return
            else:
                # the user has not used code-blocks. Maybe, the user was being lazy (:P)
                # we will treat all the content after "%qb64 " as a code.
                code_data = message.content[5:]
        else:
            #lets extract code from message
            if(vb_mentioned):
                p = message.content.find("```vb")+5
            else:
                p = message.content.find("```")+3

            code_data = message.content[p:message.content.find("```", p)]

        if(code_data.find("'$debug-bot-cloud")!=-1) : debug = True

        if(debug) : response += "[QB64_BOT_DEBUG_MODE]\n"

        await message.add_reaction("⏳")

        if(debug):response+="[QB64_BOT: attemtping to save the code in '/tmp/source.txt']\n"

        # saving the code data in '/tmp/source.txt'
        try:
            f_hnd = open("/tmp/source.txt", 'w')
            f_hnd.write(code_data)
            f_hnd.close()
            if(debug):response+="[QB64_BOT: code saved in 'tmp/source.txt' successfully.]\n"
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
                program_output = f_hnd.read(1500)
                if(program_output.strip()==''): program_output = "[QB64_BOT: Program does not produce any output]"
                response+= program_output + "\n" #in this case, we will send only 1024bytes of the output
            else:
                program_output = f_hnd.read(1500)
                if(program_output.strip()==''): program_output = "[QB64_BOT: Program does not produce any output]"
                response+= program_output + "\n"
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
        await message.channel.send(response)
        return
    else:
        # %wiki KEYWORD command
        if(message.content[:6]=="%wiki "):
            help_word = message.content[5:].strip().upper()
            response = ""
            if(help_word in keywords_known):
                await message.add_reaction("✅")
                response = ">>> {} : http://qb64.org/wiki/".format(message.author.mention)+help_word
            else:
                await message.add_reaction("❌")
                response = ">>> {} : keyword not found. Try again. 🤷‍\n Use %bot-help to know about commands".format(message.author.mention)
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
                response = ">>> {} keyword not found. Try again. 🤷‍ \nUse %bot-help to know about commands".format(message.author.mention)
            
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
                response = ">>> {} : keyword not found. Try again. :(\n Use %bot-help to know about commands".format(message.author.mention)
            
            await message.channel.send(response)
            return
        # %bot-help command
        if(message.content.strip()=="%bot-help"):
            response = ">>> **QB64 BOT Help -** \n\n"
            response += "_To run code using Luke's L-BASIC, use the following syntax :-_ \n%qb64\n\`\`\`\n'your code\n\`\`\`\n_OR_"
            response += "\n%qb64\n\`\`\`vb\n'your code\n\`\`\`\nOR\n%qb64 your_code\n"
            response += "_To get full documentation for a keyword, use the following syntax :-_\n`%help keyword_name`\n"
            response += "_To get example for a keyword, use the following syntax :-_\n`%example keyword_name`\n"
            response += "_To get wiki link for a keyword, use the following syntax :-_\n`%wiki keyword_name`\n"
            response += "_To get this help message use the following syntax :-_\n`%bot-help`"
            await message.channel.send(response)
            return


client.run(os.getenv('DISCORD_BOT_TOKEN'))
