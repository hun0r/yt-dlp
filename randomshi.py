from yt_dlp.extractor.common import traverse_obj
from yt_dlp.extractor.youtube import YoutubeTabIE
from yt_dlp import YoutubeDL
import json
downloader = YoutubeDL()
ie = YoutubeTabIE(downloader)


def merge_runs(runs: list[dict[str, str]]) -> str:
    return ''.join(traverse_obj(runs, ('runs', ..., 'text')) or []) or None

def side_key(path, value, key=None):
    def func(k, v):
        return traverse_obj(v, path) == value and (k == key or key is None)

    return func

def get_artists(browseid: str):
    data = ie._extract_response(browseid, {'browseId': browseid}, ep='browse', api_hostname='music.youtube.com', default_client='web_music')
    with open('tmp.json', 'w') as f:
        json.dump(data, f, indent=2)

    album_artist = [merge_runs(i) for i in traverse_obj(data, ('onResponseReceivedActions', ..., 'openPopupAction', 'popup', 'dismissableDialogRenderer', 'sections', ..., 'dismissableDialogContentSectionRenderer', 'subtitle'))]\
    or [merge_runs(i) for i in traverse_obj(data, ('onResponseReceivedActions', ..., 'openPopupAction', 'popup', 'dismissableDialogRenderer', 'metadata', 'musicMultiRowListItemRenderer', 'subtitle')) or []]

    traverse_obj(data, ('onResponseReceivedActions', 0, 'openPopupAction', 'popup', 'dismissableDialogRenderer', 'sections', 0, 'dismissableDialogContentSectionRenderer', side_key(('title', 'runs', 0, 'text'), 'Performed by', 'subtitle'), 'runs', ..., 'text'))

    return None, None

def get_track(videoid: str):
    data = ie._extract_response(videoid, {'videoId': videoid}, ep='next', api_hostname='music.youtube.com', default_client='web_music')
    track = traverse_obj(data, ('contents', 'singleColumnMusicWatchNextResultsRenderer', 'tabbedRenderer', 'watchNextTabbedResultsRenderer', 'tabs', 0, 'tabRenderer', 'content', 'musicQueueRenderer', 'content', 'playlistPanelRenderer', 'contents', 0, 'playlistPanelVideoRenderer', 'title', 'runs', 0, 'text'))
    artist = traverse_obj(data, ('contents', 'singleColumnMusicWatchNextResultsRenderer', 'tabbedRenderer', 'watchNextTabbedResultsRenderer', 'tabs', 0, 'tabRenderer', 'content', 'musicQueueRenderer', 'content', 'playlistPanelRenderer', 'contents', 0, 'playlistPanelVideoRenderer', 'longBylineText', 'runs', 0, 'text'))\
    or traverse_obj(data, ('contents', 'singleColumnMusicWatchNextResultsRenderer', 'tabbedRenderer', 'watchNextTabbedResultsRenderer', 'tabs', 0, 'tabRenderer', 'content', 'musicQueueRenderer', 'content', 'playlistPanelRenderer', 'contents', 0, 'playlistPanelVideoRenderer', 'shortBylineText', 'runs', 0, 'text'))

    artists_id = traverse_obj(data, ('contents', 'singleColumnMusicWatchNextResultsRenderer', 'tabbedRenderer', 'watchNextTabbedResultsRenderer', 'tabs', ..., 'tabRenderer', 'content', 'musicQueueRenderer', 'content', 'playlistPanelRenderer', 'contents', ..., 'playlistPanelVideoRenderer', 'menu', 'menuRenderer', 'items', ..., side_key(('icon', 'iconType'), 'PEOPLE_GROUP', 'menuNavigationItemRenderer'), 'navigationEndpoint', 'browseEndpoint', 'browseId'))[0]
    artists, composers = get_artists(artists_id)
    return track, artist


def get_album(browseid: str) -> tuple[dict[str, str], list[str]]:
    data = ie._extract_response(browseid, {'browseId': browseid}, ep='browse', api_hostname='music.youtube.com', default_client='web_music')

    info_dict = {}

    info_dict['album'] = traverse_obj(data, ('microformat', 'microformatDataRenderer', 'title')) \
        or merge_runs(traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'tabs', ..., 'tabRenderer', 'content', 'sectionListRenderer', 'contents', ..., 'musicResponsiveHeaderRenderer', 'title')))\
        or traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'tabs', ..., 'tabRenderer', 'content', 'sectionListRenderer', 'contents', ..., 'musicResponsiveHeaderRenderer', 'buttons', ..., 'musicPlayButtonRenderer', 'accessibilityPauseData', 'accessibilityData', 'label')).removeprefix('Pause ')\
        or traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'tabs', ..., 'tabRenderer', 'content', 'sectionListRenderer', 'contents', ..., 'musicResponsiveHeaderRenderer', 'buttons', ..., 'musicPlayButtonRenderer', 'accessibilityPlayData', 'accessibilityData', 'label')).removeprefix('Play ')

    info_dict['album_type'] = traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'tabs', 0, 'tabRenderer', 'content', 'sectionListRenderer', 'contents', 0, 'musicResponsiveHeaderRenderer', 'subtitle', 'runs', 0, 'text'))

    info_dict['release_year'] = traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'tabs', 0, 'tabRenderer', 'content', 'sectionListRenderer', 'contents', 0, 'musicResponsiveHeaderRenderer', 'subtitle', 'runs', 2, 'text'))

    artists_id = traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'secondaryContents', 'sectionListRenderer', 'contents', ..., 'musicShelfRenderer', 'contents', ..., 'musicResponsiveListItemRenderer', 'menu', 'menuRenderer', 'items', ..., side_key(('icon', 'iconType'), 'PEOPLE_GROUP', 'menuNavigationItemRenderer'), 'navigationEndpoint', 'browseEndpoint', 'browseId'), default=0)[0]

    artists_info = get_artists(artists_id)

    return info_dict

'browse/MPREb_cqCwG4dDfGj'
print(get_track('e3OBPOKtMgA'))
exit(0)
print(get_track('agboF2zU0mg'))
print(get_album('MPREb_MQYYcdQhCqL'))
get_album('MPREb_cqCwG4dDfGj')
get_album('MPREb_gTAcphH99wE')
