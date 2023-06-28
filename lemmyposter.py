### Lemmy Poster
##  Uses Lemmy HTTP requests via API: https://join-lemmy.org/api/classes/LemmyHttp.html

import requests

## Obtain auth token
## Returns token
## Reference: https://join-lemmy.org/api/classes/LemmyHttp.html#login

def login(server, username, pw):
    userDetails = {
        "username_or_email": username,
        "password": pw
    }
    
    try:
        request = requests.post(f"{server}/api/v3/user/login", json = userDetails)
        return request.json()["jwt"]
        
    except Exception as e:
        print(f"Error logging in with {username}: {e}")
        exit()
    

## Get Community ID from Community Name (NOT display name)
## Returns community id
## Reference: https://join-lemmy.org/api/classes/LemmyHttp.html#getCommunity

def getCommunityID(server, communityName):
        try:
            request = requests.get(f"{server}/api/v3/community?name={communityName}")
            communityId = request.json()["community_view"]["community"]["id"]
            return communityId   
            
        except Exception as e:
            print(f"Error when fetching community ID for '{communityName}': {e}")
            exit()


## Create Post
## Returns post id
## Reference: https://join-lemmy.org/api/classes/LemmyHttp.html#createPost

def setPost(authToken, server, community, postName, postURL = None, postBody = None, nsfw = False):
    postContent = {
        "auth": authToken,
        "community_id": getCommunityID(server, community),
        "name": postName,
        "language_id" : 37, # I think that's English going by the json received from other posts
        "nsfw" : nsfw
    }
    
    if postURL:
         postContent["url"] = postURL
         
    if postBody:
         postContent["body"] = postBody
         
    try:
        request = requests.post(f"{server}/api/v3/post", json = postContent)
        return request.json()["post_view"]["post"]["id"]  
        
    except Exception as e:
        print(f"Error encountered while posting: '{postContent}': {e}")
        return False     
      

## Create a comment for a given Post
## Reference: https://join-lemmy.org/api/classes/LemmyHttp.html#createComment

def setComment(authToken, server, content, postId, parentID = None):
    commentContent = {
        "auth" : authToken,
        "content" : content,
        "post_id" : postId,
    }
    
    if parentID:
         commentContent["parent_id"] = parentID
         
    request = requests.post(f"{server}/api/v3/comment", json = commentContent)
    
    if not request.ok:
        print(f"Error encountered while commenting: {request.text}")
        
    return request.json()["comment_view"]["comment"]["id"]    


## Distinguish a comment 
## Reference: https://join-lemmy.org/api/classes/LemmyHttp.html#editComment

def distinguishComment(authToken, server, commentID):
    commentContent = {
        "auth" : authToken,
        "comment_id" : commentID,
        "distinguished" : True
    }
    
    request = requests.put(f"{server}/api/v3/comment", json = commentContent)
    
    if not request.ok:
        print(f"Error encountered while distinguishing comment: {request.text}")
        
    return request.json()["comment_view"]["comment"]["distinguished"]    


## Get posts from a Community by Community Name (NOT display name)
## Returns list of posts
## Reference: https://join-lemmy.org/api/classes/LemmyHttp.html#getPosts

def getPosts(authToken, server, communityName):
    try:
        posts = []
        page = 1       
        while ((request := requests.get(f"{server}/api/v3/post/list?auth={authToken}&community_name={communityName}&page={page}")) and len(request.json()["posts"]) > 0):
            for postDetails in request.json()["posts"]:            
                posts.append(postDetails)                
            page += 1

        return posts   
        
    except Exception as e:
        print(f"Error when fetching posts from '{communityName}' on '{server}': {e}")
        exit()
            
## Get comments for a specific post
## Returns list of comments
## Reference: https://join-lemmy.org/api/classes/LemmyHttp.html#getComments
def getComments(server, postID):
        try:
            request = requests.get(f"{server}/api/v3/comment/list?post_id={postID}")
            posts = request.json()
            return posts   
            
        except Exception as e:
            print(f"Error when fetching comments from '{communityName}' on '{server}': {e}")
            exit()
            
## Get the "credit" comment for a specific post (if there is one)
## Returns a single comment
## Reference: https://join-lemmy.org/api/classes/LemmyHttp.html#getComments
def getCreditComment(server, postID):
        try:
            request = requests.get(f"{server}/api/v3/comment/list?post_id={postID}&sort=Old")
            posts = request.json()
            
            #Our credit comments are distinguished so we can use this to check
            if(len(posts["comments"]) > 0 and posts["comments"][0]["comment"]["distinguished"] and "Originally posted by" in posts["comments"][0]["comment"]["content"]):
                return posts["comments"][0]["comment"]["content"]
            else:
                return "" # We must return an empty string here to avoid breaking iteration later - "None" for example will generate an error
            
        except Exception as e:
            print(f"Error when fetching credit comment from '{communityName}' on '{server}': {e}")
            exit()
