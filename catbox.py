### Catbox Uploader
##  Takes images hosting on a list of known "unwanted" URLs and uploads them to Catbox
##  Uses Catbox API: https://catbox.moe/tools.php

import requests

# List of URLs we don't want to use
listOfURLs = ["imgur", "redd.it"]

def checkURL(url):

    for checkURL in listOfURLs:  
    
        if(checkURL in url):
            return True
        
    return False

def transferToCatbox(server, userhash, url, nsfw = 0):
    payload = {
        "reqtype" : "urlupload",
        "userhash" : userhash,
        "url" : url
    }
    try:       
        request = requests.post(server, payload)
        # Check for a successful upload - if an invalid or old image URL is used it might not be accessible anymore
        if request.status_code == 200:        
            return request.text
        else:
            return None
        
    except Exception as e:
        print(f"Error uploading to Catbox {url}: {e}")
        return False
    
    return True
