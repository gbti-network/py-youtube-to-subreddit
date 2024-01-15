import re
import praw
import json
import googleapiclient.discovery
import logging

# Configure logging to write debug information to a file
logging.basicConfig(filename='debug.log', level=logging.DEBUG)

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Initialize YouTube API
def init_youtube_api():
    try:
        youtube = googleapiclient.discovery.build(
            'youtube', 'v3', developerKey=config['youtube_api_key'])
        return youtube
    except Exception as e:
        # Log the error
        logging.error(f"Failed to connect to YouTube API: {e}")
        print("Failed to connect to YouTube API:", e)
        return None

# Initialize Reddit API
def init_reddit_api():
    try:
        reddit_config = config['reddit']
        reddit = praw.Reddit(
            client_id=reddit_config['client_id'],
            client_secret=reddit_config['client_secret'],
            username=reddit_config['username'],
            password=reddit_config['password'],
            user_agent='YouTube to Reddit Poster'
        )
        return reddit
    except Exception as e:
        # Log the error
        logging.error(f"Failed to connect to Reddit API: {e}")
        print("Failed to connect to Reddit API:", e)
        return None

# Function to parse YouTube URL and get ID
def parse_youtube_url(url):
    channel_id = None
    playlist_id = None

    if 'channel' in url:
        channel_id = url.split('/channel/')[-1].split('/')[0]
        # Check if the channel ID is valid
        if not is_valid_channel(init_youtube_api(), channel_id):
            logging.error(f"Invalid YouTube channel ID: {channel_id}")
            print(f"Invalid YouTube channel ID: {channel_id}")
            return None, None
    elif 'playlist' in url:
        playlist_id = re.search('list=(.*)', url).group(1)
    else:
        # Additional handling for custom URLs needed here
        pass

    return channel_id, playlist_id

# Function to check if a channel ID is valid
def is_valid_channel(youtube, channel_id):
    try:
        # Make a request to retrieve channel information
        request = youtube.channels().list(
            part="snippet",
            id=channel_id
        )
        response = request.execute()

        # If the response contains items, the channel is valid
        return 'items' in response
    except googleapiclient.errors.HttpError as e:
        # An error occurred, indicating that the channel is not valid
        return False

# Function to get videos based on channel ID or playlist ID with pagination
def get_youtube_videos(youtube, channel_id=None, playlist_id=None, max_results=100, order='date', direction='desc'):
    videos = []
    next_page_token = None

    while True:
        if channel_id:
            request = youtube.search().list(
                part="snippet",
                channelId=channel_id,
                maxResults=min(max_results - len(videos), 50),  # Limit to 50 per page or remaining limit
                order=order,
                type="video",
                pageToken=next_page_token
            )
        elif playlist_id:
            request = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=min(max_results - len(videos), 50),  # Limit to 50 per page or remaining limit
                pageToken=next_page_token
            )
        else:
            break

        # Log the API request
        logging.debug(f"API Request: {request.to_json()}")

        response = request.execute()
        videos += response.get('items', [])
        next_page_token = response.get('nextPageToken')

        if not next_page_token or len(videos) >= max_results:
            break

    # Manually sort the videos by date in the specified direction
    if direction == 'asc':
        videos.sort(key=lambda x: x['snippet']['publishedAt'])
    elif direction == 'desc':
        videos.sort(key=lambda x: x['snippet']['publishedAt'], reverse=True)

    # Print the titles of the loaded videos
    for video in videos:
        title = video['snippet']['title']
        print(f"Loaded video: {title}")

    if not videos:
        # Log query and response data when no videos are found
        logging.warn(f"No videos found for query: {request.to_json()}, response: {response}")

    return videos





# Function to check if a Reddit post already exists in the subreddit for a video
def reddit_post_exists(reddit, subreddit_name, video_title):
    subreddit = reddit.subreddit(subreddit_name)
    video_title = video_title.replace('&#39;', "'")
    for submission in subreddit.new(limit=10):  # Check the latest 10 posts
        if submission.title == video_title:
            return True
    return False

