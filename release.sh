#! /usr/bin/env sh
set -e

export SOURCE_DATE_EPOCH=$(date +%s)
bumpversion --message "Releasing version {new_version} with SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}" $1 
flit build
flit publish
