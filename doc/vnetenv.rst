######################################################
はじめに
######################################################

本書ではFreeBSD 14.0およびbhyveを使用した仮想ネットワーク環境の
構築手順を説明する。

*******************************
ハードウェア
*******************************

本書では以下のハードウェア構成において動作確認を行っている。

+------------+----------------------------+-------------+
|項目        | 型番・スペック             | 備考        |
+============+============================+=============+
|PC          | DELL Optiplex 7060 Micro   |             |
+------------+----------------------------+-------------+
|  CPU       | Intel Core i5-8500         | 6 CPUs      |
+------------+----------------------------+-------------+
|  Memory    | 16 GB                      |             |
+------------+----------------------------+-------------+

+------------+----------------------------+-------------+
|項目        | 型番・スペック             | 備考        |
+============+============================+=============+
|PC          | CF-RZ4                     |             |
+------------+----------------------------+-------------+
|  CPU       | Intel Core M-5Y71          | 1.20 GHz    |
+------------+----------------------------+-------------+
|  Memory    | 4 GB (DDR3)                |             |
+------------+----------------------------+-------------+
|  Storage   | 128 GB (SATA AHCI)         |             |
+------------+----------------------------+-------------+

*******************************
ソフトウェア
*******************************

ホストPC
===================================

OS: FreeBSD 14.0-RELEASE-p6, amd64

vm-bhyve 1.5.0

NAT用仮想マシンOS
===================================

NAT用仮想マシンのOSにはNAT機能を備えているOPNsenseを採用する。

+------------+----------------------------+-------------+
|項目        | 型番・スペック             | 備考        |
+============+============================+=============+
|OS          | OPNsense 24.1              |             |
+------------+----------------------------+-------------+

クライアント用仮想マシンOS
===================================

+----------------------------+------------------------------------------------+
| OS                         | 備考                                           |
+============================+================================================+
| NetBSD 10.0 amd64          |                                                |
+----------------------------+------------------------------------------------+
| Alpine 3.19.1 x86_64       |                                                |
+----------------------------+------------------------------------------------+
| Rocky Linux 9.3 x86_64     | GRUBでシリアルコンソール有効化が必要           |
+----------------------------+------------------------------------------------+

###############################################################
ネットワーク構成
###############################################################

*******************************
ネットワーク構成図
*******************************

本書では以下のネットワーク構成を作成する。

.. code-block::

   <Host Area>               <Bridge Area>       <Virtual Switch/Machine Area>

   +-------------------+     +-------------+     +------------------+
   | host              |     | bridge1     |     | sw1              |
   |   em0:            | NAT |             |     | (no ip addr)     |
   |   192.168.0.53/24 |-----| 192.168.1.1 |-----|                  |
   +-------------------+     +-------------+     +------------------+
                                                   |
                                                   +------------------------+
                                                                            |
                                                                          +--------------------------+
                                                 +------------------+     |   vnet1: 192.168.1.10/24 |
                                                 | sw10             |     |                          |
                                                 | 192.168.10.84/24 |-----| hostname: opnsense10     |
                                                 |                  |     |   gw: 192.168.1.1        |
                                                 +------------------+     |                          |
                                                   |                      |   vnet0: 192.168.10.1/24 |
                                                   |                      +--------------------------+
                                                   |
                                                   +------------------------+
                                                                            |
                                                                          +---------------------------+
                                                 +------------------+     |   vnet1: 192.168.10.20/24 |
                                                 | sw20             |     |                           |
                                                 | 192.168.20.84/24 |-----| hostname: opnsense20      |
                                                 |                  |     |   gw:    192.168.10.1     |
                                                 +------------------+     |                           | 
                                                   |                      |   vnet0: 192.168.20.1/24  |
                                                   |                      +---------------------------+
                                                   |
                              +--------------------+-----------------------------------+
                              |                                                        |
                          +---------------------------+                            +---------------------------+
   +------------------+   |   vnet1: 192.168.20.30/24 |     +------------------+   |   vnet1: 192.168.20.31/24 |
   | sw30             |   |                           |     | sw31             |   |                           |
   | 192.168.30.84/24 |---| hostname: opnsense30      |     | 192.168.31.84/24 |---| hostname: opnsense31      |
   |                  |   |   gw:    192.168.20.1     |     |                  |   |   gw:    192.168.20.1     |
   +------------------+   |                           |     +------------------+   |                           |
                          |   vnet0: 192.168.30.1/24  |                            |   vnet0: 192.168.31.1/24  |
                          +---------------------------+                            +---------------------------+

