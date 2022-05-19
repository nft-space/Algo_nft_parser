from algosdk.v2client.indexer import IndexerClient
from datetime import datetime,timezone
import urllib
import base64

# from . import ipfs_img

class NFTIndexer(IndexerClient):

    def __init__(self, indexer_token, indexer_address, headers=None):
        super().__init__(indexer_token, indexer_address, headers=headers)
        
        # these are to allow caching last accessed asset id info since
        # client code typcially processes assets one by one serially
        # (e.g. processing each inclduing minting timestamp takes 4 successive calls to nft_asset_info)
        self._cached_asset_id = 0
        self._cached_asset_info = None


    def _is_nft(self,asset_params):
        
        try:
            if asset_params['decimals'] == 0 and asset_params['name'] and asset_params['url']:
                return True                     
            else:
                return False
        except:
            return False

        
    # return nft metadata json - if None is returned then the asset likely has been deleted
    def nft_asset_info(self, asset_id):
        if asset_id == self._cached_asset_id:
            return self._cached_asset_info
        else:    
            retval = None
            asset_list=[]
            try:
                asset_list = self.search_assets(asset_id=asset_id)['assets']
            except urllib.error.URLError as e:
                pass
            if len(asset_list) > 0:
                #print(f"found info for asset {asset_id}")
                if self._is_nft(asset_list[0]['params']):
                    retval = asset_list[0]
            else:
                #print(f"cannot find asset {asset_id}")
                pass 
            self._cached_asset_id = asset_id
            self._cached_asset_info = retval
            return retval
   
    def search_nfts_in_address(self, address:str, limit:int=0):
        # address is public key
        # limit is the number of NFT asset must >= 0, if limit = 0, there is no limit 
        # this function returns  a list of NFT metadata dictionaries
        # To get the asset, the amount must be greater than 1       
        
        response = self.account_info(address=address)
        nft_list = []
        nft_counter = 0
       
        if limit < 0:
            raise ValueError ("limit must be greart than 0")
        else:            
            for asset in response['account']['assets']:
                if asset['amount'] >0: 
                    asset_info = self.nft_asset_info(asset['asset-id'])
                    if asset_info:                    
                        nft_list.append(asset_info)
                        nft_counter +=1
                        if limit>0 and nft_counter>=limit:
                            break            

        return nft_list

    # convert block timestamp into isoform datetime, if the block info does not exist anymore
    # this returns None
    def block_datetime(self,block):
        try:
            return datetime.fromtimestamp(self.block_info(block=block)['timestamp']).isoformat("T")
        except urllib.error.URLError as e:
            return None

    # this function return the datetime when the nft asset is created
    # if None is returned then this menas the nft has likely been deleted
    def nft_mint_date(self, asset_id=None, created_at_block=None):

        if created_at_block:
            return self.block_datetime(created_at_block)
        if asset_id:
            asset_info = self.nft_asset_info(asset_id=asset_id)
            if asset_info != None:
                created_at_block=self.nft_asset_info(asset_id=asset_id)['created-at-round']
                return self.block_datetime(created_at_block)
            else:
                return None

    def get_nft_owners(self,asset_id,block=None):
    # this function return the owner's address
        asset_info=self.asset_balances(asset_id=asset_id,block=block)
        # pprint.pprint(account_list)
        account_list= asset_info['balances']
        owner_list = []
       
        for account in account_list:
            if account['amount'] >=1: 
                           
                owner_list.append(account)
       
        if owner_list:
            return {'owners':owner_list,'current-round': asset_info['current-round']}  
        else:
            return  None
  
   
    def creation_list(self,address=None, asset_id=None,count=1000):
        if address:
            response = self.search_assets(creator=address,limit=count)            
        elif asset_id:
            address = self.nft_asset_info(asset_id)['params']['creator']           
            response = self.search_assets(creator=address,limit=count)
        else:
            ValueError("No address or asset_id is found in input") 
        
        if response.get('assets'):
            return response['assets']
        else:
            return None


    def nft_transaction_history(self, asset_id, min_price=203001):
        
        transaction_list= self.search_asset_transactions(asset_id=asset_id,min_amount=0,txn_type='axfer')['transactions']
        transaction_history = []
        for transcation in transaction_list:

            if  transcation['asset-transfer-transaction']['amount'] >=1:   
                payment_transcations=self.search_transactions_by_address(transcation['asset-transfer-transaction']['receiver'],
                block=transcation['confirmed-round'],txn_type='pay',min_amount=min_price)['transactions']
                for payment_transcation in payment_transcations:
                    # pprint.pprint(payment_transcation)
                    if payment_transcation['group'] == transcation['group']:                     

                        transaction_info = {
                            "timestamp":payment_transcation['round-time'],
                            "sender": transcation['sender'],
                            "receiver": transcation['asset-transfer-transaction']['receiver'],
                            "quantity": transcation['asset-transfer-transaction']['amount'],
                            "amount":payment_transcation['payment-transaction']['amount']
                        }
                        transaction_history.append(transaction_info)
        return transaction_history


    def search_nft_id(self, min_round:int,max_round:int):

        # if block range is too large, it may get timed out
        # it is recommanded to use a block range of 5000
        # this function returns two lists: one is nft minted and another is nft deleted
        nft_added_list=[]
        nft_deleted_list =[]
        transactions = self.search_transactions(txn_type='acfg',min_round= min_round,max_round=max_round)['transactions']
        for transaction in transactions:   
            amount = transaction['asset-config-transaction']['params']['total']                 
            if self._is_nft(transaction['asset-config-transaction']['params']) and amount >0 and transaction['asset-config-transaction']['asset-id']==0:
                                     
                nft_added_list.append(transaction['created-asset-index'])
            elif amount==0 and 'manager' not in transaction['asset-config-transaction']['params']:
                nft_deleted_list.append(transaction['asset-config-transaction']['asset-id'])
    
        return nft_added_list, nft_deleted_list

    def _get_collection_name(self, unit_name:str):
        
        # search # in unit_name
        if '#' in unit_name:
            return unit_name.split('#')[0].strip()
        # search : in unit_name
        elif ':' in unit_name:
            return unit_name.split(':')[0].strip()
        else:
        # if cannot find any: search if there is a number in unit name
            for i, s in enumerate(unit_name.split()):
                if s.isdigit():
                    return unit_name.split()[i-1].strip()
                    
        return unit_name
    
    def get_latest_block(self):
        time_now = datetime.now(timezone.utc).isoformat()   
        return self.search_transactions(end_time=time_now,limit=1)['current-round']

    def _get_single_nft_arc69_metadata(self,asset_id,creator=None,min_round=None):
        if not creator:
                try:
                    creator = self.nft_asset_info(asset_id)['params']['creator']
                except:
                    creator = None
        metadata = None   
        transaction_info=self.search_asset_transactions(asset_id=asset_id,address=creator,min_round=min_round) 
        if transaction_info.get('transactions'):
            for transaction in transaction_info.get('transactions'):
                if transaction.get('note') and 'asset-config-transaction' in transaction:                   
                    note = base64.b64decode(transaction.get('note')).decode('utf-8')
                    if note.startswith('{') and "arc69" in note:
                        
                        try:                            
                            metadata = {
                                'txid':transaction['id'],
                                'confirmed-round': transaction['confirmed-round'],
                                'round-time': transaction['round-time'],
                                'note': transaction['note']
                            }          
                            break
                        except:
                            print("note could not be converted to JSON")
            if metadata:
                return metadata                          
            else:
                print (f"cannot find {asset_id}'s metadata in acfg")
                return metadata

    def get_arc69_meta_data(self,asset_id,creator=None,min_round=None):

        out = {}
        if type(asset_id) == int:
           res = self._get_single_nft_arc69_metadata(asset_id,creator=creator)
           if res:
               out[asset_id] =res

        elif type(asset_id) == list:
            
            nft_not_found=[]
            if not creator:
                raise ValueError (f"creator cannot be none if asset id is a list")
            transaction_info=self.search_transactions(address=creator,txn_type='acfg',min_round=min_round)            
            if transaction_info.get('transactions'):
                for nft_id in asset_id:
                    nft_found = False
                    if transaction_info.get('transactions'):
                        for transaction in transaction_info['transactions']:                        
                            if transaction.get('created-asset-index') == nft_id or transaction.get('asset-config-transaction').get('asset-id') == nft_id:                                
                                nft_found = True 
                                if transaction.get('note') and 'asset-config-transaction' in transaction:                   
                                    note = base64.b64decode(transaction.get('note')).decode('utf-8')
                                    if note.startswith('{') and "arc69" in note:
                                        try:
                                            metadata = {
                                                'txid':transaction['id'],
                                                'confirmed-round': transaction['confirmed-round'],
                                                'round-time': transaction['round-time'],
                                                'note': transaction['note']
                                            }        
                                            out[nft_id]=metadata                                                            
                                            break
                                        except:
                                            print("note could not be converted to JSON")
                    if not nft_found:
                        nft_not_found.append(nft_id)
               
                if len(nft_not_found):                    
                    for nft_id in nft_not_found: 
                        print(f"search metadata for {nft_id}")
                        metadata = self._get_single_nft_arc69_metadata(nft_id,creator,min_round=min_round)                        
                        if type(metadata) == dict:
                            out[nft_id] = metadata
              
            else:
                print(f"cannot find nfts in address {creator}")                
                
        else:
            print(f"asset_id is {asset_id} - unknown type")
        
        return out




 

