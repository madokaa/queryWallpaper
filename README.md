# queryWallpaper
查找幻灯片模式下 Windows 当前使用的桌面壁纸

### a) 软件作用
Windows桌面背景可以设定为幻灯片模式，选定一个文件夹为图片来源。当图片文件有几百几千时，看到喜欢或者不喜欢的图片，却很难找到当前放映的背景图片源文件。
本程序可以快速查找并打开图片源文件，用以进行收藏或者删除。

### b) 使用方法
1. 安装 Pillow 
``` shell
pip3 install Pillow
```
2. 修改文件中的 `wallpaper_dir` 为当前设置的桌面壁纸路径
3. 运行初始化命令（之后添加文件都要运行）
``` shell
python3 ./main.py init
```
4. 查找并打开当前壁纸
``` shell
python3 ./main.py
```

### c) 使用 `AHK` 设置快捷键运行
通过ahk软件可以方便的用快捷键执行脚本，下面为实例脚本（请见路径替换为自己的实际路径）
``` ahk
; ----- 在桌面按 ctrl+W 建打开当前桌面壁纸文件 -----
~^w::
{
    MouseGetPos, mX, mY, mId
    WinGetClass, className, ahk_id %mId%
    if (className = "WorkerW") {
        Run .\venv\Scripts\python.exe ./wallpaper/main.py, D:\Code\Python, Hide
    }
    Return
}
```
