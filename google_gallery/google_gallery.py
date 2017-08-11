#!/usr/bin/python2.7
 
# module ----  
import os
import webbrowser
from datetime import datetime, timedelta
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
import gdata.photos.service
import gdata.media
import gdata.geo
import httplib2
import json
import urllib2
 
# global variables ----
photo_arr = []

# Google Authetication
def OAuth2Login(client_secrets, credential_store, email):
    scope='https://picasaweb.google.com/data/'
    user_agent='picasawebuploader'
    storage = Storage(credential_store)
    credentials = storage.get()
 
    if credentials is None or credentials.invalid:
        flow = flow_from_clientsecrets(client_secrets, scope=scope, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        uri = flow.step1_get_authorize_url()
        webbrowser.open(uri)
        code = raw_input('Enter the authentication code: ').strip()
        credentials = flow.step2_exchange(code)
        storage.put(credentials)
 
    if (credentials.token_expiry - datetime.utcnow()) < timedelta(minutes=5):
        http = httplib2.Http()
        http = credentials.authorize(http)
        credentials.refresh(http)
 
    gd_client = gdata.photos.service.PhotosService(source=user_agent,
                                               email=email,
                                               additional_headers={'Authorization' : 'Bearer %s' % credentials.access_token})
    return gd_client
 

# main ----- 
if __name__ == '__main__':
    email = os.environ['EMAIL']
    confDir = os.path.abspath(os.path.dirname(__file__))
    client_secrets = os.path.join(confDir, 'photo-gallery.json') 
    credential_store = os.path.join(confDir, 'credentials.dat') 
    gd_client = OAuth2Login(client_secrets, credential_store, email)
 
    albums = gd_client.GetUserFeed()
    for album in albums.entry:
        print 'Album: %s (%s)' % (album.title.text, album.numphotos.text)
 
        photos = gd_client.GetFeed('/data/feed/api/user/default/albumid/%s?kind=photo' % (album.gphoto_id.text))
        for photo in photos.entry:
            print(photo.title.text)
            photo_arr.append(photo)

    
    f = open(photo_arr[0].title.text, 'w')
    f.write(urllib2.urlopen(photo_arr[0].content.src).read())
    f.close()