# Function to post videos to Reddit
def post_to_reddit(reddit, youtube, subreddit_name, video):
    video_id = video['id']['videoId'] if 'videoId' in video['id'] else video['snippet']['resourceId']['videoId']
    title = video['snippet']['title']
    title = title.replace('&#39;', "'")
    url = f'https://www.youtube.com/watch?v={video_id}'

    video_details_request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    video_details_response = video_details_request.execute()

    if not video_details_response.get('items'):
        print(f"Failed to fetch details for video ID: {video_id}")
        return

    description = video_details_response['items'][0]['snippet']['description']
    description = description.replace('&#39;', "'")

    for removal_string in config.get('comment_removal', []):
        description = description.replace(removal_string, '')

    logging.debug(f"Processing video: {title}, URL: {url}")

    print(f"Ready to post video: {title}\nURL: {url}")
    post_decision = input("Publish this video? (yes/skip): ").lower()
    if post_decision not in ['yes', 'y']:
        print("Video skipped.")
        return

    comment_template = config.get("comment_template", "")
    comment = comment_template.replace("{youtube.description}", description)
    comment = comment.replace("{youtube.title}", title)

    print("Prepared Comment:")
    print(comment)

    # Check if debug_mode is enabled
    debug_mode = config.get('debug_mode', False)

    subreddit = reddit.subreddit(subreddit_name)
    try:
        submission = subreddit.submit(title, url=url)

        if debug_mode:
            logging.debug(f"Reddit Post Submission: Title - {title}, URL - {url}")
            logging.debug(f"Submission ID: {submission.id}, Submission URL: {submission.url}")

    except Exception as e:
        logging.error(f"Failed to post to Reddit: {e}")
        print(f"Failed to post to Reddit: {e}")
        return

    comment_decision = input("Add description as a comment? (yes/no): ").lower()
    if comment_decision in ['yes', 'y']:
        try:
            comment_response = submission.reply(comment)
            print("Video and comment published.")

            if debug_mode:
                logging.debug(f"Comment Posted. Comment ID: {comment_response.id}")

        except Exception as e:
            logging.error(f"Failed to post comment to Reddit: {e}")
            print(f"Failed to post comment to Reddit: {e}")
    else:
        print("Video published without comment.")


# Main process
# Main process
def main():
    youtube = init_youtube_api()
    if not youtube:
        return

    reddit = init_reddit_api()
    if not reddit:
        return

    print("Successfully connected to YouTube and Reddit APIs.")
    logging.info("Successfully connected to YouTube and Reddit APIs.")

    subreddit_name = input("Enter the subreddit name to post videos: ")
    source_url = input("Enter YouTube channel or playlist URL: ")

    channel_id, playlist_id = parse_youtube_url(source_url)

    if not channel_id and not playlist_id:
        print("Invalid YouTube channel or playlist URL.")
        return

    max_results = input("Enter the maximum number of videos to pull (default is 100): ")
    if not max_results:
        max_results = 100
    else:
        max_results = int(max_results)

    sorting_options = ['date', 'rating', 'relevance', 'title', 'videoCount', 'viewCount']
    print("Available sorting options:", sorting_options)
    order = input("Enter the sorting order (default is 'date'): ").lower()
    if not order:
        order = 'date'
    elif order not in sorting_options:
        print("Invalid sorting order. Using default 'date' sorting order.")
        order = 'date'

    direction_options = ['asc', 'desc']
    print("Available sorting directions:", direction_options)
    direction = input("Enter the sorting direction (default is 'desc'): ").lower()
    if not direction:
        direction = 'desc'
    elif direction not in direction_options:
        print("Invalid sorting direction. Using default 'desc' sorting direction.")
        direction = 'desc'

    videos = get_youtube_videos(youtube, channel_id=channel_id, playlist_id=playlist_id, max_results=max_results, order=order, direction=direction)

    if not videos:
        print("No videos found.")
        return

    for video in videos:
        video_title = video['snippet']['title']
        if not reddit_post_exists(reddit, subreddit_name, video_title):
            post_to_reddit(reddit, youtube, subreddit_name, video)
        else:
            print(f"Skipping video '{video_title}' as it already exists in subreddit.")

# Run the main process
if __name__ == "__main__":
    main()