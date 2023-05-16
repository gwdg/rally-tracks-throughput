#!/bin/bash
wc -l data.json | awk '{print $1}'
