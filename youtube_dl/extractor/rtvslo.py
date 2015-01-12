from __future__ import unicode_literals

from datetime import date

from .common import InfoExtractor


class RTVSloIE(InfoExtractor):
    _VALID_URL = r'http://4d\.rtvslo\.si/arhiv/.+?/(?P<id>[0-9]+)'
    _TEST = {
        'url': 'http://4d.rtvslo.si/arhiv/zrcalo-tedna/174313788',
        'info_dict': {
            'id': '174313788',
            'ext': 'flv',
            'title': u'Zrcalo tedna'
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        # Retrieve .smil XML file. SMIL URL includes date, which unfortunately
        # I am not able to determine. The current solution is to check
        # every date from today backwards.
        today = date.today()
        year  = today.year
        month = today.month
        day   = today.day
        smil_url = None
        MAX_DAYS_BACK = 100
        while True:
            BASE_SMIL_URL = 'http://ios.rtvslo.si/simplevideostreaming42/_definst_/'
            smil_url = BASE_SMIL_URL + '{year}/{month:0>2}/{day:0>2}/{video_id}.smil/jwplayer.smil'.format(
                    year=year, month=month, day=day, video_id=video_id)
            smil_xml = self._download_webpage(smil_url, video_id)
            if len(smil_xml) > 144:
                # SMIL XML content is larger than the empty-SMIL XML content.
                # Assuming that this url is therefore the correct one.
                break
            # Default empty-SMIL XML was received. Go back a day.
            MAX_DAYS_BACK -= 1
            if MAX_DAYS_BACK == 0:
                print('Unable to find SMIL URL!')
                break
            day -= 1
            if day == 0:
                month -= 1
                day = 31
            if month == 0:
                month = 12
                year -= 1

        formats = self._extract_smil_formats(smil_url, video_id)
        video_thumbnail = self._og_search_thumbnail(webpage)
        video_title = self._og_search_title(webpage)
        return {
            'id': video_id,
            'title': video_title,
            'thumbnail': video_thumbnail,
            'formats': formats,
            'rtmp_live': True  # if rtmpdump is not called with "--live" argument, the download is blocked and cannnot be completed.
        }
