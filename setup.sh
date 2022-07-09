# install dependencies
apt install -y --no-install-recommends gcc
# download submodules
cd $(dirname -- "$0";); git submodule update --init
# install flare package
cd flare; pip3 install --no-cache-dir -r requirements.txt && python3 setup.py install
#copy library to pyenv
cp -R flare/ /opt/venv/lib/python3.8/site-packages/
cd ..; pip3 install -r requirements.txt
# uninstall dependencies
apt remove -y gcc --purge && apt autoremove -y && apt clean -y
