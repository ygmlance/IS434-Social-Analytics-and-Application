from instaloader import Instaloader, Hashtag, Profile, InstaloaderContext
from itertools import dropwhile, takewhile
import datetime
import os

def read_file(filename):
    result = []
    with open(filename, 'r') as f:
        for line in f:
            result.append(line.strip())
    return result

def write_file(write_list, filename):
    with open(filename, 'a') as f:
        result = ''
        for line in write_list:
            have_emoji = False
            for ch in line:
                if len(ch) != len(ch.encode()):
                    have_emoji = True
                    
            if not have_emoji:
                result += line + '\n'
                    
        f.write(result.strip())

def get_instance():
    scraper = Instaloader(
        compress_json=False, 
        filename_pattern='{date_utc:%Y-%m-%d}_UTC/{date_utc}_UTC_{shortcode}_{owner_id}',

        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        max_connection_attempts=0
    )
    
    return scraper

def get_suggested_account(filename):
    
    #Get instance
    scraper = get_instance()
    
    # Login
    scraper.load_session_from_file('amazinglance_')
    
    target_profiles = read_file(filename)

    for profile_name in target_profiles:
        profile = Profile.from_username(scraper.context, profile_name)
        
        suggested_profiles = list( map( lambda s_profile : s_profile.username, profile.get_similar_accounts() ) )
        write_file(suggested_profiles, 'pending_target_profile.txt')
        
    scraper.close()

def get_suggested_tag(filename):
    #Get instance
    scraper = get_instance()
    
    # Login
    scraper.load_session_from_file('amazinglance_')
    
    target_hashtags = read_file(filename)
    
    for hashtag_name in target_hashtags:
        hashtag = Hashtag.from_name(scraper.context, hashtag_name)
        
        suggested_hashtags = list( map( lambda s_hashtag : s_hashtag.name, hashtag.get_related_tags() ) )
        
        print (suggested_hashtags)
        write_file(suggested_hashtags, 'pending_target_hashtag.txt')
        
    scraper.close()

def scrape_profile(filename):
    #Get instance
    scraper = get_instance()
    
    target_profiles = read_file(filename)
    

    for profile_name in target_profiles:
        current_count = 0
        skip_count = 0
        
        profile = Profile.from_username(scraper.context, profile_name)
        user_posts = profile.get_posts() 
        
        # for post in takewhile(lambda p: p.date > start_date, dropwhile(lambda p: p.date > end_date, user_posts)):
        #     scraper.download_post(post, target=profile.username)
        print ('Scraping Username:   ' + profile.username)
        for post in user_posts:
            if post.date > start_date and post.date < end_date:
                current_count += 1
                print ('[ {} / {} ]'.format(current_count + skip_count, profile.mediacount), end=" ")
                scraper.download_post(post, target=profile.username)
            else:
                skip_count += 1
                print ('[ {} / {} ]'.format(current_count + skip_count, profile.mediacount), 'Skipping')
    
    scraper.close()
        
            
def scrape_hashtag(filename):
    #Get instance
    scraper = get_instance()
    
    target_hashtags = read_file(filename)
    
    
    for hashtag_name in target_hashtags:
        current_count = 0
        skip_count = 0
        
        hashtag = Hashtag.from_name(scraper.context, hashtag_name)
        hashtag_post = hashtag.get_all_posts()
        
        
        print ('Scraping Username:   ' + hashtag.name)
        
        for post in hashtag_post:
            if post.date > start_date and post.date < end_date:
                current_count += 1
                print ('[ {} / {} ]'.format(current_count + skip_count, hashtag.mediacount), end=" ")
                scraper.download_post(post, target='#' + hashtag.name)
            else:
                skip_count += 1
                print ('[ {} / {} ]'.format(current_count + skip_count, hashtag.mediacount), 'Skipping')
            
    scraper.close()
           
           
# Save all files into this folder relative to the programme
if not os.path.isdir('raw_insta_data'):
    os.mkdir('raw_insta_data')
os.chdir('raw_insta_data')

#Filter Parameter
start_date = datetime.datetime(2020, 4, 8)
end_date = datetime.datetime(2020, 6, 2)

# To scrape data from endpoints
scrape_profile('target_profiles.txt')
scrape_hashtag('target_hashtags.txt')

# Snowballing the recommended hashtag and accounts to continue scraping
get_suggested_account('target_profiles.txt')
get_suggested_tag('target_hashtags.txt')