*******************************
ネットワーク構成詳細
*******************************

ネットワークセグメント
===================================

単一のホスト内に以下の４つの仮想ネットワークセグメントを作成する。

+-------------------------------+----------------------+----------------------+
| セグメント                    | ネットワーク         | 備考                 |
+===============================+======================+======================+
| 物理ネットワークセグメント0   | 192.168.0.0/24       | ホストが所属         |
+-------------------------------+----------------------+----------------------+
| 仮想ネットワークセグメント1   | 192.168.1.0/24       |                      |
+-------------------------------+----------------------+----------------------+
| 仮想ネットワークセグメント10  | 192.168.10.0/24      |                      |
+-------------------------------+----------------------+----------------------+
| 仮想ネットワークセグメント20  | 192.168.20.0/24      |                      |
+-------------------------------+----------------------+----------------------+
| 仮想ネットワークセグメント30  | 192.168.30.0/24      |                      |
+-------------------------------+----------------------+----------------------+
| 仮想ネットワークセグメント31  | 192.168.31.0/24      | 分岐構成の確認用     |
+-------------------------------+----------------------+----------------------+

NAT
==========================================================================

ホストの属するセグメント(192.168.0.0/24) と セグメント1(192.168.1.0/24) は
ホストのNAT機能を利用してセグメント1の端末が外部に接続できるようにする。

一方、仮想ネットワークセグメント間のNAT接続は、仮想スイッチ間をOPNsenseで接続することで
実現する。

hostおよびbridge/switchのIPアドレス
===================================================================

- ホスト(em0)の固定IPアドレスは任意。ここでは192.168.0.53/24とする。
- bridge1はホストの属するネットワークとは分離し、且つゲートウェイとするため、192.168.1.1/24を
  割り当てる。
- bridge1にsw1を紐付け、sw1にはIPアドレスを設定しない。
- sw10/sw20/sw30/sw31には192.168.(swのID).84/24を割り当てる。

+----------+--------------------------------+---------------------------+
| 項目     | 設定値                         | 備考                      |
+==========+================================+===========================+
| em0      | 192.168.0.53/24                | host, 固定IPアドレス      |
+----------+--------------------------------+---------------------------+
| bridge1  | 192.168.1.1/24                 |                           |
+----------+--------------------------------+---------------------------+
| sw1      | (no ip address)                |                           |
+----------+--------------------------------+---------------------------+
| sw10     | 192.168.10.84/24               |                           |
+----------+--------------------------------+---------------------------+
| sw20     | 192.168.20.84/24               |                           |
+----------+--------------------------------+---------------------------+
| sw30     | 192.168.30.84/24               |                           |
+----------+--------------------------------+---------------------------+
| sw31     | 192.168.31.84/24               |                           |
+----------+--------------------------------+---------------------------+


############################
準備
############################

**************************************
ホストOSのセットアップ
**************************************

今回は仮想ネットワークをFreeBSD上に構築する。

FreeBSDのサイトまたはミラーサイトから FreeBSD-14.0-RELEASE-amd64-disc1.iso などを入手し、
ISOファイルをUSBメモリに書き込み、USBメモリからFreeBSDのインストーラを起動させる。

USBメモリから起動するとFreeBSDのロゴが表示され起動メニューが表示されるので、
1. Boot Installerが選択されていることを確認し、Enterを押す。

.. code-block::

   1. Boot Installer [Enter]

Welcomeメッセージが表示される。
インストールを開始するか、live CDとして利用するかのメニューが表示されるので、
[Install]を選択されていることを確認し、Enterを押す。

