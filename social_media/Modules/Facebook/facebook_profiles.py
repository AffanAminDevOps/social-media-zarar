import time
import random
import re
# from database import *
from .utils import *
from . import conf 
from datetime import date
import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
from ...models import *

def get_features(text, link=None, post_link=None):
    try:
        shared = False
        if 'reels' in text:
            post_message = text.split("Reels")[0].strip().split('\n')[:-1]
            post_message = post_message[0]
            upload_time = text.split('Reels')[1].strip().split('.')[0].split('\n')[0].replace('·', '').strip()
            reactions, comments, shares = text.split('·')[-1].strip().split('\n')
            post_type = 'reel'
        else:
            #for message
            post_message_start = text.index("·") + 1
            post_message_end = text.index("All reactions:")
            post_message = text[post_message_start:post_message_end].strip().replace('See translation','')
            video_time_pattern = re.compile(r"\d+:\d+ / \d+:\d+")
            post_message =video_time_pattern.sub("", post_message).strip()
    
            if "·" in post_message:
                post_message = post_message.replace('·', '')
                shared = True
        
            # Extract reactions, comments, and shares
            reactions_start = text.index("All reactions:") + len("All reactions:")
            reactions_end = text.index("Like")
            reactions = text[reactions_start:reactions_end].strip()
            reactions = reactions.split('\n')[0]
        
            likes = text.split('All reactions:')[1].split("\nLike\n")[0]
            comments = likes.split('\n')[-2].replace("comments", "").strip()
            shares = likes.split('\n')[-1].replace("shares", "").strip()
            
            #upload time
            upload_time = text.split('\n')[1]
        
            #type of the post
            # Extract the video time using regular expression
            video_time_pattern = re.compile(r"\d+:\d+ / \d+:\d+")
            video_time_match = video_time_pattern.search(text)
            post_type = 'text'
            
            if video_time_match:
                post_type = "video"
                post_type += " " + video_time_match.group()
            
    
            if link != None and 'text' in post_type:
                post_type = 'photo'   
        print("Post:\n", post_message)
        print(f"\nReactions: {reactions}  Shares: {shares} Comments: {comments}")
        print("Type:",post_type, "Upload Time:", upload_time, "Shared:", shared)
        
        data = {
        "Post": str(post_message),
        "Reactions": str(reactions),
        "Shares": str(shares),
        "Comments": str(comments),
        "Type": str(post_type),
        "Upload Time": str(date.today()),
        "Shared": str(shared),
        "Post_Link": str(post_link),
        "Photo": link
        }
        # print(data)
        return data
    except Exception as e:
        print(e)
        print("Text is :", text)
        return None
        
           
def facebook_data_to_db(account, data):
    # photo_data= None
    # if data['Photo'] != None:
    #     # Read and convert the image file to bytes
    #     with open(data['Photo'], 'rb') as photo_file:
    #         photo_data = photo_file.read()
    #         print("File converted")
    try:
        if facebook_post.objects.filter(account=account,post=data['Post']).first():
            fb_post=facebook_post.objects.filter(account=account,post=data['Post']).first()
            fb_post.reactions=data['Reactions'],
            fb_post.shares=data['Shares'],
            fb_post.comments=data['Comments'],
            fb_post.shared=data['Shared'],
            fb_post.last_scraped=datetime.now()
            fb_post.save()
        else:
            photo_path = None
            if data['Photo'] != None and data['Type'] != 'reel':
                print("Photo: ", data['Photo'])
                photo_path = download_image(data['Photo'])
            fb_post=facebook_post(
                account=account,
                post=data['Post'],
                reactions=data['Reactions'],
                shares=data['Shares'],
                comments=data['Comments'],
                type=data['Type'],
                upload_time=data['Upload Time'],
                shared=data['Shared'],
                thumbnail_link=photo_path,
                link=data['Post_Link'],
                last_scraped=datetime.now()
            )
            fb_post.save()
            print("Post saved")
        
    except:
        print("Post Not saved")


def get_last_posts(driver,account, last_posts):
    try:
        for post_number in range(1,last_posts+1):
            scroll_post(driver)
            time.sleep(2)
            # Find the <div> element with a specific aria-posinset value
            div_elements = driver.find_elements(By.XPATH ,f"//div[@aria-posinset='{post_number}']")
            print("Post Number: ", post_number)
            # Print details of the found elements
            for div_element in div_elements:
                tag_name = div_element.tag_name
                text = div_element.text
                attributes = div_element.get_attribute("outerHTML")
            
                photo = False
                soup = BeautifulSoup(attributes, 'html.parser')
                img_tags = soup.find_all('img')
                # Print details of each <img> tag
                for img_tag in img_tags:
                    src_value = img_tag.get('src')
                    if "scontent" in src_value:
                        photo = True
                        break
                post_link = None
                try:
                    # Getting post link
                    target_keywords = ['live', 'photo', 'video']
                    filtered_links = [a['href'] for a in soup.find_all('a', href=True) if any(keyword in a['href'] for keyword in target_keywords)]
                    # cleaning link metadata
                    for link in filtered_links:
                        if "videos" in link:
                            link = link.split("/?")[0]
                            post_link= link
                        if "photo" in link:
                            link = link.split("&set")[0]
                            post_link= link
                    print("Post Link: ", post_link) 
                except Exception as e:
                    print("Error on Cleaning Post Links")                    
                    print(e)
                if photo:
                    data = get_features(text.strip(), link=src_value, post_link=post_link)
                    if data:
                        facebook_data_to_db(account, data)
                    else:
                        print(text)
                else:
                    data = get_features(text.strip(), post_link=post_link)
                    if data:
                        facebook_data_to_db(account, data)
                    else:
                        print(text)
                print("---"*30)            
    except Exception as e:
        print(e)
        print("Error in get last posts..........................><><><><>")




def facebook_profile(profile=''):
    # setup_database()
    while(True):
        try:
            driver = open_profile(profile='facebook')
            driver.get('https://www.facebook.com/')
            check_login(driver)
            time.sleep(4)
            accounts=[]
            if profile=='':
                all_profiles = list(profiles.objects.values_list('profile', flat=True))
                all_sources = list(profiles.objects.values_list('source', flat=True))
                for index in range(len(all_profiles)):
                    if all_sources[index]=='facebook' or all_sources[index]=='Facebook':
                        accounts.append(all_profiles[index])
            else:
                accounts.append(profile)
            # accounts1 = ['mansooralikhanlive', 'DawnNews','anwarlodhi', 'MoeedPirzada', 'SabirShakirARY']
            # accounts2 = ['GeoUrduDotTv', 'expressnewspk', 'UDarOfficial', 'arynewsasia', 'samaatvnews' ]
            while(True):
                # if is_between_1am_and_3am():
                #     print("Time to sleep boy........"*4)
                #     driver.quit()
                #     time.sleep(21600)
                #     driver = open_profile(profile='facebook')
                #     driver.get('https://www.facebook.com/')
                #     check_login(driver)
                random.shuffle(accounts)
                for account in accounts:
                    print("Account:", account)
                    driver.get(r'https://www.facebook.com/'+account+'/')
                    time.sleep(5)
                    get_last_posts(driver,account, 10)
                driver.get('https://www.facebook.com/')
                scroll_post(driver, posts=5)
                time.sleep(15)

                driver.quit()
                return True
        except Exception as e:
            print(e)
            try:
                driver.quit()
            except:
                pass

    # driver.quit()
# if __name__ == "__main__":
#     main()
