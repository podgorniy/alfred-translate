#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import json
import feedback

dict_api_key = 'dict.1.1.20140108T003739Z.52c324b8a4eea3ac.5767100e8cc7b997dad88353e47aa4857e786beb'
translate_api_key = 'trnsl.1.1.20130512T104455Z.8a0ed400b0d249ba.48af47e72f40c8991e4185556b825273d104af68'

def is_ascii(s):
	"""http://stackoverflow.com/questions/196345/how-to-check-if-a-string-in-python-is-in-ascii"""
	return all(ord(c) < 128 for c in s)


def get_translation_direction(text):
	"""Returns direction of translation. en-ru or ru-en"""
	if is_ascii(text):
		return 'en-ru'
	else:
		return 'ru-en'


def is_word(text):
	"""Determines word as string without spaces inside"""
	return not ' ' in text.strip()


def get_vocabulary_article(word):
	"""Returns response from vocabulary API"""
	params = {
		'key': dict_api_key,
		'lang': get_translation_direction(word),
		'text': word,
		'flags': 4
	}
	request = urllib2.urlopen('https://dictionary.yandex.net/api/v1/dicservice.json/lookup', urllib.urlencode(params))
	response_json = json.loads(request.read())
	return response_json


def get_translation(text):
	params = {
		'key': translate_api_key,
		'lang': get_translation_direction(text),
		'text': text
	}
	request = urllib2.urlopen('https://translate.yandex.net/api/v1.5/tr.json/translate', urllib.urlencode(params))
	response_json = json.loads(request.read())
	return response_json


def translate_suggestions(text):
	fb = feedback.Feedback()
	if is_word(text):
		vocabulary_articles = get_vocabulary_article(text)
		for article in vocabulary_articles['def']:
			for translation in article['tr']:
				fb.add_item(title=translation['text'], arg=translation['text'], subtitle=translation['pos'])
	else:
		translation_variants = get_translation(text)
		for translation in translation_variants['text']:
			fb.add_item(title=translation, arg=translation)
	return fb
