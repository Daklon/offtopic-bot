import praw

#create a reddit instance
reddit = praw.Reddit('offtopic-bot', user_agent='Linux:com.offtopic-bot:v0.1 (by /u/Daklon15)')
subreddit = reddit.subreddit('homelab')

print(subreddit.display_name)  # Output: redditdev
print(subreddit.title)         # Output: reddit Development
print(subreddit.description)   # Output: A subreddit for discussion of ...
