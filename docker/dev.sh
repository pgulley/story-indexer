# sourced by deploy.sh to set private, deployment-specific values
# "export" is NOT NEEDED!
#
# If you're adding variable VARIABLE here, you MUST:
# 1. add it to staging & prod configs too!!!
# 2. add an "add VARIABLE # private" line to deploy.sh
# 3. expand {{variable}} in docker-compose.yml.j2
#	(typically as VARIABLE: {{variable}})
#
# PLEASE KEEP IN SORTED ORDER!!!
#
# used by archiver.py
ARCHIVER_B2_ACCESS_KEY_ID=xxxxxxx
ARCHIVER_B2_BUCKET=NO_ARCHIVE
ARCHIVER_B2_REGION=  # MUST be empty to disable B2
ARCHIVER_B2_SECRET_ACCESS_KEY=..........
#
ARCHIVER_S3_ACCESS_KEY_ID=AKxxxxxx
ARCHIVER_S3_BUCKET=NO_ARCHIVE
ARCHIVER_S3_REGION=  # MUST be empty to disable S3
ARCHIVER_S3_SECRET_ACCESS_KEY=..........
#
ELASTICSEARCH_SNAPSHOT_REPO=
# used by {arch,hist,rss}-queuer.py (read only)
QUEUER_S3_ACCESS_KEY_ID=AKxxxxxx
QUEUER_S3_REGION=us-east-1
QUEUER_S3_SECRET_ACCESS_KEY=..........
#
# if RSS_FETCHER_URL set use rss-puller instead of rss-queuer
RSS_FETCHER_PASS=
RSS_FETCHER_URL=
RSS_FETCHER_USER=
#
# SENTRY only enabled when SENTRY_DSN is non-empty
SENTRY_DSN=
SENTRY_ENVIRONMENT=disabled_by_empty_dsn
