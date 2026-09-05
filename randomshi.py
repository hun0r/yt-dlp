from yt_dlp.extractor.common import traverse_obj, str_to_int
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
    data = ie._extract_response(
        browseid, {'browseId': browseid}, ep='browse', api_hostname='music.youtube.com', default_client='web_music')
    info_dict = {}
    with open('tmp.json', 'w') as f:
        json.dump(data, f, indent=2)

    info_dict['artists'] = traverse_obj(data, ('onResponseReceivedActions', 0, 'openPopupAction',
        'popup', 'dismissableDialogRenderer', 'sections', 0, 'dismissableDialogContentSectionRenderer',
        side_key(('title', 'runs', 0, 'text'), 'Performed by', 'subtitle'), 'runs', ..., 'text'))[::2]
    info_dict['composers'] = traverse_obj(data, ('onResponseReceivedActions', 0, 'openPopupAction',
        'popup', 'dismissableDialogRenderer', 'sections', 0, 'dismissableDialogContentSectionRenderer',
        side_key(('title', 'runs', 0, 'text'), 'Written by', 'subtitle'), 'runs', ..., 'text'))[::2]

    return info_dict

def get_track(videoid: str):
    data = ie._extract_response(
        videoid, {'videoId': videoid}, ep='next', api_hostname='music.youtube.com', default_client='web_music')
    with open('tmp.json', 'w') as f:
        json.dump(data, f, indent=2)
    info_dict = {}
    info_dict['track'] = traverse_obj(data, ('contents', 'singleColumnMusicWatchNextResultsRenderer',
        'tabbedRenderer', 'watchNextTabbedResultsRenderer', 'tabs', 0, 'tabRenderer', 'content',
        'musicQueueRenderer', 'content', 'playlistPanelRenderer', 'contents', 0,
        'playlistPanelVideoRenderer', 'title', 'runs', 0, 'text'))
    artists_id = traverse_obj(data, ('contents', 'singleColumnMusicWatchNextResultsRenderer',
        'tabbedRenderer', 'watchNextTabbedResultsRenderer', 'tabs', ..., 'tabRenderer', 'content',
        'musicQueueRenderer', 'content', 'playlistPanelRenderer', 'contents', ...,
        'playlistPanelVideoRenderer', 'menu', 'menuRenderer', 'items', ...,
        side_key(('icon', 'iconType'), 'PEOPLE_GROUP', 'menuNavigationItemRenderer'),
        'navigationEndpoint', 'browseEndpoint', 'browseId'))
    if artists_id:
        info_dict.update(get_artists(artists_id[0]))
    else:
        info_dict['artists'] = merge_runs(traverse_obj(data, ('contents',
            'singleColumnMusicWatchNextResultsRenderer', 'tabbedRenderer',
            'watchNextTabbedResultsRenderer', 'tabs', 0, 'tabRenderer', 'content',
            'musicQueueRenderer', 'content', 'playlistPanelRenderer', 'contents', 0,
            'playlistPanelVideoRenderer', 'shortBylineText')))\
        or traverse_obj(data, ('contents', 'singleColumnMusicWatchNextResultsRenderer',
            'tabbedRenderer', 'watchNextTabbedResultsRenderer', 'tabs', 0, 'tabRenderer', 'content',
            'musicQueueRenderer', 'content', 'playlistPanelRenderer', 'contents', 0,
            'playlistPanelVideoRenderer', 'longBylineText', 'runs', 0, 'text'))
    return info_dict


