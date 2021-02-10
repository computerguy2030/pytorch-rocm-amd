##Ubuntu autoinstall stuff:
#Check for Ubuntu
if lsb_release -d | grep Ubuntu &> /dev/null; then
    echo 'You are using Ubuntu'
    echo '----------------------------------------------------------------------------------------------------------'
    #Check correct Ubuntu version
    if ! { lsb_release -d | grep 18.04 || lsb_release -d | grep 20.04 || lsb_release -d | grep 20.10; }; then
        echo 'You are not using either Ubuntu 18.04, 20.04, or 20.10. Please use maunal instructions and modify according to your version.'
        exit
    fi
    #Start terminal on login
    mkdir ~/.config/autostart &> /dev/null
    echo '
    [Desktop Entry]
    Type=Application
    Exec=gnome-terminal
    Hidden=false
    NoDisplay=false
    X-GNOME-Autostart-enabled=true
    Name[en_NG]=Terminal
    Name=Terminal
    Comment[en_NG]=Start Terminal On Startup
    Comment=Start Terminal On Startup
    ' > ~/.config/autostart/gnome-terminal.desktop
    #Enable auto login
    sudo sed -i 's/.*AutomaticLogin.*/ /' /etc/gdm3/custom.conf && sudo sed -i "/\[daemon\]/a AutomaticLoginEnable=True\nAutomaticLogin=$USER" /etc/gdm3/custom.conf || { sed -i 's/bash ~\/Downloads\/amd_build_script.sh//' ~/.bashrc; exit; }

    #Check for, Install, and boot 5.4 kernel
    if ! uname -r | grep 5.4 &> /dev/null; then
        while true; do
            read -p "You are not using the required kernel 5.4. This script will install this kernel, remove all others, and reboot. Installing with 5.6 not tested. If you wish to ovverride check github instructions to start from specific line. Do you want to continue? yn? " yn
            case $yn in
                [Yy]* ) break;;
                [Nn]* ) exit;;
                * ) echo "Please answer yes or no.";;
            esac
        done
        #Download .deb files for 5.4 kernel. Ubunu 20.10 does not support apt installing 5.4.
        if lsb_release -d | grep 20.10; then 
            mkdir ~/Downloads/5.4_kernel
            cd ~/Downloads/5.4_kernel
            wget -nc https://kernel.ubuntu.com/~kernel-ppa/mainline/v5.4.42/linux-headers-5.4.42-050442_5.4.42-050442.202005200734_all.deb &> /dev/null
            wget -nc https://kernel.ubuntu.com/~kernel-ppa/mainline/v5.4.42/linux-headers-5.4.42-050442-generic_5.4.42-050442.202005200734_amd64.deb &> /dev/null
            wget -nc https://kernel.ubuntu.com/~kernel-ppa/mainline/v5.4.42/linux-image-unsigned-5.4.42-050442-generic_5.4.42-050442.202005200734_amd64.deb &> /dev/null
            wget -nc https://kernel.ubuntu.com/~kernel-ppa/mainline/v5.4.42/linux-modules-5.4.42-050442-generic_5.4.42-050442.202005200734_amd64.deb &> /dev/null
            sudo dpkg -i *.deb &> /dev/null || exit
            sudo sed -i 's/GRUB_DEFAULT=.*/GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux 5.4.42-050442-generic"/' /etc/default/grub
        fi
        if { lsb_release -d | grep 18.04 || lsb_release -d | grep 20.04; }; then
            sudo apt install linux-image-5.4.0-42-generic -y &> /dev/null || exit; 
            sudo sed -i 's/GRUB_DEFAULT=.*/GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux 5.4.0-42-generic"/' /etc/default/grub;
        fi
        sudo update-grub;
        while true; do
            read -p "Are you ready to reboot? y/n " yn
            case $yn in
                [Yy]* ) echo "bash ~/Downloads/amd_build_script.sh" >> ~/.bashrc && sudo reboot || { echo 'Unable to reboot. Another process must be preventing restart eg. update manager. Please exit process and restart script. ' ; exit 1; };;
                [Nn]* ) exit;;
                * ) echo "Please answer yes or no.";;
            esac
        done
    #Remove all kernels except 5.4 
    else
        sed -i 's/bash ~\/Downloads\/amd_build_script.sh//' ~/.bashrc
        while true; do
            read -p "You are using the correct kernel version(5.4). Removing all remaining kernels. Please confirm y/n " yn
            case $yn in
                [Yy]* ) break;;
                [Nn]* ) exit;;
                * ) echo "Please answer yes or no.";;
            esac
        done
    rm -r ~/Downloads/5.4_kernel &> /dev/null
    sudo apt --purge autoremove -y $(dpkg --list | grep 'linux-image\|linux-modules\|linux-headers' | grep -v 'linux-.*5.4.*' | cut -d " " -f 3) &> /dev/null || exit
    sudo apt update
    fi

