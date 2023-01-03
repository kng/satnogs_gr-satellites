REQ = jq gr_satellites
K := $(foreach exec,$(REQ),$(if $(shell which $(exec)),some string,$(error "No $(exec) in PATH")))

ifeq ($(PREFIX),)
	PREFIX := /usr/local
endif

install: grsat-wrapper.sh find_samp_rate.py kiss_satnogs.py kiss_geoscan.py satnogs-pre satnogs-post udp.conf
	install -d $(DESTDIR)$(PREFIX)/bin/
	install -m 755 grsat-wrapper.sh $(DESTDIR)$(PREFIX)/bin/
	install -m 755 find_samp_rate.py $(DESTDIR)$(PREFIX)/bin/
	install -m 755 kiss_satnogs.py $(DESTDIR)$(PREFIX)/bin/
	install -m 755 kiss_geoscan.py $(DESTDIR)$(PREFIX)/bin/
	install -m 755 satnogs-pre $(DESTDIR)$(PREFIX)/bin/
	install -m 755 satnogs-post $(DESTDIR)$(PREFIX)/bin/
	install -d $(DESTDIR)/etc/gnuradio/conf.d/
	install -m 644 udp.conf $(DESTDIR)/etc/gnuradio/conf.d/
