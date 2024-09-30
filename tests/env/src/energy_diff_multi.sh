#!/bin/bash

x=$(cat /sys/cray/pm_counters/energy) 

h=$(hostname)

echo $x &> $h

sleep 5

cat /sys/cray/pm_counters/energy >> $h

