import AddressUtils

__author__ = 'Mathieu'
import bitcoin
import bitcoin.rpc
import bitcoin.core.script
import sys
import Network
from bitcoin.core import CTransaction
import binascii
from multiprocessing.context import  Process

from datetime import datetime
class TransactionCrawler:
    def __init__(self):
        self.to_crawl =[]
        self.crawled = []
        self.proxy = bitcoin.rpc.Proxy()
        self.db_server = "0.0.0.0"
        self.db_port = 27017
        self.network = Network.Network(self.db_server,self.db_port)
        self.start = datetime.now()
        self.block_crawling_limit = 5000

    def crawl_block(self,block_id):

        try:
            hash = self.proxy.getblockhash(block_id)
        except IndexError as ex:
            print("No more blocks!")
            return False

        block = self.proxy.getblock(hash)
        for tx in block.vtx[1:]: #ignore mining tx
            self.parse_transaction(tx)
        return True;

    def parse_transaction(self,transaction):
            assert isinstance(transaction,CTransaction)
            signed_script_input = []
            try:
                for vin in transaction.vin:
                    push_data_sig = vin.scriptSig[0]
                    signed_script = vin.scriptSig[1:]
                    signed_script = signed_script[push_data_sig:]
                    signed_script_input.append(signed_script)
            except:
                print("WARNING : Unable to process transation ", binascii.hexlify(transaction.GetHash()[::-1]) )
            self.network.process_transaction_data(signed_script_input, transaction.vout)


def start():
        crawler = TransactionCrawler()
        start_block_id  = int(sys.argv[1])
        block_id = start_block_id
        process = None
        try:
            while crawler.crawl_block(block_id):
                print("Block %d crawled" % block_id)

                if block_id - start_block_id > 0 and (block_id - start_block_id) % crawler.block_crawling_limit == 0:
                    crawler.network.check_integrity()
                    while  process is not None and process.is_alive():
                        print("Waiting for insertion thread to complete...")
                        process.join()

                    if process is not None and process.exitcode > 0 : #error
                        raise Exception("Errorcode %d in DB Sync Thread, aborting" % process.exitcode)
                    process = Process(target=crawler.network.synchronize_mongo_db)
                    process.start()
                    crawler.network = Network.Network(crawler.db_server,crawler.db_port) #Starting a new graph while other graph data is inserted.

                if process is not None and not process.is_alive() and process.exitcode > 0 : #error
                        raise Exception("Errorcode %d in DB Sync Thread, aborting" % process.exitcode)
                block_id+=1

            #Finished Crawling, Flushing to DB.
            #Waiting for any previous DB Sync
            while  process is not None and process.is_alive():
                print("Waiting for insertion thread to complete...")
                process.join()

            #Sync the rest
            process = Process(target=crawler.network.synchronize_mongo_db)
            process.start()
            process.join()

            #DONE!

        #For Debugging purpose
        except:
            input("An exception will rise ")
            raise


if __name__ == "__main__":
    if len(sys.argv) == 2 :
        start()
    else:
        print("Usage: python BlockchainCrawler.py <starting block id>")