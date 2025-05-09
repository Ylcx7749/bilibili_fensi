# B站粉丝监测桌宠 - FansMonitorApp

## 项目简介

**FansMonitorApp** 是一个专为B站用户粉丝监测设计的桌面应用程序，支持实时更新多个用户的粉丝数，并提供桌宠形式的显示方式。该程序会自动监控多个B站用户的粉丝数变化，支持实时数据显示、趋势图展示和数据导出（CSV/Excel）。它还提供了可定制的背景和UI、托盘图标功能、用户管理等功能，使得用户可以方便地添加或删除用户并查看粉丝动态。

### 主要功能

- **实时监控粉丝数**：支持添加多个B站用户进行粉丝数监控，显示实时粉丝数。
- **粉丝数趋势图**：提供粉丝数随时间变化的趋势图，方便查看涨粉或掉粉情况。
- **数据导出**：支持将粉丝数历史数据导出为CSV或Excel文件，便于进一步分析。
- **透明背景无边框窗口**：程序主界面为透明背景和无边框形式，类似桌宠。
- **托盘图标功能**：程序可以最小化到系统托盘，提供显示、隐藏、退出等功能。
- **多用户管理**：支持添加、删除多个用户，并监控其粉丝数变化。
- **自定义背景和皮肤**：用户可以更改程序背景和皮肤，提供个性化定制。
- **开机自启**：支持设置开机启动，自动运行粉丝监测程序。

## 安装与运行

### 1. 克隆项目

在终端中运行以下命令克隆项目：

```bash
git clone https://github.com/Ylcx7749/bilibili_fensi.git
cd bilibili_fensi

尚未打包.exe
cmd输入python main.py运行

### 项目结构
bilibili_fensi/
├── skins/                  # 背景和皮肤文件夹
│   └── default.jpg         # 默认背景图
├── main.py                 # 程序主文件
├── requirements.txt        # 依赖库文件
├── followers.json          # 存储用户粉丝数数据的文件
├── README.md               # 项目说明文件
└── LICENSE                 # 项目许可协议
