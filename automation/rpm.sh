#!/bin/bash -xe

EXPORT_DIR="${EXPORT_DIR:=exported-artifacts}"

mkdir -p $EXPORT_DIR

mkdir -p "`rpm --eval %_topdir`" "`rpm --eval %_sourcedir`"

make rpm

cp ovirt-lldp-labeler-*.tar.gz $EXPORT_DIR/

cp ~/rpmbuild/RPMS/noarch/ovirt-lldp-labeler-*.noarch.rpm $EXPORT_DIR/
cp ~/rpmbuild/SRPMS/ovirt-lldp-labeler-*.src.rpm $EXPORT_DIR/
