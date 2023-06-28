import datetime
import requests
import praw

def captureSubreddit(clientID, clientSecret, userAgent, subReddit, numPosts, newPosts = True):

    r = praw.Reddit(client_id = clientID, client_secret = clientSecret, user_agent = userAgent)
    submissions = []

    subreddit = r.subreddit(subReddit)
    
    try:
        if(newPosts):
            # Cut off time set to 48 hours ago. This allows time for moderation of spam etc.
            cutoffTime = datetime.datetime.now(datetime.timezone.utc).timestamp()-172800 
            for submission in subreddit.new():    
                if (submission.created_utc < cutoffTime):
                    id = submission.id                
                    redditResponse = requests.get(f'https://www.reddit.com/comments/{id}/.json?raw_json=1', headers={'User-Agent': 'Subreddit archiver' })
                    redditResponse.raise_for_status()
                    redditJSON = redditResponse.json()
                    
                    submissions.append(redditJSON)
        else:
            for submission in subreddit.top(limit=numPosts):    
                id = submission.id
                redditResponse = requests.get(f'https://www.reddit.com/comments/{id}/.json?raw_json=1', headers={'User-Agent': 'Subreddit archiver' })
                redditResponse.raise_for_status()
                redditJSON = redditResponse.json()
                
                submissions.append(redditJSON)
            
    except Exception as e:
        # We may get exceptions if the subreddit has been made private / banned etc, or if Reddit is down
        print(f"Error when fetching posts from '{subreddit}': {e}")
        exit()        
        
    return submissions
    
# The information we want is held in ['data']['children']. T3 is a post. T1 is a comment. The latter will need recursive iteration.
    
    
def getPostInformation(postDataFromJSON):

    # Post data we want:
    # ["data"]["children"][0]["kind"] = t3
    # ["data"]["children"][0]["data"]["title"]
    # ["data"]["children"][0]["data"]["author"]
    # ["data"]["children"][0]["data"]["created"]
    # ["data"]["children"][0]["data"]["url"]
    # ["data"]["children"][0]["data"]["permalink"]
    # ["data"]["children"][0]["data"]["over_18"]
    # ["data"]["children"][0]["data"]["selftext"]

    postInformation = {}    #{} is dictionary and allows us to use named keys. [] is a list and keys are integers
    postInformation["title"] = postDataFromJSON["data"]["children"][0]["data"]["title"]
    postInformation["url"] = postDataFromJSON["data"]["children"][0]["data"]["url"]
    postInformation["id"] = postDataFromJSON["data"]["children"][0]["data"]["id"]   
    postInformation["nsfw"] = postDataFromJSON["data"]["children"][0]["data"]["over_18"]   
    postInformation["body"] = postDataFromJSON["data"]["children"][0]["data"]["selftext"]
    
    
    postAuthor = postDataFromJSON["data"]["children"][0]["data"]["author"] 
    postPermalink = postDataFromJSON["data"]["children"][0]["data"]["permalink"]       
    postDate = datetime.datetime.fromtimestamp(postDataFromJSON["data"]["children"][0]["data"]["created"])    
    
    postInformation["creditComment"] = f'#### {postInformation["title"]}\r\n\r\n`Originally posted by u/{postAuthor} on {postDate}` ([{postInformation["id"]}](https://www.reddit.com{postPermalink})).'
        
    return postInformation
        
def extractAllComments(commentList, postData):  

    # Comment data we want:    
    # For each comment in ["data"]["children"][i]
    #   
    #   ["data"]["id"]
    #   ["data"]["parent_id"]
    #   ["data"]["body"]
    #   ["data"]["created"]
    #   ["data"]["permalink"]
    #   ["data"]["author"]
    #   ["data"]["replies"]
    #   If replies > 0 then recursively call the function again to obtain all nested comments

    for comment in postData["data"]["children"]:        

        try:
            commentData = {}
            commentData["commentID"] = comment["data"]["id"]
            commentData["commentParentID"] = comment["data"]["parent_id"]
            commentData["commentBody"] = comment["data"]["body"]
            commentData["commentCreated"] = comment["data"]["created"]
            commentData["commentPermalink"] = comment["data"]["permalink"]
            commentData["commentAuthor"] = comment["data"]["author"]
            
            commentList.append(commentData)
            
            if (len(comment["data"]["replies"]) > 0):
                extractAllComments(commentList, comment["data"]["replies"])
                
            return commentList
            
        except Exception as e:
            # Sometimes we hit JSON errors - unclear why as it is intermittent. Possibly due to the Reddit response?
            # We can skip the erroneous record and continue, no need to stop as the post will be picked up next time.
            print(f"Error extracting comments: {e}")
            print(comment)
        
    

# Wrapper for recursive function extractAllComments
def getCommentsforPost(postDataFromJSON):

    allComments = []
    
    extractAllComments(allComments, postDataFromJSON)
           
    return allComments



