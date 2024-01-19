from django.db import models

# Create your models here.
class web(models.Model):
    title=models.CharField(max_length=10000)
    description=models.CharField(max_length=100000)
    link=models.CharField(max_length=10000,primary_key=True)
    image=models.CharField(max_length=10000,null=True)
    platform=models.CharField(max_length=10000)
    news_creation_date=models.DateTimeField()
    view=models.BooleanField(default=True)
    platform_type=models.CharField(default="web",max_length=500)
    def __str__(self):
        return self.title


    
    

class youtube_channel(models.Model):
    description=models.CharField(max_length=100000,null=True)
    links=models.CharField(max_length=10000,null=True)
    email=models.CharField(max_length=1000,null=True)
    url=models.CharField(max_length=2000)
    subscriber_count=models.CharField(max_length=2000,null=True)
    videos_count=models.CharField(max_length=2000,null=True)
    views=models.CharField(max_length=2000,null=True)
    join_date=models.CharField(max_length=10000,null=True)
    country=models.CharField(max_length=1000,null=True)
    channel_name=models.CharField(primary_key=True,max_length=1000)
    last_scraped_user=models.DateTimeField(null=True)
    # view=models.BooleanField(default=True)
    def __str__(self):
        return self.channel_name

class youtube_video(models.Model):
    id=models.AutoField(primary_key=True)
    title=models.CharField(max_length=10000,null=True)
    video_duration=models.CharField(max_length=1000,null=True)
    views_count=models.CharField(max_length=10000,null=True)
    link=models.CharField(max_length=10000,null=True)
    image=models.CharField(max_length=10000,null=True)
    channel_name=models.ForeignKey(youtube_channel,on_delete=models.CASCADE,null=True)
    keyword=models.CharField(max_length=10000,null=True)
    upload_date=models.DateTimeField(null=True)
    last_scraped_video=models.DateTimeField(null=True)
    view=models.BooleanField(default=True)
    platform_type=models.CharField(default="youtube",max_length=500)
    
    def __str__(self):
        return self.title  

# class extracted_tweets(models.Model):
#     Tid=models.CharField(max_length=1000,primary_key=True)
#     description=models.CharField(max_length=100000,null=True)
#     views=models.IntegerField(default=0)
#     reply_count=models.IntegerField(default=0)
#     quote_count=models.IntegerField(default=0)
#     favorite_count=models.IntegerField(default=0)
#     retweet_count=models.IntegerField(default=0)
#     bookmark_count=models.IntegerField(default=0)
#     created_at_time=models.DateTimeField(null=True)
#     image=models.CharField(max_length=10000,null=True)
#     link=models.CharField(max_length=10000,null=True)
#     Media_data=models.CharField(max_length=10000,null=True)
#     last_scraped_tweet=models.DateTimeField(null=True)
#     keyword=models.CharField(max_length=1000,null=True)
    
#     def __str__(self):
#         return self.Tid
    

# class tweet(models.Model):
#     Tid=models.CharField(max_length=1000,primary_key=True)
#     description=models.CharField(max_length=100000,null=True)
#     views=models.IntegerField(default=0)
#     reply_count=models.IntegerField(default=0)
#     quote_count=models.IntegerField(default=0)
#     favorite_count=models.IntegerField(default=0)
#     retweet_count=models.IntegerField(default=0)
#     bookmark_count=models.IntegerField(default=0)
#     created_at_time=models.DateTimeField(null=True)
#     image=models.CharField(max_length=10000,null=True)
#     link=models.CharField(max_length=10000,null=True)
#     Media_data=models.CharField(max_length=10000,null=True)
#     last_scraped_tweet=models.DateTimeField(null=True)
#     keyword=models.CharField(max_length=1000,null=True)
    
#     def __str__(self):
#         return self.Tid
    


class twitter_user(models.Model):
    id=models.CharField(max_length=10000,primary_key=True)
    is_blue_varified=models.BooleanField(default=False,null=True)
    can_dm=models.BooleanField(default=False,null=True)
    created_at=models.DateTimeField(null=True)
    default_profile=models.BooleanField(default=False,null=True)
    user_description=models.CharField(max_length=10000,null=True)
    display_url=models.CharField(max_length=10000,null=True)
    expanded_url=models.CharField(max_length=10000,null=True)
    link=models.CharField(max_length=10000,null=True)
    favourites_count=models.IntegerField(default=0,null=True)
    fast_followers_count=models.IntegerField(default=0,null=True)
    followers_count=models.IntegerField(default=0,null=True)
    friends_count=models.IntegerField(default=0,null=True)
    location=models.CharField(max_length=10000,null=True)
    media_count=models.IntegerField(default=0,null=True)
    name=models.CharField(max_length=10000,null=True)
    normal_followers_count=models.IntegerField(default=0,null=True)
    screen_name=models.CharField(max_length=10000,null=True)
    statuses_count=models.IntegerField(default=0,null=True)
    created_at_time=models.DateTimeField(null=True)
    # view=models.BooleanField(default=True)
    def __str__(self):
        return self.id
    

