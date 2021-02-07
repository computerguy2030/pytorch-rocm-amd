<h1>MY FORK: </h1>

<h3>WHY: </h3>
I am creating this fork to create a simple guide for installing pytorch on AMD cards and listing some usefull general usefull information on AMD Machine Learning after being incredibly frustrated for several days of being unable to figure out how to install Pytorch while trying out DeOldify, a ML project for colorizing video. I am also creating a DeOldify fork with instructions for an AMD build. Hope this will help someone get a basic understanding of ML on AMD without the hassles I endured.

<h3>Pytorch Information: </h3>
Running Pytorch on AMD requires the ROCm platform. ROCm is AMD open source alternative to CUDA which is unfortunately not widely used. AMD's official Pytorch/ROCM documentation unfortunately only provides a docker container and no instructions for bare metal/native install. Instructions posted here are mainly sourced from two tutorials I found after dumpster diving the internet: <br>

* https://github.com/aieater/rocm_pytorch_informations/tree/cf102198afb4dd2e94bf2c9724b9d1d54291b210#GPU-visibly-masking-and-multiple-GPUs <br>
* https://lernapparat.de/pytorch-rocm/ <br>

<br>
<h3>Instructions: </h3>

**These instructions/scripts were tested with fresh installs of Ubuntu 18 and 20 so if it doesn't work it's probably your configuration's fault. In this case you will have to follow manual instructions posted and do some troubleshooting.** 