def get_album(browseid: str) -> tuple[dict[str, str], list[str]]:
    data = ie._extract_response(
        browseid, {'browseId': browseid}, ep='browse', api_hostname='music.youtube.com', default_client='web_music')
    with open('tmp.json', 'w') as f:
        json.dump(data, f, indent=2)

    info_dict = {}

    info_dict['album'] = traverse_obj(data, ('microformat', 'microformatDataRenderer', 'title')) \
        or merge_runs(traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'tabs', ...,
            'tabRenderer', 'content', 'sectionListRenderer', 'contents', ..., 'musicResponsiveHeaderRenderer', 'title')))\
        or traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'tabs', ..., 'tabRenderer',
            'content', 'sectionListRenderer', 'contents', ..., 'musicResponsiveHeaderRenderer', 'buttons',
            ..., 'musicPlayButtonRenderer', 'accessibilityPauseData', 'accessibilityData', 'label')).removeprefix('Pause ')\
        or traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'tabs', ..., 'tabRenderer',
            'content', 'sectionListRenderer', 'contents', ..., 'musicResponsiveHeaderRenderer', 'buttons',
            ..., 'musicPlayButtonRenderer', 'accessibilityPlayData', 'accessibilityData', 'label')).removeprefix('Play ')

    info_dict['album_type'] = traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'tabs',
        0, 'tabRenderer', 'content', 'sectionListRenderer', 'contents', 0, 'musicResponsiveHeaderRenderer',
        'subtitle', 'runs', 0, 'text'))

    info_dict['release_year'] = traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'tabs',
        0, 'tabRenderer', 'content', 'sectionListRenderer', 'contents', 0, 'musicResponsiveHeaderRenderer',
        'subtitle', 'runs', 2, 'text'))

    artists_id = traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'secondaryContents',
        'sectionListRenderer', 'contents', ..., 'musicShelfRenderer', 'contents', ...,
        'musicResponsiveListItemRenderer', 'menu', 'menuRenderer', 'items', ...,
        side_key(('icon', 'iconType'), 'PEOPLE_GROUP', 'menuNavigationItemRenderer'),
        'navigationEndpoint', 'browseEndpoint', 'browseId'))
    if artists_id:
        info_dict.update(get_artists(artists_id[0]))

    entries = []
    for track in traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'secondaryContents',
                 'sectionListRenderer', 'contents', 0, 'musicShelfRenderer', 'contents',
                 ..., 'musicResponsiveListItemRenderer')):
        track_id = traverse_obj(data, ('playlistItemData', 'videoId'))\
        or traverse_obj(data, ('overlay', 'musicItemThumbnailOverlayRenderer', 'content',
            'musicPlayButtonRenderer', 'playNavigationEndpoint', 'watchEndpoint', 'videoId'))\
        or traverse_obj(data, ('flexColumns', ..., 'musicResponsiveListItemFlexColumnRenderer', 'text',
            'runs', ..., 'navigationEndpoint', 'watchEndpoint', 'videoId'))\
        or traverse_obj(data, ('menu', 'menuRenderer', 'topLevelButtons', ..., 'likeButtonRenderer',
            'target', 'videoId'))\
        or traverse_obj(data, ('menu', 'menuRenderer', 'items', ..., 'menuNavigationItemRenderer',
            'navigationEndpoint', 'watchEndpoint', 'videoId'))\
        or traverse_obj(data, ('menu', 'menuRenderer', 'items', ..., 'menuServiceItemRenderer',
            'serviceEndpoint', 'queueAddEndpoint', 'queueTarget', 'videoId'))\
        or traverse_obj(data, ('menu', 'menuRenderer', 'items', ..., 'menuServiceItemRenderer',
            'serviceEndpoint', 'queueAddEndpoint', 'queueTarget', 'onEmptyQueue', 'watchEndpoint', 'videoId'))\
        or traverse_obj(data, ('menu', 'menuRenderer', 'items', ..., 'menuServiceItemDownloadRenderer',
            'serviceEndpoint', 'offlineVideoEndpoint', 'videoId'))\
        or traverse_obj(data, ('menu', 'menuRenderer', 'items', ..., 'menuServiceItemDownloadRenderer',
            'serviceEndpoint', 'offlineVideoEndpoint', 'onAddCommand', 'getDownloadActionCommand', 'videoId'))\

        track_index = str_to_int(merge_runs(traverse_obj(track, ('index')))) \
        or traverse_obj(track, ('overlay', 'content', 'musicPlayButtonRenderer', 'playNavigationEndpoint',
            'watchEndpoint', 'index'), default=0) + 1
        if not track_id:
            ie._error_or_warning(f'track {track} couldn\'t be extracted')

    return info_dict

def get_artist(browseid: str):
    data = ie._extract_response(
        browseid, {'browseId': browseid}, ep='browse', api_hostname='music.youtube.com', default_client='web_music')
    with open('tmp.json', 'w') as f:
        json.dump(data, f, indent=2)
print(get_artist())
exit(0)
'browse/MPREb_cqCwG4dDfGj'
print(get_track('e3OBPOKtMgA'))
print(get_track('agboF2zU0mg'))
print(get_album('MPREb_MQYYcdQhCqL'))
print(get_album('MPREb_cqCwG4dDfGj'))
print(get_album('MPREb_gTAcphH99wE'))
