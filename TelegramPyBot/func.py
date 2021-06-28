import time
import os
import bot
import sqlite3

#bot init
token=bot.token

#create db
db = sqlite3.connect("TelegramUser",check_same_thread=False)  # i suggest you to change the "TelegramUser" Db name but you can leave it

#owner/admin id
adminId=bot.adminId


############################################## CREATE TABLES & co ##############################################

############## RUN SQL COMMANDS #############
def run(commands):
    c=db.cursor()
    c.execute(commands)
    db.commit()
    return True

cur = db.cursor()
run('''CREATE TABLE IF NOT EXISTS telegram_user(
          user_id INTEGER,
          username TEXT,
          is_banned INTEGER,
          is_subscribed INTEGER,
          user_notes TEXT)''')

## BOT LOCK TABLE ##
run('''CREATE TABLE IF NOT EXISTS bot(
          bot_lock INTEGER)''')

#  set a value for bot_lock column to prevent error later
cur.execute('SELECT bot_lock FROM bot')
count = 0
row=cur.fetchall()
count=len(row)

if count == 0:  # when there is no row for bot_lock column
    exec("INSERT INTO bot(bot_lock) VALUES(0)")

######################################################### [GENERAL FUNCTIONS] #########################################################

## not working function ##
############## check if user is banned or not and  return true when not ##############
def notBanned(userId):
    print("Here")
    c = db.cursor()
    c.execute(f"SELECT COUNT(user_id) FROM telegram_user WHERE user_id={userId} and is_banned=0")
    if c.fetchall():
        return True
    return False

############## check if bot is locked or not and return true when not locked ##############
def notLocked():
    c = db.cursor()
    c.execute(f"SELECT bot_lock from bot WHERE bot_lock=1")
    row=c.fetchall()
    count=len(row) #length of the row
    if count==0:
        return True
    return False
## [END] ##

############## add new user to the db ##############
def addUser(userid, username):
    c = db.cursor().cursor()
    c.execute("SELECT user_id FROM telegram_user WHERE user_id = ?", (userid,))
    # extract row count from fetchall
    listCount = 0
    rowList = c.fetchall()
    listCount=len(rowList)
    if not listCount >= 1:
        exec("INSERT INTO telegram_user(user_id,username,is_banned,is_subscribed,user_notes) VALUES (?,?,0,1,'no notes')", (userid, username))
    else:
        exec("UPDATE telegram_user SET user_id=?,username=?,is_banned=0,is_subscribed=1 WHERE user_id=?", (userid, username, userid))

############## Total member count ##############
def getMemberCount():
    print("memberCount")
    c = db.cursor().cursor()
    c.execute("SELECT user_id FROM telegram_user")
    return len(c.fetchall())

############## Total banned user count ##############
def getBannedCount():
    print("bannedCount")
    c = db.cursor().cursor()
    c.execute("SELECT is_banned FROM telegram_user WHERE is_banned=1")
    return len(c.fetchall())

############## Subscribed user count ##############
def getSubscribedCount():
    print("subscribedCount")
    c = db.cursor().cursor()
    c.execute("SELECT is_subscribed FROM telegram_user WHERE is_subscribed=1")
    return len(c.fetchall())

############## Remove blocked user ##############
def updateDb():
    c = db.cursor().cursor()
    with open("blockedUser.txt", 'r') as f:
        for i in f.readlines():
            i = i.replace("\n", "")
            c.execute("DELETE FROM telegram_user WHERE user_id=?", (i,))
    os.remove("blockedUser.txt")
    bot.send_message(adminId, "<b>Bot database is updated!</b>")
    db.commit()

######################################################### [ADMIN FUNCTIONS] #########################################################

############## Ban user ##############
def ban(banid):
    c = db.cursor()
    c.execute("SELECT (user_id FROM telegram_user WHERE user_id = ?", (banid,)) #check if user id exist
    # extract row count from fetchall
    count = 0
    rowList = c.fetchall()
    count=len(rowList)
    if count >= 1:  # if the row count for userid is >1
        c.execute("UPDATE telegram_user SET is_banned=1 WHERE user_id=?", (banid,))
        db.commit()
        return True

    return False

############## Unban user ##############
def unban(unbanid):
    c = db.cursor()
    c.execute("SELECT user_id FROM telegram_user WHERE user_id = ?", (unbanid,)) #check if user id exist
    # extract row count from fetchall
    count = 0
    rowList = c.fetchall()
    count=len(rowList)

    if count >= 1:  # if the row count for userid is >1
        c.execute("UPDATE telegram_user SET is_banned=0 WHERE user_id=?", (unbanid,))
        db.commit()
        return True

    return False

############## Lock/Unlock the  Bot ##############
def lockUnlock(trueOrFalse):
    c = db.cursor()
    if trueOrFalse == "true":
        c.execute("UPDATE bot SET bot_lock=1") #lock the bot
        return True
    elif trueOrFalse == "false":
        c.execute("UPDATE bot SET bot_lock=0") #unlock the bot
        return True

    db.commit()
    return False

############## Broadcast a message ##############
def broadcast(msgToSend,message):
    c = db.cursor()
    allUser = c.execute("SELECT * FROM telegram_user WHERE is_subscribed=1")
    dumb = allUser.fetchall()  # fetch all result as tuple
    count = 0
    error = 0
    if dumb:  # if id of subscribed user exist
        bot.send_message(adminId, f"Sending: <b>{msgToSend}</b>")
        time.sleep(2)
        for i in dumb:
            # choose the first column of the tuple -> [ userid ] <=this, username, isbanned,issubscribed, notes
            try:  # try to send the message
                bot.send_message(i[0], msgToSend)
                count += 1
            except:  # expect that the user blocked the bot or any other error
                error += 1
                f = open("blockedUser.txt", 'a') #add user id when they blocked the bot(to remove later w)
                f.write(f"{i[0]}\n")
                f.close()
        # send count to admin
        m_id = message.message_id + 1
        bot.edit_message_text(
            f"<b>Success: {count}\nError: {error}</b>", message.chat.id, m_id)
    else:  # if not
        bot.send_message(adminId, "<b>No user are subscribed to the Bot!</b>")

############## Get the Bot status(member count, banned user & co) ##############
def botstat():
    memberCount = getMemberCount()
    bannedCount = getBannedCount()
    subscribedCount = getSubscribedCount()
    unsubscribedCount = memberCount-subscribedCount
    allTog = f'''
    <b>Total member : </b>{memberCount}
<b>Banned user: </b>{bannedCount}
<b>Subscribed user: </b>{subscribedCount}
<b>Unsubscribed user: </b>{unsubscribedCount}'''
    return allTog

######################################################### [USER FUNCTIONS] #########################################################

############## Unsubscribe a user ##############
def unsubscribe(userid):
    c = db.cursor()
    if c.execute("UPDATE telegram_user SET is_subscribed=0 WHERE user_id=?", (userid,)):
        db.commit()
        return True
    return False