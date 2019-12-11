import yaml
import praw
import shutil
import sqlite3
import requests


class Reddit_Interface():
    def __init__(self):
        #create a reddit instance
        with open("config.yaml", 'r') as yamlfile:
            self.cfg = yaml.safe_load(yamlfile)
        self.reddit = praw.Reddit('offtopic-bot', user_agent='Linux:com.offtopic-bot:v0.1 (by /u/Daklon15)')
        self.subreddit = self.reddit.subreddit(self.cfg['reddit']['subreddit'][0])
        self.image_formats = ('jpg','png','gif','jpeg')
        self.db = sqlite3.connect('database.sqlite')
        self.cursor = self.db.cursor()
        self.check_database()

    def get_image(self):
        #get a random submission
        submission = self.get_random()
        self.cursor.execute('SELECT COUNT(link) FROM links_visitados WHERE link=?',(submission,))
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('INSERT INTO links_visitados(link) VALUES(?)',(submission,))
            self.db.commit()
            return submission
        else:
            self.get_image()

    def get_random(self):
        submission = self.subreddit.random()
        while submission.url.split(".")[-1] not in self.image_formats:
            submission = self.subreddit.random()
        return submission.url

    def check_database(self):
        #create database if it doesn't exists yet
        self.cursor.execute("SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name='links_visitados';");
        if int(self.cursor.fetchone()[0]) == 0:
            ##The database doesnt exist, lets create it
            print("Creating database")
            self.cursor.execute("CREATE TABLE links_visitados(link TEXT PRIMARY KEY)")

if __name__ == "__main__":
    print("test")
    ri = Reddit_Interface()