else
    echo''
    echo '----------------------------------------------------------------------------------------------------------'
    echo 'It seems you are not using Ubuntu. This script was desiged and tested on Ubuntu 18.04 and 20.04. Please use manual Instructions and modify accordingly.' 
    exit
fi


##Checking requirements:
if ! uname -r | grep '.*5.4.*'; then
    echo ''
    echo '----------------------------------------------------------------------------------------------------------'
    echo 'You do not have the correct configuration. Ensure you are booted into "Ubuntu, with Linux 5.4.0-42-generic" Please diagnose or use manual install.'
fi

sudo apt-get install git -y || exit
##Install ROCM
echo ''
echo '----------------------------------------------------------------------------------------------------------'
echo 'Installing basic packages'
sudo sed -i '/cdrom/d' /etc/apt/sources.list #For Ubuntu 20.10
sudo apt update &> /dev/null || exit
sudo apt upgrade -y &> /dev/null || exit
sudo apt dist-upgrade -y &> /dev/null || exit
sudo apt install libnuma-dev -y &> /dev/null || exit

echo 'Adding apt source'
wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add - &> /dev/null
echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/debian/ xenial main' | sudo tee /etc/apt/sources.list.d/rocm.list > /dev/null
sudo apt update &> /dev/null
echo 'Installing ROCm'
sudo apt install rocm-dkms -y || exit

##Groups
echo 'Creating and joining groups'
sudo usermod -a -G video $LOGNAME 
echo 'ADD_EXTRA_GROUPS=1' | sudo tee -a /etc/adduser.conf &> /dev/null
echo 'EXTRA_GROUPS=video' | sudo tee -a /etc/adduser.conf &> /dev/null
if { lsb_release -d | grep 20.; }; then
    sudo usermod -a -G render $LOGNAME; 
    echo 'EXTRA_GROUPS=render' | sudo tee -a /etc/adduser.conf &> /dev/null;
fi

##Reboot
echo ''
echo 'Rebooting'
while true; do
    read -p "Are you ready to reboot? y/n " yn
    case $yn in
        [Yy]* ) echo "tail -n +132 ~/Downloads/amd_build_script.sh | bash" >> ~/.bashrc && sudo reboot || { echo 'Unable to reboot. Another process must be preventing restart eg. update manager. Please exit process and restart script. '; sed -i '$d' ~/.bashrc; exit 1; };;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

##Cleanup
sed -i '$d' ~/.bashrc;
echo 'Finishing up'
export PATH=$PATH:/opt/rocm/bin:/opt/rocm/rocprofiler/bin:/opt/rocm/opencl/bin
echo 'PATH=$PATH:/opt/rocm/bin:/opt/rocm/rocprofiler/bin:/opt/rocm/opencl/bin' >> ~/.bashrc

echo ''
echo 'ROCM installed'	
echo '----------------------------------------------------------------------------------------------------------'


##Pytorch
echo ''
echo 'Cloning Pytorch (My fork)'
sleep 10
git clone https://github.com/computerguy2030/pytorch-rocm-amd.git
cd pytorch-rocm-amd || exit
echo ''
echo 'Git submodule (may take awhile)'
git submodule sync 
git submodule update --init --recursive &> /dev/null

echo ''
echo 'Pytorch downloaded'
echo '----------------------------------------------------------------------------------------------------------'

##Hipify
python3 tools/amd_build/build_amd.py > /dev/null

echo ''
echo "Pytorch HIPified"
echo '----------------------------------------------------------------------------------------------------------'

#Additional Packages:
echo 'Installing Additional Packages (this may take awhile)'
sudo apt install -y gcc cmake clang ccache llvm ocl-icd-opencl-dev
sudo apt install -y python3-pip python3 python &> /dev/null
sudo apt install -y rocrand rocblas miopen-hip miopengemm rocfft rocprim rocsparse rocm-cmake rocm-dev rocm-device-libs rocm-libs rccl hipcub rocthrust &> /dev/null
pip3 install -r requirements.txt &> /dev/null

##Wheel (Most errors will be here)
echo ''
echo '----------------------------------------------------------------------------------------------------------'
echo 'Creating .whl. Most errors will occur here. Will take long to compile'
sleep 10
RCCL_DIR=/opt/rocm/rccl/lib/cmake/rccl/ PYTORCH_ROCM_ARCH=gfx900 hip_DIR=/opt/rocm/hip/cmake/ USE_NVCC=OFF BUILD_CAFFE2_OPS=0 PATH=/usr/lib/ccache/:$PATH USE_CUDA=OFF python3 setup.py bdist_wheel

echo ''
echo 'Hardest part over'
echo '----------------------------------------------------------------------------------------------------------'


##Install
echo 'Installing Pytorch .whl'
echo ''
if sudo pip3 install dist/*.whl > /dev/null; then
    echo ''
    echo 'Pytorch installed'
    echo '----------------------------------------------------------------------------------------------------------'
else
    echo 'Install failed'
    echo '----------------------------------------------------------------------------------------------------------'
fi
