

Reproducing an issue with BBR + pfifo qdisc
===========================================

To reproduce I used a fresh Debian Stretch install with 4.18 kernel from backports.debian.org, running in a KVM. This is not debian specific, I've had this issue with self compiled vanilla kernels too, nor is it KVM specific, as it happens on real hardware too::

    root@stretch:~# uname -a 
    Linux stretch 4.18.0-0.bpo.1-amd64 #1 SMP Debian 4.18.6-1~bpo9+1 (2018-09-13) x86_64 GNU/Linux
    root@stretch:~# dpkg -l | grep linux-image-4.18
    ii  linux-image-4.18.0-0.bpo.1-amd64     4.18.6-1~bpo9+1                   amd64        Linux 4.18 for 64-bit PCs

Required is to have tcp congestion control set to BBR::

    root@stretch:~# sysctl net.ipv4.tcp_congestion_control
    net.ipv4.tcp_congestion_control = bbr

and qdisc set to pfifo::

    root@stretch:~# tc qdisc show
    qdisc noqueue 0: dev lo root refcnt 2 
    qdisc pfifo_fast 0: dev ens3 root refcnt 2 bands 3 priomap  1 2 2 2 1 2 0 0 1 1 1 1 1 1 1 1

Routes::

    root@stretch:~# ip route
    default via 10.0.2.2 dev ens3 
    10.0.2.0/24 dev ens3 proto kernel scope link src 10.0.2.15 


On another box, I run a TCP server. Anything will do, I used netcat::

    while true ; do nc -l -p 9900 ; sleep 0.2 ; done

On stretch image, run ``python makeconn.py server_ip port``, which creates a socket with nodelay and keepalive. There seems to be required for the reproduction to work that the connection has some packets in send queue.

Now pull down the interface::

    ifdown ens3

``vmstat 1`` output (interrupt count goes to 200k when interface is pulled down and back to idle when brought back up)::

    root@stretch:~# vmstat 1
    procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
     r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
     0  0      0 592820  16692 204516    0    0     0     0   46   63  1  0 99  0  0
     0  0      0 592820  16692 204516    0    0     0     0   40   56  2  0 98  0  0
     0  0      0 589744  16692 204620    0    0   128     0   48   79  2  0 97  1  0
     0  0      0 589744  16692 204648    0    0     0     0   31   34  2  0 98  0  0
     0  0      0 589776  16692 204648    0    0     0     0   27   32  2  1 97  0  0
     0  0      0 589776  16692 204648    0    0     0     0   25   26  0  0 100  0  0
     0  0      0 589652  16692 204648    0    0     0     0   21   23  0  0 100  0  0
     0  0      0 588604  16696 204688    0    0     8     0   44  152  2  1 97  0  0
     0  0      0 590072  16708 204676    0    0     4    32 13299  229  1  3 95  0  1
     0  0      0 590092  16708 204688    0    0     0     0 214186   60  0  8 93  0  0
     0  0      0 590124  16708 204688    0    0     0     0 213530   29  0  3 97  0  0
     0  0      0 590124  16708 204688    0    0     0    24 208693   34  0  5 95  0  0
     0  0      0 590124  16708 204688    0    0     0     0 213226   29  3  0 97  0  0
     0  0      0 590124  16708 204688    0    0     0     0 210818   41  0  3 97  0  0
     0  0      0 590124  16716 204680    0    0     0    28 215156   62  0  7 93  0  0
     0  0      0 589964  16716 204688    0    0     0     0 213227   65  3  5 93  0  0
     1  0      0 589964  16716 204688    0    0     0   216 213257   92  0  8 93  0  0
     0  0      0 587812  16724 205212    0    0   184    48 62505  878 19 18 62  1  0
     0  0      0 587812  16724 205212    0    0     0     0   30   42  0  0 100  0  0
     0  0      0 587812  16724 205212    0    0     0     0   32   44  0  0 100  0  0
     0  0      0 587844  16724 205212    0    0     0     0   27   34  0  0 100  0  0
     0  0      0 587844  16724 205212    0    0     0     0   24   35  0  0 100  0  0
     0  0      0 587844  16732 205204    0    0     0    20   28   34  0  0 99  1  0

