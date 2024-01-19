
# from .models import Youtube_Channel profile_tweets_driver
from .Modules.TwitterApi.Twitter_keyword import twitter_keyword_driver
from .Modules.TwitterApi.TwitterProfile import profile_tweets_driver
from .Modules.Youtube.YT_channel_crawler import channel_crawler_youtube_driver
from .Modules.Youtube.YT_keyword_crawler import youtube_keyword_crawler
import pandas as pd
from django.db.models.functions import Substr
# Create your views here.
from django.db.models import Sum
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.decorators import api_view
import datetime
from .models import *
from django.db.models import Q, F, Value, CharField
from .serializers import *
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .Modules.utility import *
from django.core.serializers import serialize
from django.db.models import F, Case, When, Value, CharField,DecimalField, ExpressionWrapper,IntegerField
from django.db.models.functions import Cast
# from django.db import connection
from collections import defaultdict
from django.db.models import Count
from django.db.models.functions import TruncDate
from itertools import groupby
from operator import itemgetter
# from .models import keyword
import tldextract
from rest_framework import status
import threading
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.serializers import serialize
import pytz
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
######################################################## Nimar Modules ########################################################

@csrf_exempt
@api_view(['GET'])
def reset_profiles(request):
    try:
        state=request.query_params.get('state',None)
        if state is None:
            return Response(status.HTTP_400_BAD_REQUEST)
        print("State",state)
        profiles_view=profiles.objects.all()
        for profile in profiles_view:
            profile.checked=state
            profile.save()
        return Response(status.HTTP_200_OK)
    except Exception as e:
        return Response({'message':e},status.HTTP_500_INTERNAL_SERVER_ERROR)

