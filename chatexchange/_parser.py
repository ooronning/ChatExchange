"""
Classes for parsing different HTML pages into structured data.
"""

import datetime
import logging
import re
from html import escape as escape_html

from lxml.etree import ElementBase
import lxml.html
from lxml.html import html5parser

from . import _obj_dict



logger = logging.getLogger(__name__)


def _dom_outer_html(dom):
    return lxml.html.tostring(dom, encoding=str, with_tail=False)


def _dom_inner_html(dom):
    return escape_html(dom.text, False) + ''.join(
        lxml.html.tostring(child_dom, encoding=str, with_tail=True)
        for child_dom in dom.iterchildren())


def _dom_text_content(dom):
    return lxml.html.tostring(dom, encoding=str, method='text')


class _ParsedDOM:
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
            logger.debug("Parsing HTML to DOM...")
            html = str(dom)
    
            # lxml only allows characters that are valid in XML, but the web is dark and full of terrors.
            # see https://stackoverflow.com/a/25920392/1114
            # via https://github.com/django-haystack/pysolr/pull/88/files
            html = html[int(len(html) * 0.5):int(len(html) * 0.51)]
            print(repr(html))
            sanitized_html = re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+', '�', html)
            self._dom = self._parser.parse(sanitized_html).getroot()
    
    __repr__ = _obj_dict.repr
        


class TranscriptPage(_ParsedDOM):
    class Message:
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

        room_name_link ,= self._dom.cssselect('#info .room-name a')
        self.room_id = int(room_name_link.get('href').split('/')[2])
        self.room_name = room_name_link.text

        logger.debug("Interpreting transcript DOM for room %s %s.", self.room_id, self.room_name)

        self.first_day = None
        self.previous_day = None
        self.next_day = None
        self.last_day = None

        self.first_day_url = None
        self.previous_day_url = None
        self.next_day_url = None
        self.last_day_url = None

        def date_from_url(url):
            _, _, _, y, m, d, *_ = url.split('/')
            return datetime.date(year=int(y), month=int(m), day=int(d))

        for other_day_el in self._dom.cssselect('#main > a[href^="/transcript"]'):
            if 'first day' in other_day_el.text:
                self.first_day_url = other_day_el.get('href')
                self.first_day = date_from_url(self.first_day_url)
            elif 'previous day' in other_day_el.text:
                self.previous_day_url = other_day_el.get('href')
                self.previous_day = date_from_url(self.previous_day_url)
            elif 'next day' in other_day_el.text:
                self.next_day_url = other_day_el.get('href')
                self.next_day = date_from_url(self.next_day_url)
            elif 'last day' in other_day_el.text:
                self.last_day_url = other_day_el.get('href')
                self.last_day = date_from_url(self.last_day_url)

        self.messages = []

        for monologue_el in self._dom.cssselect('.monologue'):
            user_signature ,= monologue_el.cssselect('.signature .username')
            user_name = _dom_text_content(user_signature).strip()
            
            user_links = user_signature.cssselect('a')    
            if user_links:
                user_link ,= user_links
                user_id = int(user_link.get('href').split('/')[2])
            else:
                user_id = None

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
