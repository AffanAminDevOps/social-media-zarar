# from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # path('search_keywords/',views.search_on_keywords,name="search_on_keywords"),#search_on_keywords search_on_keyword_profile
    # # path('tweeter_keyword/',views.tweeter_keyword,name="tweeter_keyword"),
    # path('link_based/',views.link_based,name="link_based"), #E
    # path('search_on_keyword/',views.search_on_keyword,name="search_on_keyword"),
    # path('count_records_keywords/',views.count_records_keywords,name="count_records_keywords"),
    # path('mention_count_keyword/',views.mention_count_keyword,name="mention_count_keyword"),
    path('social_reach_profile/',views.social_reach_profile,name="social_reach_profile"), #E
    path('platform_mentions_profile/',views.platform_mentions_profile,name="platform_mentions_profile"), # P
    # path('social_reach/',views.social_reach,name="social_reach"),
    # path('all_keywords/',views.all_keywords,name="all_keywords"),
    path("ProfilesView/",views.ProfilesView.as_view(),name="ProfilesView"),
    # path("KeywordView/",views.KeywordView.as_view(),name="KeywordView"),
    path("mentions_count/",views.mentions_count,name="mentions_count"), #E
    # path("platform_mentions/",views.platform_mentions,name="platform_mentions"), #E
    path("search_on_keyword_profile/",views.search_on_keyword_profile,name="search_on_keyword_profile"),
    path("update_youtube_video/",views.update_youtube_video,name="update_youtube_video"),
    path("update_tweet/",views.update_tweet,name="update_tweet"),
    path("update_facebook_post/",views.update_facebook_post,name="update_facebook_post"),
    path("update_web_post/",views.update_web_post,name="update_web_post"),
    path("reset_posts/",views.reset_posts,name="reset_posts"),
    path("ADsView/",views.ADsView.as_view(),name="ADsView"),
    path("get_profiles_data/",views.get_profiles_data,name="get_profiles_data"),
    path("get_track_ad/<str:ad>/",views.get_track_ad,name="get_track_ad"),
    path("reset_profiles/",views.reset_profiles,name="reset_profiles")

    
    
    
]