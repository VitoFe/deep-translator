"""
google translator API
"""

from deep_translator.constants import BASE_URLS, PAPAGO_LANGUAGE_TO_CODE
from deep_translator.exceptions import TooManyRequests, LanguageNotSupportedException, TranslationNotFound, NotValidPayload, RequestError
from deep_translator.parent import BaseTranslator
from bs4 import BeautifulSoup
import requests
from time import sleep
import warnings
import logging


class PapagoTranslator(object):
    """
    class that wraps functions, which use google translate under the hood to translate text(s)
    """
    _languages = PAPAGO_LANGUAGE_TO_CODE
    supported_languages = list(_languages.keys())

    def __init__(self, client_id, secret_key, source="auto", target="en"):
        """
        @param source: source language to translate from
        @param target: target language to translate to
        """
        self.__base_url = BASE_URLS.get("PAPAGO_API")
        self.client_id = client_id
        self.secret_key = secret_key
        if self.is_language_supported(source, target):
            self._source, self._target = self._map_language_to_code(source.lower(), target.lower())

    @staticmethod
    def get_supported_languages(as_dict=False):
        """
        return the supported languages by the google translator
        @param as_dict: if True, the languages will be returned as a dictionary mapping languages to their abbreviations
        @return: list or dict
        """
        return PapagoTranslator.supported_languages if not as_dict else PapagoTranslator._languages

    def _map_language_to_code(self, *languages):
        """
        map language to its corresponding code (abbreviation) if the language was passed by its full name by the user
        @param languages: list of languages
        @return: mapped value of the language or raise an exception if the language is not supported
        """
        for language in languages:
            if language in self._languages.values() or language == 'auto':
                yield language
            elif language in self._languages.keys():
                yield self._languages[language]
            else:
                raise LanguageNotSupportedException(language)

    def is_language_supported(self, *languages):
        """
        check if the language is supported by the translator
        @param languages: list of languages
        @return: bool or raise an Exception
        """
        for lang in languages:
            if lang != 'auto' and lang not in self._languages.keys():
                if lang != 'auto' and lang not in self._languages.values():
                    raise LanguageNotSupportedException(lang)
        return True

    def translate(self, text, **kwargs):
        """
        function that uses google translate to translate a text
        @param text: desired text to translate
        @return: str: translated text
        """

        if self._validate_payload(text):
            text = text.strip()

            if self.payload_key:
                self._url_params[self.payload_key] = text

            response = requests.get(self.__base_url,
                                    params=self._url_params,
                                    proxies=self.proxies)
            print("url: ", response.url)
            if response.status_code == 429:
                raise TooManyRequests()

            if response.status_code != 200:
                raise RequestError()

            soup = BeautifulSoup(response.text, 'html.parser')
            print("soup: ", soup)
            #exit()
            element = soup.find(self._element_tag, self._element_query)
            print("element: ", element)
            if not element:
                raise TranslationNotFound(text)
            else:
                return element.get_text(strip=True)

    def translate_file(self, path, **kwargs):
        """
        translate directly from file
        @param path: path to the target file
        @type path: str
        @param kwargs: additional args
        @return: str
        """
        try:
            with open(path) as f:
                text = f.read().strip()
            return self.translate(text)
        except Exception as e:
            raise e

    def translate_sentences(self, sentences=None, **kwargs):
        """
        translate many sentences together. This makes sense if you have sentences with different languages
        and you want to translate all to unified language. This is handy because it detects
        automatically the language of each sentence and then translate it.

        @param sentences: list of sentences to translate
        @return: list of all translated sentences
        """
        warnings.warn("deprecated. Use the translate_batch function instead", DeprecationWarning, stacklevel=2)
        logging.warning("deprecated. Use the translate_batch function instead")
        if not sentences:
            raise NotValidPayload(sentences)

        translated_sentences = []
        try:
            for sentence in sentences:
                translated = self.translate(text=sentence)
                translated_sentences.append(translated)

            return translated_sentences

        except Exception as e:
            raise e

    def translate_batch(self, batch=None):
        """
        translate a list of texts
        @param batch: list of texts you want to translate
        @return: list of translations
        """
        if not batch:
            raise Exception("Enter your text list that you want to translate")

        print("Please wait.. This may take a couple of seconds because deep_translator sleeps "
              "for two seconds after each request in order to not spam the google server.")
        arr = []
        for i, text in enumerate(batch):

            translated = self.translate(text)
            arr.append(translated)
            print("sentence number ", i+1, " has been translated successfully")
            sleep(2)

        return arr



if __name__ == '__main__':
    t = PapagoTranslator(source="en", target="de").translate("cute")
    print(t)

