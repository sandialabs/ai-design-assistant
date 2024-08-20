# this file should be sourced, not executed
# Ex, should be run by:
# source buildESP.sh

# ==========================================================
if ! command -v serveCSM &> /dev/null; then
# ==========================================================
currentPWD=$(pwd)
homeDir=$HOME

rm -rf ESP
mkdir ESP

cd $currentPWD/ESP
brew upgrade gcc
unset PYTHONINC
curl -O https://acdl.mit.edu/ESP/ESP.tgz -o ESP.tgz
tar -xf $currentPWD/ESP/ESP.tgz

# may need to change these lines to accomodate correct processor
curl -O https://acdl.mit.edu/ESP/OCC770-macos-arm64.tgz -o OCC770-macos-arm64.tgz
tar -xf $currentPWD/ESP/OCC770-macos-arm64.tgz

cd $currentPWD/ESP/EngSketchPad/config
./makeEnv $currentPWD/ESP/OpenCASCADE-7.7.0
cd $currentPWD/ESP/EngSketchPad
source ESPenv.sh
cd $currentPWD/ESP/EngSketchPad/src
make

cd $homeDir

temp_file=$(mktemp)

cat << EOF > $temp_file
# ==========================================================
# Added by Ada when building ESP
# Must come before any python path settings to ensure the
# correct version of python is called
# ==========================================================
source $currentPWD/ESP/EngSketchPad/ESPenv.sh
serveCSM='$currentPWD/ESP/EngSketchPad/bin/serveCSM'
export PATH='$currentPWD/ESP/EngSketchPad/bin:\$PATH'
# ==========================================================
EOF

cat .zshenv >> $temp_file
mv $temp_file .zshenv

cd $currentPWD 

# ==========================================================
else
# ==========================================================
echo "serveCSM was detected, assuming that ESP is already installed"
return
# ==========================================================
fi
# ==========================================================