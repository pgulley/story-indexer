#!/bin/sh

. bin/func.sh

run_python indexer.workers.fetcher.csv-queuer "$@"
