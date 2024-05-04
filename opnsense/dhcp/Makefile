.SUFFIXES:
.SUFFIXES: .log .txt

HOSTS = opnsense10 opnsense20 opnsense30 opnsense31

TXTFILES = $(HOSTS:=.txt)
LOGFILES = $(HOSTS:=.log)

all : text dhcp

text :
	touch $(TXTFILES)

dhcp : $(LOGFILES)

.txt.log :
	ssh -q $* cat /var/dhcpd/var/db/dhcpd.leases > $@

.PHONY : all clean dhcp

