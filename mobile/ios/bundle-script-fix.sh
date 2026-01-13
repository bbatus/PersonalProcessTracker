#!/bin/bash
# Fixed bundle script for React Native 0.76.6

set -e

export NODE_BINARY=node
export SOURCEMAP_FILE="${CONFIGURATION_BUILD_DIR}/${UNLOCALIZED_RESOURCES_FOLDER_PATH}/main.jsbundle.map"

WITH_ENVIRONMENT="../node_modules/react-native/scripts/xcode/with-environment.sh"
REACT_NATIVE_XCODE="../node_modules/react-native/scripts/react-native-xcode.sh"

if [ -f "$WITH_ENVIRONMENT" ]; then
  /bin/sh -c "$WITH_ENVIRONMENT $REACT_NATIVE_XCODE"
else
  /bin/sh "$REACT_NATIVE_XCODE"
fi