* Scripts:
	included in repository: one [concise](https://github.com/computerguy2030/pytorch-rocm-amd/blob/master/amd_build_script.sh) and one [verbose](https://github.com/computerguy2030/pytorch-rocm-amd/blob/master/amd_build_script_verbose.sh) output (Note must uncomment lines for Ubuntu 20 accordingly). The concise script has the most important and most error prone code displayed while the verbose script has all terminal messages displayed (for comprehensive debugging purposes).
	- Must be in ~/Downloads directory
	- Script should complete all operations autonomously (reboots etc.) on Ubuntu 18.04, 20.04, or 20.10 versions and should require no intervention. Other Ubuntu versions, you may need to open the terminal after login/reboot. Non-Ubuntu distros you will need to use and modify manual instructions.
<br>	

* If you already sucesfuly installed ROCm use:
```
tail -n +143 /home/$USER/Downloads/amd_build_script.sh | bash
```
This should do everything but install ROCm.

<h3>Requirements </h3>
You must uninstall all other kernels except 5.4 or ROCm will not install. I have found that after install, ROCm commands still work if you reinstall and boot to other kernels (tested 5.6 and 5.8). Hopefully AMD will fix their seemingly arbitrary 5.4 requirement. 

1. Install ROCM: <br>
3. Clone Pytorch <br>
4. "Hipify" code <br>
5. Create .whl (pip) <br>
6. Install with pip <br>
<br>

**1. Install ROCM (Copied from AMD documentation)** <br>
https://rocmdocs.amd.com/en/latest/Installation_Guide/Installation-Guide.html#supported-operating-systems

* apt install:
```
sudo apt update && sudo apt upgrade -y
sudo apt dist-upgrade -y
sudo apt install libnuma-dev -y
sudo reboot
```
```
wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add -
echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/debian/ xenial main' | sudo tee /etc/apt/sources.list.d/rocm.list
```
```
sudo apt update
sudo apt install rocm-dkms -y && sudo reboot
```
--------------------------------------------------------------------------------------
* Create "video" and "render" groups for permissions:

```sudo usermod -a -G video $LOGNAME```

Add new users to group by default:
```
echo 'ADD_EXTRA_GROUPS=1' | sudo tee -a /etc/adduser.conf

echo 'EXTRA_GROUPS=video' | sudo tee -a /etc/adduser.conf
```
##For Ubuntu 20:
```
echo 'EXTRA_GROUPS=render' | sudo tee -a /etc/adduser.conf
sudo usermod -a -G render $LOGNAME
```
* Restart

--------------------------------------------------------------------------------------
* Test:
```
sudo /opt/rocm/bin/rocminfo
sudo /opt/rocm/opencl/bin/clinfo
```
You should see information about your card. 

--------------------------------------------------------------------------------------
* Add to PATH and end of bashrc:
```
export PATH=$PATH:/opt/rocm/bin:/opt/rocm/rocprofiler/bin:/opt/rocm/opencl/bin
echo 'PATH=$PATH:/opt/rocm/bin:/opt/rocm/rocprofiler/bin:/opt/rocm/opencl/bin' >> ~/.bashrc
```
--------------------------------------------------------------------------------------
* Reboot
--------------------------------------------------------------------------------------
<br><br>

**2. Clone Pytorch**
```
git clone https://github.com/computerguy2030/pytorch-rocm-amd.git
cd pytorch-rocm-amd
git submodule sync
git submodule update --init --recursive
```
This clones my fork; however, the main pytorch branch works too as of 2-7-2020
<br>

**3. "Hipify" code**
Converts all CUDA instructions to HIP.
```
python3 tools/amd_build/build_amd.py
```
<br>

**4. Create .whl (pip)**
* Install additional packages:
```
sudo apt install -y gcc cmake clang ccache llvm ocl-icd-opencl-dev python3-pip 
sudo apt install -y rocrand rocblas miopen-hip miopengemm rocfft rocprim rocsparse rocm-cmake rocm-dev rocm-device-libs rocm-libs rccl hipcub rocthrust 
pip3 install -r requirements.txt
```
* If you forget a package or must install additional packages, you must use: `make clean` before restarting compilation

--------------------------------------------------------------------------------------
* Create .whl: (Where errors most occur)<br>
Note: Only use "PYTORCH_ROCM_ARCH=gfx900" if you have Vega 56/64 card. Simply delete PYTORCH_ROCM_ARCH to compile for all platforms. or execute /opt/rocm/bin/rocm_agent_enumerator to find your arch. Then replace accordingly.
```
RCCL_DIR=/opt/rocm/rccl/lib/cmake/rccl/ PYTORCH_ROCM_ARCH=gfx900 hip_DIR=/opt/rocm/hip/cmake/ USE_NVCC=OFF BUILD_CAFFE2_OPS=0 PATH=/usr/lib/ccache/:$PATH USE_CUDA=OFF python3 setup.py bdist_wheel
```
Note:
If compiler fails, due to dependency issues etc. use:
<br>```make clean``` 
before restarting compilation

<br>

**5. Install with pip**
```
sudo pip3 install dist/*.whl
``` 
<br>

**6. Test pytorch**
Note: Do not execute in github folder
```
python3
import torch  ## (no errors)
torch.__version__
torch.cuda.get_device_name(0) ## (should show your arch eg. Vega 56/64)
```
Also try:
```
torch.cuda.is_available()
torch.cuda.device_count()
torch.cuda.current_device()
```
<br>
<br>

<h3>Information: (My current understanding)</h3>
Running CUDA programs on AMD:
One can run CUDA programs on AMD cards by using HIPify tool which converts CUDA to HIP language (technically C++ Runtime API). HIP is a thin layer where code is either translated to CUDA API and compiled with nvcc on Nvidia or compiled for ROCm on AMD with the HCC compiler. HCC is an open source C++ compiler. The hipcc compiler will "call the appropriate toolchain depending on the desired platform". Converting CUDA to HIP theoretically has little to no impact on NVIDIA performance while allowing code to be run on both platforms; however, you may mix CUDA and HIP code. <br> 
Links: <br>

* HIP FAQ: https://rocmdocs.amd.com/en/latest/Programming_Guides/HIP-FAQ.html <br>
* HCC: https://github.com/RadeonOpenCompute/hcc <br>
* HIP: https://github.com/ROCm-Developer-Tools/HIP <br>
<br>
ROCM:
rocm is essentially the AMD version of CUDA.
<br>

<h3>Troubleshoot: </h3>
<h4>General:<h4>

* To continue script from specific line:
```
 tail -n +(Enter line) /home/$USER/Downloads/amd_build_script.sh | bash
```
* Most issues I found were caused by dependency issues

* Dependency issues try: `pip3 install -r requirements.txt` from root pytorch folder
* If script fails or is interrupted and you cannot get to bash upon opening terminal, remove last line in ~/.bashrc by:

Under Edit--> Preferences--> Command <br>
Check "Run a custom command instead of my shell" <br>
Enter /bin/bash --norc <br><br>

* Check installed kernels:
```
dpkg --list | grep linux-image
```
* Set default kernel: (Must set `GRUB_DEFAULT=saved` in /etc/default/grub
```
grub-set-default 
```
<br>

* If during compiling you receive error:
```
    ERROR: Cannot create report: [Errno 17] File exists: '/var/crash/rock-dkms-firmware.0.crash'
    Error! Bad return status for module build on kernel: 5.8.0-41-generic (x86_64)
    Consult /var/lib/dkms/amdgpu/4.0-23/build/make.log for more information.
    dpkg: error processing package rock-dkms (--configure):
     installed rock-dkms package post-installation script subprocess returned error exit status 10
    dpkg: dependency problems prevent configuration of rocm-dkms:
     rocm-dkms depends on rock-dkms; however:
      Package rock-dkms is not configured yet. 
```
You are probably don't have ROCm properly installed likely due to having kernels other than 5.4 installed. Uninstall all other kernels, make sure `rocm info` command works, and retry compilation. 
<br>

<h3>Uninstall: </h3>
ROCm:

    sudo apt autoremove rocm-opencl rocm-dkms rocm-dev rocm-utils rocrand rocblas miopen-hip miopengemm rocfft rocprim rocsparse rocm-cmake rocm-dev rocm-device-libs rocm-libs rccl hipcub rocthrust
    sudo reboot
Pytorch:

    #find with:
    import torch
    print(torch.__file__)

In my case:

    sudo rm -r /usr/local/lib/python3.6/dist-packages/torch*

<br>
<h3>Usefull Tools </h3>

* radeontop (monitor AMD usage like nvidia-smi)
* bpytop (Cool CPU monitoring tool)
* rocminfo (built into ROCm)

<!--stackedit_data:
eyJoaXN0b3J5IjpbLTI4NDA5MjM2NCwtNzAwMjY0MzksLTc3Mj
k2Mzg1LDUwMjE2ODI2OSwzMTYyNjA4MjAsLTEzNjg4NDgyNDQs
LTEwNDM4MjQyMTMsMjc5MzI0MDg0LDIwODc4OTY2MzgsLTEyMz
gyMTAzNzYsNTIyNjA1NzkwLC0xNjMxOTk3NDIwLC0xMjkzOTE3
MTEyLDIxMjc3NjYyMjEsODY2MDcxMjY3LC04NTg0OTYxMzYsMT
AyMjAxNTkxOF19
-->