from lxml.html import html5parser, tostring as dom_to_html

import re


class _ParsedPage(object):
    _parser = html5parser.HTMLParser(namespaceHTMLElements=False)

    def __init__(self, html):
        # Strip unicode characters that are invalid in XML (which lxml does not support).
        # see https://stackoverflow.com/a/25920392/1114
        # via https://github.com/django-haystack/pysolr/pull/88/files
        sanitized_html = re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+', '', html)
        self._dom = self._parser.parse(sanitized_html).getroot()
        # for JavaScripties:
        # .cssselect() === .querySelectorAll()
        # .get() == .getAttribute()


class TranscriptPage(_ParsedPage):
    def __str__(self):
        return "<TranscriptPage %x of %s %r>" % (id(self), self.room_id, self.room_name)

    def __init__(self, html):
        super().__init__(html)

        room_name_link ,= self._dom.cssselect('.room-name a')
        self.room_id = int(room_name_link.get('href').split('/')[2])
        self.room_name = room_name_link.text
