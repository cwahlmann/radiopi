#!/bin/bash
sudo iwlist wlan0 scan | grep -Eo "(ESSID:\".+\")|(level=[0-9]+/[0-9]+)|(Quality=[0-9]+/[0-9]+)"
