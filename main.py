###################### START CONFIGURATION DATA ######################

# If true, will not actually upload to Catbox and Lemmy - useful for simulation
testMode = True

### Catbox ###

# Catbox API URL
catboxAPIURL = "https://catbox.moe/user/api.php"
# Catbox User Key
catboxUserhash = ""



### Reddit ###

#API connection setup
clientID = ""
clientSecret = ""
userAgent = ""

# SubReddit to capture
subreddit = ""

# Capture "New" posts? If False, will default to "Top" posts instead.
newContent = False

# Number of posts to capture. Only works if newContent = False. Max value is 1000 due to API limit.
postCaptureCount = 10



### Lemmy ###

# Lemmy Server / Instance
lemmyServer = ""

# Lemmy Credentials
username = ""
password = ""

# Lemmy community to migrate to
lemmyCommunity = ""


###################### END CONFIGURATION DATA ######################

import datetime
import requests
import redditcapture as rc
import catbox as cb
import lemmypost as lp

# Start by getting the subreddit post data. This may take a while depending on the number of posts requested.
print("Connecting to Reddit")
posts = rc.captureSubreddit(clientID, clientSecret, userAgent, subreddit, postCaptureCount, newContent)
print(f"Obtained {len(posts)} posts from {subreddit}")

# The variable "posts" now contains two list items [0] is the post information, [1] is all the comments
# Let's process these:

processedPosts = []
print("Processing JSON")
for post in posts:
    postData = []
    postData.append(rc.getPostInformation(post[0]))
    postData.append(rc.getCommentsforPost(post[1]))    
    processedPosts.append(postData)
# processedPosts is now our list of posts from the subreddit in the format processedPosts[i] -> [[postdata],[commentdata]]

# Next we need a list of all the posts we currently have in our Lemmy community so that we can dedup the list of processedPosts
print(f"Getting Lemmy Community posts for {lemmyCommunity} on {lemmyServer}")
lemmyPosts = lp.getPosts(lemmyServer, lemmyCommunity)

# Now we need the comments from these that contain the Reddit post ID as part of the "credit"
lemmyCreditComments = []
for lemmyPost in lemmyPosts:
    creditComment = lp.getCreditComment(lemmyServer, lemmyPost["post"]["id"])  
    lemmyCreditComments.append(creditComment)

# Now we have all the Reddit comments AND the Lemmy "credit" comments, we can compare and dedup.
print(f"Deduplicating:")
dedupList = []
for i in processedPosts:
    if (len(lemmyCreditComments) > 0):
        if any(i[0]["id"] in s for s in lemmyCreditComments):
            continue
        else:
            dedupList.append(i)      
    else:
        dedupList.append(i) 
        
print(f"    {len(dedupList)} new posts identified")
        
# This gives us a deduplicated list of posts that are ready to process in dedupList
# BUT
# Before we can transfer this to Lemmy, we need to serve images somewhere. 
# Imgur has banned nsfw content, and we don't want to rely on i.redd.it... so we use catbox for now
# A better solution would be to download the image and upload it to Lemmy but I can't see how to do this via the API
print(f"Processing {len(dedupList)} images to catbox")
for post in dedupList:
    if not testMode:
        if (cb.checkURL(post[0]["url"])):
            catboxURL = (cb.transferToCatbox(catboxAPIURL, catboxUserhash, post[0]["url"]))
            post[0]["url"] = catboxURL

# We now have a set of posts that's ready to hit Lemmy! 
print(f"Posting {len(dedupList)} posts to Lemmy")
userToken = lp.login(lemmyServer, username, password)
postCount = 0
commentCount = 0
for post in dedupList:
    # First, post the actual post.
    print(f'Posting {postCount+1} of {len(dedupList)}: {post[0]["title"]}')
    if not testMode:
        postID = lp.setPost(userToken, lemmyServer, lemmyCommunity, post[0]["title"], post[0]["url"], post[0]["body"], nsfw = post[0]["nsfw"])
        giveCredit = lp.setComment(userToken, lemmyServer, post[0]["creditComment"], postID)
        lp.distinguishComment(userToken, lemmyServer, giveCredit)
    postCount += 1    
    
    # Now we'll post the comments. We keep track of which onces we've posted to be able to correctly nest comment replies
    # Note the [3:] which strips the "t1_" from the front of the ID we get via the Reddit API
    postedComments = {}        
    for comment in post[1]:
        if not testMode:
            commentDate = datetime.datetime.fromtimestamp(comment["commentCreated"])  
            commentContent = f'{comment["commentBody"]}\r\n\r\nOriginally commented by u/{comment["commentAuthor"]} on {commentDate} ([{comment["commentID"]}](https://www.reddit.com{comment["commentPermalink"]}))'        
            lemmyCommentID = lp.setComment(userToken, lemmyServer, commentContent, postID, parentID = postedComments.get(comment["commentParentID"][3:]))
            postedComments[comment["commentID"]] = lemmyCommentID
        commentCount += 1       
        
print(f"Uploaded {postCount} post(s) and {commentCount} comment(s) to {lemmyCommunity} on {lemmyServer} as {username}")
    
# Done! Thanks :) 
