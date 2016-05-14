#!/usr/bin/env python3
#
# Telegram bot to play UNO in group chats
# Copyright (c) 2016 Jannes Höke <uno@jhoeke.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import logging
from datetime import datetime
from credentials import WAIT_TIME

import card as c


class Player(object):
    """
    This class represents a player.
    It is basically a doubly-linked ring list with the option to reverse the
    direction. On initialization, it will connect itself to a game and its
    other players by placing itself behind the current player.
    """

    def __init__(self, game, user):
        self.cards = list()
        self.game = game
        self.user = user
        self.logger = logging.getLogger(__name__)

        # Check if this player is the first player in this game.
        if game.current_player:
            self.next = game.current_player
            self.prev = game.current_player.prev
            game.current_player.prev.next = self
            game.current_player.prev = self
        else:
            self._next = self
            self._prev = self
            game.current_player = self

        for i in range(7):
            self.cards.append(self.game.deck.draw())

        self.bluffing = False
        self.drew = False
        self.anti_cheat = 0
        self.turn_started = datetime.now()
        self.waiting_time = WAIT_TIME
        self.uno = False
        self.unoDrawn = False

    def leave(self):
        """ Leave the current game """
        if self.next is self:
            return

        self.next.prev = self.prev
        self.prev.next = self.next
        self.next = None
        self.prev = None

        for card in self.cards:
            self.game.deck.dismiss(card)

        self.cards = list()

    def __repr__(self):
        return repr(self.user)

    def __str__(self):
        return str(self.user)

    @property
    def next(self):
        return self._next if not self.game.reversed else self._prev

    @next.setter
    def next(self, player):
        if not self.game.reversed:
            self._next = player
        else:
            self._prev = player

    @property
    def prev(self):
        return self._prev if not self.game.reversed else self._next

    @prev.setter
    def prev(self, player):
        if not self.game.reversed:
            self._prev = player
        else:
            self._next = player

    def playable_cards(self):
        """ Returns a list of the cards this player can play right now """

        playable = list()
        last = self.game.last_card

        self.logger.debug("Last card was " + str(last))

        cards = self.cards
        if self.drew:
            cards = self.cards[-1:]

        # You may only play a +4 if you have no cards to play
        self.bluffing = False
        for card in cards:
            if self.card_playable(card, playable):
                self.logger.debug("Matching!")
                playable.append(card)
        
               
        if not self.drew: #Se comeu, o valor do blefe é mantido.
        	self.bluffing = False;
	        for card in playable:
	        	if(card.special != c.DRAW_FOUR):
	        		self.bluffing = True
                        
        #self.bluffing = len(playable) > 0
        # You may not play a chooser or +4 as your last card
        #if len(self.cards) == 1 and self.cards[0].special:
        #    return list()

        return playable

    def card_playable(self, card, playable):
        """ Check a single card if it can be played """

        is_playable = True
        last = self.game.last_card
        self.logger.debug("Checking card " + str(card))

        if (card.color != last.color and card.value != last.value and
                not card.special):
            self.logger.debug("Card's color or value doesn't match")
            is_playable = False
        elif last.value == c.DRAW_TWO and self.game.draw_counter:
        	if(card.value != c.DRAW_TWO and card.special != c.DRAW_FOUR):
        		is_playable = False
        	if(self.game.fouyer and card.special == c.DRAW_FOUR):
        		is_playable = False
        elif last.special == c.DRAW_FOUR and self.game.draw_counter:
        	is_playable = ((card.value == c.DRAW_TWO and card.color == last.color) or card.special == c.DRAW_FOUR)
#         
#         
#         
#         
#          and not \
#                 card.value == c.DRAW_TWO and self.game.draw_counter:
#             self.logger.debug("Player has to draw and can't counter")
#             is_playable = False
#         elif last.special == c.DRAW_FOUR and not card.value == c.DRAW_TWO and self.game.draw_counter:
#             self.logger.debug("Player has to draw and can't counter")
#             is_playable = False
        #elif (last.special == c.CHOOSE or last.special == c.DRAW_FOUR) and \
        #        (card.special == c.CHOOSE or card.special == c.DRAW_FOUR):
        #    self.logger.debug("Can't play colorchooser on another one")
        #    is_playable = False
        elif not last.color or card in playable:
            self.logger.debug("Last card has no color or the card was "
                              "already added to the list")
            is_playable = False

        return is_playable
