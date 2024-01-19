from rest_framework import serializers
from . import models

class web_serializer(serializers.ModelSerializer):
    class Meta:
        model=models.web
        fields='__all__'
        

class youtube_video_serializer(serializers.ModelSerializer):
    class Meta:
        model=models.youtube_video
        fields='__all__'
        
class youtube_channel_serializer(serializers.ModelSerializer):
    class Meta:
        model=models.youtube_channel
        fields='__all__'
        
class userTweets_serializer(serializers.ModelSerializer):
    class Meta:
        model=models.scraped_tweets
        fields='__all__'
   

class users_serializer(serializers.ModelSerializer):
    class Meta:
        model=models.twitter_user
        fields='__all__'
        
        
class profiles_serializer(serializers.ModelSerializer):
    class Meta:
        model=models.profiles
        fields='__all__'
        
        
# class keyword_serializer(serializers.ModelSerializer):
#     class Meta:
#         model=models.keyword
#         fields='__all__'
        
class facebook_post_serializer(serializers.ModelSerializer):
    class Meta:
        model=models.facebook_post
        fields='__all__'
        
        
class ads_serializer(serializers.ModelSerializer):
    class Meta:
        model=models.Ads_table
        fields='__all__'
        
class web_ads_serializer(serializers.ModelSerializer):
    class Meta:
        model=models.web_ads
        fields='__all__'
