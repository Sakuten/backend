#!/bin/sh

if [ ! "$CIRCLECI" ]; then
  echo "Hey, This script works only in Circle CI enviroment."
  echo "Don't run this locally."
  exit -1
fi

if [ "$CIRCLE_PR_NUMBER" ]; then
  echo "pr_$CIRCLE_PR_NUMBER"
  exit
fi

if [ "$CIRCLE_TAG" ]; then
  echo "$CIRCLE_TAG"
  exit
fi

if [ "$CIRCLE_BRANCH" == "master" ]; then
  echo "latest"
  exit
fi


echo "$CIRCLE_BRANCH" | sed 's/[^[:alnum:]._-]/_/g'
exit
