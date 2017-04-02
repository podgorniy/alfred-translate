#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import json
import feedback
from multiprocessing import Pool
import re

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


def get_lang(text):
	"""Returns either 'ru' or 'en' corresponding for text"""
	if is_ascii(text):
		return 'en'
	else:
		return 'ru'


def convert_spelling_suggestions(spelling_suggestions):
	res = []
	if len(spelling_suggestions) != 0:
		for spelling_suggestion in spelling_suggestions:
			res.append({
				'title': spelling_suggestion,
				'autocomplete': spelling_suggestion
			})
	return res



def get_spelling_suggestions(spelling_suggestions):
	"""Returns spelling suggestions from JSON if any """
	res = []
	if spelling_suggestions and spelling_suggestions[0] and spelling_suggestions[0]['s']:
		res = spelling_suggestions[0]['s']
	return res



def get_translation_suggestions(input_string, spelling_suggestions, translation_suggestions, vocabulary_article):
	"""Returns XML with translate suggestions"""
	res = []
	if len(spelling_suggestions) == 0 and len(translation_suggestions) == 0:
		return res

	if len(vocabulary_article['def']) != 0:
		for article in vocabulary_article['def']:
			for translation in article['tr']:
				if 'ts' in article.keys():
					subtitle = article['ts']
				elif 'ts' in translation.keys():
					subtitle = translation['ts']
				else:
					subtitle = ''
				res.append({
					'translation': translation['text'],
					'transcription': subtitle,
				})
	if len(res) == 0:
		if translation_suggestions and len(translation_suggestions['text']) != 0:
			for translation in translation_suggestions['text']:
				if translation != input_string.decode('utf-8'):
					res.append({
						'translation': translation.replace('\\ ', ' '), # otherwise prints slash before spaces
						'transcription': ''
					})
	return res



def process_response_as_json(request_url):
	"""Accepts request url returns response as """
	request = urllib2.urlopen(request_url)
	response_json = json.loads(request.read())
	return response_json



def get_output(input_string):
	"""Main entry point"""
	pool = Pool(processes=3)
	fb = feedback.Feedback()
	input_string = input_string.strip()
	if not input_string:
		fb.add_item(title="Translation not found", valid="no")
		return fb

	# Building urls
	translationDirection = get_translation_direction(input_string)

	# Build spell check url
	spellCheckParams = {
		'text': input_string,
		'lang': get_lang(input_string)
	}
	spellCheckUrl = 'https://speller.yandex.net/services/spellservice.json/checkText' + '?' + urllib.urlencode(spellCheckParams)

	# Build article url
	articleParams = {
		'key': dict_api_key,
		'lang': translationDirection,
		'text': input_string,
		'flags': 4
	}
	articleUrl = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup' + '?' + urllib.urlencode(articleParams)

	# Build translation url
	translationParams = {
		'key': translate_api_key,
		'lang': translationDirection,
		'text': input_string
	}
	translationUrl = 'https://translate.yandex.net/api/v1.5/tr.json/translate' + '?' + urllib.urlencode(translationParams)

	# Making requests in parallel
	requestsUrls = [spellCheckUrl, translationUrl, articleUrl]
	responses = pool.map(process_response_as_json, requestsUrls)

	spelling_suggestions_items = get_spelling_suggestions(responses[0])
	# Generate possible xml outputs
	formatted_spelling_suggestions = convert_spelling_suggestions(spelling_suggestions_items)
	formated_translation_suggestions = get_translation_suggestions(input_string, spelling_suggestions_items, responses[1], responses[2])
	words_in_phase = len(re.split(' ', input_string.decode('utf-8')))

	# Output
	if len(formatted_spelling_suggestions) == 0 and len(formated_translation_suggestions) == 0:
		fb.add_item(title="Translation not found", valid="no")
		return fb

	# Prepare suggestions output
	# Spellcheck error
	if words_in_phase <= 2 and len(formatted_spelling_suggestions) != 0:
		for spelling_suggestion in formatted_spelling_suggestions:
			fb.add_item(title=spelling_suggestion['title'],
				autocomplete=spelling_suggestion['autocomplete'],
				icon='spellcheck.png')

	# Translations output
	for formatted_translated_suggestion in formated_translation_suggestions:
		fb.add_item(title=formatted_translated_suggestion['translation'], arg=formatted_translated_suggestion['translation'], subtitle=formatted_translated_suggestion['transcription'])
	return fb
