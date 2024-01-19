from .models import *
from .Modules.TwitterApi.Twitter_keyword import twitter_keyword_driver
from .Modules.TwitterApi.TwitterProfile import profile_tweets_driver
from .Modules.Youtube.YT_channel_crawler import channel_crawler_youtube_driver
from .Modules.Youtube.YT_keyword_crawler import youtube_keyword_crawler
from datetime import datetime
from .Modules.utility import *
from celery import shared_task
from .Modules.Facebook.facebook_profiles import *
# from .Modules.Facebook.facebook_keyword_crawler import facebook_keyword
# from background_task import background
import pytz
# from celery import task
from celery import shared_task
from social_media_monitoring.celery import app
from django.db.models import Q
########################### Web Scrapers #######################################
from .Modules.Web.bol_news import bol_news_scraper
from .Modules.Web.jang_news import jang_news_scraper
from .Modules.Web.dawn import dawn_news_scrape
from .Modules.Web.AryNewsScapper import scrape_ary_news
from .Modules.Web.daily_pakistan_crawler import daily_pakistan
from .Modules.Web.express_news import express_news_crawler
from .Modules.Web.geo_news import geo_news_scrapper
from .Modules.Web.dunya import duniya_news_scrap
from .Modules.Ad_tracking.main import ads_detection
from .Modules.Web.app import app_scrape
import pandas as pd
# from celery import app
# @app.task
@shared_task(bind=True)
def ad_tracking_urdu_point(self):
    try:
        ads_detection(source="urdu_point")
        print("Ads detection done of urdu point")
    except:
        pass
    
def profile_scrap(profile,source):
    if source=="facebook" or source=="Facebook":
        try:
            facebook_profile(profile)
            
        except:
            pass
    elif source=="Twitter" or source=="twitter":
        users,tweets=profile_tweets_driver(profile)
        print("---------------------------------------------------",tweets)
        print("Twitter profile saving: ",profile,users,len(tweets))
        for index,row in users.iterrows():
            # try:
            instance=twitter_user(
                id=row['id'],
                is_blue_varified=row['is_blue_verified'],
                can_dm=row['can_dm'],
                created_at=row['created_at'],
                default_profile=row['default_profile'],
                user_description=row['user_description'],
                display_url=row['display_url'], 
                expanded_url=row['expanded_url'],
                link=row['link'],
                favourites_count=row['favourites_count'],
                fast_followers_count=row['fast_followers_count'],
                followers_count=row['followers_count'],
                friends_count=row['friends_count'],
                location=row['location'],
                media_count=row['media_count'],
                name=row['name'],
                normal_followers_count=row['normal_followers_count'],
                screen_name=row['screen_name'],
                statuses_count=row['statuses_count'],
                created_at_time=datetime.now()
            )
            instance.save()
            
            # except:
            #     pass
        for index,row in tweets.iterrows():
            print("-----------------------------------------",row['id'])
            try:
                tweeter_user=twitter_user.objects.get(id=row['id'])
                instance=scraped_tweets(
                    Tid=tweeter_user,
                    description=row['description'],
                    views=row['views'],
                    reply_count=row['reply'],
                    quote_count=row['quote_count'],
                    favorite_count=row['favorite_count'],
                    retweet_count=row['retweet_count'],
                    bookmark_count=row['bookmark_count'],
                    created_at_time=row['created_at'],
                    image=row['image'],
                    link=row['link'],
                    Media_data=row['image_data'],
                    last_scraped_tweet=datetime.now(),
                    keyword=row['keyword'],
                )
                instance.save()
                
            except:
                print("Profile Not Exists")
        del users
        del tweets
    elif source=="Youtube" or source=="youtube":
        user,videos=channel_crawler_youtube_driver(profile)
        print("-------------------------------",user)
        for index, row in user.iterrows():
            try:
                if youtube_channel.objects.filter(row['details']['url']).count()>0:
                    channel=youtube_channel.objects.filter(row['details']['url']).first()
                    channel.subscriber_count=row['details']['subscriber_count']
                    channel.videos_count=row['details']['videos_count']
                    channel.views=row['details']['views']
                    channel.save()
                else:
                    instance = youtube_channel(
                        description=row['description'],
                        links=row['links'],
                        # email=row['details']['email'],
                        url=row['details']['url'],
                        subscriber_count=row['details']['subscriber_count'],
                        videos_count=row['details']['videos_count'],
                        views=row['details']['views'],
                        join_date=row['details']['join_date'],
                        country=row['details']['country'],
                        channel_name=row['channel_name'],
                        last_scraped_user=datetime.now()
                    )

                    instance.save()
            except Exception as e:
                print("e")
                
        for index, row in videos.iterrows():
        #     print(row)
            try:
                channel=youtube_channel.objects.get(channel_name=row['channel_name'])
                if youtube_video.objects.filter(title=row['title']).count()==0:
                    instance = youtube_video(
                        title=row['title'],
                        video_duration=row['video_duration'],
                        views_count=row['views_count'],
                        link=row['link'],
                        channel_name=channel,
                        image=row['image'],
                        keyword=row['keyword'],
                        upload_date=row['upload_date'],
                        last_scraped_video=datetime.now()
                    )

                    instance.save()
                    print("Videosaved")
                else:
                    yt_post=youtube_video.objects.filter(title=row['title']).first()
                    yt_post.views_count=row['views_count']
                    yt_post.last_scraped_video=datetime.now()
                    yt_post.save()
            except Exception as e:
                print(f"Error: {e} video not saved")
            #     # pass
        
        
        del user
        del videos




        
    


