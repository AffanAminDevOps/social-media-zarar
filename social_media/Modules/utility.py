from ..models import *
from datetime import datetime

# For Youtube
def video_exists(video_title):
    """
    Check if a video with the given title exists in the YouTube videos database.

    Parameters:
    - video_title (str): The title of the video to check.

    Returns:
    - bool: True if a video with the given title exists, False otherwise.
    """
    video=youtube_video.objects.filter(title=video_title).count()
    if video>0:
        return True
    else:
        return False


def update_video(video_title,video_info):
    """
    Updates a video in the database with the given video title and video information.

    Parameters:
        video_title (str): The title of the video.
        video_info (dict): A dictionary containing the video information.

    Returns:
        bool: True if the video was successfully updated, False otherwise.
    """
    video=youtube_video.objects.filter(title=video_title).count()
    if video>0:
        video=youtube_video.objects.get(title=video_title)
        video.views_count=max(video_info['views_count'],video.views_count)
        # if video.views_count<video_info['views_count']:
        #     video.views_count=video_info['views_count']
        video.last_scraped_video=datetime.now()
        video.save()
        return True
    else:
        return False
    
    
def youtube_channel_exists(url):
    """
    Check if a channel with the given URL exists in the YouTube channels database.

    Parameters:
    - url (str): The URL of the channel to check.

    Returns:
    - bool: True if a channel with the given URL exists, False otherwise.
    """
    channel=youtube_channel.objects.filter(url=url).count()
    if channel>0:
        return True
    else:
        return False
    
def update_channel_info(url,channel_info):
    """
    Updates a channel in the database with the given URL and channel information.

    Parameters:
        url (str): The URL of the channel.
        channel_info (dict): A dictionary containing the channel information.

    Returns:
        bool: True if the channel was successfully updated, False otherwise.
    """
    channel=youtube_channel.objects.filter(url=url).count()
    if channel>0:
        channel=youtube_channel.objects.get(url=url)
        channel.subscriber_count = max(channel.subscriber_count, channel_info['details']['subscriber_count'])
        channel.videos_count = max(channel.videos_count, channel_info['details']['videos_count'])
        channel.views = max(channel.views, channel_info['details']['views'])
        channel.last_scraped_user=datetime.now()
        # if channel.subscriber_count<channel_info['details']['subscriber_count']:
        #     channel.subscriber_count=channel_info['details']['subscriber_count']
        # if channel.videos_count<channel_info['details']['videos_count']:
        #     channel.videos_count=channel_info['details']['videos_count']
        # if channel.views<channel_info['details']['views']:
        #     channel.views=channel_info['details']['views']
        channel.save()
        return True
    else:
        return False
# For Twitter


def tweet_exists(description):
    """
    Check if a tweet with the given description exists in the Twitter tweets database.

    Parameters:
    - description (str): The description of the tweet to check.

    Returns:
    - bool: True if a tweet with the given description exists, False otherwise.
    """
    tweet=scraped_tweets.objects.filter(description=description).count()
    if tweet>0:
        return True
    else:
        return False
    

def update_tweet(description,tweet_info):
    """
    Updates a tweet in the database with the given description and tweet information.

    Parameters:
        description (str): The description of the tweet.
        tweet_info (dict): A dictionary containing the tweet information.

    Returns:
        bool: True if the tweet was successfully updated, False otherwise.
    """
    tweet=scraped_tweets.objects.filter(description=description).count()
    if tweet>0:
        tweet=scraped_tweets.objects.get(description=description)
        tweet.views=max(tweet_info['views'],tweet.views)
        tweet.reply_count=max(tweet_info['reply'],tweet.reply_count)
        tweet.quote_count=max(tweet_info['quote_count'],tweet.quote_count)
        tweet.favorite_count=max(tweet_info['favorite_count'],tweet.favorite_count)
        tweet.retweet_count=max(tweet_info['retweet_count'],tweet.retweet_count)
        tweet.bookmark_count=max(tweet_info['bookmark_count'],tweet.bookmark_count)
        
        
        tweet.last_scraped_tweet=datetime.now()
        tweet.save()
        return True
    else:
        return False
    
    
def twitter_profile_exists(id):
    """
    Check if a profile with the given id exists in the Twitter profiles database.

    Parameters:
    - id (str): The id of the profile to check.

    Returns:
    - bool: True if a profile with the given id exists, False otherwise.
    """
    profile=twitter_user.objects.filter(id=id).count()
    if profile>0:
        return True
    else:
        return False

def update_profile(id,profile_info):
    """
    Updates a profile in the database with the given id and profile information.

    Parameters:
        id (str): The id of the profile.
        profile_info (dict): A dictionary containing the profile information.

    Returns:
        bool: True if the profile was successfully updated, False otherwise.
    """
    profile=twitter_user.objects.filter(id=id).count()
    if profile>0:
        profile=twitter_user.objects.get(id=id)
        profile.is_blue_varified=profile_info['is_blue_varified']
        profile.can_dm=profile_info['can_dm']
        if profile_info['user_description']!=None:
            profile.user_description=profile_info['user_description']
        profile.favourites_count=max(profile.favourites_count,profile_info['favourites_count']) 
        profile.fast_followers_count=max(profile.fast_followers_count,profile_info['fast_followers_count'])
        profile.friends_count=max(profile.friends_count,profile_info['friends_count'])
        profile.normal_followers_count=max(profile_info['normal_followers_count'])
        profile.statuses_count=max(profile.statuses_count,profile_info['statuses_count']) 
        
        
        profile.last_scraped_user=datetime.now()
        profile.save()
        return True
    else:
        return False