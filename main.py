import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import threading
import time
import json
import os
from datetime import datetime
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import pandas as pd
import pystray
from pystray import MenuItem as item
from PIL import Image as PILImage
import sys
import ctypes

# 文件路径
DATA_FILE = "followers.json"
SKIN_FOLDER = "skins"

# 工具函数：资源路径适配
def resource_path(relative):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative)

# 主程序类
class FansMonitorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # 无边框
        self.root.geometry("300x400+100+100")
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "pink")
        self.root.configure(bg="pink")

        # 数据结构
        # 数据结构
        self.users = [{"uid": "1051623622", "name": "之箬曦", "face": "https://i1.hdslb.com/bfs/face/40b59ec60328d982b84423bc2b796240ba38cb62.jpg@120w_120h_1c"}]
        self.follow_data = {}
        self.load_data()


        # 背景皮肤
        self.bg_image = None
        self.bg_label = None
        self.set_background(os.path.join(SKIN_FOLDER, "default.png"))

        # 创建UI
        self.create_ui()
        self.setup_window_drag()
        self.root.after(5000, self.update_loop)

        # 托盘图标
        self.create_tray_icon()

        self.root.mainloop()

    def set_background(self, path):
        try:
            img = Image.open(path).resize((300, 400))
            self.bg_image = ImageTk.PhotoImage(img)
            if self.bg_label:
                self.bg_label.config(image=self.bg_image)
            else:
                self.bg_label = tk.Label(self.root, image=self.bg_image, bg="pink")
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"背景加载失败: {e}")

    def create_ui(self):
        self.info_labels = {}
        self.avatar_labels = {}
        y = 60
        for user in self.users:
            uid = user["uid"]
            img = self.get_avatar(user)
            img_label = tk.Label(self.root, image=img, bd=0, bg="pink")
            img_label.image = img
            img_label.place(x=20, y=y)

            lbl = tk.Label(self.root, text=f"{user['name']}: 加载中...", fg="black", bg="pink")
            lbl.place(x=80, y=y + 10)

            self.info_labels[uid] = lbl
            self.avatar_labels[uid] = img_label
            y += 70

        tk.Button(self.root, text="添加用户", command=self.add_user).place(x=20, y=10)
        tk.Button(self.root, text="图表", command=self.show_chart).place(x=110, y=10)
        tk.Button(self.root, text="导出", command=self.export_data).place(x=180, y=10)

    def get_avatar(self, user):
        try:
            if not user.get("face"):
                url = f"https://api.bilibili.com/x/space/wbi/acc/info?mid={user['uid']}"
                res = requests.get(url).json()
                user["name"] = res["data"]["name"]
                user["face"] = res["data"]["face"]
            response = requests.get(user["face"], stream=True)
            img = Image.open(response.raw).resize((48, 48))
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"头像获取失败：{e}")
            return ImageTk.PhotoImage(Image.new("RGB", (48, 48), color="gray"))

    def add_user(self):
        def do_add():
            uid = entry.get().strip()
            if uid and uid.isdigit():
                new_user = {"uid": uid, "name": f"用户{uid}", "face": ""}
                self.users.append(new_user)
                self.follow_data[uid] = []
                self.save_data()
                self.root.destroy()
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:
                messagebox.showerror("错误", "请输入正确的 UID")

        top = tk.Toplevel(self.root)
        top.geometry("200x100")
        top.title("添加用户")
        tk.Label(top, text="输入UID:").pack()
        entry = tk.Entry(top)
        entry.pack()
        ttk.Button(top, text="添加", command=do_add).pack()

    def fetch_fans(self, uid):
        try:
            url = f"https://api.bilibili.com/x/relation/stat?vmid={uid}"
            headers = {
                "User-Agent": "Mozilla/5.0"
            }
            res = requests.get(url, timeout=5, headers=headers)
            if res.status_code == 200:
                data = res.json()
                return data['data']['follower']
        except Exception as e:
            print(f"粉丝获取失败：{e}")
        return -1

    def update_loop(self):
        for user in self.users:
            uid = user["uid"]
            count = self.fetch_fans(uid)
            if count != -1:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if uid not in self.follow_data:
                    self.follow_data[uid] = []
                self.follow_data[uid].append((now, count))
                self.info_labels[uid].config(text=f"{user['name']}：{count} 粉丝")
        self.save_data()
        self.root.after(5000, self.update_loop)

    def show_chart(self):
        for uid, data in self.follow_data.items():
            if data:
                times = [x[0] for x in data]
                counts = [x[1] for x in data]
                plt.plot(times, counts, label=uid)
        plt.xticks(rotation=45)
        plt.legend()
        plt.title("粉丝变化趋势")
        plt.tight_layout()
        plt.show()

    def export_data(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if path:
            all_data = []
            for uid, records in self.follow_data.items():
                for time_str, count in records:
                    all_data.append({"UID": uid, "时间": time_str, "粉丝数": count})
            df = pd.DataFrame(all_data)
            df.to_excel(path, index=False)
            messagebox.showinfo("导出成功", f"数据保存到 {path}")

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.follow_data, f, ensure_ascii=False)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        self.follow_data = json.loads(content)
                    else:
                        self.follow_data = {}
            except Exception as e:
                print(f"加载数据失败：{e}")
                self.follow_data = {}
        else:
            self.follow_data = {}

    def create_tray_icon(self):
        image = PILImage.new("RGB", (64, 64), color=(255, 192, 203))
        self.icon = pystray.Icon("bili_fans", image, "B站涨粉桌宠", menu=pystray.Menu(
            item("显示窗口", self.show_window),
            item("退出程序", self.exit_app)
        ))
        threading.Thread(target=self.icon.run, daemon=True).start()

    def show_window(self):
        self.root.deiconify()

    def exit_app(self):
        self.icon.stop()
        self.root.destroy()

    def setup_window_drag(self):
        def start_move(event):
            self.root.x = event.x
            self.root.y = event.y

        def do_move(event):
            x = self.root.winfo_x() + (event.x - self.root.x)
            y = self.root.winfo_y() + (event.y - self.root.y)
            self.root.geometry(f"+{x}+{y}")

        self.root.bind("<Button-1>", start_move)
        self.root.bind("<B1-Motion>", do_move)

if __name__ == "__main__":
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    FansMonitorApp()