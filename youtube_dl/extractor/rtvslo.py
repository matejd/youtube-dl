from __future__ import unicode_literals

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
        api_client_id = '82013fb3a531d5414f478747c1aca622'  # TODO: Expires?
        response_json = self._download_json(
            'http://api.rtvslo.si/ava/getRecording/{0}?client_id={1}'.format(video_id, api_client_id),
            video_id)

        formats = []
        if 'addaptiveMedia' in response_json['response']:
            smil_url = response_json['response']['addaptiveMedia']['jwplayer']
            formats = self._extract_smil_formats(smil_url, video_id)
        else:
            # Handle some special case, e.g. http://4d.rtvslo.si/arhiv/tv-izobrazevalni/174313767
            for mediaFile in response_json['response']['mediaFiles']:
                bitrate = int(mediaFile['bitrate']) / 1000
                formats.append({
                    'url': mediaFile['streamer'],
                    'play_path': mediaFile['filename'],
                    'ext': 'flv',
                    'format_id': 'rtmp-%d' % bitrate,
                    'tbr': bitrate,
                    'width': int(mediaFile['width']),
                    'height': int(mediaFile['height']),
                })

        video_thumbnail = self._og_search_thumbnail(webpage)
        video_title = self._og_search_title(webpage)
        return {
            'id': video_id,
            'title': video_title,
            'thumbnail': video_thumbnail,
            'formats': formats,
            'rtmp_live': True  # if rtmpdump is not called with "--live" argument, the download is blocked and cannnot be completed.
        }