def data_to_db(data):
    for index,row in data.iterrows():
        try:
            if web.objects.filter(link=row['link']).count()>0:
                pass
            else:
                news_obj=web.objects.create(
                    title=row['title'],
                    link=row['link'],
                    image=row['image'],
                    description=row['description'],
                    news_creation_date=row['news_creation_date'],
                    platform=row['platform']
                )
                news_obj.save()
                print("News Saved")
        except Exception as e:
            print(e)
    
############################################## Uncomment ############################################
@shared_task(bind=True)
def web_scrapers_nimar(self):
    print("############ scrapping bol News ################")
    bol_news=bol_news_scraper()
    data_to_db(bol_news)
    print("############ scrapping bol News Done ################")
    
    # print("############ scrapping jang News ################")
    # # jang_news=jang_news_scraper()
    # # 
    print("############ scrapping dawn News ################")
    dawn_news=dawn_news_scrape()
    data_to_db(dawn_news)
    print("############ scrapping dawn News Done ################")
    
    print("############ scrapping ary News ################")
    ary_news=scrape_ary_news()
    data_to_db(ary_news)
    print("############ scrapping Ary News Done ################")
    # print(ary_news)
    print("############ scrapping daily pakistan News ################")
    daily_pk=daily_pakistan()
    data_to_db(daily_pk)
    print("############ scrapping daily pakistan News Done ################")
    
    print("############ scrapping express News ################")
    express=express_news_crawler()
    data_to_db(express)
    print("############ scrapping express News Done ################")
    
    print("############ scrapping Geo News ################")
    geo_news=geo_news_scrapper()
    data_to_db(geo_news)
    print("############ scrapping Geo News Done################")
    print("############ scrapping duniya News ################")
    news=duniya_news_scrap()
    data_to_db(news)
    print("############ scrapping duniya News ################")
    app_scrape(scrape_all_pages=True)
    return "News Scraping done"
    
# app_scrape() 
    
# @shared_task(bind=True)
# @shared_task
# @background(schedule=900)
# @shared_task(bind=True) 
# def keyword_based_scraping(self):
#     all_keywords = list(keyword.objects.values_list('keywords', flat=True))
#     # all_youtube = list(keyword.objects.values_list('youtube_keyword', flat=True))
#     all_facebook_crawl = list(keyword.objects.values_list('facebook_crawl', flat=True))
#     all_youtube_crawl=list(keyword.objects.values_list('youtube_crawl', flat=True))
#     all_twitter_crawl=list(keyword.objects.values_list('twitter_crawl', flat=True))
    
#     count_user=0
#     count_tweets=0
#     count_videos=0
    
