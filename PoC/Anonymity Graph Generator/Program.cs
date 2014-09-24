using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace PFE_Anonymat
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.SetWindowSize(100, 50);
            Console.SetBufferSize(100, 1000);
            List<List<string>> addrs = new List<List<string>>();
            string url = "https://blockchain.info/rawtx/{0}";
            Console.WriteLine("Enter Tx number or hash  [54690175]");
            string tx_index = Console.ReadLine();
            tx_index = String.IsNullOrEmpty(tx_index)?"54690175":tx_index;
            int last_index = 0;
            Console.WriteLine("Starting graph for tx number: {0}", tx_index);
           

            WebClient client = new WebClient();
            string data = client.DownloadString(string.Format(url, tx_index));
            var t = (JObject)JsonConvert.DeserializeObject(data);

            while (t["inputs"][0].HasValues)
            {
                //match addresses
                List<string> txAddrs = t["inputs"].Select(w => w["prev_out"]["addr"].ToString()).ToList();
                List<string> existingEntry = addrs.FirstOrDefault(u=> u.Intersect(txAddrs).Any());
                if (existingEntry != null)
                    existingEntry.AddRange(txAddrs.Except(existingEntry));
                else
                    addrs.Add(txAddrs);

                var prev_out = t["inputs"][0]["prev_out"];
                Console.WriteLine("from {0} to {1}, Tx Number: {2}",prev_out["addr"], t["out"][last_index]["addr"],tx_index);
                tx_index = prev_out["tx_index"].ToString();
                last_index = (int)prev_out["n"];
                data = client.DownloadString(string.Format(url, tx_index));
                t = (JObject)JsonConvert.DeserializeObject(data);
            }
            Console.WriteLine("Mined by {0}, Tx Index : {1}", t["out"][last_index]["addr"],t["tx_index"]);



            Console.WriteLine("\r\n\r\n Press a key to continue :");
            Console.ReadKey();
            foreach (var addr in addrs.Where(u=> u.Count > 1))
            {
                Console.WriteLine("\r\nAll those addressed belong to the same persone :");
                addr.Sort();
                Console.WriteLine(addr.Aggregate((u, v) => u + ", " + v));
            }
            Console.ReadKey();
        }
    }
}
