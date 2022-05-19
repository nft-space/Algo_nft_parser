import json
from indexer import NFTIndexer
from datetime import datetime
from pprint import pprint
import base64

# connect to your indexer node:
indexer_client = NFTIndexer(indexer_address="https://algoindexer.algoexplorerapi.io",indexer_token="",headers={
            'User-Agent': 'Mozilla/5.0'}
    )

def test_is_nft():    

    # params from NFT asset id:356872169
    params = indexer_client.search_assets(asset_id=356872169)['assets'][0]['params']    
    assert indexer_client._is_nft(params) is True

    # params for USDT (not a NFT)
    params = indexer_client.search_assets(asset_id=312769)['assets'][0]['params']
    assert indexer_client._is_nft(params) is False
	
# get data with algoexplorer then paste in  
def test_nft_asset_info():
    metadata = indexer_client.nft_asset_info(asset_id=356872169)
    created_at_round = 16629682
    asset_id = 356872169
    creator = 'PVOQB55GQYX75HVSLLMH4UJDG4RWUUHI6TGOP32AYS5K4367T26D2PV6MI'

    assert [metadata['created-at-round'], metadata['index'], metadata['params']['creator']] == [created_at_round, asset_id,creator]

def test_search_nfts_in_address():
    address = 'PVOQB55GQYX75HVSLLMH4UJDG4RWUUHI6TGOP32AYS5K4367T26D2PV6MI'
    asset_id=indexer_client.search_nfts_in_address(address,limit=1)[0]['index']
    assert asset_id == 348416550

def test_nft_mint_datetime():
    # get created time from algo explorer:
    created_at_time = datetime(2021,10,21,22,4,46).isoformat("T")
    assert indexer_client.nft_mint_date(asset_id=379067271) == created_at_time

def test_nft_owner():
    
    # test a nft with total supply of 1
    assert indexer_client.nft_owner(338223552,block=16533008) == '4QT45IJEA5BAQPKCPOD7SJ566JQSGQ2YYNADVYYD5Q4B2WCII6MPTZY33M'
    # test a nft with total supply of 1000
    assert indexer_client.nft_owner(371939866,block=16533008) == 'multiple owners'

def test_creation_list():
    nft_list = indexer_client.creation_list('OCULJCK525B36MA7JGX4YUYMAKOIB6K6L35AEWDVJSGOIIU5M3KI43HXFI')
    index = []
    for nft in nft_list:
        index.append(nft['index'])
    assert 377639655 in index     
   

def test_nft_transaction_history():
    transcation = indexer_client.nft_transaction_history('307568440')
    # print(transcation)
    assert transcation[-1]['sender'] == 'MPOR6ZFJHC4UPUSINCE7DHBDFZHL65KB4QNCNGT4VB6M3A4OZLJQDEQWEM'

def test_get_owners_nfts():
    
    address = 'BXSAHPGA5FLUP5TJJRL24JZZTWXKAK3PRK45XSYPXZTRM3YNGFMJE2LOKA'
    asset_ids=indexer_client.account_info(address)['account']['assets']    
    asset_ids = [id for id in asset_ids if id.get('amount') > 0]
    asset_ids = sorted(asset_ids, key=lambda id: id['asset-id'],reverse=True)
    assert asset_ids 

def test_get_arc69_meta_data():  
   
    meta_data = indexer_client.get_arc69_meta_data(418378869)    
    assert meta_data['standard'] == 'arc69'
    meta_data = indexer_client.get_arc69_meta_data(308692403)
    assert meta_data == None

def test_get_arc69_metadata_list():
    asset_id=[418632519,418631877,418631762]
    meta_data = indexer_client.get_arc69_meta_data(asset_id,creator='KLKLHRAT525BOEPR72XMBIPDK77AI52TF6QC5LGNV2J2J3SCUGKDJVLCX4')
    print(meta_data)
    

if __name__ == "__main__":
    test_get_arc69_metadata_list()