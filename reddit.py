import praw
import requests
import shutil


class Reddit_Interface():
    def __init__(self):
        #create a reddit instance
        self.reddit = praw.Reddit('offtopic-bot', user_agent='Linux:com.offtopic-bot:v0.1 (by /u/Daklon15)')
        self.subreddit = self.reddit.subreddit('images')

    def get_image(self):
        #get a random submission
        submission = self.subreddit.random()
        #get another random until a jpg is received
        while 'jpg' not in submission.url:
            print(submission.url)
            submission = self.subreddit.random()
        #return the requested image
        return submission.url
