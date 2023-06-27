# Reddit to Lemmy

Export (the top posts of) a Reddit subreddit to a Lemmy community

## Dependencies

https://github.com/praw-dev/praw

## Usage

Download all the `.py` files and put them in the same location.

Open `main.py` and update the configuration parameters.

Run `main.py`. (Note: sometimes JSON parse errors are encountered, I am unsure why as they are inconsistent and repeating the same run again will not always reproduce the error. I suggest retrying if this happens.)

#### Parameter explanation
`testMode (boolean)` `True` for testing connectivity without actually uploading anything. `False` to enable uploads.

`catboxAPIURL (string)` Preset to the Catbox API URL but may need to be changed if the URL changes.

`catboxUserhash (string)` Create an account on Catbox and your profile page will show your user hash.

`clientID (string)` Create an app within Reddit here: https://www.reddit.com/prefs/apps. Select "Script for personal use" . Find your client ID under the name of the app.

`clientSecret (string)` Similar to the client ID, this is for the client secret.

`userAgent(string)` This is to provide the user agent to Reddit, but can be set to whatever you like e.g. Reddit To Lemmy migration.

`subreddit (string)` The subreddit name (no preceding r/) to migrate from.

`newContent (boolean)` EXPERIMENTAL, results not guaranteed: Obtain new posts rather than top posts if `True`.

'postCaptureCount (integer)' Number of posts to capture. Numbers over 1000 are capped due to the Reddit API but I recommend running in smaller batches in case of JSON parse issues.

`lemmyServer (string)` Lemmy instance to migrate to.

`username (string)` Username of Lemmy account. 

`password (string)` Password of Lemmy account.

`lemmyCommunity (string)` Lemmy community on the above instance to migrate to.


## Plan

### Use Reddit API to obtain list of posts from a subreddit. 
This will need to be done without pushshift for the time being.
Need to do something like take 1000 new posts that are at least 48? hours old to allow for moderation etc. 
***How to verify we aren't going to be dealing with duplicates?*** If we're avoiding our own database in the middle then we'll need to do some checks before uploading.

✅ Done 

### Parse the data of those posts into a format we can iterate through for uploading.
The posts themselves are easy enough but nested comment trees are going to be more challenging. Need to be able to parse the json from the Reddit output - is there anything out there doing that already I wonder? 

✅ Done

### Validate / dedup the posts
As per the above, need to obtain a list of what's currently in the Lemmy community so that we don't duplicate. This could be done by retaining the original reddit post ID in a comment which we can then read into a list for each upload process. Feels data heavy, but means we don't need a database to record what we've done so far.

✅ Done

### Upload image to Catbox
Imgur is removing NSFW content, and i.reddit defeats the point of moving away from reddit. So if the image is hosted on either of these, move it to catbox https://catbox.moe/tools.php

✅ Done

### Upload to Lemmy
Hopefully straightforward using Lemmy's HTTP request API.

✅ Done

### Write Documentation as readme.md

✅ Done
