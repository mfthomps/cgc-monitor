make clean
make
dpkg-buildpackage -us -uc -d
sudo dpkg -i ../cgc-monitor-ida_0.1_amd64.deb
