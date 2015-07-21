Abstract:
Even if your only ID on the network is a public key, all Bitcoin transactions are public. By analysing that public data, we can correlate and regroup useful pieces of information.
During this talk, we will present a toolkit that, amongst other uses, makes it easier to link multiple addresses as being owned by a single user, thereby allowing you to associate address groups to a real identity using other public sources of information, and who knows, we might just be able to track down the next Silk Road…

The Tool:
This tool was presented at NorthSec 2015. It can partially deanonymize the Blockchain by regrouping data and associate it to a same entity. In this first release, you can actually regroup addresses by entity and query them using a MongoDB database.
Usage : python BlockchainCrawler.py <starting block id> 

Requirements:
- Python 3
- pytho-bitcoinlib https://github.com/petertodd/python-bitcoinlib
- pymongo


My Slides :
https://docs.google.com/presentation/d/1e1XQpVCMT9pcJF_BLILIgpNrYSaoGoISOq6CFpUiKBM/edit?usp=sharing

The Talk :
https://www.youtube.com/watch?v=hqF1k7xiSFI
