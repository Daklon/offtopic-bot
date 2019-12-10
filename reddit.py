import yaml
import praw
import requests
import shutil


class Reddit_Interface():
    def __init__(self):
        #create a reddit instance
        with open("config.yaml", 'r') as yamlfile:
            self.cfg = yaml.safe_load(yamlfile)
        self.reddit = praw.Reddit('offtopic-bot', user_agent='Linux:com.offtopic-bot:v0.1 (by /u/Daklon15)')
        self.subreddit = self.reddit.subreddit(self.cfg['reddit']['subreddit'][0])
        self.image_formats = ('jpg','png','gif','jpeg')

    def get_image(self):
        #get a random submission
        print("enter")
        submission = self.subreddit.random()
        #get another random until a jpg is received
        while submission.url.split(".")[-1] not in self.image_formats:
            print(submission.url)
            submission = self.subreddit.random()
        #return the requested image
        return submission.url
