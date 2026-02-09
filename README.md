# rtim
Real Time Intelligent Machining of Conjugate Mapping of Streamline Fields（基于流线场共扼映射的实时智能加工平台）

# 1. Development
## 1.1. ZOA
使用development/phase01/zoa.py程序：
```bash
======================================================================
Milling Chatter Stability Analysis - ZOA Method
======================================================================
System Parameters:
  - Modal mass: m = 0.5 kg
  - Stiffness: k = 20.0 x 10^6 N/m
  - Damping: c = 80.0 N·s/m
  - Natural frequency: f_n = 1006.6 Hz
  - Damping ratio: ζ = 0.0126
  - Number of teeth: N = 4
  - Cutting coefficient: Kt = 6.00 x 10^8 N/m^2
  - Radial force ratio: Kr = 0.3

Speed range: 1000 - 20000 RPM
Data points: 1500

Calculating stability lobes...
Successfully plotted 1500 data points
```
![i24.png](./docs/images/d00/i00.png "")

## 1.2. 开发 OCCT 几何特征提取模块（C++）
### 1.2.1. 开发环境搭建
```bash
# 1. 更新系统并安装基础依赖
sudo apt update
sudo apt install build-essential cmake git libx11-dev libxext-dev \
                 libxrender-dev libxmu-dev libxmuu-dev libfreetype6-dev \
                 libgl1-mesa-dev libfreeimage-dev libtbb-dev libglu1-mesa-dev

# 2. 安装Open CASCADE Technology (OCCT)
# 方法一：从官方仓库安装（推荐）
sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
sudo apt update
sudo apt install libopencascade-dev

# 方法二：从源码编译（获取最新版本）
cd ~
git clone https://github.com/Open-Cascade-SAS/OCCT.git
cd OCCT
git checkout V7_9_3
mkdir build && cd build
sudo apt install libvtk9-dev
cmake .. \
  -DINSTALL_DIR=~/opencascade \
  # FreeImage配置（解决之前的错误）
  -D3RDPARTY_FREEIMAGE_INCLUDE_DIR=/usr/include \
  -D3RDPARTY_FREEIMAGE_LIBRARY=/usr/lib/x86_64-linux-gnu/libfreeimage.so \
  # TIFF配置（解决之前的错误）
  -D3RDPARTY_TIFF_INCLUDE_DIR=/usr/include/x86_64-linux-gnu \
  -D3RDPARTY_TIFF_LIBRARY=/usr/lib/x86_64-linux-gnu/libtiff.so \
  # 其他可能需要的配置
  -DBUILD_MODULE_Draw=ON \
  -DUSE_TCL=ON \
  -DUSE_TK=ON \
  -DUSE_FREEIMAGE=ON
make -j$(nproc)
sudo make install

vim /home/yantao/opencascade/lib/pkgconfig/opencascade.pc
#################################################################################################
# 文件内容
#################################################################################################
prefix=/home/yantao/opencascade
exec_prefix=${prefix}
libdir=${exec_prefix}/lib
includedir=${prefix}/include/opencascade

Name: OpenCASCADE
Description: Open CASCADE Technology, 3D modeling & numerical simulation
Version: 7.9.3
Requires:
Libs: -L${libdir} -lTKernel -lTKMath -lTKBRep -lTKTopAlgo -lTKPrim -lTKBool -lTKShHealing -lTKMesh -lTKSTEP -lTKIGES -lTKSTL -lTKVRML -lTKXSBase -lTKG2d -lTKG3d -lTKGeomBase -lTKGeomAlgo -lTKFillet -lTKOffset -lTKFeat -lTKHDF -lTKService -lTKHLR -lTKBO -lTKCAF -lTKCDF -lTKLCAF -lTKTObj -lTKVCAF -lTKXDESTEP -lTKXDEIGES -lTKXmlXCAF -lTKRWMesh -lTKXS -lTKOpenGL -lTKMeshVS -lTKV3d -lTKViewerTest -lTKIVtk -lTKD3DHost -lTKQADraw -lTKTObjDRAW -lTKDraw -lTKTopTest -lTKXSDRAW -lTKDCAF -lTKStdL -lTKStd -lTKBinL -lTKBin -lTKXmlL -lTKXml -lTKPShape -lTKShapeSchema -lTKBinTObj -lTKXmlTObj -lTKBinXCAF -lTKXmlXCAF -lFWOSPlugin -lTKOpenGlTest
Cflags: -I${includedir} -DHAVE_CONFIG_H
########################################################################################################
# 编辑 ~/.bashrc（如果使用 bash）
echo 'export PKG_CONFIG_PATH=/home/yantao/opencascade/lib/pkgconfig:$PKG_CONFIG_PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/home/yantao/opencascade/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
# 使配置生效
source ~/.bashrc

# 3. 验证OCCT安装
pkg-config --modversion opencascade
# 显示7.9.3即为正确安装
```

