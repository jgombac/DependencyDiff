from urllib.parse import urlparse, urlunparse

import html
import os
import re

# Local Libraries
import gflags
FLAGS = gflags.FLAGS


gflags.DEFINE_spaceseplist(
    'ignore_prefixes', [],
    'URL prefixes that should not be crawled.')

gflags.DEFINE_bool(
    'keep_query_string', False,
    'Keep the query string when cleaning URLs')


# URL regex rewriting code originally from mirrorrr
# http://code.google.com/p/mirrorrr/source/browse/trunk/transform_content.py

# URLs that have absolute addresses
ABSOLUTE_URL_REGEX = r"(?P<url>(http(s?):)?//[^\"'> \t]+)"
# URLs that are relative to the base of the current hostname.
BASE_RELATIVE_URL_REGEX = (
    r"/(?!(/)|(mailto:)|(http(s?)://)|(url\())(?P<url>[^\"'> \t]*)")
# URLs that have '../' or './' to start off their paths.
TRAVERSAL_URL_REGEX = (
    r"(?P<relative>\.(\.)?)/(?!(/)|"
    r"(http(s?)://)|(url\())(?P<url>[^\"'> \t]*)")
# URLs that are in the same directory as the requested URL.
SAME_DIR_URL_REGEX = r"(?!(/)|(mailto:)|(http(s?)://)|(#)|(url\())(?P<url>[^\"'> \t]+)"
# URL matches the root directory.
ROOT_DIR_URL_REGEX = r"(?!//(?!>))/(?P<url>)(?=[ \t\n]*[\"'> /])"
# Start of a tag using 'src' or 'href'
TAG_START = (
    r"(?i)(?P<tag>\ssrc|href|action|url|background)"
    r"(?P<equals>[\t ]*=[\t ]*)(?P<quote>[\"']?)")
# Potential HTML document URL with no fragments.
MAYBE_HTML_URL_REGEX = (
    TAG_START + r"(?P<absurl>(http(s?):)?//[^\"'> \t]+)")

REPLACEMENT_REGEXES = [
    (TAG_START + SAME_DIR_URL_REGEX,
     "\g<tag>\g<equals>\g<quote>%(accessed_dir)s\g<url>"),
    (TAG_START + TRAVERSAL_URL_REGEX,
     "\g<tag>\g<equals>\g<quote>%(accessed_dir)s/\g<relative>/\g<url>"),
    (TAG_START + BASE_RELATIVE_URL_REGEX,
     "\g<tag>\g<equals>\g<quote>%(base)s/\g<url>"),
    (TAG_START + ROOT_DIR_URL_REGEX,
     "\g<tag>\g<equals>\g<quote>%(base)s/"),
    (TAG_START + ABSOLUTE_URL_REGEX,
     "\g<tag>\g<equals>\g<quote>\g<url>"),
]

def get_domain(url):
    parts = urlparse(url)
    return '%s://%s' % (parts.scheme, parts.netloc)

def get_domain_name(url):
    return get_domain(url).replace("https://", "").replace("http://", "").replace(":", "")


def clean_url(url, force_scheme=None):
    """Cleans the given URL."""
    # URL should be ASCII according to RFC 3986
    url = str(url)
    # Collapse ../../ and related
    url_parts = urlparse(url)
    path_parts = []
    for part in url_parts.path.split('/'):
        if part == '.':
            continue
        elif part == '..':
            if path_parts:
                path_parts.pop()
        else:
            path_parts.append(part)

    url_parts = list(url_parts)
    if force_scheme:
        url_parts[0] = force_scheme
    url_parts[2] = '/'.join(path_parts)

    if not FLAGS.keep_query_string:
        url_parts[4] = ''    # No query string

    url_parts[5] = ''    # No path

    # Always have a trailing slash
    if not url_parts[2]:
        url_parts[2] = '/'

    return urlunparse(url_parts)


def extract_urls(url, data, unescape=html.unescape):
    """Extracts the URLs from an HTML document."""
    parts = urlparse(url)
    prefix = '%s://%s' % (parts.scheme, parts.netloc)

    accessed_dir = os.path.dirname(parts.path)
    if not accessed_dir.endswith('/'):
        accessed_dir += '/'

    for pattern, replacement in REPLACEMENT_REGEXES:
        fixed = replacement % {
            'base': prefix,
            'accessed_dir': accessed_dir,
        }
        data = re.sub(pattern, fixed, data)

    result = set()
    for match in re.finditer(MAYBE_HTML_URL_REGEX, data):
        found_url = unescape(match.groupdict()['absurl'])
        found_url = clean_url(
            found_url,
            force_scheme=parts[0])  # Use the main page's scheme
        result.add(found_url)

    return result


IGNORE_SUFFIXES = frozenset([
    'jpg', 'jpeg', 'png', 'css', 'js', 'xml', 'json', 'gif', 'ico', 'doc'])


def prune_urls(url_set, allowed_list, ignored_list):
    """Prunes URLs that should be ignored."""
    result = set()

    for url in url_set:
        allowed = False
        for allow_url in allowed_list:
            if url.startswith(allow_url):
                allowed = True
                break

        if not allowed:
            continue

        ignored = False
        for ignore_url in ignored_list:
            if url.startswith(ignore_url):
                ignored = True
                break

        if ignored:
            continue

        prefix, suffix = (url.rsplit('.', 1) + [''])[:2]
        if suffix.lower() in IGNORE_SUFFIXES:
            continue

        result.add(url)

    return result
