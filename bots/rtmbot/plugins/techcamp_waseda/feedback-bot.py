#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from rtmbot.core import Plugin
import random
import re

class FeedbackBot(Plugin):
  LIMIT = 3
  MEMBER_LIST = [
    'jiosotoyama',
    'yuta-takahashi',
    'ueda-yukihiro',
    'ryo-umeki',
    'satsuki-kajiya',
    'keisuke.awa',
    'sawa-uchida',
    'makiko-shimizu'
    ]

  def process_message(self, data):
    feedback_pattern = re.compile(r'.*<@U3GAKNMHQ.*(feedback).*', re.DOTALL|re.IGNORECASE)
    if not ( re.match( feedback_pattern, data['text'] ) ):
      return

    self.outputs.append(
      [data['channel'], u'今回のフィードバックメンバーはこちら！より良い教室を作るため、フィードバックにご協力ください。 :bow:']
    )

    i = 0
    random.shuffle(self.MEMBER_LIST)
    for member in self.MEMBER_LIST:
      if i >= self.LIMIT:
        break
        self.outputs.append(
          [data['channel'], u'<@{}>'.format(
            member
          )]
        )
      i += 1

    print('Done FeedbackBot')
    
