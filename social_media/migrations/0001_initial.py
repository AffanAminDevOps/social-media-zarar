# Generated by Django 4.2.8 on 2024-01-04 10:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ads_table',
            fields=[
                ('ad_name', models.CharField(max_length=10000, primary_key=True, serialize=False)),
                ('tracking', models.BooleanField(default=True)),
                ('template_path', models.CharField(blank=True, max_length=10000, null=True)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='facebook_post',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('account', models.CharField(blank=True, max_length=10000, null=True)),
                ('post', models.CharField(blank=True, max_length=10000, null=True)),
                ('reactions', models.CharField(blank=True, max_length=10000, null=True)),
                ('shares', models.CharField(blank=True, max_length=10000, null=True)),
                ('comments', models.CharField(blank=True, max_length=10000, null=True)),
                ('type', models.CharField(blank=True, max_length=10000, null=True)),
                ('upload_time', models.CharField(blank=True, max_length=10000, null=True)),
                ('shared', models.CharField(blank=True, max_length=10000, null=True)),
                ('thumbnail_link', models.CharField(blank=True, max_length=10000, null=True)),
                ('image', models.BinaryField(blank=True, null=True)),
                ('link', models.CharField(blank=True, max_length=10000, null=True)),
                ('last_scraped', models.DateTimeField(null=True)),
                ('view', models.BooleanField(default=True)),
                ('platform_type', models.CharField(default='facebook', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='profiles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile', models.CharField(max_length=10000)),
                ('profile_link', models.CharField(max_length=10000, null=True)),
                ('source', models.CharField(max_length=10000)),
                ('checked', models.BooleanField(default=True)),
                ('counts', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='twitter_user',
            fields=[
                ('id', models.CharField(max_length=10000, primary_key=True, serialize=False)),
                ('is_blue_varified', models.BooleanField(default=False, null=True)),
                ('can_dm', models.BooleanField(default=False, null=True)),
                ('created_at', models.DateTimeField(null=True)),
                ('default_profile', models.BooleanField(default=False, null=True)),
                ('user_description', models.CharField(max_length=10000, null=True)),
                ('display_url', models.CharField(max_length=10000, null=True)),
                ('expanded_url', models.CharField(max_length=10000, null=True)),
                ('link', models.CharField(max_length=10000, null=True)),
                ('favourites_count', models.IntegerField(default=0, null=True)),
                ('fast_followers_count', models.IntegerField(default=0, null=True)),
                ('followers_count', models.IntegerField(default=0, null=True)),
                ('friends_count', models.IntegerField(default=0, null=True)),
                ('location', models.CharField(max_length=10000, null=True)),
                ('media_count', models.IntegerField(default=0, null=True)),
                ('name', models.CharField(max_length=10000, null=True)),
                ('normal_followers_count', models.IntegerField(default=0, null=True)),
                ('screen_name', models.CharField(max_length=10000, null=True)),
                ('statuses_count', models.IntegerField(default=0, null=True)),
                ('created_at_time', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='web',
            fields=[
                ('title', models.CharField(max_length=10000)),
                ('description', models.CharField(max_length=100000)),
                ('link', models.CharField(max_length=10000, primary_key=True, serialize=False)),
                ('image', models.CharField(max_length=10000, null=True)),
                ('platform', models.CharField(max_length=10000)),
                ('news_creation_date', models.DateTimeField()),
                ('view', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='youtube_channel',
            fields=[
                ('description', models.CharField(max_length=100000, null=True)),
                ('links', models.CharField(max_length=10000, null=True)),
                ('email', models.CharField(max_length=1000, null=True)),
                ('url', models.CharField(max_length=2000)),
                ('subscriber_count', models.CharField(max_length=2000, null=True)),
                ('videos_count', models.CharField(max_length=2000, null=True)),
                ('views', models.CharField(max_length=2000, null=True)),
                ('join_date', models.CharField(max_length=10000, null=True)),
                ('country', models.CharField(max_length=1000, null=True)),
                ('channel_name', models.CharField(max_length=1000, primary_key=True, serialize=False)),
                ('last_scraped_user', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='youtube_video',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=10000, null=True)),
                ('video_duration', models.CharField(max_length=1000, null=True)),
                ('views_count', models.CharField(max_length=10000, null=True)),
                ('link', models.CharField(max_length=10000, null=True)),
                ('image', models.CharField(max_length=10000, null=True)),
                ('keyword', models.CharField(max_length=10000, null=True)),
                ('upload_date', models.DateTimeField(null=True)),
                ('last_scraped_video', models.DateTimeField(null=True)),
                ('view', models.BooleanField(default=True)),
                ('platform_type', models.CharField(default='youtube', max_length=500)),
                ('channel_name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='social_media.youtube_channel')),
            ],
        ),
        migrations.CreateModel(
            name='web_ads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(null=True)),
                ('top_left_coordinates', models.CharField(blank=True, max_length=10000, null=True)),
                ('bottom_right_coordinates', models.CharField(blank=True, max_length=10000, null=True)),
                ('position_relative_to_page', models.CharField(blank=True, max_length=10000, null=True)),
                ('position', models.CharField(blank=True, max_length=10000, null=True)),
                ('image', models.BinaryField(blank=True, null=True)),
                ('ad_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='social_media.ads_table')),
            ],
        ),
        migrations.CreateModel(
            name='scraped_tweets',
            fields=[
                ('description', models.CharField(max_length=100000, primary_key=True, serialize=False)),
                ('views', models.CharField(max_length=10000, null=True)),
                ('reply_count', models.IntegerField(default=0, null=True)),
                ('quote_count', models.IntegerField(default=0, null=True)),
                ('favorite_count', models.IntegerField(default=0, null=True)),
                ('retweet_count', models.IntegerField(default=0, null=True)),
                ('bookmark_count', models.IntegerField(default=0, null=True)),
                ('created_at_time', models.DateTimeField(null=True)),
                ('image', models.CharField(max_length=1000, null=True)),
                ('link', models.CharField(max_length=1000, null=True)),
                ('Media_data', models.CharField(max_length=10000, null=True)),
                ('last_scraped_tweet', models.DateTimeField(null=True)),
                ('keyword', models.CharField(max_length=1000, null=True)),
                ('view', models.BooleanField(default=True)),
                ('platform_type', models.CharField(default='twitter', max_length=500)),
                ('Tid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social_media.twitter_user')),
            ],
        ),
    ]