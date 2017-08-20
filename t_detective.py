#!/usr/bin/env python
# 
import praw
import numpy as np
import time
users = []
def get_user_list(submission=None, comment_tree_depth=0):
    """ Get a list of users participating in a post

    >>> users = get_user_list(submission, comment_tree_depth=5)
    """
    if not submission:
        return None
    
    # Expand the comment trees
    submission.comments.replace_more(limit=comment_tree_depth)
    users = []
    for comment in submission.comments:
        if comment: # Ignore Nonetype comments (removed comments, ect)
            # Link back to the original comment for possible reply services
            if comment.author: # Ignore Nonetype authors
                comment.author.original_comment = comment
            users.append(comment.author)

    # Remove any extraneous nonetypes in the user list (deleted accounts, ect)
    users = [user for user in users if user]
    return users


def check_user_comments(users, flagged_subs, sortby='new', depth=100):
    """ Check the user list for users that have posted recently on flagged subreddits

    >>> check_user_comments(users, flagged_subs)
    >>> check_user_comments(users, flagged_subs, sortby='top', depth=10)
    """

    # The list of flagged subreddits
    flagged_users = set()
    for user in users:
        user.flagged_for = set()
        user.flagged_comments = []
        user.flagged_posts = []

        # Check the user's comment history
        user.comment_count = 0
        user.comment_depth = 0
        for comment in user.comments.new(limit=depth):
            user.comment_depth += 1
            if comment.subreddit.display_name.lower() in flagged_subs:
                user.comment_count += 1
                user.flagged_comments.append(comment)
                user.flagged_for.add(comment.subreddit.display_name.lower())
                flagged_users.add(user)

        # Check the user's post history
        user.post_count = 0
        user.post_depth = 0
        for post in user.submissions.new(limit=depth):
            user.post_depth += 1
            if post.subreddit.display_name.lower() in flagged_subs:
                user.post_count += 1
                user.flagged_for.add(post.subreddit.display_name.lower())
                user.flagged_posts.append(post)
                flagged_users.add(user)

    # list(set()) used to quickly remove duplicate users
    # ie. flagged user posted multiple times in the current post
    return list(flagged_users)
    

def get_top_post_comment(user):
    """ Get the top post made in a flagged sub
 
    >>> user = get_top_post(user)
    """
    if user.flagged_posts:
        score = []
        for post in user.flagged_posts:
            score.append(post.score)
        user.top_flagged_post = user.flagged_posts[np.argsort(score)[-1]]
    if user.flagged_comments:
        score = []
        for comment in user.flagged_comments:
            score.append(comment.score)
        user.top_flagged_comment = user.flagged_comments[np.argsort(score)[-1]]
    return user


def report_info(user):
    """ Report info on a flagged user

    >>> report(flagged_user)
    """
    msg = []
    user = get_top_post_comment(user)
    for sub in user.flagged_for:
        msg.append('\n/u/{0} has posted recently in /r/{1}!'
                    .format(user.name, sub))
    if user.flagged_posts:
        msg.append('{0} out of {1} recent posts were made on flagged subreddits'
                   .format(user.post_count, user.post_depth))
        msg.append('Top flagged post: https://www.reddit.com{}'
                   .format(user.top_flagged_post.permalink))
    if user.flagged_comments:
        msg.append('{0} out of {1} recent comments were made on flagged subreddits'
                   .format(user.comment_count, user.comment_depth))
        msg.append('Top flagged comment: https://www.reddit.com{}'
                   .format(user.top_flagged_comment.permalink()))

    for line in msg:
        print(line)
    return msg

def t_detective():
    r = praw.Reddit('t_detective')
    sub = r.subreddit('askreddit')
    subs2check = ['the_donald', 'the_red_pill']
    for submission in sub.hot(limit=1):
        users = get_user_list(submission)
        flagged_users = check_user_comments(users, subs2check)
        for i, user in enumerate(flagged_users):
            print('\n')
            msg = report_info(user)
            user.msg = msg
            flagged_users[i] = user

t_detective()

# class flagged_user():

#     def __init__(user, subs2check):
#         self.flagged_for = set()
#         self.comment_count = 0
#         self.post_count = 0
#         for sub in subs2check:
#             for comment in self.flagged_comments:
#                 if comment.subreddit.display_name.lower() in sub:
#                     self.flagged_for.add(sub)
#                     comment_count += 1

#             for post in self.flagged_posts:
#                 if post.subreddit.display_name.lower() in sub:
#                     self.flagged_for.add(sub)
#                     post_count += 1
#         self.comment_count = comment_count
#         self.post_count = post_count

        
#         for sub in self.flagged_for:
#             print('flagged for: {0}'.format(sub))
#             print('found {0} comments'.format(user.comment_count))
#             print('found {0} posts'.format(user.post_count))
#         flagged_users[i] = user
#     return flagged_users
        
                    
                    
                    
                    
                    
        









    