.. code-block::

   Welcome to FreeBSD! Would you
   like to begin an installation
   or use the live CD?

   [Install]

キーマップを選択する。
矢印キーの下を押してJapanese 106を選択した状態でSpaceを押す。

.. code-block::

   Keymap Selection
   ...
   ...
   (*) Japanese 106

選択肢の一番上に戻り、jp.kbdが選択されていることを確認し、
Continueを選択してEnterを押す。

.. code-block::

   Continue with jp.kbd keymap

ホスト名を設定する。
ここではPCの型番の cfrz4 とする。

.. code-block::

   Set Hostname
   cfrz4

機能を選択する。
インストール容量を削減するために kernel-dbgを選択してSpaceを押し、
kernel-dbgの選択を外し、Enterを押す。

.. code-block::

   [ ] kernel-dbg
   ...
   [*] lib32

パーティションの設定を行う。
Auto (ZFS)を選択し、Enterを押す。 

.. code-block::

   Partitioning
   Auto (ZFS)  Guided Root-on-ZFS

ZFSの設定を行う。
ZFS poolの名前を設定する。デフォルトのzrootのままでEnterを押す。

.. code-block::

   ZFS Configuration
   zroot is already taken, please enter a name for the ZFS pool
   (Or confirm using the same name by just pressing enter)

   zroot

ZFSの設定を行う。
Installが選択されていることを確認し、Enterを押す。

.. code-block::

   ZFS Configuration
   Configure Options:
   >>> Install

ZFSの追加設定を行う。
デフォルトのstripeが選択されていることを確認し、Enterを押す。

.. code-block::

   ZFS Configuration
   stripe  Stripe - No Redundancy

ZFSに用いるストレージを指定する。
複数のストレージが選択されている場合は、ZFSに用いるストレージに
カーソルを合わせ、Spaceを押して選択し、Enterを押す。

.. code-block::

   ZFS Configuration
   [*] ada0  SAMSUNG MZNLN128HCGR-00000

ZFSの設定を行う。
表示されているストレージのコンテンツが削除される旨が表示される。
コンテンツを削除しても問題ないことを確認し、Enterを押す。


.. code-block::

   ZFS Configuration
   Last Chance! Are you sure you want to destroy
   the current contents of the following disk:

   ada0

   < YES >

インストールが開始され、base.txzなどが展開される。
処理が完了するまで待機する。

.. code-block::

   Archive Extraction
     base.txz
     kernel.txz
     lib32.txz

ブートの設定を行う。
EFIパーティションにFreeBSDのエントリーを追加する旨が表示されるので、
Enterを押す。

.. code-block::

   Boot Configuration
   There are multiple "FreeBSD" EFI
   boot entries. Would you
   like to remove them all and
   add a new one?

   < YES >

管理者アカウントのパスワードを設定する。
パスワードを２回入力する。

.. code-block::

   Please select a password for the system management account (root):
   Typed characters will not be visible.
   Changing local password for root
   New Password:

ネットワークインターフェースを選択する。
複数のネットワークインターフェース（たとえば有線LANと無線LAN）がある場合は
利用したいインターフェースを選択し、Enterを押す。

.. code-block::

   Network Configuration
   Please select a network interface to
   configure:

   em0  Intel(R) I218-LM (3)
   iwm0 Intel(R) Dual Band Wireless AC 7265

   [ OK ]

選択したネットワークインターフェースでIPv4を設定するか決定する。
デフォルトのYesが選択されていることを確認し、Enterを押す。

.. code-block::

   Network Configuration
   Would you like to configure
   IPv4 for this interface?

   [ Yes ]

選択したインターフェースでDHCPを利用するか決定する。
デフォルトのYesが選択されていることを確認し、Enterを押す。

.. code-block::

   Network Configuration
   Would you like to use DHCP
   to configure this interface?

   [ Yes ]

選択したネットワークインターフェースでIPv6を利用するか決定する。
今回はIPv6を利用しないため、TABキーを押してNoを選択し、
Enterを押す。

.. code-block::

   Network Configuration
   Would you like to configure
   IPv6 for this interface?

   [ No ]

