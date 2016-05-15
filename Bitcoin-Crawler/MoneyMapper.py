import sys
import AddressUtils
import bitcoin.rpc

__author__ = 'Mathieu'
import BlockchainCrawler
import Settings
from pymongo import MongoClient

class MoneyMapper(BlockchainCrawler.BlockchainCrawler):

    def __init__(self):
        super().__init__()
        self.money_movements = []
        self.addr_utils = AddressUtils.Addressutils()

    def do_work(self,inputs, outputs):
        if len(inputs) == 0: #No Valid Tx, an empty block with only one mining tx
            return
        try:
            source = self.addr_utils.convert_hash160_to_addr(self.addr_utils.convert_public_key_to_hash160(inputs[0]))
            for out in outputs:
                dest = self.addr_utils.get_hash160_from_CScript(out.scriptPubKey)
                entry = {'block_id':self.block_id,'source_n_id':-1,'source':source,'destination_n_id':-1,'destination':dest,'amount':(out.nValue/100000000)}
                self.money_movements.append(entry)
        except Exception:
            #print("Unable to parse Tx for Money : %s" %  repr(outputs))
            return


    def insert_into_db(self):
        if len(self.money_movements) == 0:
            print("Warning: no money movements to insert. Aborting.")
            return

        client = MongoClient(Settings.db_server, Settings.db_port)
        db = client.bitcoin
        collection = db.transactions
        collection.insert_many(self.money_movements, ordered=False)
        client.close()
        print("DB Sync Finished")





def start(start_block_id):
        mapper = MoneyMapper()
        block_id = start_block_id

        try:
            while mapper.crawl_block(block_id):
                print("Money of Block %d mapped" % block_id)

                if block_id - start_block_id > 0 and (block_id - start_block_id) % Settings.block_crawling_limit == 0:
                    mapper.insert_into_db()
                    mapper.money_movements = []
                    mapper.proxy = bitcoin.rpc.Proxy()

                block_id+=1

            #Sync the rest
            mapper.insert_into_db()

            #DONE!

        #For Debugging purpose
        except:
            input("An exception will rise ")
            raise


if __name__ == "__main__":
    mapper = MoneyMapper()
    if len(sys.argv) == 2 :
        start(int(sys.argv[1]))
    else:
        print("Usage: python %s  <starting block id>" % sys.argv[0])