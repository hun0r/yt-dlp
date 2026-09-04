from yt_dlp.extractor.common import traverse_obj
from yt_dlp.extractor.youtube import YoutubeTabIE
from yt_dlp import YoutubeDL
import json
downloader = YoutubeDL()
ie = YoutubeTabIE(downloader)


def merge_runs(runs: list[dict[str, str]]) -> str:
    return ''.join(traverse_obj('runs', ..., 'text', str) or []) or None


def get_artists(browseid: str):
    pass


def get_album(browseid: str) -> tuple[dict[str, str], list[str]]:
    data = ie._extract_response(browseid, {'browseId': browseid}, ep='browse', api_hostname='music.youtube.com', default_client='web_music')
    with open('tmp.json', 'w') as f:
        json.dump(data, f, indent=2)

    info_dict = {
        'release_year',
        'album',
        'album_type',
        'album_artists',
    }

    info_dict['album'] = traverse_obj(data, ('microformat', 'microformatDataRenderer', 'title')) \
        or merge_runs(traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'tabs', ..., 'tabRenderer', 'content', 'sectionListRenderer', 'contents', ..., 'musicResponsiveHeaderRenderer', 'title')))\
        or traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'tabs', ..., 'tabRenderer', 'content', 'sectionListRenderer', 'contents', ..., 'musicResponsiveHeaderRenderer', 'buttons', ..., 'musicPlayButtonRenderer', 'accessibilityPauseData', 'accessibilityData', 'label')).removeprefix('Pause ')\
        or traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'tabs', ..., 'tabRenderer', 'content', 'sectionListRenderer', 'contents', ..., 'musicResponsiveHeaderRenderer', 'buttons', ..., 'musicPlayButtonRenderer', 'accessibilityPlayData', 'accessibilityData', 'label')).removeprefix('Play ')

    info_dict['album_type'] = traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'tabs', 0, 'tabRenderer', 'content', 'sectionListRenderer', 'contents', 0, 'musicResponsiveHeaderRenderer', 'subtitle', 'runs', 0, 'text'))

    info_dict['release_year'] = traverse_obj(data, ('contents', 'twoColumnBrowseResultsRenderer', 'tabs', 0, 'tabRenderer', 'content', 'sectionListRenderer', 'contents', 0, 'musicResponsiveHeaderRenderer', 'subtitle', 'runs', 2, 'text'))


get_album('MPREb_gTAcphH99wE')
