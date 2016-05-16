#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from api import ConcentrationGameApi
from models import User, GameP1, GameP2


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send daily reminder email to each User with active games. Email
        includes the urlsafe_game_key. Called every day using a cron job"""
        app_id = app_identity.get_application_id()

        gamesp1 = GameP1.query(GameP1.game_over != True)
        gamesp2 = GameP2.query(GameP2.game_over != True)

        for game in gamesp1:
            user = User.query(
                ndb.AND(User.key == game.user, User.email != None)).get()
            subject = 'Concentration game reminder'
            body = ('Hello {}, you have a active single player game of '
                    'Concentration. The game key is: {}'.format(user.name,
                                                                game.key))
            # This will send test emails, the arguments to send_mail are:
            # from, to, subject, body
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)

        for game in gamesp2:
            # notify user1
            user = User.query(
                ndb.AND(User.key == game.user1, User.email != None)).get()
            subject = 'Concentration game reminder'
            body = ('Hello {}, you have a active single player game of '
                    'Concentration. The game key is: {}'.format(user.name,
                                                                game.key))
            # This will send test emails, the arguments to send_mail are:
            # from, to, subject, body
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)
            # notify user2
            user = User.query(
                ndb.AND(User.key == game.user2, User.email != None)).get()
            subject = 'Concentration game reminder'
            body = ('Hello {}, you have a active single player game of '
                    'Concentration. The game key is: {}'.format(user.name,
                                                                game.key))
            # This will send test emails, the arguments to send_mail are:
            # from, to, subject, body
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)

app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail)
], debug=True)
