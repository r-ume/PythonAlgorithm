#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# rtmbot関連
# これを最初に書かないとエラーが出てしまう。
from __future__ import print_function
from __future__ import unicode_literals
from rtmbot.core import Plugin

# 標準ライブラリ
# 乱数ライブラリ
import random
# 正規表現操作
import re
# OSファイルアクセスのため
import os
# 時間
from datetime import datetime, timedelta
# ファイル操作
import io
import urllib2
# ウェブブラウザコントローラー
import webbrowser
# スクレイピング
from xml.etree import ElementTree

# オープンソースライブラリ
# Google Data Client
import gdata.photos.service
import gdata.media
import gdata.geo
# Google OAuth認証
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
# Slack Client認証
from slackclient import SlackClient
# リクエスト関係
import requests
# 画像サイズ変更
from PIL import Image
# Httpリクエストライブラリ
import httplib2


class MediaType (object):
    PHOTO = 0
    MOVIE = 1


class PhotoGalleryBot (Plugin):
    MEDIA_ARR = []
    RANDOM_NUMBER = 0
    EMAIL = os.version['EMAIL']
    CHANNEL_POST = ''
    SLACK_BOT_TOKEN = os.version['SLACK_BOT_TOKEN']

    PLUGIN_CHILD_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
    PLUGIN_DIRECTORY = os.path.abspath(
        os.path.join(PLUGIN_CHILD_DIRECTORY, os.pardir)
    )
    RTMBOT_DIRECTORY = os.path.abspath(
        os.path.join(PLUGIN_DIRECTORY, os.pardir)
    )
    CLIENT_SECRETS = os.path.join(RTMBOT_DIRECTORY, os.version['SECRET_JSON'])
    CREDENTIAL_STORE = os.path.join(
        RTMBOT_DIRECTORY, os.version['CREDENTIAL_DAT']
    )

    def process_message(self, data):
        """ This is where all custom methods start. It is a main function in JAVA.

        Args:
            data: Data from Slack.
        """
        feedback_pattern = re.compile(
            r'.*<@U3GAKNMHQ.*(Gallery).*', re.DOTALL | re.IGNORECASE
        )

        if not (re.match(feedback_pattern, data['text'])):
            return

        self.CHANNEL_POST = data['channel']

        # 1
        self.download_notification()
        # 2
        self.fetch_all_media()
        # 3
        self.choose_todays_media()
        # 4
        self.post_notification()
        # 5
        self.post_random_media()
        # 6
        self.post_time_media_taken()
        # 7
        self.delete_random_media()

    # 1 -----
    def download_notification(self):
        """Posts a message that makes a notification of downloading a media onto slack
        """
        message = u"本日の画像/映像をダウンロードしています！少しお待ち下さい！ "
        message += "動画の場合は、ダウンロードに時間がかかる場合があります。"
        response = self.slack_client.api_call(
            "chat.postMessage",
            channel=self.CHANNEL_POST,
            text=message,
            link_names=1,
            as_user=True
        )

    # 2 ------
    def oauth_login(self, client_secrets, credential_store, email):
        """Google OAuth2 Authetication
        Reference URL:
            http://se-u-ske.blogspot.jp/2016/02/pythongoogle-photo.html

        Args:
            client_secret(json file): A json file that has info on client
            credential_store(json file): A json file that puts credential.
            email (str): A google account that you retrieve medias from.

        Returns:
            gd_client(PhotoService): User info when using google data service.

        """
        scope = 'https://picasaweb.google.com/data/'
        user_agent = 'picasawebuploader'
        storage = Storage(credential_store)
        credentials = storage.get()
        now_time = datetime.utcnow()

        if credentials is None or credentials.invalid:
            flow = flow_from_clientsecrets(
                client_secrets,
                scope=scope,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )
            uri = flow.step1_get_authorize_url()
            webbrowser.open(uri)
            code = raw_input('Enter the authentication code: ').strip()
            credentials = flow.step2_exchange(code)
            storage.put(credentials)

        if (credentials.token_expiry - now_time) < timedelta(minutes=5):
            http = httplib2.Http()
            http = credentials.authorize(http)
            credentials.refresh(http)

        gd_client = gdata.photos.service.PhotosService(
            source=user_agent,
            email=email,
            additional_headers={
                'Authorization': 'Bearer %s' % credentials.access_token
            }
        )

        return gd_client

    def get_random_number_in_array(self, arr):
        """Get the length of the list and decide a random number from 0 and the length.
        Args:
            arr(list): A list that you get a random number from it.

        Returns:
            A number randomed chosen within the range of 0 and the list length.
        """
        max_length = len(arr)
        return random.randint(0, max_length)

    def fetch_all_media(self):
        """ Fetch all media from the email and put it into MEDIA_ARR
        """
        gd_client = self.oauth_login(
            self.CLIENT_SECRETS,
            self.CREDENTIAL_STORE,
            self.EMAIL
        )

        albums = gd_client.GetUserFeed()
        for album in albums.entry:
            medias = gd_client.GetFeed(
                '/data/feed/api/user/default/albumid/%s' %
                (album.gphoto_id.text)
            )
            for media in medias.entry:
                self.MEDIA_ARR.append(media)

    # 3 ------
    def get_kind_of_media(self, media_object):
        """ Telling the type of the media from media_object
        Args:
            media_object: PhotoEntry Object randomly retrieved from MEDIA_ARR

        Returns:
            MOVIE or PHOTO in enum
        """
        media_title = media_object.title.text

        if media_title.upper().endswith('.MOV'):
            return MediaType.MOVIE
        else:
            return MediaType.PHOTO

    def download_photo(self, media_object):
        """ Downloading the photo type media.

        Args:
            media_object: PhotoEntry Object randomly retrieved from MEDIA_ARR
        """
        media_title = media_object.title.text
        f = open(media_title, 'wb')
        f.write(urllib2.urlopen(media_object.content.src).read())
        f.close()

    def download_movie(self, media_object):
        """ Downloading the photo type media.

        Args:
            media_object(PhotoEntry): PhotoEntry randomly chosen from MEDIA_ARR

        Cautions:
            Get the source url that DOES NOT HAVE .MOV IN IT below.
        """
        xmlstr = str(media_object)
        root = ElementTree.fromstring(xmlstr)
        media_url_tag_key = '{http://search.yahoo.com/mrss/}content'

        for group_elems in root:
            for elem in group_elems:
                tag = elem.tag
                if tag == media_url_tag_key:
                    url = elem.attrib['url']

                    if not url.upper().endswith('.MOV'):
                        response = requests.get(url)
                        media_file = open(media_object.title.text, 'wb')
                        media_file.write(response.content)
                        media_file.close()

    def cr2_to_jpg(self, photo_title, img_object):
        """Convert CR2 extension to jpg

        Args:
            photo_title(str): the title of photo that you convert.
            img_object(PhotoEntry): cr2 img PhotoEntry object.

        Returns:
            photo_title(str): the title of the photo that has 'jpeg' extension.
            img_object(PhotoEntry): PhotoEntry whose title has been updated
        """
        photo_title = photo_title.replace('.CR2', '.jpg')
        img_object.save(photo_title)

        return photo_title, img_object

    def resize_photo(self, media_object):
        """Change the size of photo

        Args:
            media_object(PhotoEntry): The size of the photo that you change
        """
        photo_title = self.RTMBOT_DIRECTORY + "/" + media_object.title.text
        img_object = Image.open(photo_title)

        if photo_title.endswith('.CR2'):
            photo_title, img_object = self.cr2_to_jpg(photo_title, img_object)

        resize_rate = 1.7
        (current_photo_width, current_photo_height) = img_object.size
        resized_width = int(current_photo_width * resize_rate)
        resized_height = int(current_photo_height * resize_rate)
        resize_size = (resized_width, resized_height)

        img_resized = img_object.resize(resize_size)
        img_resized.save(photo_title)

    def choose_todays_media(self):
        """Randomly picking up a media in MEDIA_ARR and download it.
        """
        self.RANDOM_NUMBER = self.get_random_number_in_array(self.MEDIA_ARR)
        media_object = self.MEDIA_ARR[self.RANDOM_NUMBER]

        if self.get_kind_of_media(media_object) == MediaType.PHOTO:
            self.download_photo(media_object)
            self.resize_photo(media_object)
        elif self.get_kind_of_media(media_object) == MediaType.MOVIE:
            self.download_movie(media_object)

    # 4 -----
    def post_notification(self):
        """ Makes a notification message before posting the media onto Slack.
        Depending the media, the content of the message gets changed.
        """
        media_object = self.MEDIA_ARR[self.RANDOM_NUMBER]

        if self.get_kind_of_media(media_object) == MediaType.PHOTO:
            message = u"写真をアップロードします！今日の写真はこちら！"
        elif self.get_kind_of_media(media_object) == MediaType.MOVIE:
            message = u"動画をアップロードします！今日の動画はこちら！"

        response = self.slack_client.api_call(
            "chat.postMessage",
            channel=self.CHANNEL_POST,
            text=message,
            link_names=1,
            as_user=True
        )

    # 5 -----
    def post_random_media(self):
        """Post the random media already downloaded in the server onto Slack.
        Depending on the media, the title of message get changed.
        """
        media_object = self.MEDIA_ARR[self.RANDOM_NUMBER]
        media_path = self.RTMBOT_DIRECTORY + "/" + media_object.title.text

        if media_path.endswith('.CR2'):
            media_path = media_path.replace('.CR2', '.jpg')

        if self.get_kind_of_media(media_object) == MediaType.PHOTO:
            media = u"PHOTO!"
        elif self.get_kind_of_media(media_object) == MediaType.MOVIE:
            media = u"MOVIE！"

        with open(media_path, 'rb') as f:
            param = {
                'token': self.SLACK_BOT_TOKEN,
                'channels': self.CHANNEL_POST,
                'title': u'Today\'s ' + media
            }
            r = requests.post(
                "https://slack.com/api/files.upload",
                params=param,
                files={'file': f}
            )

    # 6 ------
    def post_time_media_taken(self):
        """Posting a time when the media was taken.
        """
        media_object = self.MEDIA_ARR[self.RANDOM_NUMBER]
        time_media_taken = str(
            datetime.fromtimestamp(int(media_object.timestamp.text)/1000)
        )
        post_message = "撮影日時はこちら！" + time_media_taken

        response = self.slack_client.api_call(
            "chat.postMessage",
            channel=self.CHANNEL_POST,
            text=post_message,
            link_names=1,
            as_user=True
        )

    # 7 ------
    def delete_random_media(self):
        """ Deleting a media file in the server.
        """
        media_object = self.MEDIA_ARR[self.RANDOM_NUMBER]
        media_path = self.RTMBOT_DIRECTORY + "/" + media_object.title.text
        os.remove(media_path)

        cr2_photo_path = media_path.replace('.CR2', '.jpg')
        if cr2_photo_path:
            os.remove(cr2_photo_path)
