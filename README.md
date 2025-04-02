# Identity Searcher for Substrate

A Python-based identity searcher for Substrate-based blockchain networks utilizing the [Identity Pallet](https://substrate.dev/rustdocs/v2.0.0/pallet_identity/index.html).

## Overview

The Identity Pallet allows account owners to associate real-world information with their on-chain accounts. This is particularly useful for validator identification, Council member metadata, and other use cases. Learn more about Substrate-based identities in the [official Polkadot wiki](https://wiki.polkadot.network/docs/en/learn-identity).

## Installation

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/al3mart/substrate_identity_searcher.git
cd substrate_identity_searcher
```

It is recommended to use a virtual environment:

```bash
pip install virtualenv
virtualenv .
source bin/activate
pip install substrate-interface
```

Run the script with:

```bash
python ./searcher.py [options] <target>
```

## Usage

This script connects to a Substrate-based blockchain node and searches for identities matching the specified `target`. The node endpoint can be specified using the `--endpoint` option, and a cache file can be set using the `--cache` option.

### Default Values

- **Endpoint**: `http://127.0.0.1:9933`
- **Cache File**: `./.identities_cache.json`

If the default values are sufficient, these options can be omitted. Note that public nodes typically do not expose HTTP endpoints, so using WebSocket (WSS) endpoints is recommended.

### Required Argument

The script requires a `target` argument, which specifies the string to search for in the identity metadata. For help, run:

```bash
python ./searcher.py --help
```

### Filters

The `target` can include an optional filter to narrow the search to a specific identity field. Filters are specified in the format `filter:target_string`. Supported filters include:

- `additional`
- `display`
- `legal`
- `web`
- `riot`
- `email`
- `pgpFingerprint`
- `image`
- `twitter`

For example, `display:Alice` searches for identities where the `display` field contains "Alice".

### Matching Behavior

- The script returns identities where the `target` is found in any metadata field.
- If a filter is provided, the search is restricted to the specified field.
- Partial matches are included. For example, searching for "bob" will match "bobamazoo".

### Caching

To improve performance, the script uses a persistent cache system. The cache stores results from previous searches, reducing the need for repeated full searches. The cache is automatically updated if the on-chain identity data changes.

## Features

- Search for identities containing a specific `target` in any metadata field.
- Use filters to restrict searches to specific fields.
- Supports partial matches (e.g., "bob" matches "bobamazoo").
- Persistent caching for faster repeated searches.

## Dependencies

- [substrate-interface](https://github.com/polkascan/py-substrate-interface)

## Example

To search for identities containing "Alice" in the `display` field:

```bash
python ./searcher.py --endpoint ws://127.0.0.1:9944 display:Alice
```

This will return all identities where the `display` field contains "Alice".
