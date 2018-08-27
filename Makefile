# Copyright 2018 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
NAME=ovirt-lldp-labeler
VERSION=1.0.1
GIT_VERSION=$(shell git rev-parse --short HEAD)
RELEASE=$(GIT_VERSION)
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
	cp README.adoc $(BUILD)/$(DIST_DIR)/
	cp ovirt-lldp-labeler.spec.in $(BUILD)/$(DIST_DIR)/ovirt-lldp-labeler.spec
	sed -i \
    		-e s/@RELEASE@/$(RELEASE)/ \
    		-e s/@VERSION@/$(VERSION)/ \
    		$(BUILD)/$(DIST_DIR)/ovirt-lldp-labeler.spec

	tar -zcf $(DIST_FILE) -C $(BUILD) $(DIST_DIR)
	make clean-build

rpm: dist
	mkdir -p $(RPM_SOURCE)
	cp $(DIST_FILE) $(RPM_SOURCE)
	rpmbuild -ta $(DIST_FILE)
	rm -rf $(DIST_FILE)
