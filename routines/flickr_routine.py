#!/bin/env python

import sys
import time
import flickrapi
from xml.etree import ElementTree
import urllib2
import subprocess
import os

api_key = ''  # use privileged API key
flickr = flickrapi.FlickrAPI(api_key)

lastPhotoFilename = 'web/last_photo'

while True:
    # get my public photo streams
    photos = flickr.people_getPhotos(user_id='') # get public photo stream
    # get the latest photo ID from Flickr
    latestId = photos.find('photos').find('photo').attrib['id']
    # get the last processed ID from local file
    lastFile = open(lastPhotoFilename, 'r')
    lastId = lastFile.read().strip("\n")
    lastFile.close()

    print 'latestId:%s, lastId:%s' % (latestId, lastId)

    if latestId != lastId:
        # download the latest photo
        # 1) get the metadata
        photo = photos.find('photos').find('photo')
        farm = photo.attrib['farm']
        id = photo.attrib['id']
        secret = photo.attrib['secret']
        server = photo.attrib['server']
        
        # 2) construct photo URL
        photoUrl = "https://farm%s.staticflickr.com/%s/%s_%s_c.jpg" % (farm, server, id, secret)
    
        # 3) download photo into local disc
        print '    downloading image from: %s' % photoUrl
        resp = urllib2.urlopen(photoUrl)
        output = open("web/photo_files/%s.jpg" % id, "wb")
        output.write(resp.read())
        output.close()
        resp.close()

        # 4) update 'last_photo' file
        print '    updating last_photo file to %s' % (id)
        lastFile = open(lastPhotoFilename, 'wb')
        lastFile.write("%s\n" % id)
        lastFile.close()

        # 5) call recognizer program to recognize logos
        # clear result first
        print '    clearing detection result'
        open("web/detected_result", "wb").close()
        open("web/detected_img.jpg", "wb").close()

        print '    start logo detection'
        os.system("./logo_detector web/photo_files/%s.jpg brands web/detected_result web/detected_img.jpg" % id)

        # 6) generate the index page
        indexFile = open("index.html", "wb")
        indexFile.write("<html><body><h1>This is for Logo Recognition.</h1>")
        resultFile = open("web/detected_result", "r")
        resultLogo = resultFile.read().strip("\n")
        resultFile.close()
        if len(resultLogo) > 0:

            indexFile.write("<h2>Detected Logo: <font color=red>%s</font></h2>" % resultLogo)

        indexFile.write("<table><tr>    <td>Last Photo Uploaded:</td><td></td><td>Detection Result:</td></tr><tr>    <td><img src=web/photo_files/%s.jpg width=450 height=600></img></td><td><img src=web/arrow.png></img></td><td>" % id)
        if len(resultLogo) > 0:
            indexFile.write("<img src=web/detected_img.jpg width=450 height=600></img>")

        indexFile.write("</td></tr></body></html>");
        indexFile.close()

        print '    Finished processing %s' % (latestId)
    else:
        print '    no new data to process'
    
    print 'sleep 5 seconds.'
    time.sleep(5)

