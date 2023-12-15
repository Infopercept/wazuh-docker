#!/bin/bash

# Ensure that SDM_ADMIN_TOKEN is set in the environment
if [ -z "$SDM_ADMIN_TOKEN" ]; then
    echo "Error: SDM_ADMIN_TOKEN is not set."
    exit 1
fi

START=$(date -u -d "5 minutes ago" '+%Y-%m-%dT%H:%M:00')
END=$(date -u '+%Y-%m-%dT%H:%M:00') # End of audit slice, defaulting to now, at the top of the minute
TARGET=/var/ossec/log # Location where JSON files are written
/var/ossec/integrations/sdm audit activities --from "$START" --to "$END" -j >> "$TARGET/sdm-logs.log"
