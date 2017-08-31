"""
Auther: Charlie Chen
Last Update: 8.31.2016

This program works on Python 3.x .
"""

import re
import csv
from IPy import IP, IPSet
import time

#Dictionaries
line_split_dict = {}#[service_obj, server_obj, protocol, port, usip_enable, ip, gateway]
ip_dict = {}#[server_name, server_ip]
ip_in_gateway = {}#[server_ip, in_gateway(Yes/No)]
ip_in_vlan = {}#[server_ip, vlan]
ip_in_range = {}#[server_ip, gateway_range]
vlan_range = {}#[vlan, gateway_range]

ip_range = []


gateway_range = IPSet([IP('255.255.255.255')])
config_name = input('\n\nImport config file : ')
f_open = open(config_name, 'rt', encoding='UTF-8', errors='ignore')
f_output = open('outout.csv','w', encoding='UTF-8')
writer = csv.writer(f_output)
csvHeader = ('Service Name','Server Name','IP','Port','Protocol','USIP enable','Gateway')
print('\n\nProcessing ...\n\n')

while True:
    line = f_open.readline().rstrip('\n')
    if 'hostName' in line:
        line_split = line.split(' ')
        hostname = line_split[3]
        csvTime_Host = ('Update Time: ', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'Device:', hostname)
        writer.writerow(csvTime_Host)
        writer.writerow(csvHeader)
        break

while True:
    line = f_open.readline().rstrip('\n')
    if not line:
        print('Process Complete!\n\nSee the result in : ~/Output.csv\n')
        break
    elif 'bind vlan' in line:#Process IP and vlan of gateway
        if ':' in line:
            continue
        elif '-ifnum' in line:
            continue
        else:
            split = line.split(' ')
            IP_range = IP(split[4]).make_net(split[5])
            vlan = split[2]
            vlan_range[vlan] = IP_range
            ip_range.append(IP_range)
            gateway_range.add(IP(IP_range))
            #print(split)

    elif 'add server' in line:#Process IP of Server
        find_ip = line.rstrip('\n').split(' ')
        if '\"' in find_ip[2]:
            server = re.findall('\"[\s\S]*\"',line)
            r = server[0]
            s = re.findall('(?<= )[\S]{1,}\"', line)
            t = s[0]
            u = find_ip.index(t)
            server_ip = find_ip[u+1]
            ip_dict[r] = server_ip
            if gateway_range.isdisjoint(IPSet([IP(server_ip)])) == False:
                ip_in_gateway[server_ip] = 'Yes'
            else:
                ip_in_gateway[server_ip] = 'No'


        else:
            server_ip = find_ip[3]
            ip_dict[find_ip[2]] = server_ip
            #print(server_ip)
            try:
                if gateway_range.isdisjoint(IPSet([IP(server_ip)])) == False:
                    ip_in_gateway[server_ip] = 'Yes'
                else:
                    ip_in_gateway[server_ip] = 'No'
            except ValueError:
                continue

    elif 'add service ' in line:#Process services information
        line_split = line.split(' ')
        m = line_split.index('service')
        n = line_split.index('-usip')
        if '\"' in line_split[2]:
            a = re.findall(r'[\S]{1,10}"', line)
            b = a[0]
            c = line_split.index(b)
            e = re.findall(r'(?<= )\"[\s\S]{,30}\"(?= \S)', line)
            if len(e) >= 2:
                if 'None' in e[1]:
                    f = e[0]
                    protocol = line_split[c+2]
                    port = line_split[c+3]
                    ip = ip_dict.get(line_split[c+1])
                    line_split_dict = line_split_dict = {'service_obj': f, 'server_obj': line_split[c+1],
                                       'protocol': protocol,
                                       'port': port, 'usip_enable': line_split[n + 1], 'ip': ip, 'gateway': ip_in_gateway[ip], 'vlan': ip_in_vlan.get(ip)}
                else:
                    f = e[1]
                    x = re.findall(r'[\S]{1,10}"', line)
                    y = x[1]
                    z = line_split.index(y)
                    protocol = line_split[z + 1]
                    port = line_split[z + 2]
                    ip = ip_dict.get(f)
                    line_split_dict = {'service_obj': e[0], 'server_obj': f,
                                       'protocol': protocol,
                                       'port': port, 'usip_enable': line_split[n + 1], 'ip': ip, 'gateway': ip_in_gateway[ip], 'vlan': ip_in_vlan.get(ip)}
            else:
                f = e[0]
                protocol = line_split[c + 2]
                port = line_split[c + 3]
                ip_dict.get(line_split[c + 1])
                line_split_dict  = {'service_obj': f, 'server_obj': line_split[c+1],
                                   'protocol': protocol,
                                   'port': port, 'usip_enable': line_split[n + 1], 'ip': ip,
                                   'gateway': ip_in_gateway[ip], 'vlan': ip_in_vlan.get(ip)}
            #print(line_split_dict)
            dict = (line_split_dict['service_obj'], line_split_dict['server_obj'], line_split_dict['ip'],
                    line_split_dict['port'], line_split_dict['protocol'], line_split_dict['usip_enable'],
                    line_split_dict['gateway'])
            writer.writerow(dict)

        elif '\"' in line_split[3]:
            a = re.findall(r'(?<= )[\S]{,30}\"', line)
            b = a[2]
            c = b.lstrip(' ')
            d = line_split.index(c)
            e = re.findall(r'(?<= )\"[\s\S]{,20}\"(?= \S)',line)
            f = e[0]
            protocol = line_split[d+1]
            port = line_split[d+2]
            ip = ip_dict.get(f)
            line_split_dict = {'service_obj': line_split[2], 'server_obj': f,
                               'protocol': protocol,
                               'port': port, 'usip_enable': line_split[n + 1], 'ip': ip, 'gateway': ip_in_gateway[ip],
                               'vlan': ip_in_vlan.get(ip)}
            dict = (line_split_dict['service_obj'], line_split_dict['server_obj'], line_split_dict['ip'],
                    line_split_dict['port'], line_split_dict['protocol'], line_split_dict['usip_enable'],
                    line_split_dict['gateway'])
            writer.writerow(dict)
        else:
            ip_dict.setdefault((line_split[m+2]), '')
            protocol = line_split[4]
            ip = ip_dict.get(line_split[m+2])
            find_port = re.findall('(?<= )\d{1,5}(?= )', line)
            line_split_dict = {'service_obj': line_split[m + 1], 'server_obj': line_split[m + 2], 'protocol': line_split[4],
                               'port': find_port[0], 'usip_enable': line_split[n + 1], 'ip': ip, 'gateway': ip_in_gateway[ip],
                               'vlan': ip_in_vlan.get(ip)}
            #print(line_split_dict)
            dict = (line_split_dict['service_obj'], line_split_dict['server_obj'], line_split_dict['ip'],
                    line_split_dict['port'], line_split_dict['protocol'], line_split_dict['usip_enable'],
                    line_split_dict['gateway'])
            writer.writerow(dict)
#print(vlan_range)
f_open.close()
f_output.close()