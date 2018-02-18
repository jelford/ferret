#! /usr/bin/env sh
set -e

export SOURCE_DATE_EPOCH=$(date +%s)
flit build
bumpversion --message "Releasing version {new_version} with SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}" $1 
flit publish
