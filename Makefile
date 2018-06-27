# Copyright 2018 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
VERSION=0.9.4
NAME=ovirt-lldp-labeler
GIT_VERSION=$(shell git rev-parse --short HEAD)
BUILD=build
DIST_DIR=$(NAME)-$(VERSION)
DIST_FILE=$(NAME)-$(VERSION).tar.gz
RPM_SOURCE=$(shell rpm --eval %_sourcedir)

all:
	@echo "Usage is make rpm"


install:
	python -m compileall .
	python -O -m compileall .
	install -d $(DESTDIR)/etc/$(NAME)/conf.d
	install -m 644 -t $(DESTDIR)/etc/$(NAME)/conf.d/ etc/ovirt-lldp-labeler.conf
	install -m 600 -t $(DESTDIR)/etc/$(NAME)/conf.d/ etc/ovirt-lldp-credentials.conf

	install -d $(DESTDIR)/usr/share/$(NAME)/labeler
	install -m 644 -t $(DESTDIR)/usr/share/$(NAME)/labeler labeler/*.py*
	install -m 644 -t $(DESTDIR)/usr/share/$(NAME)/ cli/*.py*

	install -m 644 -D scripts/ovirt-lldp-labeler.timer $(DESTDIR)/usr/lib/systemd/system/ovirt-lldp-labeler.timer
	install -m 644 -D scripts/ovirt-lldp-labeler.service $(DESTDIR)/usr/lib/systemd/system/ovirt-lldp-labeler.service



template:
	find $(BUILD) -iname '*.in' | while read f; do \
		sed \
		-e "s|@LABELER_CONFIG@|$(DESTDIR)/etc/$(NAME)/conf.d/ovirt-lldp-labeler.conf|g" \
		-e "s|@LABELER_CONFIG_CREDENTIALS@|$(DESTDIR)/etc/$(NAME)/conf.d/ovirt-lldp-credentials.conf|g" \
		$${f} > "$${f/.in/}"; \
		rm -rf $${f}; \
	done;


build:
	mkdir -p $(BUILD)/$(DIST_DIR)
	mkdir -p $(BUILD)/$(DIST_DIR)/etc
	mkdir -p $(BUILD)/$(DIST_DIR)/scripts
	cp -R src/* $(BUILD)/$(DIST_DIR)
	cp -R etc/* $(BUILD)/$(DIST_DIR)/etc
	cp -R scripts/* $(BUILD)/$(DIST_DIR)/scripts
	make template

clean:
	rm -rf $(DESTDIR)/etc/ovirt-lldp-labeler*
	rm -rf $(DESTDIR)/usr/share/ovirt-lldp-labeler*
ifdef DESTDIR
	rm -rf $(DESTDIR)
endif

clean-build:
	rm -rf $(BUILD)

dist: build
	cp Makefile $(BUILD)/$(DIST_DIR)/

	cp LICENSE $(BUILD)/$(DIST_DIR)/
	cp AUTHORS $(BUILD)/$(DIST_DIR)/
	cp ovirt-lldp-labeler.spec.in $(BUILD)/$(DIST_DIR)/ovirt-lldp-labeler.spec
	sed -i \
    		-e s/@GIT_VERSION@/$(GIT_VERSION)/ \
    		-e s/@VERSION@/$(VERSION)/ \
    		$(BUILD)/$(DIST_DIR)/ovirt-lldp-labeler.spec

	tar -zcf $(DIST_FILE) -C $(BUILD) $(DIST_DIR)
	make clean-build

rpm: dist
	mkdir -p $(RPM_SOURCE)
	cp $(DIST_FILE) $(RPM_SOURCE)
	rpmbuild -ta $(DIST_FILE)
	rm -rf $(DIST_FILE)