#     # all_checked=list(profiles.objects.values_list('checked', flat=True))
#     twitter_search=[]
#     youtube_keywords=[]
#     youtube_videos_profiles=[]
#     twitter_profiles=[]
#     facebook_profiles=[]
#     for index in range(len(all_keywords)):
#         if all_youtube_crawl[index]==True:
#             youtube_keywords.append(all_keywords[index])
#         if all_twitter_crawl[index]==True:
#             twitter_search.append(all_keywords[index])
#         if all_facebook_crawl[index]==True:
#             facebook_profiles.append(all_keywords[index])
#         # youtube_keywords.append(all_keywords[index])
#         # twitter_search.append(all_keywords[index]) Post	Reactions	Shares	Comments	Type	Upload Time	Shared	Thumbnail Link	keyword	link

#     print("---------------------------------------------------------------------")
#     print(youtube_keywords,twitter_search,facebook_profiles)
#     print("---------------------------------------------------------------------")
#     for f_keyword in facebook_profiles:
#         posts_df=facebook_keyword(f_keyword)
#         for index,row in posts_df.iterrows():
#             try:
#                 if facebook_post.objects.filter(post=row['Post']).count()<=0:
#                     instance = facebook_post(
#                         post=row['Post'],
#                         reactions=row['Reactions'],
#                         shares=row['Shares'],
#                         comments=row['Comments'],
#                         type=row['Type'],
#                         upload_time=row['Upload Time'],
#                         shared=row['Shared'],
#                         thumbnail_link=row['Thumbnail Link'],
#                         keyword=row['keyword'],
#                         link=row['link'],
#                         last_scraped=datetime.now()
#                     )

#                     instance.save()
#                 else:
#                     print("Post Already Exists")
#             except:
#                 print("Post Not saved")
#     # # return 0
#     for t_keyword in twitter_search:
#         df,users=twitter_keyword_driver(t_keyword)
#         for index,row in users.iterrows():
#             try:
#                 instance=twitter_user(
#                     id=row['id'],
#                     is_blue_varified=row['is_blue_verified'],
#                     can_dm=row['can_dm'],
#                     created_at=row['created_at'],
#                     default_profile=row['default_profile'],
#                     user_description=row['user_description'],
#                     display_url=row['display_url'], 
#                     expanded_url=row['expanded_url'],
#                     link=row['link'],
#                     favourites_count=row['favourites_count'],
#                     fast_followers_count=row['fast_followers_count'],
#                     followers_count=row['followers_count'],
#                     friends_count=row['friends_count'],
#                     location=row['location'],
#                     media_count=row['media_count'],
#                     name=row['name'],
#                     normal_followers_count=row['normal_followers_count'],
#                     screen_name=row['screen_name'],
#                     statuses_count=row['statuses_count'],
#                     created_at_time=datetime.now()
#                 )
#                 instance.save()
#                 count_user+=1
#                 print(count_user)
#             except:
#                 pass
#         for index,row in df.iterrows():
#             tweeter_user=twitter_user.objects.get(id=row['id'])
#             try:
#                 instance=scraped_tweets(
#                     Tid=tweeter_user,
#                     description=row['description'],
#                     views=row['views'],
#                     reply_count=row['reply'],
#                     quote_count=row['quote_count'],
#                     favorite_count=row['favorite_count'],
#                     retweet_count=row['retweet_count'],
#                     bookmark_count=row['bookmark_count'],
#                     created_at_time=row['created_at'],
#                     image=row['image'],
#                     link=row['link'],
#                     Media_data=row['image_data'],
#                     last_scraped_tweet=datetime.now(),
#                     keyword=row['keyword'],
#                 )
#                 instance.save()
#                 count_tweets+=1
#                 print(count_tweets)
#             except:
#                 print("Error")
    
