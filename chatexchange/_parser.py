"""
Classes for parsing different HTML pages into structured data.

This performs minimal interpretation, leaving that to the user.
"""

import re
from html import escape as escape_html

from lxml.etree import ElementBase
import lxml.html
from lxml.html import html5parser

from . import _obj_dict



def _dom_outer_html(dom):
    return lxml.html.tostring(dom, encoding=str, with_tail=False)


def _dom_inner_html(dom):
    return escape_html(dom.text, False) + ''.join(
        lxml.html.tostring(child_dom, encoding=str, with_tail=True)
        for child_dom in dom.iterchildren())


def _dom_text_content(dom):
    return lxml.html.tostring(dom, encoding=str, method='text')


class _ParsedDOM(object):
    """
    Base class for a parsed document/document fragment.
    """

    # Namespaced HTML elements seem to be incompatible with .cssselect().
    _parser = html5parser.HTMLParser(namespaceHTMLElements=False)

    def __init__(self, dom):
        if isinstance(dom, ElementBase):
            self._dom = dom
        else:
            assert isinstance(dom, str)
            html = str(dom)
            self.url = None
    
            # lxml only allows characters that are valid in XML, but the web is dark and full of terrors.
            # see https://stackoverflow.com/a/25920392/1114
            # via https://github.com/django-haystack/pysolr/pull/88/files
            sanitized_html = re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]', '�', html)
            self._dom = self._parser.parse(sanitized_html).getroot()

    @staticmethod
    def _user_id_and_name_from_link(link_el):
        user_name = link_el.text
        user_id = int(link_el.get('href').split('/')[2])
        return user_id, user_name
    
    __repr__ = _obj_dict.repr
        


class TranscriptPage(_ParsedDOM):
    class Message(object):
        def __init__(self, **attrs):
            self.id = None
            self.content_html = None
            self.content_text = None
            self.room_id = None
            self.owner_user_id = None
            self.owner_user_name = None
            self.edited = None
            self.parent_message_id = None

            _obj_dict.update(self, **attrs)

        __repr__ = _obj_dict.repr

    def __init__(self, page):
        super().__init__(page)

        room_name_link ,= self._dom.cssselect('.room-name a')
        self.room_id = int(room_name_link.get('href').split('/')[2])
        self.room_name = room_name_link.text

        self.first_day_url = None
        self.previous_day_url = None
        self.next_day_url = None
        self.last_day_url = None
        self.messages = []

        for other_day_el in self._dom.cssselect('#main > a[href^="/transcript"]'):
            if 'first day' in other_day_el.text:
                self.first_day_url = other_day_el.get('href')
            elif 'previous day' in other_day_el.text:
                self.previous_day_url = other_day_el.get('href')
            elif 'next day' in other_day_el.text:
                self.next_day_url = other_day_el.get('href')
            elif 'last day' in other_day_el.text:
                self.last_day_url = other_day_el.get('href')

        for monologue_el in self._dom.cssselect('.monologue'):
            user_link ,= monologue_el.cssselect('.signature .username a')
            user_id, user_name = self._user_id_and_name_from_link(user_link)

            for message_el in monologue_el.cssselect('.message'):
                message = TranscriptPage.Message()

                message.owner_user_id = user_id
                message.owner_user_name = user_name
                message.id = int(message_el.get('id').split('-')[1])
                message.edited = bool(message_el.cssselect('.edits'))
                content_el ,= message_el.cssselect('.content')
                message.content_html = _dom_inner_html(content_el).strip()
                message.content_text = _dom_text_content(content_el).strip()

                reply_info_els = message_el.cssselect('.reply-info')
                if reply_info_els:
                    reply_info_el ,= reply_info_els
                    message.parent_message_id = int(
                        reply_info_el.get('href').partition('#')[2])
                else:
                    message.parent_message_id = None

                self.messages.append(message)

    __repr__ = _obj_dict.repr
