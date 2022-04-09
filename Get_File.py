from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import numpy as np
import struct
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
import dir

plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus'] = False

pa=dir.app_path()
p = Path(pa+r'.//awx_picture')
p.mkdir(exist_ok=True,parents=True)

def get_file():
    # 打开选择文件夹对话框
    root = tk.Tk()
    root.withdraw()
    #获得选择好的文件夹
    folderpath = filedialog.askdirectory()
    # 初始化构造Path对象
    p = Path(folderpath)
    #得到所有的awx文件
    filelist = list(p.glob("**/*.AWX"))
    files=[]
    #文件夹内文件个数
    num=0
    for file in filelist:
        files.append(file)
        num+=1
    allfile=[]
    for i in range(num):
        file_path=files[i]
        file = str(file_path)
        allfile.append(file)
        f = open(file, 'rb')
        ss=file[-17:-4]
        # 读取掉头文件
        head1 = []
        head2 = []
        head1.append(struct.unpack('12s9h8sh', f.read(40)))
        head2.append(struct.unpack('8s36h',f.read(80)))
        head_rest = []
        head_rest.append(struct.unpack('1081c', f.read(1081)))
        head_rest2 = []
        head_rest2.append(struct.unpack('1201c', f.read(1201)))
        # 头文件读取完毕，下面开始读取数据段
        # 实际横向数据个数为1201，数据个数为1201x1201=1002001个,每个数据字长为1
        awx_original_data = []
        for i in range(1201):
            for j in range(1201):
                (aa,) = struct.unpack('B', f.read(1))
                awx_original_data.append(aa)
        f.close()
        awx_data = np.array(awx_original_data).reshape(1201, 1201)
        awx_data = np.flipud(awx_data)
        awx_data = awx_data - 173.15
        awx_data = np.ma.masked_outside(awx_data, -100, -25)
        # 绘底图，四川范围
        fig = plt.figure(figsize=(10, 8))
        ax = fig.subplots()
        m5 = Basemap(llcrnrlon=97.4, llcrnrlat=26, urcrnrlon=109, urcrnrlat=34.2,
                     projection='lcc', lat_1=33, lat_2=45,lon_0=100)
        lons = np.linspace(45, 165, 1201)
        lats = np.linspace(-60, 60, 1201)
        lon, lat = np.meshgrid(lons, lats)
        x, y = m5(lon, lat)
        m5.readshapefile(pa+".//CHN_adm_shp//CHN_adm1", 'china', drawbounds=True, linewidth=1.9)  # 全国图显示省界
        m5.readshapefile(pa+".//CHN_adm_shp//china-shapefiles-master//china_nine_dotted_line", 'nine_dotted', drawbounds=True)
        m5.readshapefile(pa+".//CHN_adm_shp//CHN_adm2", "states", drawbounds=False)  # 全国图不显示地级市界
        # 只显示四川地级市
        for info, shp in zip(m5.states_info, m5.states):
            sheng = info['NAME_1']
            if (sheng == 'Sichuan'):
                poly = Polygon(shp, facecolor='w', edgecolor='k', lw=1.3)
                ax.add_patch(poly)
        # 坐标轴为经纬度
        m5.drawparallels(np.arange(0, 55., 1.), labels=[1, 0, 0, 0], fontsize=18, linewidth=0.8)
        m5.drawmeridians(np.arange(70., 140., 2.), labels=[0, 0, 0, 1], fontsize=18, linewidth=0.8)
        # m5.drawcoastlines(linewidth=1)
        m5.drawcountries(linewidth=1)
        plt.title(ss,fontsize=20)
        mycolor = ['#4B0082', '#00008B', '#0000CD', '#0000FF', '#4169E1', '#1E90FF', '#87CEFA', '#FFFFFF']
        ac = ax.contourf(x, y, awx_data, levels=np.arange(-90, -28, 10), colors=mycolor, extend='both', zorder=2)
        cb = fig.colorbar(ac, shrink=0.89)
        cb.ax.tick_params(labelsize=12)
        cb.ax.set_title('TBB(℃)')
        plt.savefig(pa+'.//awx_picture//'+ss+'.png')
        plt.close()
get_file()