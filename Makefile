NAME=ovirt-lldp-labeler
GIT_VERSION=$(shell git rev-parse --short HEAD)
DIR_NAME=$(NAME).git$(GIT_VERSION)
BUILD=build



install: build
	install -d $(DESTDIR)/etc/$(DIR_NAME)/conf.d
	install -m 644 -t $(DESTDIR)/etc/$(DIR_NAME)/conf.d/ etc/ovirt-lldp-labeler.conf
	install -m 600 -t $(DESTDIR)/etc/$(DIR_NAME)/conf.d/ etc/ovirt-lldp-credentials.conf

	install -d $(DESTDIR)/usr/share/$(DIR_NAME)/labeler
	install -m 644 -t $(DESTDIR)/usr/share/$(DIR_NAME)/labeler ${BUILD}/labeler/*.py*
	install -m 644 -t $(DESTDIR)/usr/share/$(DIR_NAME)/ ${BUILD}/cli/*.py*
	make clean-build



template:
	find ${BUILD} -iname '*.in' | while read f; do \
		sed \
		-e "s|@LABELER_CONFIG@|$(DESTDIR)/etc/$(DIR_NAME)/conf.d/ovirt-lldp-labeler.conf|g" \
		-e "s|@LABELER_CONFIG_CREDENTIALS@|$(DESTDIR)/etc/$(DIR_NAME)/conf.d/ovirt-lldp-credentials.conf|g" \
		$${f} > "$${f/.in/}"; \
		rm -rf $${f}; \
	done;


build:
	install -d ${BUILD}
	cp -R src/* ${BUILD}
	make template

clear:
	rm -rf $(DESTDIR)/etc/ovirt-lldp-labeler*
	rm -rf $(DESTDIR)/usr/share/ovirt-lldp-labeler*
ifdef DESTDIR
	rm -rf $(DESTDIR)
endif

clean-build:
	rm -rf ${BUILD}
