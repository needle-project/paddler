#!/bin/bash

ALIAS=${1}
CONFIG_FILE=${2}
{
    echo "[program:paddler-${ALIAS}]";
    echo "process_name=%(program_name)s_%(process_num)02d";
    echo "command=/usr/local/bin/paddler -c ${CONFIG_FILE}";
    echo "autorestart=true";
    echo "autostart=true";
    echo "startsecs=5";
    echo "numprocs=2";
  } > "/etc/supervisor/conf.d/${ALIAS}.conf";

supervisorctl reread
supervisorctl update
