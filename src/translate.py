#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import json
import feedback

api_key = 'dict.1.1.20140108T003739Z.52c324b8a4eea3ac.5767100e8cc7b997dad88353e47aa4857e786beb'

def is_ascii(s):
	"""http://stackoverflow.com/questions/196345/how-to-check-if-a-string-in-python-is-in-ascii"""
	return all(ord(c) < 128 for c in s)


def get_translation_direction(text):
	"""Returns direction of translation. en-ru or ru-en"""
	if is_ascii(text):
		return 'en-ru'
	else:
		return 'ru-en'


def translate(text):
	params = {
		'key': api_key,
		'lang': get_translation_direction(text),
		'text': text,
		'flags': 4
	}
	request = urllib2.urlopen('https://dictionary.yandex.net/api/v1/dicservice.json/lookup', urllib.urlencode(params))
	response_json = json.loads(request.read())
	return response_json['def']


def translate_suggestions(text):
	fb = feedback.Feedback()
	translation_variants = translate(text)
	for variant in translation_variants:
		for translation in variant['tr']:
			fb.add_item(title=translation['text'], arg=translation['text'])
	return fb