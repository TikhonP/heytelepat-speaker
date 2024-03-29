#!/bin/bash

cd .. # Exit to root directory `heytelepat-speaker`

RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Parse arguments
SKIP_DEPENDENCIES=0
REQUIREMENTS="src/requirements.txt"
DEVELOPMENT=0
while getopts "h?sdr:" opt; do
  case "$opt" in
  h | \?)
    echo "usage: ./install.sh [-h] [-s] [-d] [-r REQUIREMENTS]"
    exit 0
    ;;
  s)
    SKIP_DEPENDENCIES=1
    ;;
  d)
    DEVELOPMENT=1
    ;;
  r)
    REQUIREMENTS=$OPTARG
    ;;
  esac
done

shift $((OPTIND - 1))

[ "${1:-}" = "--" ] && shift

if ((SKIP_DEPENDENCIES == 1)); then
  echo -e "${YELLOW}Skipping apt-get dependencies installation...${NC}"
else
  # Installing all apt-get dependencies -------------------------------------------------------

  echo -n "Installing all apt-get dependencies..."
  if {
    sudo apt update
    sudo apt install portaudio19-dev libatlas-base-dev build-essential libssl-dev libffi-dev -y
    sudo apt install libportaudio0 libportaudio2 libportaudiocpp0 -y
  }; then
    echo -e "   ${GREEN}[ OK ]${NC}"
  else
    echo -e "   ${RED}[ FAILED ]${NC}"
  fi

  # Python 3.9

  if python3.9 -V; then
    echo "Python 3.9 already installed, version: $(python3.9 -V 2>&1 | grep -Po '(?<=Python )(.+)')"
  else
    echo "Installing python 3.9"
    cd installation || exit
    ./install_python3.9.sh && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"
    cd ..
  fi

  # Installing voice card driver ---------------------------

  echo "Installing voice card driver..."
  if {
    git clone https://github.com/respeaker/seeed-voicecard.git
    cd seeed-voicecard || exit
    sudo ./install.sh
    cd ..
    rm -rf seeed-voicecard
  }; then
    echo -e "   ${GREEN}[ OK ]${NC}"
  else
    echo -e "   ${RED}[ FAILED ]${NC}"
  fi

  sudo apt install libasound2-plugins
fi

# Creating python venv and installing pip dependencies

echo -n "Setting up python environment..."
if ((DEVELOPMENT == 1)); then
  echo -n -e "\n${YELLOW}Development mode. Setting python to \`python\` instead of \`python3.9\`...${NC}"
  python=python
else
  python=python3.9
fi
{
  # shellcheck disable=SC2091
  $python -m venv env
  source env/bin/activate
  env/bin/pip install -U pip
} >/dev/null && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

echo -n "Installing python requirements from \`$REQUIREMENTS\`, may take a while..."

env/bin/pip install -r "$REQUIREMENTS" && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

# Compiling grpcio

if ((SKIP_DEPENDENCIES == 1)); then
  echo -e "${YELLOW}Skipping grpcio building...${NC}"
else
  echo -n "Compiling gRPCio..."

  GRPC_RELEASE_TAG="v1.39.1"
  REPO_ROOT="grpc"
  {
    env/bin/pip uninstall grpcio
    git clone -b $GRPC_RELEASE_TAG https://github.com/grpc/grpc $REPO_ROOT
    cd $REPO_ROOT || exit
    git submodule update --init
    ../env/bin/pip install -rrequirements.txt
    GRPC_PYTHON_BUILD_WITH_CYTHON=1 ../env/bin/pip install .
  } >/dev/null && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"
fi

# Linking libffi.so

echo -n "Linking libffi.so from 6 to 7..."
{
  sudo ln -s /usr/lib/arm-linux-gnueabihf/libffi.so.6 /usr/lib/arm-linux-gnueabihf/libffi.so.7
} >/dev/null && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

# Creating systemd services --------

echo -n "Creating systemd services..."
cd installation || exit
mkdir services
../env/bin/python render_services.py "$USER" services && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"
if ((DEVELOPMENT == 1)); then
  echo -e "${YELLOW}Development mode. Skipping setting up services...${NC}"
else
  echo -n "Putting generated units into \`/etc/systemd/system/\`..."
  sudo mv -v services/* /etc/systemd/system/ >/dev/null && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"
  echo -n "Running daemon-reload..."
  sudo systemctl daemon-reload && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"
  rm -rf services
fi
cd ..

# UPDATING DEPRECATED TOKEN NEEDED
# Updating speaker to last version
#cd updater || exit
#../env/bin/python update.py --update_only || exit
#cd ..

if ((DEVELOPMENT == 1)); then
  echo -e "${YELLOW}Development mode. Skipping setting up script and enabling services...${NC}"
  exit
fi

# Granting SUDO to python executable scripts and wpa_supplicant
echo -n "Granting SUDO to shell executable scripts..."
# Scripts: src/network/add_network.sh, src/network/connect_network.sh,
# updater/start_speaker_service.sh, updater/stop_speaker_service.sh,

{
  sudo chown root:root src/network/add_network.sh src/network/connect_network.sh \
    updater/start_speaker_service.sh updater/stop_speaker_service.sh
  sudo chmod 700 src/network/add_network.sh src/network/connect_network.sh \
    updater/start_speaker_service.sh updater/stop_speaker_service.sh
  sudo chmod u+w /etc/wpa_supplicant/wpa_supplicant.conf
} >/dev/null && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

# Configuring wpa_supplicant

echo -n "Configuring wpa_supplicant..."
{
  echo "auto wlan0" | sudo tee -a /etc/network/interfaces
  echo "iface wlan0 inet manual" | sudo tee -a /etc/network/interfaces
  echo "wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf" | sudo tee -a /etc/network/interfaces
} >/dev/null && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

# Store cash for network connection

echo -n "Storing cash audio for network connection..."
cd src || exit
../env/bin/python speaker.py --store_cash >/dev/null && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"
cd ..
# Enabling system services ---------

echo -n "Enabling speaker service..."
sudo systemctl enable speaker >/dev/null && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

echo -n "Enabling speaker_updater service and timer and speaker_issue_manager..."
{
  sudo systemctl enable speaker_issue_manager.service speaker_updater.service speaker_updater.timer
} >/dev/null && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

echo -n "Starting speaker_updater service and timer and speaker_issue_manager..."
{
  sudo systemctl start speaker_issue_manager.service speaker_updater.service speaker_updater.timer
} >/dev/null && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

# shellcheck disable=SC1073
echo -e "${GREEN}Done!${NC} Please reboot system. To start speaker run \`sudo systemctl start speaker\`"
