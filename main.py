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
import io
import sys
import ctypes

# 本地数据路径
DATA_FILE = "followers.json"
SKIN_FOLDER = "skins"

# 工具函数：资源路径适配（用于打包后路径适配）
def resource_path(relative):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative)

# 主类
class FansMonitorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # 无边框
        self.root.geometry("800x600")
        self.root.configure(bg='white')

        self.users = [{"uid": "1051623622", "name": "默认用户", "face": ""}]
        self.follow_data = {}
        self.load_data()

        self.bg_image = None
        self.set_background(os.path.join(SKIN_FOLDER, "default.jpg"))

        self.create_ui()
        self.setup_window_drag()
        self.root.after(5000, self.update_loop)
        self.create_tray_icon()
        self.root.mainloop()

    def set_background(self, path):
        try:
            image = Image.open(path).resize((800, 600))
            self.bg_image = ImageTk.PhotoImage(image)
            label = tk.Label(self.root, image=self.bg_image)
            label.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            pass

    def create_ui(self):
        self.info_labels = {}
        self.avatar_labels = {}

        ttk.Button(self.root, text="添加用户", command=self.add_user).place(x=50, y=10)
        ttk.Button(self.root, text="图表分析", command=self.show_chart).place(x=150, y=10)
        ttk.Button(self.root, text="导出数据", command=self.export_data).place(x=250, y=10)
        ttk.Button(self.root, text="更新日志", command=self.show_update_log).place(x=350, y=10)

        self.refresh_user_ui()

    def refresh_user_ui(self):
        for label in self.info_labels.values():
            label.destroy()
        for img in self.avatar_labels.values():
            img.destroy()
        self.info_labels.clear()
        self.avatar_labels.clear()

        y = 80
        for user in self.users:
            uid = user["uid"]
            img = self.get_avatar(user)
            img_label = tk.Label(self.root, image=img, bg="white")
            img_label.image = img
            img_label.place(x=30, y=y)

            lbl = ttk.Label(self.root, text=f"{user['name']}：加载中...", background="white")
            lbl.place(x=90, y=y + 10)

            self.info_labels[uid] = lbl
            self.avatar_labels[uid] = img_label
            y += 80

    def get_avatar(self, user):
        try:
            if not user.get("face"):
                url = f"https://api.bilibili.com/x/space/wbi/acc/info?mid={user['uid']}"
                res = requests.get(url).json()
                if res.get("code") != 0:
                    raise Exception("UID 错误")
                user["name"] = res["data"]["name"]
                user["face"] = res["data"]["face"]

            response = requests.get(user["face"], timeout=5)
            img_data = io.BytesIO(response.content)
            img = Image.open(img_data).resize((48, 48))
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"获取头像失败：{e}")
            return ImageTk.PhotoImage(Image.new("RGB", (48, 48), color="gray"))

    def add_user(self):
        def do_add():
            uid = entry.get()
            if not uid.isdigit():
                messagebox.showerror("错误", "UID 应为纯数字")
                return
            try:
                url = f"https://api.bilibili.com/x/space/wbi/acc/info?mid={uid}"
                res = requests.get(url).json()
                if res.get("code") != 0:
                    raise Exception("无效UID")
                name = res["data"]["name"]
                face = res["data"]["face"]
                new_user = {"uid": uid, "name": name, "face": face}
                self.users.append(new_user)
                self.follow_data[uid] = []
                self.save_data()
                self.refresh_user_ui()
                top.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"添加失败：{e}")

        top = tk.Toplevel(self.root)
        top.title("添加用户")
        tk.Label(top, text="输入UID:").pack(pady=5)
        entry = tk.Entry(top)
        entry.pack(pady=5)
        ttk.Button(top, text="添加", command=do_add).pack(pady=5)

    def fetch_fans(self, uid):
        try:
            url = f"https://api.bilibili.com/x/relation/stat?vmid={uid}"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, timeout=5, headers=headers)
            if res.status_code == 200:
                data = res.json()
                return data['data']['follower']
        except Exception as e:
            print(f"获取粉丝数失败：{e}")
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
        plt.title("粉丝数变化趋势")
        plt.tight_layout()
        plt.show()

    def export_data(self):
        export_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if export_path:
            all_data = []
            for uid, records in self.follow_data.items():
                for time_str, count in records:
                    all_data.append({"UID": uid, "时间": time_str, "粉丝数": count})
            df = pd.DataFrame(all_data)
            df.to_excel(export_path, index=False)
            messagebox.showinfo("导出成功", f"数据已保存到 {export_path}")

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
            except Exception as e:
                print(f"加载数据出错：{e}")

    def create_tray_icon(self):
        image = PILImage.new("RGB", (64, 64), color=(255, 0, 0))
        self.icon = pystray.Icon("bili", image, "B站观测站", menu=pystray.Menu(
            item("显示主界面", self.show_window),
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
            deltax = event.x - self.root.x
            deltay = event.y - self.root.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

        self.root.bind("<Button-1>", start_move)
        self.root.bind("<B1-Motion>", do_move)

    def show_update_log(self):
        log = """更新日志：
- 修复添加用户失败、头像无法显示问题
- UI界面优化：头像、昵称对齐；无需重启加载
- 提升粉丝数获取稳定性与错误提示
- 增加更新日志窗口
"""
        messagebox.showinfo("更新日志", log)

if __name__ == '__main__':
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    FansMonitorApp()