@permission_classes([AllowAny])
class ADsView(APIView):
    def get(self,request):
        try:
            ads=Ads_table.objects.all()
            serializer=ads_serializer(ads,many=True)
            return Response(serializer.data) 
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def post(self,request):
        try:
            ad_name = request.POST.get('ad_name', None)
            start_date = request.POST.get('start_date', None)
            end_date=request.POST.get('end_date',None)
            source=request.POST.get('source',None)
            if Ads_table.objects.filter(ad_name=ad_name,source=source).count()>0:
                return Response({"Message":"Already Exists"},status.HTTP_302_FOUND)
            if source is None:
                return Response({"Message":"Please provide any source"},status.HTTP_400_BAD_REQUEST)
            if source == 'urdu_point' or source == 'hum_news' or source =='jang_news':
                pass
            else:
                return Response({"Message":"Please provide valid source"},status.HTTP_400_BAD_REQUEST)
               
            if start_date is not None:
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            if end_date is not None:
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            if ad_name is None:
                return Response({"Message": "Please provide an ad_name"},status.HTTP_404_NOT_FOUND)

            # Get the image from request.FILES
            file = request.FILES.get('template_image')
            if file:
                # Save the file
                path = default_storage.save('static/templates/{source}' + file.name, ContentFile(file.read()))
                ad = Ads_table(ad_name=ad_name, template_path=path, start_date=start_date,end_date=end_date,source=source)
                ad.save()
                return Response({"Message": "Ad created successfully"},status.HTTP_201_CREATED)
            else:
                return Response({"Message": "Please provide an image"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"Message" : f"500 Internal Server Error {e}"},status.HTTP_500_INTERNAL_SERVER_ERROR)
    def put(self,request):
        try:
            data=json.loads(request.body.decode("utf-8"))
            print("------------",data)
            ad_name=data.get('ad_name',None)
            if ad_name is None:
                return Response({"Message": "Please provide an ad_name"},status.HTTP_400_BAD_REQUEST)
            ad=Ads_table.objects.get(ad_name=ad_name)
            print(ad)
            if ad:
                source=data.get('source',None)
                if source is not None:
                    ad.source=source
                # try:
                start_date = data.get('start_date', None)
                if start_date is not None:
                    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                    ad.start_date=start_date
                # except:
                #     pass
                # try:
                end_date = data.get('end_date', None)
                if end_date is not None:
                    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
                    ad.end_date=end_date
                # except:
                #     pass
                
                # try:
                tracking=data.get('tracking',None)
                if tracking is not None:
                    ad.tracking=tracking
                # except:
                #     pass
                ad.save()
                return Response({"Message":"Ad Updated Successfully"},status.HTTP_200_OK)
            else:
                return Response({"Message":"Ad not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"Message" : f"500 Internal Server Error {e}"},status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self,request):
        try:
            data=json.loads(request.body.decode("utf-8"))
            ad_name=data.get('ad_name',None)
            if ad_name is None:
                return Response({"Message": "Please provide an ad_name"},status.HTTP_404_NOT_FOUND)
            ad=Ads_table.objects.get(ad_name=ad_name)
            if ad:
                os.remove(ad.template_path)
                # print("ad",ad.template_path)
                ad.delete()
                return Response({"Message":"Ad Deleted Successfully"},status.HTTP_200_OK)
            else:
                return Response({"Message":"Ad not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"Message" : f"500 Internal Server Error {e}"},status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_tweets_with_user(profiles,start_date=None,end_date=None,keyword_search=None):
    try:
        result_list=[]
        if keyword_search is not None:
            tweets_with_user_info = scraped_tweets.objects.filter(Tid__screen_name__in=profiles).select_related('Tid')
            print("tweets_with_user_info count",tweets_with_user_info.count())
            tweets_with_user_info = tweets_with_user_info.filter(Q(keyword__icontains=keyword_search) | 
                                                                Q(description__icontains=keyword_search))
            if start_date is not None:
                tweets_with_user_info=tweets_with_user_info.filter(created_at_time__gte=start_date)
            if end_date is not None:
                tweets_with_user_info=tweets_with_user_info.filter(created_at_time__lte=end_date)
        else:
            tweets_with_user_info = scraped_tweets.objects.filter(Tid__screen_name__in=profiles).select_related('Tid')
        print(tweets_with_user_info.count())
        for tweet in tweets_with_user_info:
            user_info = tweet.Tid
            user_info_data = {
                'id': user_info.id,
                'is_blue_varified': user_info.is_blue_varified,
                'can_dm': user_info.can_dm,
                'created_at': user_info.created_at,
                'default_profile': user_info.default_profile,
                'user_description': user_info.user_description,
                'display_url': user_info.display_url,
                'expanded_url': user_info.expanded_url,
                'link': user_info.link,
                'favourites_count': user_info.favourites_count,
                'fast_followers_count': user_info.fast_followers_count,
                'followers_count': user_info.followers_count,
                'friends_count': user_info.friends_count,
                'location': user_info.location,
                'media_count': user_info.media_count,
                'name': user_info.name,
                'normal_followers_count': user_info.normal_followers_count,
                'screen_name': user_info.screen_name,
                'statuses_count': user_info.statuses_count,
                'created_at_time': user_info.created_at_time,
                'description': tweet.description,
                'views': tweet.views,
                'reply_count': tweet.reply_count,
                'quote_count': tweet.quote_count,
                'favorite_count': tweet.favorite_count,
                'retweet_count': tweet.retweet_count,
                'bookmark_count': tweet.bookmark_count,
                'created_at_time_tweet': tweet.created_at_time,
                'image': tweet.image,
                'link': tweet.link,
                'Media_data': tweet.Media_data,
                'last_scraped_tweet': tweet.last_scraped_tweet,
                'keyword': tweet.keyword,
                'view': tweet.view,
                'platform_type': tweet.platform_type,
            }
            result_list.append(user_info_data)
        return result_list
    except Exception as e:
        print(f"Exception is {e}")
        return []

def get_videos_with_channel(youtube_profiles,start_date=None,end_date=None,keyword_search=None):
    try:
        result_list=[]
        if keyword_search is not None:
            videos_with_channel=youtube_video.objects.filter(channel_name__in=youtube_profiles).filter(Q(keyword__icontains=keyword_search) | 
                                                                Q(title__icontains=keyword_search)).filter().select_related('channel_name')
            if start_date is not None:
                videos_with_channel=videos_with_channel.filter(upload_date__gte=start_date)
            if end_date is not None:
                videos_with_channel=videos_with_channel.filter(upload_date__lte=end_date)
        else:
            videos_with_channel=youtube_video.objects.filter(channel_name__in=youtube_profiles).select_related('channel_name')
        print("videos_count",videos_with_channel.count())
        for video in videos_with_channel:
            channel_info = video.channel_name
            channel_info_data = {
                'channel_name': channel_info.channel_name,
                'channel_description': channel_info.description,
                'channel_url': channel_info.url,
                'subscriber_count': channel_info.subscriber_count,
                'video_count': channel_info.videos_count,
                'view_count': channel_info.views,
                'created_at_time': channel_info.join_date,
                'country': channel_info.country,
                'last_scraped_user': channel_info.last_scraped_user,
                'title': video.title,
                'video_duration': video.video_duration,
                'views_count': video.views_count,
                'link': video.link,
                'image': video.image,
                'keyword': video.keyword,
                'upload_date': video.upload_date,
                'last_scraped_video': video.last_scraped_video,
                'platform_type': video.platform_type,  
            }
            result_list.append(channel_info_data)
        return result_list
    except Exception as e:
        print(f"Exception is {e}")
        return []
@csrf_exempt
@api_view(['GET'])
def get_profiles_data(request):
    page_number=request.query_params.get('page', 1)
    print("page_number",page_number)
    page_size=48
    all_profiles = list(profiles.objects.values_list('profile', flat=True))
    all_sources = list(profiles.objects.values_list('source', flat=True))
    all_checked=list(profiles.objects.values_list('checked', flat=True))
    twitter_profiles=[]
    facebook_profiles=[]
    youtube_profiles=[]
    web_profiles=[]
    for index in range(len(all_profiles)):
        if all_checked[index]==True:
            if all_sources[index]=='twitter' or all_sources[index]=='Twitter':
                twitter_profiles.append(all_profiles[index])
            elif all_sources[index]=='youtube' or all_sources[index]=='Youtube':
                youtube_profiles.append(all_profiles[index])
            elif all_sources[index]=='facebook' or all_sources[index]=='Facebook':
                facebook_profiles.append(all_profiles[index])
            elif all_sources[index]=='web' or all_sources[index]=='Web':
                web_profiles.append(all_profiles[index])
    tweets = []
    videos=[]
    posts=[]
    web_posts=[]
    if len(twitter_profiles)>0:
        tweets=get_tweets_with_user(twitter_profiles)
    if len(youtube_profiles)>0:
        videos=get_videos_with_channel(youtube_profiles)
    if len(facebook_profiles)>0:
        facebook_posts=facebook_post.objects.filter(account__in=facebook_profiles)
        posts=facebook_post_serializer(facebook_posts,many=True).data 
        for post in posts:
            try:
                if post['last_scraped']:
                    post['last_scraped'] = pytz.utc.localize(datetime.strptime(post['last_scraped'], "%Y-%m-%dT%H:%M:%S.%fZ"))
                else:
                    print("last_scraped is None or empty")
            except ValueError as e:
                print(f"Error converting 'last_scraped' to datetime: {e}")
                print("Not changed")
                # pass
    if len(web_profiles)>0:
        web_posts=web.objects.filter(platform__in=web_profiles)
        web_posts=web_serializer(web_posts,many=True).data
        for post in web_posts:
            try:
                if post['news_creation_date']:
                    post['news_creation_date'] = pytz.utc.localize(datetime.strptime(post['news_creation_date'],'%Y-%m-%dT%H:%M:%SZ'))
                else:
                    print("news_creation_date is None or empty")
            except ValueError as e:
                print(f"Error converting 'news_creation_date' to datetime: {e}")
                print("Not changed")
    combined_media_data=tweets+videos+posts+web_posts
    print("combined_media_data",len(combined_media_data))
    print("combined_media_data",len(combined_media_data),len(tweets),len(videos),len(posts),len(web_posts))
    sorted_combined_list = sorted(combined_media_data, key=sort_by_date,reverse=True)
    paginated_data=[]
    try:
        paginator = Paginator(sorted_combined_list, 48)
        try:
            yt_queryset = paginator.page(page_number)
            paginated_data=list(yt_queryset)
        except PageNotAnInteger:
            yt_queryset = paginator.page(1)
            paginated_data=list(yt_queryset)
            
        except EmptyPage:
            yt_queryset = paginator.page(paginator.num_pages)
            paginated_data=list(yt_queryset)
            
    except:
        pass
        # return Response({'comb_data':comb_data},status.HTTP_200_OK)
    return Response({'sorted_posts':paginated_data,
                     'next': f'/get_profiles_data/?page={int(page_number) + 1}',
                    'previous': f'/get_profiles_data/?page={int(page_number) - 1}' if int(page_number) > 1 else None,
                    'current_page': int(page_number),
                    'total_pages': (len(paginated_data) + page_size - 1) // page_size},status=status.HTTP_200_OK)

def sort_by_date(item):
    try:
        if 'upload_date' in item:
            return item['upload_date']
        elif 'created_at_time_tweet' in item:
            return item['created_at_time_tweet']
        elif 'last_scraped' in item:
            print(type(item['last_scraped']))
            return item['last_scraped']
        elif 'news_creation_date' in item:
            return item['news_creation_date']
        else:
            return ''
    except:
        pass





@csrf_exempt
@api_view(['GET'])
def get_track_ad(request,ad):
    print(ad)
    ads=Ads_table.objects.get(ad_name=ad)
    webAds=web_ads.objects.filter(ad_name=ads)
    records=web_ads_serializer(webAds,many=True).data
    return Response({"records":records, "status":status.HTTP_200_OK})

        

###############################################################################################################################

def get_videos_with_profiles(profile):
    """
    Retrieves a list of videos associated with a given profile.

    Parameters:
    - profile (str): The name of the profile to retrieve videos for.

    Returns:
    - list: A list of video objects containing the following fields:
        - title (str): The title of the video.
        - video_duration (str): The duration of the video.
        - views_count (int): The number of views the video has.
        - link (str): The link to the video.
        - image (str): The URL of the video's thumbnail image.
        - channel_name (str): The name of the channel the video belongs to.
        - keyword (str): The keyword associated with the video.
        - upload_date (str): The date the video was uploaded.
        - last_scraped_video (str): The date the video was last scraped.
        - description (str): The description of the video.
        - links (str): The links associated with the video.
        - email (str): The email associated with the video.
        - url (str): The URL associated with the video.
        - subscriber_count (int): The number of subscribers the channel has.
        - videos_count (int): The number of videos the channel has.
        - views (int): The total number of views the channel has.
        - join_date (str): The date the channel joined.
        - country (str): The country the channel belongs to.
        - last_scraped_user (str): The date the user was last scraped.
    """
    try:
        channel_info = youtube_channel.objects.get(channel_name=profile)
        # channel_info=channel_info[0]
        # Query youtube_video based on channel_name
        result = youtube_video.objects.filter(channel_name=profile).values(
            'title',
            'video_duration',
            'views_count',
            'link',
            'image',
            'channel_name',
            'keyword',
            'upload_date',
            'last_scraped_video',
            'view',
            'platform_type'
        )

        # Add channel-related information to each result
        for item in result:
            item.update({
                'description': channel_info.description,
                'links': channel_info.links,
                'email': channel_info.email,
                'url': channel_info.url,
                'subscriber_count': channel_info.subscriber_count,
                'videos_count': channel_info.videos_count,
                'views': channel_info.views,
                'join_date': channel_info.join_date,
                'country': channel_info.country,
                'last_scraped_user': channel_info.last_scraped_user,
            })

            # Print or use the modified results
        print("result count",result.count())
        return result
    except:
        return youtube_video.objects.none()

def get_tweets_with_profiles_using_keywords(keywords):
    """
    Retrieves tweets with profiles based on the given keywords.

    Args:
        keywords (list): A list of keywords to search for in the tweets.

    Returns:
        list: A list of dictionaries containing the retrieved tweets and their associated user profiles.

    """
    q_object = Q()
    for keyword in keywords:
        q_object |= Q(keyword__icontains=keyword) | Q(description__icontains=keyword)

    # Perform inner join-like operation with select_related
    tweets_with_user = scraped_tweets.objects.select_related('Tid').filter(q_object)

    # Access the queryset directly
    result_queryset = tweets_with_user.values(
        'Tid__id',
        'Tid__is_blue_varified',
        'Tid__can_dm',
        'Tid__created_at',
        'Tid__default_profile',
        'Tid__user_description',
        'Tid__display_url',
        'Tid__expanded_url',
        'Tid__link',
        'Tid__favourites_count',
        'Tid__fast_followers_count',
        'Tid__followers_count',
        'Tid__friends_count',
        'Tid__location',
        'Tid__media_count',
        'Tid__name',
        'Tid__normal_followers_count',
        'Tid__screen_name',
        'Tid__statuses_count',
        'Tid__created_at_time',
        'description',
        'views',
        'reply_count',
        'quote_count',
        'favorite_count',
        'retweet_count',
        'bookmark_count',
        'created_at_time',
        'image',
        'link',
        'Media_data',
        'last_scraped_tweet',
        'keyword',
        'view',
        'platform_type'
    )

    # Serialize the queryset to JSON
    # serialized_tweets = serialize('json', tweets_with_user, fields=fields_to_include, use_natural_primary_keys=True)
    # serialized_tweets=[]
    # # for result in result_queryset:
    # #     # Process each row in the result queryset
    # #     serialized_tweets.append(result)

    # # Alternatively, you can convert the queryset to a list if needed
    # result_list = list(result_queryset)
    # for result in result_list:
    #     serialized_tweets.append(result)
    return result_queryset


def get_twitter_counts_on_keyword(keyword):
    tweets=scraped_tweets.objects.filter(
        Q(keyword__icontains=keyword) |
        Q(description__icontains=keyword)
    ).count()
    return tweets

def get_videos_count_on_keyword(keyword):
    youtube=youtube_video.objects.filter(
        Q(keyword__icontains=keyword) |
        Q(title__icontains=keyword)
    ).count()
    return youtube

def get_videos_profile_count(profile):
    return len(get_videos_with_profiles(profile))


def get_tweets_with_profile_screenname(profile):
    # twitter_user_info = twitter_user.objects.filter(screen_name=profile).values(
    #     'id',
    #     'is_blue_varified',
    #     'can_dm',
    #     'created_at',
    #     'default_profile',
    #     'user_description',
    #     'display_url',
    #     'expanded_url',
    #     'link',
    #     'favourites_count',
    #     'fast_followers_count',
    #     'followers_count',
    #     'friends_count',
    #     'location',
    #     'media_count',
    #     'name',
    #     'normal_followers_count',
    #     'screen_name',
    #     'statuses_count',
    #     'created_at_time',
    # )

    # # Step 2: Query scraped_tweets based on Tid (id from twitter_user)
    # print(scraped_tweets.objects.get(Tid=twitter_user_info['id']))
    # scraped_tweets_info = scraped_tweets.objects.filter(Tid=twitter_user_info['id']).values(
    #     'Tid',
    #     'description',
    #     'views',
    #     'reply_count',
    #     'quote_count',
    #     'favorite_count',
    #     'retweet_count',
    #     'bookmark_count',
    #     'created_at_time',
    #     'image',
    #     'link',
    #     'Media_data',
    #     'last_scraped_tweet',
    #     'keyword',
    # )

    # # Step 3: Merge the results manually
    # merged_results = []

    # for tweet_info in scraped_tweets_info:
    #     # Find corresponding user_info based on Tid (id from twitter_user)
    #     corresponding_user_info = next(
    #         (user_info for user_info in twitter_user_info if user_info['id'] == tweet_info['Tid']),
    #         None
    #     )

    #     # If a corresponding user_info is found, merge the tweet_info and user_info
    #     if corresponding_user_info:
    #         merged_result = {**tweet_info, **corresponding_user_info}
    #         merged_results.append(merged_result)
    # return merged_results
    try:
        tweets_with_user = scraped_tweets.objects.filter(Tid__screen_name=profile).values(
            'Tid__id',
            'Tid__is_blue_varified',
            'Tid__can_dm',
            'Tid__created_at',
            'Tid__default_profile',
            'Tid__user_description',
            'Tid__display_url',
            'Tid__expanded_url',
            'Tid__link',
            'Tid__favourites_count',
            'Tid__fast_followers_count',
            'Tid__followers_count',
            'Tid__friends_count',
            'Tid__location',
            'Tid__media_count',
            'Tid__name',
            'Tid__normal_followers_count',
            'Tid__screen_name',
            'Tid__statuses_count',
            'Tid__created_at_time',
            'description',
            'views',
            'reply_count',
            'quote_count',
            'favorite_count',
            'retweet_count',
            'bookmark_count',
            'created_at_time',
            'image',
            'link',
            'Media_data',
            'last_scraped_tweet',
            'keyword',
            'view',
            'platform_type'
        )

       
        return tweets_with_user
    except:
        return scraped_tweets.objects.none()
    
    
@csrf_exempt
@api_view(['GET'])
def search_on_keyword_profile(request):
    try:
        page_number=request.query_params.get('page', 1)
        print("page_number",page_number)
        page_size=48
        print(request)
        keyword_search=request.query_params.get('keyword',None)
        if keyword_search is None:
            return Response({'message':'Please provide keyword'},status.HTTP_404_NOT_FOUND)
        try:
            start_date = datetime.strptime(request.query_params.get('start_date'), '%Y-%m-%d').date() #data.get('start_date')
            print(type(start_date))
        except:
            start_date = None
        try:
            end_date = datetime.strptime(request.query_params.get('end_date'), '%Y-%m-%d').date()#data.get('end_date')
            print(type(end_date))
        except:
            end_date = None
        print("start_date",start_date,"end_date",end_date)
        all_profiles = list(profiles.objects.values_list('profile', flat=True))
        all_sources = list(profiles.objects.values_list('source', flat=True))
        all_checked=list(profiles.objects.values_list('checked', flat=True))
        
        
        # all_checked=list(profiles.objects.values_list('checked', flat=True))
        twitter_search=[]
        youtube_profiles=[]
        
        facebook_search=[]
        facebook_posts=[]
        web_profiles=[]
        
        for index in range(len(all_profiles)):
            if all_checked[index]==True:
                if all_sources[index]=='twitter' or all_sources[index]=='Twitter':
                    twitter_search.append(all_profiles[index])
                elif all_sources[index]=='youtube' or all_sources[index]=='Youtube':
                    youtube_profiles.append(all_profiles[index])
                elif all_sources[index]=='facebook' or all_sources[index]=='Facebook':
                    facebook_search.append(all_profiles[index])
                elif all_sources[index]=='web' or all_sources[index]=='Web':
                    web_profiles.append(all_profiles[index])
        
        tweets = []
        videos=[]
        posts=[]
        web_posts=[]
        
        if len(twitter_search)>0:
            tweets=get_tweets_with_user(twitter_search,start_date,end_date,keyword_search)
        if len(youtube_profiles)>0:
            videos=get_videos_with_channel(youtube_profiles,start_date,end_date,keyword_search)
        if len(facebook_search)>0:
            facebook_posts=facebook_post.objects.filter(account__in=facebook_search)
            if keyword_search is not None:
                facebook_posts=facebook_posts.filter(post__icontains=keyword_search)
            if start_date:
                facebook_posts=facebook_posts.filter(upload_time__gte=start_date)
            if end_date:
                facebook_posts=facebook_posts.filter(upload_time__lte=end_date)
            for post in facebook_posts:
                try:
                    if post['last_scraped']:
                        post['last_scraped'] = pytz.utc.localize(datetime.strptime(post['last_scraped'], "%Y-%m-%dT%H:%M:%S.%fZ"))
                    else:
                        print("last_scraped is None or empty")
                except ValueError as e:
                    print(f"Error converting 'last_scraped' to datetime: {e}")
                    print("Not changed")
            posts=facebook_post_serializer(facebook_posts,many=True).data 
        if len(web_profiles)>0:
            web_posts=web.objects.filter(platform__in=web_profiles)
            if keyword_search is not None:
                web_posts=web_posts.filter(Q(description__icontains=keyword_search)|Q(title__icontains=keyword_search))
            if start_date:
                web_posts=web_posts.filter(news_creation_date__gte=start_date)
            if end_date:
                web_posts=web_posts.filter(news_creation_date__lte=end_date)
            web_posts=web_serializer(web_posts,many=True).data
        
        
        
        combined_media_data=tweets+videos+posts+web_posts
        print("combined_media_data",len(combined_media_data),len(tweets),len(videos),len(posts),len(web_posts))
        # sorted_combined_list = sorted(combined_media_data, key=sort_by_date,reverse=True)
        sorted_combined_list = sorted(combined_media_data, key=sort_by_date,reverse=True)
        paginated_data=[]
        try:
            paginator = Paginator(sorted_combined_list, 48)
            try:
                yt_queryset = paginator.page(page_number)
                paginated_data=list(yt_queryset)
            except PageNotAnInteger:
                yt_queryset = paginator.page(1)
                paginated_data=list(yt_queryset)
                
            except EmptyPage:
                yt_queryset = paginator.page(paginator.num_pages)
                paginated_data=list(yt_queryset)
                
        except:
            pass
        # return Response({'comb_data':comb_data},status.HTTP_200_OK)
        return Response({'sorted_posts':paginated_data,
                        'next': f'/get_profiles_data/?keyword={keyword_search}/start_date={start_date}/end_date={end_date}/page={int(page_number) + 1}',
                        'previous': f'/get_profiles_data/?keyword={keyword_search}/start_date={start_date}/end_date={end_date}/page={int(page_number) - 1}' if int(page_number) > 1 else None,
                        'current_page': int(page_number),
                        'total_pages': (len(paginated_data) + page_size - 1) // page_size},status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"message":f"Exception is {e}"},status.HTTP_500_INTERNAL_SERVER_ERROR)
# @csrf_exempt
# @api_view(['POST'])
# def search_on_keywords(request):
#     try:
#         data=json.loads(request.body.decode("utf-8"))
#         twitter_search_enable=data.get('twitter',True)
#         youtube_search_enable=data.get('youtube',True)
#         facebook_search_enable=data.get('facebook',True)
#         news_search_enable=data.get('news_web',True)
#         keyword_search=data.get('keyword',None)
        
#         if keyword_search is None:
#             return Response({'message':'Please provide keyword','status':status.HTTP_400_BAD_REQUEST})
#         start_date, end_date = None, None


#         start_date_str = data.get('start_date')
#         if start_date_str:
#             try:
#                 start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
#             except ValueError:
#                 return Response({'message': 'Invalid start date format', 'status': status.HTTP_400_BAD_REQUEST})
#         end_date_str = data.get('end_date')
#         if end_date_str:
#             try:
#                 end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
#             except ValueError:
#                 return Response({'message': 'Invalid end date format', 'status': status.HTTP_400_BAD_REQUEST})
#         # web_news=data.get('web_news',True)
#         all_keywords = list(keyword.objects.values_list('keywords', flat=True))
#         page=1
#         items_per_page=10
#         all_youtube = list(keyword.objects.values_list('youtube_keyword', flat=True))
#         all_twitter = list(keyword.objects.values_list('twitter_keyword', flat=True))
#         all_web=list(keyword.objects.values_list('web_keyword', flat=True))
#         all_facebook=list(keyword.objects.values_list('facebook_keyword', flat=True))
#         print("==============================================================================================")
#         print(all_youtube,all_twitter)
#         print("==============================================================================================")
#         twitter_search=[]
#         youtube_keywords=[]
#         web_search=[]
#         facebook_search=[]
#         facebook_posts=[]
#         for index in range(len(all_keywords)):
#             if all_youtube[index]==True:
#                 youtube_keywords.append(all_keywords[index])
#             if all_twitter[index]==True:
#                 twitter_search.append(all_keywords[index])
#             if all_web[index]==True:
#                 web_search.append(all_keywords[index])
#             if all_facebook[index]==True:
#                 facebook_search.append(all_keywords[index])
#         print("==============================================================================================")
#         print(youtube_keywords,twitter_search)
#         print("==============================================================================================")
#         filtered_querysets_twitter=scraped_tweets.objects.none()
#         filtered_querysets_youtube=youtube_video.objects.none()
#         facebook_queryset=facebook_post.objects.none()
#         filtered_querysets_web=web.objects.none()
#         if twitter_search_enable==True:
#             ###################################### Define Empty Serializer ############################################### 
            
#             ##############################################################################################################
#             if len(twitter_search)>=1:
#                 serialized_tweets=get_tweets_with_profiles_using_keywords(twitter_search)
#                 serialized_tweets=serialized_tweets.filter(view=True)
#                 print("==============================================================================================")
#                 print(serialized_tweets.count())
#                 print("==============================================================================================")
                
#                 twitter_condition = Q(keyword__icontains=keyword_search) | Q(description__icontains=keyword_search)
#                 filtered_queryset=serialized_tweets.filter(twitter_condition)
#                 print(filtered_queryset.count())
#                 if start_date:
#                     filtered_queryset = filtered_queryset.filter(created_at_time__gte=start_date)

#                 if end_date:
#                     filtered_queryset = filtered_queryset.filter(created_at_time__lte=end_date)
                
#                 filtered_querysets_twitter=list(filtered_queryset)
#         if youtube_search_enable==True:
#             if len(youtube_keywords)>=1:
#                 q_object = Q()
#                 for keyword_val in youtube_keywords:
#                     q_object |= Q(keyword__icontains=keyword_val) | Q(title__icontains=keyword_val)    
#                 youtube = youtube_video.objects.filter(q_object)
#                 youtube=youtube.filter(view=True)
#                 print("==============================================================================================")
#                 print(youtube.count())
#                 print("==============================================================================================")
                
#                 youtube_condition = Q(title__icontains=keyword_search) | Q(keyword__icontains=keyword_search)
#                 date_conditions=Q()
#                 if start_date:
#                     date_conditions &= Q(upload_date__gte=start_date)

#                 if end_date:
#                     date_conditions &= Q(upload_date__lte=end_date)
#                 combined_condition_youtube = youtube_condition & date_conditions
#                 print("combined_condition_youtube: ",combined_condition_youtube)
#                 filtered_querysets_youtube = youtube.filter(combined_condition_youtube)
#                 print("filtered_querysets_youtube: ",filtered_querysets_youtube)
                
#                 # youtube_profiles=list(paginated_youtube)
#                 filtered_querysets_youtube=youtube_video_serializer(filtered_querysets_youtube,many=True).data
#         if news_search_enable==True:
#             if len(web_search)>=1:
#                 q_object = Q()
#                 for keyword_val in web_search:
#                     q_object |= Q(description__icontains=keyword_val) | Q(title__icontains=keyword_val)
#                 news = web.objects.filter(q_object)
#                 news=news.filter(view=True)
#                 date_conditions=Q()
#                 print(news.count())
#                 if start_date:
#                     date_conditions &= Q(news_creation_date__gte=start_date)

#                 if end_date:
#                     date_conditions &= Q(news_creation_date__lte=end_date)
#                 web_condition = Q(title__icontains=keyword_search) | Q(description__icontains=keyword_search)
#                 combined_condition_web = web_condition & date_conditions
#                 filtered_querysets_web = news.filter(combined_condition_web)
#                 filtered_querysets_web=web_serializer(filtered_querysets_web,many=True).data
#         if facebook_search_enable==True:
#             if len(facebook_search)>=1:
#                 q_object=Q()
#                 for keyword_val in facebook_search:
#                     q_object |= Q(post__icontains=keyword_val) | Q(keyword__icontains=keyword_val)
#                 facebook_queryset=facebook_post.objects.filter(q_object).filter(Q(post__icontains=keyword_search))
#                 facebook_queryset=facebook_queryset.filter(view=True)
#                 print("facebook_queryset",facebook_queryset.count())
#                 facebook_queryset = facebook_queryset.filter(Q(post__icontains=keyword_search))
#                 print("facebook_queryset",facebook_queryset.count())
                
#                 if start_date:
#                     facebook_queryset = facebook_queryset.filter(last_scraped__gte=start_date)
#                     print("checkpoint",facebook_queryset.count())

#                 if end_date:
#                     facebook_queryset = facebook_queryset.filter(last_scraped__lte=end_date)
                
#                 print("facebook_queryset",facebook_queryset.count())
                
                
                
#                 facebook_posts=facebook_post_serializer(facebook_queryset,many=True).data
#         return Response({'tweets':filtered_querysets_twitter,
#                          'youtube':filtered_querysets_youtube,
#                          "web":filtered_querysets_web,"facebook":facebook_posts,"status":status.HTTP_200_OK})
#     except Exception as e:
#         return Response({"message":f"Exception is {e}","status":status.HTTP_500_INTERNAL_SERVER_ERROR})
#         # twitter_search=list(set(twitter_search))
    
    

# @csrf_exempt
# @api_view(['POST'])
# def search_on_profiles(request):

@csrf_exempt
@api_view(['POST'])
def search_on_keyword(request):
    try:
        data=json.loads(request.body.decode("utf-8"))
        keywords=data.get('keywords',None)
        if keywords is None or keywords=='':
            return Response({"message":"Please provide keyword","status":status.HTTP_400_BAD_REQUEST})
        # Search from web
        news = web.objects.filter(
            Q(title__icontains=keywords) |
            Q(description__icontains=keywords)
        )

        news_serializer = web_serializer(news, many=True)

        serialized_news = news_serializer.data
        
        
        serialized_tweets=list(get_tweets_with_profiles_using_keywords([keywords]))#get_tweets_with_profiles_using_keywords(keywords)#tweets_serializer.data
        
        # Search Youtube
        youtube=youtube_video.objects.filter(
            Q(keyword__icontains=keywords) |
            Q(title__icontains=keywords)
        )
        youtube_serializer=youtube_video_serializer(youtube,many=True)
        serialized_youtube_videos=youtube_serializer.data

        return Response({'news': serialized_news,'tweets':serialized_tweets,'youtube':serialized_youtube_videos})
    except Exception as e:
        return Response({"message":f"Exception is {e}","status":status.HTTP_500_INTERNAL_SERVER_ERROR})


        

@csrf_exempt
@api_view(['GET','POST'])
def mentions_count(request):
    if request.method=="GET":
        try:
            all_profiles = list(profiles.objects.values_list('profile', flat=True))
            all_sources = list(profiles.objects.values_list('source', flat=True))
            all_checked=list(profiles.objects.values_list('checked', flat=True))
            twitter_search=[]
            youtube_profiles=[]
            twitter_search=[]
            facebook_search=[]
            for index in range(len(all_profiles)):
                if all_checked[index]==True:
                    if all_sources[index]=='twitter' or all_sources[index]=='Twitter':
                        twitter_search.append(all_profiles[index])
                    elif all_sources[index]=='youtube' or all_sources[index]=='Youtube':
                        youtube_profiles.append(all_profiles[index])
                    elif all_sources[index]=='facebook' or all_sources[index]=='Facebook':
                        facebook_search.append(all_profiles[index])
            result_queryset_twitter = scraped_tweets.objects.none()
            result_queryset_youtube = youtube_video.objects.none()
            facebook_queryset=facebook_post.objects.none()
            for profile in twitter_search:
                tweets = get_tweets_with_profile_screenname(profile)
                print(profile,tweets.count())
                if result_queryset_twitter is None:
                    result_queryset_twitter = tweets
                else:
                    result_queryset_twitter |= tweets
            if result_queryset_twitter.count()>0:
                result_queryset_twitter=result_queryset_twitter.filter(view=True)
                result_twitter=result_queryset_twitter.annotate(date=TruncDate('created_at_time')).values('date').annotate(total_posts=Count('Tid')).order_by('date')
            else:
                result_twitter=scraped_tweets.objects.none()
            for profile in youtube_profiles:
                videos=get_videos_with_profiles(profile)
                print(type(videos))
                try:
                    print(profile,videos.count())
                    if result_queryset_youtube is None:
                        result_queryset_youtube = videos
                    else:
                        result_queryset_youtube |= videos
                except:
                    pass
            if result_queryset_youtube.count()>0:
                result_queryset_youtube=result_queryset_youtube.filter(view=True)
                result_youtube=result_queryset_youtube.annotate(date=TruncDate('upload_date')).values('date').annotate(total_posts=Count('id')).order_by('date')
            else:
                result_youtube=youtube_video.objects.none()
            if len(facebook_search)>0:
                q_object=Q()
                for facebook_profile in facebook_search:  
                    q_object |= Q(account__icontains=facebook_profile)
                facebook_queryset=facebook_post.objects.filter(q_object)
                print("facebook_queryset",facebook_queryset.count())
            if facebook_queryset.count()>0:
                print("checkpoint111")
                facebook_queryset=facebook_queryset.filter(view=True)
                result_facebook=facebook_queryset.annotate(date=TruncDate('last_scraped')).values('date').annotate(total_posts=Count('id')).order_by('date')
                for post in result_facebook:
                    print(post)
            else:
                result_facebook=facebook_post.objects.none()
            
            print("result_twitter",result_twitter.count(),"result_youtube",result_youtube.count(),"result_facebook",result_facebook.count())
            print(result_twitter,result_youtube,result_facebook)
            all_querysets=None
            result_list=[]
            if result_twitter.count()>0 and all_querysets is None:
                all_querysets=result_twitter
                
            elif result_facebook.count()>0:
                if all_querysets is None:
                    all_querysets=result_facebook
                else:
                    all_querysets=all_querysets.union(result_facebook)
            elif result_youtube.count()>0:
                if all_querysets is None:
                    all_querysets=result_youtube 
                else:
                    all_querysets=all_querysets.union(result_youtube)
            if all_querysets is not None:
                print("Youtube",result_youtube.count(),"Twitter",result_twitter.count(),"Facebook",result_facebook.count(),"total",all_querysets.count())
                # Group by date and sum the total_posts
                grouped_data = {key: sum(item['total_posts'] for item in group) for key, group in groupby(sorted(all_querysets, key=itemgetter('date')), key=itemgetter('date'))}

                # Convert the grouped_data into a list of dictionaries
                result_list = [{"date": key, "total_posts": value} for key, value in grouped_data.items()]

                # Sort the result_list by date
                result_list.sort(key=lambda x: x["date"])
            return Response({'mentions':result_list})
        except Exception as e:
            return Response({"message":f"Exception is {e}",'status':status.HTTP_500_INTERNAL_SERVER_ERROR})
    elif request.method=="POST":
        # try:
            data=json.loads(request.body.decode("utf-8"))
            print(data)
            try:
                start_date = datetime.datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
                print("start_date", start_date)
                print(type(start_date))
            except Exception as e:
                start_date = None
                print("Error parsing start_date:", e)

            try:
                end_date = datetime.datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
                print("end_date", end_date)
                print(type(end_date))
            except Exception as e:
                end_date = None
                print("Error parsing end_date:", e)

            print("start_date", start_date, "end_date", end_date)
            
            keyword_search=data.get('keyword',None)
            if keyword_search=='' or keyword_search==None:
                return Response({"message":"Please Enter Any Keyword",'status':status.HTTP_400_BAD_REQUEST})
            
            all_profiles = list(profiles.objects.values_list('profile', flat=True))
            all_sources = list(profiles.objects.values_list('source', flat=True))
            all_checked=list(profiles.objects.values_list('checked', flat=True))
            
            # all_checked=list(profiles.objects.values_list('checked', flat=True))
            twitter_search=[]
            youtube_profiles=[]
            twitter_search=[]
            facebook_search=[]
            # youtube_keywords=[]
            for index in range(len(all_profiles)):
                if all_checked[index]==True:
                    if all_sources[index]=='twitter' or all_sources[index]=='Twitter':
                        twitter_search.append(all_profiles[index])
                    elif all_sources[index]=='youtube' or all_sources[index]=='Youtube':
                        youtube_profiles.append(all_profiles[index])
                    elif all_sources[index]=='facebook' or all_sources[index]=='Facebook':
                        facebook_search.append(all_profiles[index])
            # print("twitter searches available are: ",twitter_search)
            result_queryset_twitter = None
            result_queryset_youtube = None
            facebook_queryset=None
            result_twitter=scraped_tweets.objects.none()
            result_youtube=youtube_video.objects.none()
            result_facebook=facebook_post.objects.none()
            print("Twitter search",twitter_search)
            for profile in twitter_search:
                tweets = get_tweets_with_profile_screenname(profile)
                
                # Check if tweets queryset is not empty
                print(profile,tweets.count())
                if result_queryset_twitter is None:
                    result_queryset_twitter = tweets
                else:
                    result_queryset_twitter |= tweets
            if result_queryset_twitter is not None:
                result_queryset_twitter=result_queryset_twitter.filter(view=True)
                twitter_condition = Q(keyword__icontains=keyword_search) | Q(description__icontains=keyword_search)
                date_conditions = Q()
                if start_date and end_date:
                    date_conditions &= Q(created_at_time__range=[start_date, end_date])
                elif start_date:
                    date_conditions &= Q(created_at_time__gte=start_date)
                elif end_date:
                    date_conditions &= Q(created_at_time__lte=end_date)

                filtered_querysets_twitter = result_queryset_twitter.filter(twitter_condition).filter(date_conditions)
                result_twitter=filtered_querysets_twitter.annotate(date=TruncDate('created_at_time')).values('date').annotate(total_posts=Count('Tid')).order_by('date')
                
            for profile in youtube_profiles:
                videos=get_videos_with_profiles(profile)
                print(type(videos))
                try:
                    print(profile,videos.count())
                    if result_queryset_youtube is None:
                        result_queryset_youtube = videos
                    else:
                        result_queryset_youtube |= videos
                except:
                    pass
            if result_queryset_youtube is not None:
                result_queryset_youtube=result_queryset_youtube.filter(view=True)
                youtube_condition = Q(title__icontains=keyword_search) | Q(keyword__icontains=keyword_search)
                date_conditions = Q()
                if start_date and end_date:
                    date_conditions &= Q(upload_date__range=[start_date, end_date])
                elif start_date:
                    date_conditions &= Q(upload_date__gte=start_date)
                elif end_date:
                    date_conditions &= Q(upload_date__lte=end_date)
                filtered_querysets_youtube = result_queryset_youtube.filter(youtube_condition).filter(date_conditions)
                result_youtube=filtered_querysets_youtube.annotate(date=TruncDate('upload_date')).values('date').annotate(total_posts=Count('id')).order_by('date')
            if len(facebook_search)>0:
                q_object=Q()
                for facebook_profile in facebook_search:  
                    q_object |= Q(account__icontains=facebook_profile)
                facebook_queryset=facebook_post.objects.filter(q_object)
            if facebook_queryset is not None:
                facebook_queryset=facebook_queryset.filter(view=True)
                facebook_queryset=facebook_queryset.filter(Q(post__icontains=keyword_search))
                print("facebook_queryset",facebook_queryset.count())
                
                if start_date:
                    facebook_queryset = facebook_queryset.filter(last_scraped__gte=start_date)
                    print("checkpoint",facebook_queryset.count())
                if end_date:
                    facebook_queryset = facebook_queryset.filter(last_scraped__lte=end_date)
                    print("checkpoint",facebook_queryset.count())

                result_facebook=facebook_queryset.annotate(date=TruncDate('last_scraped')).values('date').annotate(total_posts=Count('id')).order_by('date')
            result_list=[]
            # try:
            print(result_twitter,result_youtube,result_facebook)
            all_querysets=None
            if result_twitter.count()>0 and all_querysets is None:
                all_querysets=result_twitter
                
            elif result_facebook.count()>0:
                if all_querysets is None:
                    all_querysets=result_facebook
                else:
                    all_querysets=all_querysets.union(result_facebook)
            elif result_youtube.count()>0:
                if all_querysets is None:
                    all_querysets=result_youtube 
                else:
                    all_querysets=all_querysets.union(result_youtube)
                
                
            # all_querysets = result_twitter.union(result_youtube,result_facebook)
            print("checkpoint3: ",all_querysets)
            # except:
            #     all_querysets=None
            if all_querysets is not None:
                # print("Youtube",result_youtube.count(),"Twitter",result_twitter.count(),"facebook",result_facebook.count(),"total",result_youtube.count())
                # if result_youtube.count()>0:
                grouped_data = {key: sum(item['total_posts'] for item in group) for key, group in groupby(sorted(all_querysets, key=itemgetter('date')), key=itemgetter('date'))}
                result_list = [{"date": key, "total_posts": value} for key, value in grouped_data.items()]
                result_list.sort(key=lambda x: x["date"])
            return Response({'mentions':result_list})
        # except Exception as e:
        #     return Response({"message":"Internal Server Error",'status':status.HTTP_500_INTERNAL_SERVER_ERROR})

####################### Graphs for mentions #######################
@csrf_exempt
@api_view(['GET','POST'])
def platform_mentions_profile(request):
    if request.method=="GET":
        try:
            all_profiles = list(profiles.objects.values_list('profile', flat=True))
            all_sources = list(profiles.objects.values_list('source', flat=True))
            all_checked=list(profiles.objects.values_list('checked', flat=True))
            
            # all_checked=list(profiles.objects.values_list('checked', flat=True))
            twitter_search=[]
            youtube_profiles=[]
            facebook_profiles=[]
            twitter_search=[]
            youtube_count=0
            tweets_count=0
            facebook_count=0
            # youtube_keywords=[]
            for index in range(len(all_profiles)):
                if all_checked[index]==True:
                    if all_sources[index]=='twitter' or all_sources[index]=='Twitter':
                        twitter_search.append(all_profiles[index])
                    elif all_sources[index]=='youtube' or all_sources[index]=='Youtube':
                        youtube_profiles.append(all_profiles[index])
                    elif all_sources[index]=='facebook' or all_sources[index]=='Facebook':
                        facebook_profiles.append(all_profiles[index])
            print("twitter searches available are: ",twitter_search)
            result_queryset_twitter = None
            result_queryset_youtube = None
            facebook_queryset=None
            for profile in twitter_search:
                tweets = get_tweets_with_profile_screenname(profile)
                
                # Check if tweets queryset is not empty
                print(profile,tweets.count())
                if result_queryset_twitter is None:
                    result_queryset_twitter = tweets
                else:
                    result_queryset_twitter |= tweets
            if result_queryset_twitter is not None:
                result_queryset_twitter=result_queryset_twitter.filter(view=True)
            for profile in youtube_profiles:
                videos=get_videos_with_profiles(profile)
                print(type(videos))
                try:
                    print(profile,videos.count())
                    if result_queryset_youtube is None:
                        result_queryset_youtube = videos
                    else:
                        result_queryset_youtube |= videos
                except:
                    pass
            if result_queryset_youtube is not None:
                result_queryset_youtube=result_queryset_youtube.filter(view=True)
            # for profile in facebook_profiles:
            q_object=Q()
            if len(facebook_profiles)>0:
                for facebook_profile in facebook_profiles:  
                    q_object |= Q(account__icontains=facebook_profile)
                facebook_queryset=facebook_post.objects.filter(q_object)
            if facebook_queryset is not None:
                facebook_queryset=facebook_queryset.filter(view=True)
                facebook_count=facebook_queryset.count()
            if result_queryset_twitter is not None:
                tweets_count=result_queryset_twitter.count()
            if result_queryset_youtube is not None:
                youtube_count=result_queryset_youtube.count()
            return Response({'tweets':tweets_count,'youtube':youtube_count,'facebook':facebook_count})
        except Exception as e:
            return Response({"message":"Internal Server Error",'status':status.HTTP_500_INTERNAL_SERVER_ERROR})
    elif request.method=="POST":
        try:
            tweets_count=0
            youtube_count=0
            facebook_count=0
            data=json.loads(request.body.decode("utf-8"))
            print(data)
            try:
                start_date = datetime.datetime.strptime(data.get('start_date'), '%Y-%m-%d').date() #data.get('start_date')
                print(type(start_date))
            except:
                start_date = None
            try:
                end_date = datetime.datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()#data.get('end_date')
                print(type(end_date))
            except:
                end_date = None
            
            keyword_search=data.get('keyword',None)
            if keyword_search=='' or keyword_search==None:
                return Response({"message":"Please Enter Any Keyword",'status':status.HTTP_400_BAD_REQUEST})
            
            
            all_profiles = list(profiles.objects.values_list('profile', flat=True))
            all_sources = list(profiles.objects.values_list('source', flat=True))
            all_checked=list(profiles.objects.values_list('checked', flat=True))
            facebook_profiles=[]
            # all_checked=list(profiles.objects.values_list('checked', flat=True))
            twitter_search=[]
            youtube_profiles=[]
            twitter_search=[]
            
            # youtube_keywords=[]
            for index in range(len(all_profiles)):
                if all_checked[index]==True:
                    if all_sources[index]=='twitter' or all_sources[index]=='Twitter':
                        twitter_search.append(all_profiles[index])
                    elif all_sources[index]=='youtube' or all_sources[index]=='Youtube':
                        youtube_profiles.append(all_profiles[index])
                    elif all_sources[index]=='facebook' or all_sources[index]=='Facebook':
                        facebook_profiles.append(all_profiles[index])
            # print("twitter searches available are: ",twitter_search)
            result_queryset_twitter = None
            result_queryset_youtube = None
            facebook_queryset=None
            for profile in twitter_search:
                tweets = get_tweets_with_profile_screenname(profile)
                
                # Check if tweets queryset is not empty
                print(profile,tweets.count())
                if result_queryset_twitter is None:
                    result_queryset_twitter = tweets
                else:
                    result_queryset_twitter |= tweets

                # tweets_with_user=get_tweets_with_profile_screenname(profile="iihtishamm")
                # print(type(tweets_with_user))

            if result_queryset_twitter is not None:
                result_queryset_twitter=result_queryset_twitter.filter(view=True)
                twitter_condition = Q(keyword__icontains=keyword_search) | Q(description__icontains=keyword_search)

                date_conditions = Q()
                if start_date:
                    date_conditions |= Q(created_at_time__gte=start_date)

                if end_date:
                    date_conditions |= Q(created_at_time__lte=end_date)

                combined_condition_twitter = twitter_condition & date_conditions
                print(combined_condition_twitter)

                filtered_querysets_twitter = result_queryset_twitter.filter(combined_condition_twitter)
                if filtered_querysets_twitter is not None:
                    tweets_count=filtered_querysets_twitter.count()
            for profile in youtube_profiles:
                videos=get_videos_with_profiles(profile)
                print(type(videos))
                try:
                    print(profile,videos.count())
                    if result_queryset_youtube is None:
                        result_queryset_youtube = videos
                    else:
                        result_queryset_youtube |= videos
                except:
                    pass
            if result_queryset_youtube is not None:
                result_queryset_youtube=result_queryset_youtube.filter(view=True)
                date_conditions = Q()
                if start_date:
                    date_conditions &= Q(upload_date__gte=start_date)

                if end_date:
                    date_conditions &= Q(upload_date__lte=end_date)
                youtube_condition = Q(title__icontains=keyword_search) | Q(keyword__icontains=keyword_search)
                combined_condition_youtube = youtube_condition & date_conditions
                filtered_querysets_youtube = result_queryset_youtube.filter(combined_condition_youtube)
                if filtered_querysets_youtube is not None:
                    youtube_count=filtered_querysets_youtube.count()  
            q_object=Q()
            print("facebook_profiles: ",facebook_profiles)
            if len(facebook_profiles)>0:
                for facebook_profile in facebook_profiles:  
                    q_object |= Q(account__icontains=facebook_profile)
                facebook_queryset=facebook_post.objects.filter(q_object)
            if facebook_queryset is not None:
                facebook_queryset=facebook_queryset.filter(view=True)
                print("facebook_queryset",facebook_queryset.count())
                
                facebook_queryset = facebook_queryset.filter(Q(post__icontains=keyword_search))
                print("facebook_queryset",facebook_queryset.count())
                date_conditions = Q()
                if start_date:
                    date_conditions |= Q(last_scraped__gte=start_date)

                if end_date:
                    date_conditions |= Q(last_scraped__lte=end_date)
                facebook_queryset=facebook_queryset.filter(date_conditions)
                for face in facebook_queryset:
                    print("--------",face)
                facebook_count=facebook_queryset.count()
            ######################### Facebook #########################
            
            return Response({'tweets':tweets_count,'youtube':youtube_count,'facebook':facebook_count})
        except Exception as e:
            return Response({"message":"Internal Server Error {e}",'status':status.HTTP_500_INTERNAL_SERVER_ERROR})

@csrf_exempt
@api_view(['GET','POST'])
def social_reach_profile(request):
    if request.method=="GET":
        try:
            all_profiles = list(profiles.objects.values_list('profile', flat=True))
            all_sources = list(profiles.objects.values_list('source', flat=True))
            all_checked=list(profiles.objects.values_list('checked', flat=True))
            
            # all_checked=list(profiles.objects.values_list('checked', flat=True))
            twitter_search=[]
            youtube_profiles=[]
            twitter_search=[]
            youtube_views=0
            tweets_views=0
            favourite_count=0
            retweet_count=0
            Views=0
            Engagement=0
            
            # youtube_keywords=[]
            for index in range(len(all_profiles)):
                if all_checked[index]==True:
                    if all_sources[index]=='twitter' or all_sources[index]=='Twitter':
                        twitter_search.append(all_profiles[index])
                    elif all_sources[index]=='youtube' or all_sources[index]=='Youtube':
                        youtube_profiles.append(all_profiles[index])
            print("twitter searches available are: ",twitter_search)
            result_queryset_twitter = None
            result_queryset_youtube = None
            # facebook_queryset=None
            for profile in twitter_search:
                tweets = get_tweets_with_profile_screenname(profile)
                
                # Check if tweets queryset is not empty
                print(profile,tweets.count())
                if result_queryset_twitter is None:
                    result_queryset_twitter = tweets
                else:
                    result_queryset_twitter |= tweets
            if result_queryset_twitter is not None:
                result_queryset_twitter=result_queryset_twitter.filter(view=True)
                for tw in result_queryset_twitter:
                    
                    try:
                        # print("tw['favorite_count'],tw['retweet_count']",type(tw['favorite_count']),type(tw['retweet_count']))
                        if tw['favorite_count'] is not None:
                            favourite_count += tw['favorite_count']
                        if tw['retweet_count'] is not None:
                            retweet_count += tw['retweet_count']
                        views_count_lower = tw['views'].lower()
                        print("views_count_lower",views_count_lower)

                        if 'k' in views_count_lower:
                            tweets_views += float(views_count_lower.split('k')[0]) * 1000
                        elif 'm' in views_count_lower:
                            tweets_views += float(views_count_lower.split('m')[0]) * 1000000
                        else:
                            tweets_views += float(views_count_lower)
                        print("tweets_views",tweets_views)
                    except:
                        pass
            for profile in youtube_profiles:
                videos=get_videos_with_profiles(profile)
                print(type(videos))
                try:
                    print(profile,videos.count())
                    if result_queryset_youtube is None:
                        result_queryset_youtube = videos
                    else:
                        result_queryset_youtube |= videos
                except:
                    pass
            if result_queryset_youtube is not None:
                result_queryset_twitter=result_queryset_youtube.filter(view=True)
            
                for yt in result_queryset_youtube:
                    if yt['views_count'] is not None:
                        if 'k' in yt['views_count'].lower():
                            youtube_views += float(yt['views_count'].lower().split('k')[0]) * 1000
                        elif 'm' in yt['views_count'].lower():
                            youtube_views += float(yt['views_count'].lower().split('m')[0]) * 1000000
                        elif yt['views_count'].isdigit():
                            youtube_views += float(yt['views_count'])
            
            Views=int(tweets_views)+int(youtube_views)
            Engagement=favourite_count+retweet_count
            return Response({'views':Views,'Engagement':Engagement})
        except Exception as e:
            return Response({"message":"Internal Server Error {e}",'status':status.HTTP_500_INTERNAL_SERVER_ERROR})
    elif request.method=="POST":
        try:
            data=json.loads(request.body.decode("utf-8"))
            tweets=0
            try:
                start_date = datetime.datetime.strptime(data.get('start_date'), '%Y-%m-%d').date() #data.get('start_date')
                print(type(start_date))
            except:
                start_date = None
            try:
                end_date = datetime.datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()#data.get('end_date')
                print(type(end_date))
            except:
                end_date = None
            
            keyword_search=data.get('keyword',None)
            if keyword_search=='' or keyword_search==None:
                return Response({"message":"Please Enter Any Keyword",'status':status.HTTP_400_BAD_REQUEST})
            
            all_profiles = list(profiles.objects.values_list('profile', flat=True))
            all_sources = list(profiles.objects.values_list('source', flat=True))
            all_checked=list(profiles.objects.values_list('checked', flat=True))
            
            # all_checked=list(profiles.objects.values_list('checked', flat=True))
            twitter_search=[]
            youtube_profiles=[]
            twitter_search=[]
            youtube_views=0
            tweets_views=0
            favourite_count=0
            retweet_count=0
            Views=0
            Engagement=0
            
            # youtube_keywords=[]
            for index in range(len(all_profiles)):
                if all_checked[index]==True:
                    if all_sources[index]=='twitter' or all_sources[index]=='Twitter':
                        twitter_search.append(all_profiles[index])
                    elif all_sources[index]=='youtube' or all_sources[index]=='Youtube':
                        youtube_profiles.append(all_profiles[index])
            print("twitter searches available are: ",twitter_search)
            result_queryset_twitter = None
            result_queryset_youtube = None
            for profile in twitter_search:
                tweets = get_tweets_with_profile_screenname(profile)
                
                # Check if tweets queryset is not empty
                print(profile,tweets.count())
                if result_queryset_twitter is None:
                    result_queryset_twitter = tweets
                else:
                    result_queryset_twitter |= tweets
            if result_queryset_twitter is not None:
                result_queryset_twitter=result_queryset_twitter.filter(view=True)
            print("Checkpoint 1")
            for profile in youtube_profiles:
                videos=get_videos_with_profiles(profile)
                print(type(videos))
                try:
                    print(profile,videos.count())
                    if result_queryset_youtube is None:
                        result_queryset_youtube = videos
                    else:
                        result_queryset_youtube |= videos
                except:
                    pass
            print("Checkpoint 2")
            
              
            print("result_queryset_youtube",result_queryset_youtube)
            print("result_queryset_twitter",result_queryset_twitter)
            if result_queryset_twitter is not None:
                twitter_condition = Q(keyword__icontains=keyword_search) | Q(description__icontains=keyword_search)
                # if result_queryset_twitter is not None:
                date_conditions = Q()
                if start_date:
                    date_conditions &= Q(created_at_time__gte=start_date)

                if end_date:
                    date_conditions &= Q(created_at_time__lte=end_date)

                combined_condition_twitter = twitter_condition & date_conditions

                filtered_querysets_twitter = result_queryset_twitter.filter(combined_condition_twitter)
                for tw in filtered_querysets_twitter:
                    try:
                        
                        if tw['favorite_count'] is not None:
                            favourite_count += tw['favorite_count']
                        if tw['retweet_count'] is not None:
                            retweet_count += tw['retweet_count']
                        views_count_lower = tw['views'].lower()

                        if 'k' in views_count_lower:
                            tweets_views += float(views_count_lower.split('k')[0]) * 1000
                        elif 'm' in views_count_lower:
                            tweets_views += float(views_count_lower.split('m')[0]) * 1000000
                        else:
                            tweets_views += float(views_count_lower)
                    except:
                        pass
            ######################### Twitter #########################
            ######################### Youtube #########################
            if result_queryset_youtube is not None:
                result_queryset_youtube=result_queryset_youtube.filter(view=True) 
                date_conditions = Q()
                if start_date:
                    date_conditions &= Q(upload_date__gte=start_date)

                if end_date:
                    date_conditions &= Q(upload_date__lte=end_date)
                youtube_condition = Q(title__icontains=keyword_search) | Q(keyword__icontains=keyword_search)
                combined_condition_youtube = youtube_condition & date_conditions
                filtered_querysets_youtube = result_queryset_youtube.filter(combined_condition_youtube)
            
            
                for yt in filtered_querysets_youtube:
                    if yt['views_count'] is not None:
                        if 'k' in yt['views_count'].lower():
                            youtube_views += float(yt['views_count'].lower().split('k')[0]) * 1000
                        elif 'm' in yt['views_count'].lower():
                            youtube_views += float(yt['views_count'].lower().split('m')[0]) * 1000000
                        elif yt['views_count'].isdigit():
                            youtube_views += float(yt['views_count'])
            
            Views=int(tweets_views)+int(youtube_views)
            Engagement=favourite_count+retweet_count
            return Response({'views':Views,'Engagement':Engagement})
        except Exception as e:
            return Response({"message":f"Internal Server Error {e}","status":status.HTTP_500_INTERNAL_SERVER_ERROR})

        
@permission_classes([AllowAny])
class ProfilesView(APIView):
    def get(self, request):
        try:
            profile = profiles.objects.all().order_by('-id')
            for profile_obj in profile:
                if profile_obj.source=='Youtube' or profile_obj.source=='youtube':
                    try:
                        profile_obj.counts=get_videos_profile_count(profile_obj.profile)
                        profile_obj.save()
                    except:
                        pass
                elif profile_obj.source=='Twitter' or profile_obj.source=='twitter':
                    try:
                        profile_obj.counts=get_tweets_with_profile_screenname(profile_obj.profile).count()
                        profile_obj.save()
                    except:
                        pass
                elif profile_obj.source=='Facebook' or profile_obj.source=='facebook':
                    try:
                        profile_obj.counts=facebook_post.objects.filter(account=profile_obj.profile).count()
                        profile_obj.save()
                    except:
                        pass
                elif profile_obj.source=='Web' or profile_obj.source=='web':
                    try:
                        profile_obj.counts=web.objects.filter(platform=profile_obj.profile).count()
                        profile_obj.save()
                    except:
                        pass
            profile_serializer = profiles_serializer(profile, many=True)
            serialized_profile = profile_serializer.data
            return Response({'profiles': serialized_profile},status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"Internal Server Error {e}"},status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            print("----------",data)
            selected = data.get('selected')
            profile_id = data.get("id",None)
            if profile_id==None or profile_id=='':
                return Response({'message':"profile id can not be empty"},status.HTTP_400_BAD_REQUEST)
            updated = profiles.objects.get(id=profile_id)
            if updated is None:
                return Response({'message':"profile not found"},status.HTTP_400_BAD_REQUEST)
            if updated.checked:
                updated.checked = False
            else:
                updated.checked = True
            updated.save()
            profile = profiles.objects.all().order_by('-id')
            profile_serializer = profiles_serializer(profile, many=True)
            serialized_profile = profile_serializer.data
            return Response({'profiles': serialized_profile},status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"Internal Server Error {e}"},status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            selected = True
            print(data)
            profile = data.get('profile',None)
            src=profile
            if profile is None or profile == '':
                return Response({'message':"profile can not be empty"},status.HTTP_400_BAD_REQUEST)
            print(profile)
            if profile.endswith('/'):
                profile = profile[:-1]
            
            print(profile)
            if 'twitter' in profile:
                profile=profile.rsplit("/", 1)[-1]
                source="twitter"
            elif 'youtube' in profile:
                profile=profile.split('@')[1]
                source="youtube"
            elif 'facebook' in profile or 'fb' in profile:
                profile=profile.rsplit("/", 1)[-1]
                source="facebook"
            else:
                try:
                    profile=tldextract.extract(profile).domain
                    if profile=='dawn' or profile=='dunyanews' or profile=='arynews' or profile=='bolnews' or profile=='dailypakistan' or profile=='express' or profile=='geo':
                        source="web"
                    else:
                        return Response({'message':"This web profile not available"},status.HTTP_406_NOT_ACCEPTABLE)
                except:
                    return Response({'message':"Source can be only Twitter, Youtube or Facebook"},status.HTTP_400_BAD_REQUEST)
            
            # source = data.get('source')
            exists = profiles.objects.filter(profile=profile, source=source).count()
            print(exists)
            if exists == 0:
                profile_obj = profiles(profile=profile, source=source, checked=selected,counts=0,profile_link=src)
                profile_obj.save()
            else:
                return Response({'message':"profile already exists"},status.HTTP_400_BAD_REQUEST)
            print("checkpoint1111111111111111")
            if source=="twitter" or source=="facebook" or source=="youtube":
                background_thread = threading.Thread(target=profile_scrap, args=(profile,source))
                background_thread.start()
            profiles_all = profiles.objects.all().order_by('-id')
            print(profiles_all)
            profile_serializer = profiles_serializer(profiles_all, many=True)
            serialized_profile = profile_serializer.data
            return Response({'profiles': serialized_profile},status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"Internal Server Error {e}"},status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            profile_id = data.get('id',None)
            if profile_id=='' or profile_id==None:
                return Response({'message':"profile id can not be empty"},status.HTTP_400_BAD_REQUEST)
            obj = profiles.objects.get(id=profile_id)
            if obj is None:
                return Response({'message':"profile not found"},status.HTTP_400_BAD_REQUEST)
            obj.delete()
            profile = profiles.objects.all().order_by('-id')
            profile_serializer = profiles_serializer(profile, many=True)
            serialized_profile = profile_serializer.data
            return Response({'profiles': serialized_profile},status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"Internal Server Error {e}"},status.HTTP_500_INTERNAL_SERVER_ERROR)




@csrf_exempt
@api_view(['POST'])
def update_youtube_video(request):
    try:
        data=json.load(request.body.decode("utf-8"))
        id=data.get("id",None)
        if id==None:
            return Response({'message':"youtube video id can not be empty"},status.HTTP_400_BAD_REQUEST)
        obj = youtube_video.objects.get(id=id)
        if obj is None:
            return Response({'message':"youtube video not found"},status.HTTP_400_BAD_REQUEST)
        if obj.views==True:
            obj.views=False
        else:
            obj.views=True
        obj.save()
        return Response({'message':"youtube video updated successfully"},status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"message": f"Internal Server Error {e}"},status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
def update_tweet(request):
    try:
        data=json.load(request.body.decode('utf-8'))
        description=data.get("description",None)
        if description==None:
            return Response({'message':"tweet id can not be empty"},status.HTTP_400_BAD_REQUEST)
        obj=scraped_tweets.objects.get(description=description)
        if obj is None:
            return Response({'message':"tweet not found"},status.HTTP_400_BAD_REQUEST)
        if obj.views==True:
            obj.views=False
        else:
            obj.views=True
        obj.save()
        return Response({'message':"tweet updated successfully"},status.HTTP_200_OK)
    except Exception as e:
        return Response({"message":f"Internal Server Error {e}"},status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@csrf_exempt
@api_view(['POST'])
def update_facebook_post(request):
    try:
        data=json.load(request.body.decode("utf-8"))
        id=data.get('id',None)
        if id==None:
            return Response({'message':"facebook id can not be empty"},status.HTTP_400_BAD_REQUEST)
        obj=facebook_post.objects.get(id=id)
        if obj is None:
            return Response({"message":"facebook post not found"},status.HTTP_204_NO_CONTENT)
        else:
            if obj.views==True:
                obj.views=False
            else:
                obj.views=True
            obj.save()
            return Response({"message":"facebook post updated successfully"},status.HTTP_200_OK)
    except Exception as e:
        return Response({"message":f"Internal Server Error {e}"},status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
def update_web_post(request):
    try:
        data=json.load(request.body.decode("utf-8"))
        id=data.get('id',None)
        if id==None:
            return Response({"message":"web id can not be empty"},status.HTTP_400_BAD_REQUEST)
        obj=web.objects.get(id=id)
        if obj is None:
            return Response({"message":"web post not found"},status.HTTP_204_NO_CONTENT)
        else:
            if obj.views==True:
                obj.views=False
            else:
                obj.views=True
            obj.save()
            return Response({"message":"web post updated successfully"},status.HTTP_200_OK)
    except Exception as e:
        return Response({"message":f"Internal Server Error {e}"},status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
def reset_posts(request):
    try:
        data=json.load(request.body.decode("utf-8"))
        youtube=data.get("youtube",True)
        twitter=data.get("twitter",True)
        facebook=data.get("facebook",True)
        web_posts=data.get("web_posts",True)
        if youtube:
            youtube_video.objects.all().update(views=True)
        if twitter:
            scraped_tweets.objects.all().update(views=True)
        if facebook:
            facebook_post.objects.all().update(views=True)
        if web_posts:
            web.objects.all().update(views=True)
        return Response({"message":"posts reset successfully"},status.HTTP_200_OK)
    except Exception as e:
        return Response({"message":f"Internal Server Error {e}"},status.HTTP_500_INTERNAL_SERVER_ERROR)
        
from .tasks import *
# web_scrapers()
# ad_tracking_urdu_point()
# keyword_based_scraping()



