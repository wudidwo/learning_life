import sys
from concurrent.futures import ThreadPoolExecutor
import threading,socket
import argparse
from tqdm import tqdm


def port_scan(ip,port):
    try:
        request=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        request.settimeout(1)
        result=request.connect_ex((ip,port))

        if result == 0:
            print("{} port is opining".format(port))
            return f"{port}"
        request.close()
    except Exception as e:
        pass
    return None

def main():
    # ip = input("input target ip")
    # start_port = input("input start port")
    # end_port = input("input end port")
    parser = argparse.ArgumentParser(description="simply port scan")
    parser.add_argument("-i",type=str,help="input target ip")
    parser.add_argument("-pt",type=int,help="target start port")
    parser.add_argument("-pe",type=int,help="target end port")
    parser.add_argument("-d",type=str,help="domain")
    args = parser.parse_args()

    if not args.i and not args.d:
        print("input a ip or a domain")
        return
    elif not args.i and args.d:
        try:
            args.i = socket.gethostbyname(args.d)
        except socket.gaierror:
            print(f"Failed to resolve domain: {args.d}")
            return
        if not args.pe:
            args.pe = 65535
        if not args.pt:
            args.pt = 1

    open_ports = []
        #创建线程池，设置最大线程数量为10
    try:
        with ThreadPoolExecutor(max_workers=10) as executor:

            ports = range(args.pt,args.pe+1)
            #for i in range(args.pt,args.pe):
                #executor.submit(port_scan,args.i,i)
            result = list(tqdm(executor.map(port_scan,[args.i] * len(ports),ports),total=len(ports),desc='processing'))


            open_ports = [res for res in result if res]
            print("\n".join(map(str,open_ports)))

    except KeyboardInterrupt:
        sys.exit()


    print("complate")


if __name__ == '__main__':
    main()