Resolverの設定を行う。
DHCPを有効化するとDNS #1の設定が自動的に入力されている。
問題ないことを確認し、Enterを押す。

.. code-block::

   Network Configuration
   Resolver Configuration
   Search          (empty)
   IPv4 DNS #1     192.168.0.1 (automatically)
   IPv4 DNS #2     (empty)

   [ OK ]

.. code-block::

   Select local or UTC (Greenwich Mean Time) clock
   Is this machine's CMOS clock set to UTC? If it is set to local time,
   or you don't know, please choose No here!

   [ No ]

Time Zoneを設定する。5のAsiaを選択しEnterを押す。


.. code-block::

   Time Zone Selector
   Select a region

   5  Asia

国を設定する。19 Japanを選択し、Enterを押す。

.. code-block::

   Countries in Asia
   Select a country or region

   19 Japan

省略名がJSTであることを確認し、Enterを押す。

.. code-block::

   Configuration
   Does the abbreviation `JST' look reasonable?

   [ Yes ]

日付を設定する。問題ない場合は Skip を押す。

.. code-block::

   Time & Date

   [ Skip ]

時刻を設定する。問題ない場合は Skip を押す。

.. code-block::

   HH:MM:SS

   [ Skip ]

サービスの設定を行う。
sshd/ntpd/ntpd_sync_on_startのそれぞれにカーソルを合わせ、
Spaceを押して有効化する。

.. code-block::

   System Configuration

   [X] sshd
   [X] ntpd
   [X] ntpd_sync_on_start

.. code-block::

   System Hardening

   (default)

   [ OK ]

.. code-block::

   Add User Accounts
   Would you like to add
   users to the installed
   system now?

   < No >

.. code-block::

   Final Configuration

   Exit

   < OK >

.. code-block::

   Manual Configuration

   < No >

.. code-block::

   Complete

   [ Reboot ]

.. code-block::

   FreeBSD/amd64 (cfrz4) (ttyv0)

   login:


sshによるrootログインの許可
=====================================

デフォルトでは管理者のrootアカウントではssh接続できない。
一時的にrootアカウントによるsshログインを許可する。

以下のようにsshd_configを編集し、PermitRootLoginをyesに設定する。

.. code-block::

   # vi /etc/ssh/sshd_config
   ....
   ....
   PermitRootLogin yes
   ....

sshd_configを編集後、sshdを再起動する。

.. code-block::

   # service sshd restart
   
ssh接続を行う前にifconfigでFreeBSDのIPアドレスを確認する。
lo0以外のインターフェースにおいて、inetの後ろの数字列を覚えておく。

.. code-block::

   # ifconfig
   root@cfrz4:~ # ifconfig
   em0: flags=1008843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST,LOWER_UP> metric 0 mtu 1500
           options=4e524bb<RXCSUM,TXCSUM,VLAN_MTU,VLAN_HWTAGGING,JUMBO_MTU,VLAN_HWCSUM,LRO,
           WOL_MAGIC,VLAN_HWFILTER,VLAN_HWTSO,RXCSUM_IPV6,TXCSUM_IPV6,HWSTATS,MEXTPG>
           ether a8:13:74:94:ef:d9
           inet 192.168.0.53 netmask 0xffffff00 broadcast 192.168.0.255
           media: Ethernet autoselect (1000baseT <full-duplex>)
           status: active
           nd6 options=29<PERFORMNUD,IFDISABLED,AUTO_LINKLOCAL>
   lo0: flags=1008049<UP,LOOPBACK,RUNNING,MULTICAST,LOWER_UP> metric 0 mtu 16384
           options=680003<RXCSUM,TXCSUM,LINKSTATE,RXCSUM_IPV6,TXCSUM_IPV6>
           inet 127.0.0.1 netmask 0xff000000
           inet6 ::1 prefixlen 128
           inet6 fe80::1%lo0 prefixlen 64 scopeid 0x2
           groups: lo
           nd6 options=21<PERFORMNUD,AUTO_LINKLOCAL>

別のPCから覚えておいたIPアドレス宛にrootアカウントで接続する。
この際にパスワード入力を求められるので、インストール時に設定したパスワードを入力する。

.. code-block::

   # ssh 192.168.0.53 -l root
   (root@192.168.0.53) Password for root@cfrz4:
   Last login: Sun May  5 20:34:28 2024
   FreeBSD 14.0-RELEASE (GENERIC) #0 releng/14.0-n265380-f9716eee8ab4: Fri Nov 10 05:57:23 UTC 2023
   
   Welcome to FreeBSD!

   Release Notes, Errata: https://www.FreeBSD.org/releases/
   Security Advisories:   https://www.FreeBSD.org/security/
   FreeBSD Handbook:      https://www.FreeBSD.org/handbook/
   FreeBSD FAQ:           https://www.FreeBSD.org/faq/
   Questions List:        https://www.FreeBSD.org/lists/questions/
   FreeBSD Forums:        https://forums.FreeBSD.org/

   Documents installed with the system are in the /usr/local/share/doc/freebsd/
   directory, or can be installed later with:  pkg install en-freebsd-doc
   For other languages, replace "en" with a language code like de or fr.
   
   Show the version of FreeBSD installed:  freebsd-version ; uname -a
   Please include that output and any error messages when posting questions.
   Introduction to manual pages:  man man
   FreeBSD directory layout:      man hier

   To change this login announcement, see motd(5).
   root@cfrz4:~ # 
   
公開鍵認証
=====================================

sshのパスワード入力を省略する。

FreeBSDとは別のPCにおいて、事前に鍵ペアを作成する。

.. code-block::

   $ ssh-keygen -t ed25519

公開鍵（この例ではid_ed25519.pub）の内容をクリップボードにコピーし、
パスワード認証でログインしているFreeBSDの端末を用いて
.ssh/authorized_keysファイルに公開鍵の内容をペーストする。

.. code-block::

   $ cat ~/.ssh/id_ed25519.pub
   ssh-ed25519 AAA ..........

   root@cfrz4:~ # mkdir .ssh
   root@cfrz4:~ # vi .ssh/authorized_keys
   ssh-ed25519 AAA ..........

   root@cfrz4:~ # cat .ssh/authorized_keys
   ssh-ed25519 AAA ..........

一度FreeBSDへのssh接続を終了し、再度ssh接続する。
この際にパスワードの入力が求められないことを確認する。

.. code-block::

   root@cfrz4:~ # exit
   $ ssh 192.168.0.53 -l root
   (パスワード入力なし)
   ...
   root@cfrz4:~ #

パスワード認証無効化
=====================================

公開鍵認証ができるようになったため、
FreeBSD側でパスワード認証を無効化する。
通常はPasswordAuthenticationの設定がコメントアウトされているため、
行頭の#を削除する。

.. code-block::

   # vi /etc/ssh/sshd_config
   ...
   ...
   PasswordAuthentication no
   ...
   ...

sshd_configを編集後、sshdを再起動する。

.. code-block::

   # service sshd restart


パッケージインストール
=========================================================

pkgコマンドを実行すると、pkgコマンドがインストールされていない場合は
自動的にpkgコマンドがインストールされる。

.. code-block::

   root@cfrz4:~ # pkg update
   The package management tool is not yet installed on your system.
   Do you want to fetch and install it now? [y/N]: y
   Bootstrapping pkg from pkg+http://pkg.FreeBSD.org/FreeBSD:14:amd64/quarterly, please wait...
   Verifying signature with trusted certificate pkg.freebsd.org.2013102301... done
   Installing pkg-1.21.2...
   Extracting pkg-1.21.2: 100%
   Updating FreeBSD repository catalogue...
   Fetching meta.conf: 100%    178 B   0.2kB/s    00:01    
   Fetching data.pkg: 100%    7 MiB   1.8MB/s    00:04    
   Processing entries: 100%
   FreeBSD repository update completed. 34061 packages processed.
   All repositories are up to date.
   root@cfrz4:~ #

必要に応じてパッケージをインストールする。
パッケージを検索するには pkg searchコマンドを実行する。

.. code-block::

   # pkg search python3
   py39-antlr4-python3-runtime-4.9,1 ANother Tool for Language Recognition (python3 runtime)
   py39-python3-openid-3.2.0_1    Python 3 port of the python-openid library
   py39-python3-saml-1.16.0       Add SAML support to your Python software
   python3-3_3                    Meta-port for the Python interpreter 3.x
   python310-3.10.14_2            Interpreted object-oriented programming language
   python311-3.11.9               Interpreted object-oriented programming language
   python38-3.8.19_2              Interpreted object-oriented programming language
   python39-3.9.18_2              Interpreted object-oriented programming language
   unit-python39-1.32.0           Python module for NGINX Unit

パッケージをインストールするには pkg install コマンドを実行する。
以下にpython3をインストールする例を示す。

.. code-block::

   root@cfrz4:~ # pkg install python3
   Updating FreeBSD repository catalogue...
   FreeBSD repository is up to date.
   All repositories are up to date.
   Updating database digests format: 100%
   The following 7 package(s) will be affected (of 0 checked):

   New packages to be INSTALLED:
           gettext-runtime: 0.22.5
           indexinfo: 0.3.1
           libffi: 3.4.4_1
           mpdecimal: 4.0.0
           python3: 3_3
           python39: 3.9.18_2
           readline: 8.2.10

   Number of packages to be installed: 7

   The process will require 123 MiB more space.
   19 MiB to be downloaded.

   Proceed with this action? [y/N]: y
   [1/7] Fetching indexinfo-0.3.1.pkg: 100%    6 KiB   6.0kB/s    00:01
   [2/7] Fetching mpdecimal-4.0.0.pkg: 100%  158 KiB 161.4kB/s    00:01
   [3/7] Fetching python39-3.9.18_2.pkg: 100%   19 MiB   1.8MB/s    00:11
   [4/7] Fetching libffi-3.4.4_1.pkg: 100%   44 KiB  45.5kB/s    00:01
   [5/7] Fetching readline-8.2.10.pkg: 100%  396 KiB 405.9kB/s    00:01
   [6/7] Fetching python3-3_3.pkg: 100%    1 KiB   1.1kB/s    00:01
   [7/7] Fetching gettext-runtime-0.22.5.pkg: 100%  231 KiB 236.7kB/s    00:01
   Checking integrity... done (0 conflicting)
   [1/7] Installing indexinfo-0.3.1...
   [1/7] Extracting indexinfo-0.3.1: 100%
   [2/7] Installing mpdecimal-4.0.0...
   [2/7] Extracting mpdecimal-4.0.0: 100%
   [3/7] Installing libffi-3.4.4_1...
   [3/7] Extracting libffi-3.4.4_1: 100%
   [4/7] Installing readline-8.2.10...
   [4/7] Extracting readline-8.2.10: 100%
   [5/7] Installing gettext-runtime-0.22.5...
   [5/7] Extracting gettext-runtime-0.22.5: 100%
   [6/7] Installing python39-3.9.18_2...
   [6/7] Extracting python39-3.9.18_2: 100%
   [7/7] Installing python3-3_3...
   [7/7] Extracting python3-3_3: 100%
   =====
   Message from python39-3.9.18_2:

   --
   Note that some standard Python modules are provided as separate ports
   as they require additional dependencies. They are available as:

   py39-gdbm       databases/py-gdbm@py39
   py39-sqlite3    databases/py-sqlite3@py39
   py39-tkinter    x11-toolkits/py-tkinter@py39
   root@cfrz4:~ #

IPアドレス設定
=====================================

FreeBSDの固定IPアドレスを設定する。
/etc/rc.confのifconfig_em0の値を以下のように修正する。

.. code-block::

   # vi /etc/rc.conf
   ...
   ...
   # ifconfig_em0="DHCP"    <-- コメントアウト
   ifconfig_em0="inet 192.168.0.53 netmask 255.255.255.0"
   defaultrouter="192.168.0.1"
   ...
   ...

********************************************************
NAT
********************************************************

NATを利用するため、/boot/loader.conf に以下を追記する。

.. code-block::

   # vi /boot/loader.conf
   ...
   ...
   ipfw_load="YES"
   ipdivert_load="YES"
   net.inet.ip.fw.default_to_accept="1"

また、ブリッジを作成するため、以下を/etc/rc.confに追記する。

.. code-block::

   # vi /etc/rc.conf
   ...
   ...
   cloned_interfaces="bridge1"
   ifconfig_bridge1="inet 192.168.1.1 netmask 255.255.255.0"

設定後、FreeBSDを再起動する。

再起動後、ifconfigコマンドを実行し、bridge1のIPアドレスが適切に設定されているか確認する。

.. code-block::

   root@cfrz4:~ # ifconfig bridge1
   bridge1: flags=1008843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST,LOWER_UP> metric 0 mtu 1500
           options=0
           ether 58:9c:fc:10:ff:80
           inet 192.168.1.1 netmask 0xffffff00 broadcast 192.168.1.255
           id 00:00:00:00:00:00 priority 32768 hellotime 2 fwddelay 15
           maxage 20 holdcnt 6 proto rstp maxaddr 2000 timeout 1200
           root id 00:00:00:00:00:00 priority 32768 ifcost 0 port 0
           groups: bridge
           nd6 options=9<PERFORMNUD,IFDISABLED>
   root@cfrz4:~ #

また、bridge1のIPアドレス宛にsshでログインできるか確認する。

.. code-block::

   root@cfrz4:~ # ssh 192.168.1.1
   The authenticity of host '192.168.1.1 (192.168.1.1)' can't be established.
   ED25519 key fingerprint is SHA256:6dVRINBd/0RikzGtxLItFBrP/+oGuPNaxmIYUR2plzg.
   This key is not known by any other names.
   Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
   Warning: Permanently added '192.168.1.1' (ED25519) to the list of known hosts.
   (root@192.168.1.1) Password for root@cfrz4:
   Last login: Sun May  5 21:49:08 2024 from 192.168.0.98
   FreeBSD 14.0-RELEASE (GENERIC) #0 releng/14.0-n265380-f9716eee8ab4: Fri Nov 10 05:57:23 UTC 2023

   Welcome to FreeBSD!

   Release Notes, Errata: https://www.FreeBSD.org/releases/
   Security Advisories:   https://www.FreeBSD.org/security/
   FreeBSD Handbook:      https://www.FreeBSD.org/handbook/
   FreeBSD FAQ:           https://www.FreeBSD.org/faq/
   Questions List:        https://www.FreeBSD.org/lists/questions/
   FreeBSD Forums:        https://forums.FreeBSD.org/

   Documents installed with the system are in the /usr/local/share/doc/freebsd/
   directory, or can be installed later with:  pkg install en-freebsd-doc
   For other languages, replace "en" with a language code like de or fr.

   Show the version of FreeBSD installed:  freebsd-version ; uname -a
   Please include that output and any error messages when posting questions.
   Introduction to manual pages:  man man
   FreeBSD directory layout:      man hier

   To change this login announcement, see motd(5).
   root@cfrz4:~ #

exitコマンドを実行し、bridge1のIPアドレスへの接続が切断されたことを確認する。

.. code-block::

   root@cfrz4:~ # exit
   Connection to 192.168.1.1 closed.
   root@cfrz4:~ #

NAT設定
=====================================

.. code-block::

   # vi /etc/rc.conf
   ...
   ...
   gateway_enable="YES"
   firewall_enable="YES"
   firewall_type="OPEN"
   
   natd_enable="YES"
   natd_interface="em0"
   natd_flags="-f /etc/natd.conf"


.. code-block::

   # vi /etc/natd.conf
   log
   log_denied
   use_sockets
   same_ports
   unregistered_only
   log_ipfw_denied


上記の設定後、FreeBSDを再起動させる。

.. code-block::

   # reboot

**********************************************
bhyve
**********************************************

bhyve用パッケージインストール
==============================================

.. code-block::

   # pkg install vm-bhyve bhyve-firmware grub2-bhyve

bhyve設定
==============================================

.. code-block::

   # zfs create -o mountpoint=/vm zroot/vm

.. code-block:: text

   # vi /etc/rc.conf
   ...
   ...
   vm_enable="YES"
   vm_dir="zfs:zroot/vm"
   vm_delay="5"

.. code-block::

   # vm init


############################
OPNsense
############################

**********************************************
IPアドレス設定
**********************************************

WAN Interface
==============================================

WANインターフェースのIPアドレス変更は、LANインターフェースにSSH接続した
状態で行う。

SSH接続後、OPNsense Shellを起動する。

.. code-block::

   # /usr/local/sbin/opnsense-shell


.. code-block::

    LAN (vtnet0)    -> v4: 192.168.10.1/24                          
    WAN (vtnet1)    -> v4: 192.168.1.254/24                         
                                                                 
    HTTPS: SHA256 D1 58 0B F7 62 6C 8F 17 33 2A 40 FF FC DF 23 92   
               EA CD 3D 5A B2 48 F2 34 B2 36 C8 C4 10 EA EB 2F   
    SSH:   SHA256 5UTNw8eHIek9Vh2tZifKRxkLQVNyNfbwfwiu96VX5KQ (ECDSA)                                                                 
    SSH:   SHA256 WleszrpbMwDYvND6nXB3kmT78tYACFfffZBnUZmUEio (ED25519)                                                               
    SSH:   SHA256 AhuEnrDmBmHrkCOPqMkOinYbWymlFYFTjYFuulcw8GU (RSA) 
                                                                                                                                   
     0) Logout                              7) Ping host            
     1) Assign interfaces                   8) Shell                
     2) Set interface IP address            9) pfTop                
     3) Reset the root password            10) Firewall log         
     4) Reset to factory defaults          11) Reload all services  
     5) Power off system                   12) Update from console  
     6) Reboot system                      13) Restore a backup

    Enter an option:

.. code-block::
    
   Enter an option: 2


.. code-block::

   Available interfaces:

   1 - LAN (vtnet0 - static)
   2 - WAN (vtnet1 - static)

   Enter the number of the interface to configure: 2

.. code-block::

   Configure IPv4 address WAN interface via DHCP? [Y/n] n

.. code-block::

   Enter the new WAN IPv4 address. Press <ENTER> for none:
   > 192.168.1.10

.. code-block::

   Subnet masks are entered as bit counts (like CIDR notation).
   e.g. 255.255.255.0 = 24
        255.255.0.0   = 16
        255.0.0.0     = 8

   Enter the new WAN IPv4 subnet bit count (1 to 32):
   > 24

.. code-block::

   For a WAN, enter the new WAN IPv4 upstream gateway address.
   For a LAN, press <ENTER> for none:
   > 192.168.1.1

.. code-block::

   Do you want to use the gateway as the IPv4 name server, too? [Y/n] n
   Enter the IPv4 name server or press <ENTER> for none:
   > 192.168.0.1

.. code-block::

   Configure IPv6 address WAN interface via DHCP6? [Y/n] n

WAN側ではIPv6を使用しないため、IPv6アドレスの入力は空欄とする。

.. code-block::

   Enter the new WAN IPv6 address. Press <ENTER> for none:
   > 

Web GUIのプロトコルをhttpsからhttpに変更するか尋ねられるが、
httpsを維持するためNを入力する。

.. code-block::

   Do you want to change the web GUI protocol from HTTPS to HTTP? [y/N] 

自己署名書を再生成するか尋ねられるが、
現状のものを利用するためNを入力する。

.. code-block::

   Do you want to generate a new self-signed web GUI certificate? [y/N] 

Web GUIのアクセスをデフォルト状態に復元するか尋ねられるが、
現状のままにするためNを入力する。

.. code-block::

   Restore web GUI access defaults? [y/N] 

#################################################
参考文献
#################################################

FreeBSD Handbook, Chapter 31 Advanced Networking, 31.9 Network Address Translation

https://docs-archive.freebsd.org/doc/7.4-RELEASE/usr/share/doc/handbook/network-natd.html


