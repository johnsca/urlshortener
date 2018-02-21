from uuid import uuid4

from urlshortener import exceptions


URLS = {}


def _by_url(url):
    SLRU = {v['url']: k for k, v in URLS.items()}
    return SLRU.get(url)


def list():
    return sorted(URLS.values(), key=lambda e: e['id'])


def create(url):
    if _by_url(url):
        raise exceptions.AlreadyExists()
    for attempt in range(3):
        url_id = uuid4().hex[:8]
        if url_id not in URLS:
            URLS[url_id] = entity = {'id': url_id, 'url': url, 'views': 0}
            return entity
    else:
        raise exceptions.NoAvailableIDs()


def retrieve(url_id):
    if url_id not in URLS:
        raise exceptions.NotFound()
    return URLS[url_id]


def view(url_id):
    if url_id not in URLS:
        raise exceptions.NotFound()
    URLS[url_id]['views'] += 1
    return URLS[url_id]


def update(url_id, url):
    if _by_url(url):
        raise exceptions.AlreadyExists()
    if url_id not in URLS:
        raise exceptions.NotFound()
    URLS[url_id] = entity = {'id': url_id, 'url': url, 'views': 0}
    return entity


def delete(url_id):
    if url_id not in URLS:
        raise exceptions.NotFound()
    del URLS[url_id]
