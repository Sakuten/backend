#!/bin/bash

if [ ! "$TRAVIS" ]; then
  echo "Hey, This script works only in Travis CI enviroment."
  echo "Don't run this locally."
  exit -1
fi

if [ "$TRAVIS_PULL_REQUEST" != "false" ]; then
  echo "pr_$TRAVIS_PULL_REQUEST"
  exit
fi