#     for y_keyword in youtube_keywords:
#         df=youtube_keyword_crawler(y_keyword)
#         # for index, row in df.iterrows():
#         #     print(index)
#         #     try:
#         #         if youtube_video.objects.filter(title=row['title']).count()>0:
#         #             print("video already exists")
#         #         else:
#         #             instance = youtube_video(
#         #                 title=row['title'],
#         #                 video_duration=row['video_duration'],
#         #                 views_count=row['views_count'],
#         #                 link=row['link'],
#         #                 channel_name=row['channel_name'],
#         #                 image=row['image'],
#         #                 keyword=row['keyword'],
#         #                 upload_date=row['upload_date'],
#         #                 last_scraped_video=datetime.now()
#         #             )

#         #             instance.save()
#         #             count_videos+=1
#         #     except:
#         #         pass
#     print("keyword_result",count_user,count_tweets)
#     return count_user,count_tweets,"keyword scrapping done"
    ################################################################## Uncomment this
# @shared_task 
# @background(schedule=900)
@shared_task(bind=True) 
def profile_based_scraping_nimar(self):
    all_profiles = list(profiles.objects.values_list('profile', flat=True))
    all_sources = list(profiles.objects.values_list('source', flat=True))
    all_checked=list(profiles.objects.values_list('checked', flat=True))
    twitter_search=[]
    youtube_profiles=[]
    youtube_videos_profiles=[]
    twitter_profiles=[]
    facebook_profiles=[]
    twitter_search=[]
    
    count_user=0
    count_tweets=0
    count_videos=0
    count_profiles=0
    
    for index in range(len(all_profiles)):
        if all_sources[index]=='twitter' or all_sources[index]=='Twitter':
            twitter_search.append(all_profiles[index])
        elif all_sources[index]=='youtube' or all_sources[index]=='Youtube':
            youtube_profiles.append(all_profiles[index])
        elif all_sources[index]=='facebook' or all_sources[index]=='Facebook':
            facebook_profiles.append(all_profiles[index])
    print("twitter searches available are: ",twitter_search,youtube_profiles)
    facebook_profile()
    
    
    # for prof in facebook_profiles:
    #     try:
    #         posts_df=facebook_profile(prof)
    #         for index,row in posts_df.iterrows():
    #             if facebook_post.objects.filter(post=row['Post']).count()<=0:
    #                 instance = facebook_post(
    #                     post=row['Post'],
    #                     reactions=row['Reactions'],
    #                     shares=row['Shares'],
    #                     comments=row['Comments'],
    #                     type=row['Type'],
    #                     upload_time=row['Upload Time'],
    #                     shared=row['Shared'],
    #                     thumbnail_link=row['Thumbnail Link'],
    #                     keyword=row['keyword'],
    #                     link=row['link'],
    #                     last_scraped=datetime.now()
    #                 )

    #                 instance.save()
    #             else:
    #                 print("Post Already Exists")
    #     except:
    #         pass
    #             # except:
    #             #     print("Post Not saved")
    
    for twitter_s in twitter_search:
        users,tweets=profile_tweets_driver(twitter_s)
        print("---------------------------------------------------",tweets)
        print("Twitter profile saving: ",twitter_s,users,len(tweets))
        for index,row in users.iterrows():
            try:
                if twitter_user.objects.filter(id=row['id']).count()>0:
                    tw_obj=twitter_user.objects.filter(id=row['id']).first()
                    tw_obj.favourites_count=row['favourites_count'],
                    tw_obj.fast_followers_count=row['fast_followers_count'],
                    tw_obj.followers_count=row['followers_count'],
                    tw_obj.friends_count=row['friends_count'],
                    tw_obj.location=row['location'],
                    tw_obj.media_count=row['media_count'],
                    tw_obj.name=row['name'],
                    tw_obj.normal_followers_count=row['normal_followers_count'],
                    tw_obj.screen_name=row['screen_name'],
                    tw_obj.statuses_count=row['statuses_count'],
                    tw_obj.save()
                    print("Tweeter user updated")
                else:
                    instance=twitter_user(
                        id=row['id'],
                        is_blue_varified=row['is_blue_verified'],
                        can_dm=row['can_dm'],
                        created_at=row['created_at'],
                        default_profile=row['default_profile'],
                        user_description=row['user_description'],
                        display_url=row['display_url'], 
                        expanded_url=row['expanded_url'],
                        link=row['link'],
                        favourites_count=row['favourites_count'],
                        fast_followers_count=row['fast_followers_count'],
                        followers_count=row['followers_count'],
                        friends_count=row['friends_count'],
                        location=row['location'],
                        media_count=row['media_count'],
                        name=row['name'],
                        normal_followers_count=row['normal_followers_count'],
                        screen_name=row['screen_name'],
                        statuses_count=row['statuses_count'],
                        created_at_time=datetime.now()
                    )
                    instance.save()
                    count_user+=1
                    print(count_user)
            except:
                pass
        for index,row in tweets.iterrows():
            print("-----------------------------------------",row['id'])
            try:
                tweeter_user=twitter_user.objects.get(id=row['id'])
                if scraped_tweets.objects.filter(description=row['description']).count()>0:
                    tw_obj=scraped_tweets.objects.filter(description=row['description'])
                    tw_obj.views=row['views'],
                    tw_obj.reply_count=row['reply'],
                    tw_obj.quote_count=row['quote_count'],
                    tw_obj.favorite_count=row['favorite_count'],
                    tw_obj.retweet_count=row['retweet_count'],
                    tw_obj.bookmark_count=row['bookmark_count']
                    tw_obj.save()
                    print("Tweet updated")
                else:
                    instance=scraped_tweets(
                        Tid=tweeter_user,
                        description=row['description'],
                        views=row['views'],
                        reply_count=row['reply'],
                        quote_count=row['quote_count'],
                        favorite_count=row['favorite_count'],
                        retweet_count=row['retweet_count'],
                        bookmark_count=row['bookmark_count'],
                        created_at_time=row['created_at'],
                        image=row['image'],
                        link=row['link'],
                        Media_data=row['image_data'],
                        last_scraped_tweet=datetime.now(),
                        keyword=row['keyword'],
                    )
                    instance.save()
                    count_tweets+=1
                    print(count_tweets)
            except:
                print("Profile Not Exists")
            
            # except:
            #     pass
        # except:
        #     print("Invalid Profile")
    
    for profile in youtube_profiles:
        user,videos=channel_crawler_youtube_driver(profile)
        print("-------------------------------",user)
        for index, row in user.iterrows():
            try:
                if youtube_channel.objects.filter(row['details']['url']).count()>0:
                    channel=youtube_channel.objects.filter(row['details']['url']).first()
                    channel.subscriber_count=row['details']['subscriber_count']
                    channel.videos_count=row['details']['videos_count']
                    channel.views=row['details']['views']
                    channel.save()
                else:
                    instance = youtube_channel(
                        description=row['description'],
                        links=row['links'],
                        # email=row['details']['email'],
                        url=row['details']['url'],
                        subscriber_count=row['details']['subscriber_count'],
                        videos_count=row['details']['videos_count'],
                        views=row['details']['views'],
                        join_date=row['details']['join_date'],
                        country=row['details']['country'],
                        channel_name=row['channel_name'],
                        last_scraped_user=datetime.now()
                    )

                    instance.save()
            except Exception as e:
                print("e")
        for index, row in videos.iterrows():
        #     print(row)
            try:
                channel=youtube_channel.objects.get(channel_name=row['channel_name'])
                if youtube_video.objects.filter(title=row['title']).count()==0:
                    instance = youtube_video(
                        title=row['title'],
                        video_duration=row['video_duration'],
                        views_count=row['views_count'],
                        link=row['link'],
                        channel_name=channel,
                        image=row['image'],
                        keyword=row['keyword'],
                        upload_date=row['upload_date'],
                        last_scraped_video=datetime.now()
                    )

                    instance.save()
                    print("Videosaved")
                else:
                    yt_post=youtube_video.objects.filter(title=row['title']).first()
                    yt_post.views_count=row['views_count']
                    yt_post.last_scraped_video=datetime.now()
                    yt_post.save()
            except Exception as e:
                print(f"Error: {e} video not saved")
            #     # pass
        
    return "profile scraping done"
            
# async_task_one = async_task(keyword_based_scraping)
# async_task_two = async_task(profile_based_scraping)
        