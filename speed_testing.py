import requests
import dns.resolver
import json
from time import time


class DnsResponse():
    url = None
    ip = None
    response_time = None

    def __init__(self, url, ip, response_time):
        self.url = url
        self.ip = ip
        self.response_time = response_time

    def __str__(self):
        return self.url + "," + self.ip + "," + str(self.response_time)


def main():
    urls = get_top_500_domains()
    dns_over_https_responses = {}
    dns_responses = {}

    # Make the output csv files
    results_file = open('results.csv', 'w')
    results_file.write("url, ip, doh response time, dns response time\n")
    for i in range(5):
        for url in urls:
            # Measure the time for each DoH request
            doh_response = DnsOverHTTPSRequest(url)

            if doh_response is None:
                results_file.write(url + ',,,\n')  # FOR TESTING ####
                continue

            # Measure the time for each DNS request
            dns_response = DnsRequest(url)
            if dns_response is None:
                results_file.write(url + ',,,\n')  # FOR TESTING ####
                continue

            if i == 0:  # Init the responsed dict
                dns_over_https_responses[url] = [doh_response]
                dns_responses[url] = [dns_response]
            else:
               if url in dns_over_https_responses.keys() and url in dns_over_https_responses.keys():  # check that there is data
                    dns_over_https_responses[url].append(doh_response)
                    dns_responses[url].append(dns_response)

            
            try:
                if dns_response.response_time < doh_response.response_time:
                    print "DNS was faster for: " + url + " in " + \
                        str(doh_response.response_time -
                            dns_response.response_time)
                else:
                    print "DoH was faster for: " + url + " in " + \
                        str(dns_response.response_time -
                            doh_response.response_time)
            except:
                pass

    # Write the results to a file
    for url in url:
        if url in dns_over_https_responses.keys() and url in dns_over_https_responses.keys():  # check that there is data
            results_file.write('{0},{1},{2},{3}\n'.format(url, dns_responses[url].ip, average_respnose_time(
                dns_over_https_responses[url]), average_respnose_time(dns_responses[url])))

    results_file.close()


def get_top_500_domains():
    ''' Returns a list with the top 500 domains
    '''
    file = open("top500domains.csv", 'r')
    urls = file.readlines()
    # Strip the new lines from the urls
    for index in range(len(urls)):
        urls[index] = urls[index].strip('\n')
    return urls


def DnsOverHTTPSRequest(request_url):
    """Makes a Dns over HTTPS request for Cloudflare's server.

    Arguments:
        url {string} -- The url to resolve
    """

    # A required parameter for the Cloudflare DNS server
    headers = {'accept': 'application/dns-json'}

    cloudflare_url = "https://cloudflare-dns.com/dns-query?name={0}&type=A".format(
        request_url)
    # Measure the time for the request
    start = time()
    req = requests.get(cloudflare_url, headers=headers)
    end = time()
    if req.status_code != 200:
        # An error was occured
        print "error was occured with: " + request_url
        return None
    # The response is a JSON, so we parse it to extract the IP address
    req = json.loads(req.content)

    # If no IP address was found
    if not req.has_key('Answer'):
        return None

    ip = req["Answer"][0]['data']
    return DnsResponse(request_url, ip, (end - start) * 1000)


def DnsRequest(request_url):
    my_resolver = dns.resolver.Resolver()
    # 1.1.1.1 is CloudFlare's public DNS server
    my_resolver.nameservers = ['1.1.1.1']

    try:
        start = time()
        answer = my_resolver.query(request_url)
        end = time()
    except:
        print "An error occured with: " + request_url
        return None

    ip = answer[0].to_text()
    return DnsResponse(request_url, ip, (end - start) * 1000)


def average_respnose_time(responses):
    sum = 0.0
    count = 0.0
    for response in responses:
        sum += response.response_time
        count += 1

    return sum / count


if __name__ == "__main__":
    main()
