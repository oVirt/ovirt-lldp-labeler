#!/bin/bash -xe

mkdir -p exported-artifacts

mkdir -p "`rpm --eval %_topdir`" "`rpm --eval %_sourcedir`"

make rpm

cp ovirt-lldp-labeler-*.tar.gz exported-artifacts/

cp ~/rpmbuild/RPMS/noarch/ovirt-lldp-labeler-*.noarch.rpm exported-artifacts/
cp ~/rpmbuild/SRPMS/ovirt-lldp-labeler-*.src.rpm exported-artifacts/
