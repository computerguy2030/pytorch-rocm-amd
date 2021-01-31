<h1>MY FORK: </h1>

<h3>WHY: </h3>
I am creating this fork to create a simple guide for installing pytorch on AMD cards and listing some usefull general usefull information on AMD Machine Learning after being incredibly frustrated for several days of being unable to figure out how to install Pytorch while trying out DeOldify, a ML project for colorizing video. I am also creating a DeOldify fork with instructions for an AMD build. Hope this will help someone get a basic understanding of ML on AMD without the hassle I endured.

<h3>Information: </h3>
Running Pytorch on AMD requires ROCM platform. ROCM is AMD open source alternative to CUDA which is unfortunatly not widely used. AMD's official Pytorch/ROCM documentaion unfortunatly only provides docker container and no instructions on native install. Instructions posted here are mainly sourced from two tutorials I found after dumpster diving the internet: <br>

* https://github.com/aieater/rocm_pytorch_informations/tree/cf102198afb4dd2e94bf2c9724b9d1d54291b210#GPU-visibly-masking-and-multiple-GPUs <br>
* https://lernapparat.de/pytorch-rocm/ <br>

<br>
<h3>Instructions: </h3>

* Script included in repository:
1. Install ROCM: <br>
2. Clone Pytorch <br>
3. "Hipify" code <br>
4. Create .whl (pip) <br>
5. Install with pip <br>
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

##Only for Ubuntu 20:

``` sudo usermod -a -G render $LOGNAME```

Add new users to group by default:
```
echo 'ADD_EXTRA_GROUPS=1' | sudo tee -a /etc/adduser.conf

echo 'EXTRA_GROUPS=video' | sudo tee -a /etc/adduser.conf
```
##For Ubuntu 20:
```
echo 'EXTRA_GROUPS=render' | sudo tee -a /etc/adduser.conf
```
* Restart

--------------------------------------------------------------------------------------
* Test:
```
sudo /opt/rocm/bin/rocminfo
sudo /opt/rocm/opencl/bin/clinfo
```
You should see information about your card

--------------------------------------------------------------------------------------
* Add to PATH and end of bashrc:
```
export PATH=$PATH:/opt/rocm/bin:/opt/rocm/rocprofiler/bin:/opt/rocm/opencl/bin
echo 'PATH=$PATH:/opt/rocm/bin:/opt/rocm/rocprofiler/bin:/opt/rocm/opencl/bin' >> ~/.bashrc
```
--------------------------------------------------------------------------------------
* Reboot

<br><br>

**2. Clone Pytorch**
```
git clone https://github.com/computerguy2030/pytorch-rocm-amd.git
cd pytorch-rocm-amd
git submodule sync
git submodule update --init --recursive
```
<br>

**3. "Hipify" code**
```
python3 tools/amd_build/build_amd.py
```
<br>

**4. Create .whl (pip)**
* Install additional packages:
```
sudo apt install -y gcc cmake clang ccache llvm ocl-icd-opencl-dev python3-pip 
sudo apt install -y rocrand rocblas miopen-hip miopengemm rocfft rocprim rocsparse rocm-cmake rocm-dev rocm-device-libs rocm-libs rccl hipcub rocthrust 
pip3 install dataclasses
```
--------------------------------------------------------------------------------------
* Create .whl: (Where errors most occur)<br>
Note: Only use "PYTORCH_ROCM_ARCH=gfx900" if you have Vega 56/64 card. Simply delete PYTORCH_ROCM_ARCH to compile for all platforms or execute /opt/rocm/bin/rocm_agent_enumerator to find your arch and replace accordingly.
```
RCCL_DIR=/opt/rocm/rccl/lib/cmake/rccl/ PYTORCH_ROCM_ARCH=gfx900 hip_DIR=/opt/rocm/hip/cmake/ USE_NVCC=OFF BUILD_CAFFE2_OPS=0 PATH=/usr/lib/ccache/:$PATH USE_CUDA=OFF python3 setup.py bdist_wheel
```
Note:
If compiler fails, due to dependancy issues etc. use:
<br>```make clean``` 
before restarting compilation

<br>

**5. Install with pip**
```
sudo pip3 install dist/*.whl
``` 
<br>

**6. Test pytorch**
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

* To continue script from specific line: 

    tail

<br>

* Dependency issues try: pip install -r requirements.txt from root pytorch folder

<h3>Uninstall: </h3>
ROCm:

    sudo apt autoremove rocm-opencl rocm-dkms rocm-dev rocm-utils rocrand rocblas miopen-hip miopengemm rocfft rocprim rocsparse rocm-cmake rocm-dev rocm-device-libs rocm-libs rccl hipcub rocthrust
    d
    sudo reboot

<br>
<h3>Usefull Tools </h3>

* radeontop (monitor AMD usage like nvidia-smi)
* bpytop (Cool CPU monitoring tool)
* rocminfo (built into ROCm)
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTUzNzA5MDQ0MSwtOTk4MjEwMDQsLTE1OD
gzMDgzMDNdfQ==
-->