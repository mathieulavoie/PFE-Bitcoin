import AddressUtils

__author__ = 'Mathieu'

import sys
import NetworkGraph
import Settings
import BlockchainCrawler
from multiprocessing.context import  Process


class GraphBuilder(BlockchainCrawler.BlockchainCrawler):
    def __init__(self):
        super().__init__()
        self.to_crawl =[]
        self.crawled = []
        self.network_graph = NetworkGraph.Network(Settings.db_server,Settings.db_port)

    def do_work(self,inputs, outputs):
        self.network_graph.process_transaction_data(inputs, outputs)

def start():
        builder = GraphBuilder()
        start_block_id  = int(sys.argv[1])
        block_id = start_block_id
        process = None
        try:
            while builder.crawl_block(block_id):
                print("Block %d crawled" % block_id)

                if block_id - start_block_id > 0 and (block_id - start_block_id) % Settings.block_crawling_limit == 0:
                    builder.network_graph.check_integrity()
                    while  process is not None and process.is_alive():
                        print("Waiting for insertion thread to complete...")
                        process.join()

                    if process is not None and process.exitcode > 0 : #error
                        raise Exception("Errorcode %d in DB Sync Thread, aborting" % process.exitcode)
                    process = Process(target=builder.network_graph.synchronize_mongo_db)
                    process.start()
                    builder.network_graph = NetworkGraph.Network(Settings.db_server,Settings.db_port) #Starting a new graph while other graph data is inserted.

                if process is not None and not process.is_alive() and process.exitcode > 0 : #error
                        raise Exception("Errorcode %d in DB Sync Thread, aborting" % process.exitcode)
                block_id+=1

            #Finished Crawling, Flushing to DB.
            #Waiting for any previous DB Sync
            while  process is not None and process.is_alive():
                print("Waiting for insertion thread to complete...")
                process.join()

            #Sync the rest
            process = Process(target=builder.network_graph.synchronize_mongo_db)
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
        print("Usage: python GraphBuilder.py <starting block id>")