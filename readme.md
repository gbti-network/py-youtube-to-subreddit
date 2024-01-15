# Py YouTube to Reddit

We developed this python script to accept either a Youtube channel or a YouTube playlist to import their videos into a sub reddit.

![Youtube-to-subreddit](https://github.com/gbti-labs/py-youtube-to-subreddit/assets/125175036/846e7d43-924d-4c7c-ab5b-58135e803276)

## Setup

### YouTube API Key
1. Visit the [Google Developers Console](https://console.developers.google.com/).
2. Create a project and enable the YouTube Data API v3 for it.
3. In the "Credentials" section, create an API key.

### Reddit Script Credentials
1. Log in to [Reddit](https://www.reddit.com/).
2. Go to the [Reddit Apps page](https://www.reddit.com/prefs/apps) (found under "User Settings" -> "Safety & Privacy" -> "Developer").
3. Click "Create App" or "Create Another App".
4. Fill out the form:
   - Name: Give your app a name.
   - App type: Choose "script".
   - Description: (Optional) Describe your app.
   - About URL: (Optional)
   - Permissions: (Optional)
   - Redirect URI: Use `http://localhost:8080`.
5. Click "Create app".
6. Note your `client_id` (listed just under the app name) and `client_secret` (labeled as "secret").

### Configuration File
Create a `config.json` file with the following content:

```json
{
   "youtube_api_key": "YOUR_YOUTUBE_API_KEY",
   "reddit": {
      "client_id": "YOUR_REDDIT_CLIENT_ID",
      "client_secret": "YOUR_REDDIT_CLIENT_SECRET",
      "username": "YOUR_REDDIT_USERNAME",
      "password": "YOUR_REDDIT_PASSWORD"
   },
   "debug_mode": true,
   "comment_template" : "This comment is is sourced from the video description:\r\n\r\n\"{youtube.description}\"",
   "comment_removal" : [
      "Remove some string A",
      "Remove some string B"
   ]
}
```

Replace placeholders with your actual credentials.

## Installation

### Dependencies
The script requires certain Python packages. Install them using the following steps:

1. Run the command ``pip install -r requirements.txt`` to install the dependencies.

This may require you to run as administrator. 

## Usage

In a terminal inside the application directory run:

```
py run.py
```
And follow the prompts as they will ask which subreddit to publish to, which channel or playlist should be sourced from. 

Once you've setup your import condition the script will itterate through each video and confirm that you would like to publish the video or skip it. 

The script will also ask you if you would like to post the video description as the first comment. 

### Features

* Process videos one at a time
* Can skip videos
* Can sort by date asc, date desc, view count, and likes
* Comments are optional
* Comment is powered by template in config.json
* Checks the subreddit to make sure that the post does not already exist

## Follow GBTI for more

Thanks for reading! If you like our content, please consider following us!

[Twitter/X](https://twitter.com/gbtilabs) | [GitHub](https://github.com/gbti-labs) | [YouTube](https://www.youtube.com/channel/UCh4FjB6r4oWQW-QFiwqv-UA) | [Dev.to](https://dev.to/gbti) | [Daily.dev](https://dly.to/zfCriM6JfRF) | [Hashnode](https://gbti.hashnode.dev/) | [Blog / Discord](https://gbti.io)