class scraped_tweets(models.Model):
    Tid=models.ForeignKey(twitter_user,on_delete=models.CASCADE)
    description=models.CharField(max_length=100000,primary_key=True)
    views=models.CharField(max_length=10000,null=True)
    reply_count=models.IntegerField(default=0,null=True)
    quote_count=models.IntegerField(default=0,null=True)
    favorite_count=models.IntegerField(default=0,null=True)
    retweet_count=models.IntegerField(default=0,null=True)
    bookmark_count=models.IntegerField(default=0,null=True)
    created_at_time=models.DateTimeField(null=True)
    image=models.CharField(max_length=1000,null=True)
    link=models.CharField(max_length=1000,null=True)
    Media_data=models.CharField(max_length=10000,null=True)
    last_scraped_tweet=models.DateTimeField(null=True)
    keyword=models.CharField(max_length=1000,null=True)
    view=models.BooleanField(default=True)
    platform_type=models.CharField(default="twitter",max_length=500)
    
    def __str__(self):
        return self.Tid 
    
class profiles(models.Model):
    profile=models.CharField(max_length=10000)
    profile_link=models.CharField(max_length=10000,null=True)
    source=models.CharField(max_length=10000)
    checked=models.BooleanField(default=True)
    counts=models.IntegerField(default=0)
    def __str__(self):
        return self.profile
    
    
    
# class keyword(models.Model):
#     keywords=models.CharField(max_length=10000)
#     youtube_keyword=models.BooleanField(default=False)
#     twitter_keyword=models.BooleanField(default=False)
#     facebook_keyword=models.BooleanField(default=False)
#     web_keyword=models.BooleanField(default=False)
#     checked=models.BooleanField(default=True)
#     youtube_crawl=models.BooleanField(default=False)
#     twitter_crawl=models.BooleanField(default=False)
#     facebook_crawl=models.BooleanField(default=False)
#     web_crawl=models.BooleanField(default=False)
#     counts=models.IntegerField(default=0)
#     def __str__(self):
#         return self.keywords
    
    
    
    
class facebook_post(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.CharField(max_length=10000,null=True,blank=True)
    post = models.CharField(max_length=10000,null=True,blank=True)
    reactions = models.CharField(max_length=10000,null=True,blank=True)
    shares = models.CharField(max_length=10000,null=True,blank=True)
    comments = models.CharField(max_length=10000,null=True,blank=True)
    type = models.CharField(max_length=10000,null=True,blank=True)
    upload_time = models.CharField(max_length=10000,null=True,blank=True)
    shared = models.CharField(max_length=10000,null=True,blank=True)
    thumbnail_link = models.CharField(max_length=10000,null=True,blank=True)
    image=models.BinaryField(blank=True, null=True)
    # keyword = models.CharField(max_length=10000,null=True,blank=True)
    link=models.CharField(max_length=10000,null=True,blank=True)
    last_scraped=models.DateTimeField(null=True)
    view=models.BooleanField(default=True)
    platform_type=models.CharField(default="facebook",max_length=500)

    def __str__(self):
        return self.post

class Ads_table(models.Model):
    ad_name=models.CharField(max_length=10000,primary_key=True)
    tracking=models.BooleanField(default=True)
    template_path=models.CharField(max_length=10000,null=True,blank=True)
    source=models.CharField(max_length=1000,default="urdu_point")
    start_date=models.DateField(null=True,blank=True)
    end_date=models.DateField(null=True,blank=True)
    def __str__(self):
        return self.ad_name

class web_ads(models.Model):
    timestamp = models.DateTimeField(null=True)
    top_left_coordinates = models.CharField(max_length=10000,null=True,blank=True)
    bottom_right_coordinates = models.CharField(max_length=10000,null=True,blank=True)
    position_relative_to_page = models.CharField(max_length=10000,null=True,blank=True)
    position = models.CharField(max_length=10000,null=True,blank=True)
    image = models.BinaryField(blank=True, null=True)
    ad_name = models.ForeignKey(Ads_table,on_delete=models.CASCADE,null=True,blank=True)
    def __str__(self):
        return self.ad_name    
    
    
    