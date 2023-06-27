# Reddit to Lemmy

Export a Reddit subreddit to a Lemmy community

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

### Write Documentation
In progress!
