
# Introduction 
NFTIndexer is a Python library for parsing nft metadata using algorand indexer.

The NFTIndexer class is a child class inherited from [algorand indexer](https://github.com/algorand/indexer). It is a standalone service that reads committed blocks from the Algorand blockchain and maintains a database of transactions and accounts that are searchable and indexed.

# Minimum Version Requirements

* python 3.9

# Getting Started

##	Installation process
---
```
pip3 install requirements.txt
```
## Connect to an indexer node
---
The Algorand Indexer is a feature that enables searching the blockchain for transactions, assets, accounts, and blocks with various criteria. [See details.](https://developer.algorand.org/docs/get-details/indexer/)

User needs to install a node to be able to use indexer python SDK. Alternatively, user can connect to a web api like the one offered by [Purestake](https://www.purestake.com/technology/algorand-api/).

# Features

#### is_nft: 
In algorand blockchain, fungible tokens and NFTs are both implemented as Algorand Standard Assets (ASAs). So this function is used to check if an asset is a NFT.

#### nft_asset_info:

It returns a ASA metadata dictionary. See the example below.

```python

indexer_client = NFTIndexer(indexer_address=algod_address, ndexer_token=algod_token,headers=headers)

indexer_client.nft_asset_info(292946852)

```
Which returns the metadata of asset 292946852:

```python
{'created-at-round': 15421784,
 'deleted': False,
 'index': 292946852,
 'params': {'clawback': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ',
            'creator': 'JADXUXWQ5CWU2G2TTBMY7NCWGDHO3SLY7IPYVC37GTFARAZ2N5LBLWAP5A', 
            'decimals': 0,
            'default-frozen': False,
            'freeze': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ',
            'manager': 'JADXUXWQ5CWU2G2TTBMY7NCWGDHO3SLY7IPYVC37GTFARAZ2N5LBLWAP5A',
            'name': 'Bullish',
            'name-b64': 'QnVsbGlzaA==',
            'reserve': 'JADXUXWQ5CWU2G2TTBMY7NCWGDHO3SLY7IPYVC37GTFARAZ2N5LBLWAP5A',
            'total': 33,
            'unit-name': 'MTB1',
            'unit-name-b64': 'TVRCMQ==',
            'url': 'https://ipfs.io/ipfs/bafybeiamo3qpxlujo73wib3g56fwby7epqjrkawcp63g5vz77cz2udcxpa',
            'url-b64': 'aHR0cHM6Ly9pcGZzLmlvL2lwZnMvYmFmeWJlaWFtbzNxcHhsdWpvNzN3aWIzZzU2ZndieTdlcHFqcmthd2NwNjNnNXZ6NzdjejJ1ZGN4cGE='}}
```
#### search_nfts_in_address

```python
search_nfts_in_address(self, address:str, limit:int=0)
```
This function will search NFT assets currently hold in the account using the account's public key (address). 

A limit can be applied for the number of NFTs to return

```python

somebodys_ccount = 'PVOQB55GQYX75HVSLLMH4UJDG4RWUUHI6TGOP32AYS5K4367T26D2PV6MI'
pprint.pprint(indexer_client.search_nfts_in_address(address=somebodys_ccount,limit=1))

```
which returns one NFT asset metadate in the somebody's account:

```python
[{'created-at-round': 16960255,
  'deleted': False,
  'index': 379067271,
  'params': {'clawback': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ',
             'creator': 'PVOQB55GQYX75HVSLLMH4UJDG4RWUUHI6TGOP32AYS5K4367T26D2PV6MI',
             'decimals': 0,
             'default-frozen': False,
             'freeze': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ',
             'manager': 'PVOQB55GQYX75HVSLLMH4UJDG4RWUUHI6TGOP32AYS5K4367T26D2PV6MI',
             'name': 'Quilt Block 2 Row 1',
             'name-b64': 'UXVpbHQgQmxvY2sgMiBSb3cgMQ==',
             'reserve': 'PVOQB55GQYX75HVSLLMH4UJDG4RWUUHI6TGOP32AYS5K4367T26D2PV6MI',
             'total': 1,
             'unit-name': 'QB2R1',
             'unit-name-b64': 'UUIyUjE=',
             'url': 'ipfs://bafkreibvczi5evqntmo5xkkkgagwhocf2dpqr55mbilwym4pzkor6rjfjm',
             'url-b64': 'aXBmczovL2JhZmtyZWlidmN6aTVldnFudG1vNXhra2tnYWd3aG9jZjJkcHFyNTVtYmlsd3ltNHB6a29yNnJqZmpt'}}]

```

#### parse_arc69_token_metadata

```python

get_arc69_meta_data(self,asset_id,creator=None,min_round=None)

```
ARC69 is a community Algorand NFT token standard and currently supported by most of the NFT marketplaces. For details, see [here](https://github.com/algokittens/arc69)

An ARC-69 ASA has its associated JSON metadata file stored as a note in the most recent asset configuration transaction. So this function loops through the ASA configuration transactions and parse ASA's metadata from transaction note.




# Testing

```
python -m pytest testing/testing.py

```
