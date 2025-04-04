from optparse import OptionParser
from substrateinterface import SubstrateInterface
import json
import os

""" Setting script usage, options, and args parsing """

usage = "usage: %prog [--cache, --endpoint] target"
parser = OptionParser(usage)

parser.add_option(
    '-c', '--cache',
    dest='cache_file',
    default='./.identities_cache.json',
    help='File to use as cache file, uses .json files. Default is ./.identities_cache.json',
    metavar='CACHE'
)
parser.add_option(
    '-e', '--endpoint',
    dest='endpoint',
    default='http://127.0.0.1:9933',
    help='Endpoint of the network node you want to connect to and retrieve identities from. Default is http://127.0.0.1:9933'
)

(options, args) = parser.parse_args()

if len(args) != 1:
    parser.error("Missing target to search for.\n")

""" Initializing node connection & data structures """
substrate = SubstrateInterface(url=options.endpoint)
matching_ids = {}
valid_filters = ('additional', 'display', 'legal', 'web', 'riot', 'email', 'pgpFingerprint', 'image', 'twitter')


def find_in_id_list(target, id_list):
    """
    Filters the ID list to find matches for the target.

    Parameters
    ----------
    target: str
        String to be found in id_dict.

    id_list: list
        Data collection that will be filtered or used as a source to look for the target.

    Returns
    -------
    matching_ids: dict
        Dictionary of IDs matching the target.
    """
    matching_ids[target] = []

    id_dict = {account: data for account, data in id_list}
    search_filter, target = set_search_filter(target)

    for account, data in id_dict.items():
        if search_filter is None:
            if is_matching_target(target, data['info']):
                matching_ids[target].append(account)
        else:
            if is_matching_target(target, data['info'].get(search_filter, {})):
                matching_ids[f"{search_filter}:{target}"].append(account)

    return matching_ids


def is_matching_target(target, id_data):
    """
    Checks if the target is contained in the given id_data.

    Parameters
    ----------
    target: str
        String to be found in id_data.

    id_data: dict or list
        Data collection where the target is going to be looked for.

    Returns
    -------
    bool
        True if the target is found, False otherwise.
    """
    if not id_data:
        return False

    if isinstance(id_data, dict):
        for value in id_data.values():
            if value and (target in value if isinstance(value, str) else is_matching_target(target, value)):
                return True

    elif isinstance(id_data, list):
        for value in id_data:
            if target in value:
                return True

    return False


def set_search_filter(target):
    """
    Sets metadata filter if provided in the request.

    Parameters
    ----------
    target: str
        Input from the search request.

    Returns
    -------
    tuple
        search_filter: str or None
            Filter defined in the request, None if no filter is given.
        target: str
            Target with the filter stripped out.
    """
    filtered_target = target.split(':', 1)

    if len(filtered_target) > 1:
        if filtered_target[0] not in valid_filters:
            print('\nInvalid filter provided. Valid filters are:')
            print(', '.join(valid_filters))
            print(f'\nSearch will continue looking for "{filtered_target[1]}" in all identity fields.')
            return None, filtered_target[1]

        return filtered_target[0], filtered_target[1]

    return None, target


def search(target):
    """
    Entry point for the search functionality. Handles caching and performs the search.

    Parameters
    ----------
    target: str
        The target string to search for.
    """
    cache = {}
    id_list = list(substrate.iterate_map(module='Identity', storage_function='IdentityOf'))
    id_list_hash = hash(str(id_list))

    try:
        # Try reading the cache
        if os.path.exists(options.cache_file):
            with open(options.cache_file, 'r') as f:
                cache = json.load(f)

        # Check if cache is valid or needs updating
        if 'hash' not in cache or id_list_hash != cache['hash']:
            cache = update_cache(target, id_list, id_list_hash)

    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading cache file: {e}")
        cache = update_cache(target, id_list, id_list_hash)

    print(cache.get(list(matching_ids.keys())[0], []))


def update_cache(target, id_list, id_list_hash):
    """
    Updates the cache with the latest search results.

    Parameters
    ----------
    target: str
        The target string to search for.
    id_list: list
        The list of identities to search through.
    id_list_hash: int
        The hash of the current ID list.

    Returns
    -------
    dict
        The updated cache.
    """
    cache = {
        'hash': id_list_hash,
        list(matching_ids.keys())[0]: find_in_id_list(target, id_list)[list(matching_ids.keys())[0]]
    }
    try:
        with open(options.cache_file, 'w') as f:
            json.dump(cache, f)
    except IOError as e:
        print(f"Error writing to cache file: {e}")

    return cache


if __name__ == "__main__":
    search(args[0])
