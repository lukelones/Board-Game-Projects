import time
import praw
import smtplib
import boardgamegeek
from boardgamegeek import BoardGameGeek
from email.mime.text import MIMEText

"""
BGG Wishlist Tracker v 1.1


-Tracks mentions of games on users' boardgamegeek.com wishlists on reddit.com/r/boardgames
-Sends email to user when mention occurs

--This is a work in progress.  TO DO:
    Improve string matching
        - Separate areas divided by punctuation to improve matching for games with formal names and expansions
        - Add whitespace to stop interstring matching (e.g. "coup" matches to "couple")
        - Match to first-order comments as well as title and text
    Add logger for boardgamegeek.api
    Fix bug that causes certain game names to crash the program

"""

#change these to check other bgg user and send to different email
bggUser = "shbones"
userEmail = "luke.lones@gmail.com"

r = praw.Reddit('BGG Wishlist Mention Tracker by /u/shbones v 1.1')
sent_already = []


while True:
    #Repopulate boardgamegeek.com wishlist every run
    wishlist = []
    bgg = BoardGameGeek()
    collection = bgg.collection(bggUser)
    try:
        games = collection.items
        print games
        for each_game in games:
            if each_game.wishlist == True:
                wishlist.append(each_game.name.lower())
        
        
        
        #Check for mentions in Title or Text in Top 10 current posts on reddit.com/r/boardgames
        subreddit = r.get_subreddit('boardgames')
        for submission in subreddit.get_hot(limit=10):
            post_text = submission.selftext.lower()
            post_title = submission.title.lower()
            has_game = any(string in (post_text + post_title) for string in wishlist)
            if submission.id not in sent_already and has_game:
                post_link = submission.short_link
                
                
                sender = 'board.game.bot@gmail.com'
                receivers = [userEmail]
                message = MIMEText("A game on your boardgamegeek.com wishlist was mentioned here: " + post_link)
                message['Subject'] = "Wishlist Item Mentioned"
                message['From'] = "BG Bot <" +sender + ">"
                message['To'] = "<" + userEmail + ">"
                
               
                
                username = 'board.game.bot@gmail.com'
                password = 'saltedpw'
                try:
                    server = smtplib.SMTP('smtp.gmail.com:587')
                    server.ehlo()
                    server.starttls()
                    server.login(username,password)
                    server.sendmail(sender, receivers, message.as_string())
                    server.quit()
                    print "Successfully sent email"
                except smtplib.SMTPException:
                        print "Error: unable to send email"
                        break
                sent_already.append(submission.id)
        print "Finished"
        time.sleep(1800)
    except AttributeError:
        print "BGG: No items in user's collection"
        break

