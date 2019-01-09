#!/bin/bash
ifconfig $1 | grep -Eo "inet [0-9]*.[0-9]*.[0-9]*.[0-9]*" | grep -o "[0-9].*"
