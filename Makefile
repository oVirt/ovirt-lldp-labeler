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
