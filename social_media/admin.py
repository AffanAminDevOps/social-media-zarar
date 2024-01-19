from django.contrib import admin
from . import models

admin.site.register(models.web)
admin.site.register(models.youtube_video)
admin.site.register(models.youtube_channel)
admin.site.register(models.scraped_tweets)
admin.site.register(models.twitter_user)
admin.site.register(models.profiles)
admin.site.register(models.Ads_table)
admin.site.register(models.web_ads)

admin.site.register(models.facebook_post)



# Register your models here.




