#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from rtmbot.core import Plugin
import random
import re
import time
import datetime

class LunchBot(Plugin):
  # dict of user_id:user_name
  user_dir = {}

  # channel ids
  CHANNEL_GET_USERS = "C194GMNP4"
  CHANNEL_POST = ""
  # channel history count
  HISTORY_COUNT = 15

  def process_message(self, data):
    feedback_pattern = re.compile(r'.*<@U3GAKNMHQ.*(lunch).*', re.DOTALL|re.IGNORECASE)
    if not ( re.match( feedback_pattern, data['text'] ) ):
      return

    self.CHANNEL_POST = data['channel']
    self.post_shuffle_message()
    self.generate_user_directory()
    self.shuffle_lunch()
    self.dlog('Done LunchBot')

  def shuffle_lunch(self):
    # get today's date
    today_date = datetime.date.today()
    ts = time.mktime(today_date.timetuple())

    response = self.slack_client.api_call("channels.history", 
      channel=self.CHANNEL_GET_USERS, 
      count=self.HISTORY_COUNT,
      oldest=ts)

    lunch_volunteers = []
    for message in response["messages"]:
      if (u"今日ランチ決まっていない" in message["text"] 
      and u"set up" not in message["text"]):
        lunch_volunteers = message["reactions"][0]["users"]
        self.dlog(message)

    lunch_groups = self.split_equally(lunch_volunteers)
    self.dlog(lunch_groups)
    self.post_lunch_groups(lunch_groups)


  def post_lunch_groups(self, lunch_groups):
    if len(lunch_groups) < 1:
      sorry_message = u"誰もいねぇ :obama:"
      response = self.slack_client.api_call("chat.postMessage", 
        channel=self.CHANNEL_POST, 
        text=sorry_message, 
        link_names=1,
        as_user=True)
      return

    message = u" mix結果はこちら！各グループで楽しいlunchを:cat::two_hearts: \n "
    group_num = 1
    for group in lunch_groups:
      message += "%s. \n" % group_num
      for user_id in group:
        message += "@%s " % self.user_dir[user_id]
      message += "\n"
      group_num += 1
    self.dlog(message)
    response = self.slack_client.api_call("chat.postMessage", 
      channel=self.CHANNEL_POST, 
      text=message, 
      link_names=1,
      as_user=True)

  def post_shuffle_message(self):
    message = u"締切時間だよ:clock11:mixするのでちょっと待ってね…:dancers:"
    response = self.slack_client.api_call("chat.postMessage", 
      channel=self.CHANNEL_POST, 
      text=message, 
      link_names=1,
      as_user=True)

  def split_equally(self, l):
    arrs = []
    if len(l) < 1: return arrs

  # equation to find number of equal splits
    number_of_splits = (len(l) - 1) / 4 + 1
    for i in range(0, number_of_splits): arrs.append([])

  # populate splits equally
  # use mod to randomize
    for i, elm in enumerate(l):
      arrs[i % len(arrs)].append(elm)
    return arrs


  def generate_user_directory(self):
    response = self.slack_client.api_call("users.list")
    for user in response["members"]:
      self.user_dir[user["id"]] = user["name"]

  def dlog(self, str):
  # print(str)
    return
