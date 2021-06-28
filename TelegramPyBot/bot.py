import telebot
import time
import func
from telebot import types

# general declaration and init
token = "1348440990:AAHNjomwUi26420jd0LQrGt6X0QYWhxsNyE"
bot = telebot.TeleBot(token, "HTML")

# owner info
adminId = 1137766669  # admin/owner id

# general msg
bannedMsg = "<b>Hey, It looks like you are banned!</b>\nPlease contact the owner."
lockedBotMsg = "<b>This bot is currently locked for maintenance!</b>\nPlease have some patience"
privateUse = "<b>Bot can only be used in private chat!</b>"

######################################################### [START, CMD & INFO COMMAND] #########################################################


@bot.message_handler(commands=["start", "cmds", "info"])
def sendWelcome(message):
    userid = message.from_user.id
    username = message.from_user.username

    if message.chat.type == 'private':  # check if chat type is private
        # /start command
        if message.text.find("/start") == 0:
            if message.from_user.id != adminId: #insert user info to db when user id is not adminId
                func.addUser(userid, username)
            bot.reply_to(message, f"Hello @{username},\n<b>How are you?</b>\n\nType /cmds for more")

        # /cmds command
        elif message.text.find("/cmds") == 0:
            if userid == adminId:
                allcmd = '''<b>Admin commands</b>\n/ban <i>id</i>\n/unban <i>id</i>\n/lock <i>true/false</i> 
/broadcast <i>message</i>\n/botstat\n<b>User commands</b>\n/info user info'''
                bot.reply_to(message, allcmd)
            else:
                bot.reply_to(
                message, "<b>User commands</b>\n/info user info\n/unsubscribe unsubscribe the bot")

        # /info command
        elif message.text.find("/info") == 0:
            textreply = f"<b>Your info</b>\nFirst Name: <b>{message.from_user.first_name}</b>\n" \
                        f"Last Name: <b>{message.from_user.last_name}</b>\n" \
                        f"Username: <b>@{message.from_user.username}</b>\n" \
                        f"User ID: <code>{message.from_user.id}</code>\n" \
                        f"Profile url: <a href='tg://user?id={message.from_user.id}'>Profile url</a>"
            bot.reply_to(message, textreply)

    else:
        # if the chat type is a group or anything else
        bot.reply_to(message, privateUse)

######################################################### [ADMIN COMMANDS] #########################################################


@bot.message_handler(commands=["ban", "unban", "lock", "broadcast", "botstat"])
def adminCmd(message):
    userid = message.from_user.id

    # if chat type is private(not necessary but still)
    if message.chat.type == 'private':
        if userid == adminId:  # only for admin

            ############### BAN COMMAND ###############
            if message.text.find("/ban") == 0:
                banId = message.text[5:]  # get the user id to banw
                banId = banId.replace(' ', '')  # replace all spaces
                if banId:  # if id is given
                    if func.ban(banId): #when the ban was successfull
                        bot.reply_to(message, f"<b>User [<code>{banId}</code>] is banned ✅</b>")
                        bot.send_message(banId, "<b>Your are banned!</b>")
                    else:
                        bot.reply_to(message, "<b>Error while banning the user!</b>")
                else: #if id is not given
                    bot.reply_to(message,"Well I can't ban a user who don't exist")

            ############### UNBAN COMMAND ###############
            elif message.text.find("/unban") == 0:
                unbanId=message.text[7:] # get the user id to unban
                unbanId=unbanId.replace(' ','') #replace all spaces
                if unbanId: #when id is given
                    if func.unban(unbanId): #when the unban was successfull
                        bot.reply_to(message,f"<b>User [<code>{unbanId}</code>] is unbanned ✅</b>")
                        bot.send_message(unbanId, "<b>Your are unbanned!</b>")
                    else:
                        bot.reply_to(message, "<b>Error while unbanning the user!</b>")
                else:
                    bot.reply_to(message,"Well I can't unban a user who don't exist")

            ############## LOCK/UNLOCK COMMAND ###############
            elif message.text.find("/lock") == 0:
                getBool=message.text[6:] #get true or false
                getBool=getBool.replace(' ','') #replace all spaces
                if getBool: #when a input exist
                    if getBool == "true" or getBool == "false": #only accept true or false as input
                        if func.lockUnlock(getBool): #when the lock is successfully locked or unlocked
                            if getBool == "true":
                                bot.reply_to(message,"<b>Bot is now locked</b>")
                            else:
                                bot.reply_to(message,"<b>Bot is now unlocked</b>")
                        else:
                            bot.reply_to(message,"Error while locking/unlocking the bot.\nPlease try again!")
                    else:
                        bot.reply_to(message,"Please type 'true' or 'false' nothing else!")
                else:
                    bot.reply_to(message,"The input is empty.\nPlease type 'true' or 'false'!")
            
            ############## BROADCAST A MESSAGE ###############
            elif message.text.find("/broadcast") == 0:
                messageToSend=message.text[11:]
                if messageToSend: #when message which should be send exist
                    func.broadcast(messageToSend,message)   
                    func.updateDb()
                else:
                    bot.reply_to(message,"The <code>message_to_send</code> is empty!")

            ############## BOTSTAT COMMAND ###############
            elif message.text.find("/botstat") == 0:
                bot.reply_to(message,func.botstat())

######################################################### [USER COMMANDS] #########################################################
@bot.message_handler(commands=["unsubscribe"])
def userCmd(message):
    userId= message.from_user.id
    if message.chat.type == 'private':
        if message.text.find("/unsubscribe") == 0:
            if userId != adminId:
                bot.reply_to(message,"<b>Unsubscribing...</b>")
                if func.unsubscribe(userId):
                    bot.edit_message_text("<b>Unsubscribed until /start!</b>",message.chat.id,message.message_id+1)
                else:
                    bot.edit_message_text("<b>Oops an error occurred. Please try again</b>",message.chat.id,message.message_id+1)
    else:
        bot.reply_to(message,privateUse)

######################################################### [TEXT HANDLER] #########################################################
@bot.message_handler(content_types=['text','sticker'])
# for normal msg
def normalmsg(message): #handler other text from user/admin
    userid=message.from_user.id
    if message.chat.type == 'private':
        if userid != adminId: #if user id is not admin id
                bot.forward_message(adminId,message.chat.id,message.message_id)
                bot.reply_to(message,"<b>You won't get any reply, if you privacy setting for <code>forward_message</code> dont allowed!</b>")
                time.sleep(3)
                bot.delete_message(message.chat.id,message.message_id+2) #delete the private setting message
               
        if userid == adminId and message.reply_to_message.text: #if user id is adminid and a message from sender is replied by owner
            if message.content_type == 'text': #if the content type is text
                bot.send_message(message.reply_to_message.forward_from.id, message.text) #send the text from owner to the sender
            else:
                bot.forward_message(message.reply_to_message.forward_from.id, message.chat.id, message.message_id) #if the content is sticker just forward to the sender

        


######## run the bot ########
while True:
    try:
        bot.polling()
    except:
        time.sleep(15)
