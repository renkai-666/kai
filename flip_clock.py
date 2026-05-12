import tkinter as tk
import time
import math

# ── 颜色方案 ──
BG = '#0d0d0d'
PANEL_TOP = '#2c2c2e'
PANEL_BOTTOM = '#1c1c1e'
TEXT_COLOR = '#f5f5f7'
DIVIDER = '#000000'
BORDER = '#3a3a3c'
COLON_COLOR = '#f5f5f7'
SHADOW = '#000000'

class FlipDigit:
    """单个翻页数字"""

    def __init__(self, canvas, offset_x, y, w, h):
        self.canvas = canvas
        self.x, self.y, self.w, self.h = offset_x, y, w, h
        self.value = 0
        self.animating = False
        self.font_size = int(h * 0.45)
        self.draw()

    def draw(self):
        x, y, w, h = self.x, self.y, self.w, self.h
        mid = y + h // 2

        # 阴影
        self.canvas.create_rectangle(x + 2, y + 2, x + w + 2, y + h + 2,
            fill=SHADOW, outline='', tags='shadow')

        # 上半部背景（较亮，模拟顶部采光）
        self.canvas.create_rectangle(x, y, x + w, mid,
            fill=PANEL_TOP, outline='', tags='bg')
        # 下半部背景（较暗）
        self.canvas.create_rectangle(x, mid, x + w, y + h,
            fill=PANEL_BOTTOM, outline='', tags='bg')
        # 边框
        self.canvas.create_rectangle(x, y, x + w, y + h,
            outline=BORDER, tags='border')

        # 中间深色分割线
        self.canvas.create_line(x, mid, x + w, mid,
            fill=DIVIDER, width=3, tags='divider')

        # 顶部高光线（增加立体感）
        self.canvas.create_line(x + 4, y + 2, x + w - 4, y + 2,
            fill='#3a3a3c', width=1, tags='highlight')

        # 数字
        self.top_text = self.canvas.create_text(
            x + w // 2, y + h // 4,
            text=str(self.value), fill=TEXT_COLOR,
            font=('Helvetica', self.font_size, 'bold'), tags='digits'
        )
        self.bot_text = self.canvas.create_text(
            x + w // 2, y + 3 * h // 4,
            text=str(self.value), fill=TEXT_COLOR,
            font=('Helvetica', self.font_size, 'bold'), tags='digits'
        )

    def set_value(self, new_val, animate=True):
        if new_val == self.value:
            return
        old_val = self.value
        self.value = new_val

        if not animate:
            self.canvas.itemconfig(self.top_text, text=str(new_val))
            self.canvas.itemconfig(self.bot_text, text=str(new_val))
            return

        if self.animating:
            return

        self.animating = True
        x, y, w, h = self.x, self.y, self.w, self.h
        mid = y + h // 2
        fs = self.font_size
        steps = 8

        # 创建翻页 flap：覆盖上半部的旧数字
        flap = self.canvas.create_rectangle(
            x, y, x + w, mid,
            fill=PANEL_TOP, outline=BORDER, tags='flap'
        )
        flap_text = self.canvas.create_text(
            x + w // 2, y + h // 4,
            text=str(old_val), fill=TEXT_COLOR,
            font=('Helvetica', fs, 'bold'), tags='flap'
        )

        # flap 上半部高光线
        flap_hl = self.canvas.create_line(
            x + 4, y + 2, x + w - 4, y + 2,
            fill='#3a3a3c', width=1, tags='flap'
        )

        # 底层更新为新数字
        self.canvas.itemconfig(self.top_text, text=str(new_val))
        self.canvas.itemconfig(self.bot_text, text=str(new_val))

        # 将 flap 提到最前
        self.canvas.tag_raise('flap')

        # 动画：flap 从顶部翻到中间，高度逐渐缩小
        def animate(step=0):
            if step > steps:
                self.canvas.delete('flap')
                self.animating = False
                return

            progress = (step + 1) / (steps + 1)
            # 使用 ease-out 曲线
            ease = 1 - (1 - progress) ** 2
            flap_y = y + (mid - y) * ease
            flap_h = (mid - y) * (1 - ease * 0.85)
            if flap_h < 1:
                flap_h = 0

            self.canvas.coords(flap, x, flap_y, x + w, flap_y + flap_h)
            text_y = flap_y + flap_h / 2
            self.canvas.coords(flap_text, x + w // 2, text_y)
            self.canvas.coords(flap_hl, x + 4, flap_y + 2, x + w - 4, flap_y + 2)

            # 随高度缩小字体
            if flap_h > 2:
                shrink_fs = max(6, int(fs * (flap_h / (mid - y))))
                self.canvas.itemconfig(flap_text, font=('Helvetica', shrink_fs, 'bold'))

            self.canvas.after(35, lambda: animate(step + 1))

        animate()


class FlipClock:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('翻页时钟')
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        w_total = 660
        h_total = 300

        # 窗口居中
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        wx = (sw - w_total) // 2
        wy = (sh - h_total) // 2
        self.root.geometry(f'{w_total}x{h_total}+{wx}+{wy}')

        # 顶层窗口
        self.root.attributes('-topmost', True)

        # Canvas
        self.canvas = tk.Canvas(
            self.root, width=w_total, height=h_total,
            bg=BG, highlightthickness=0
        )
        self.canvas.pack()

        # 参数
        panel_w = 72
        panel_h = 130
        panel_y = (h_total - panel_h) // 2 - 15
        gap = 8
        colon_w = 18

        # 计算起始 x
        total_w = 6 * panel_w + 2 * colon_w + 7 * gap
        start_x = (w_total - total_w) // 2

        # 创建 6 个翻页数字面板
        self.digits = []
        x = start_x
        for i in range(6):
            if i in (2, 4):
                # 冒号
                colon_x = x
                self._draw_colon(colon_x, panel_y, colon_w, panel_h)
                x += colon_w + gap

            fd = FlipDigit(self.canvas, x, panel_y, panel_w, panel_h)
            self.digits.append(fd)
            x += panel_w + gap

        # 日期显示
        self.date_text = self.canvas.create_text(
            w_total // 2, h_total - 30,
            text='', fill='#8e8e93',
            font=('Helvetica', 14)
        )

        # 闪烁的冒号状态（初始隐藏，第一个 tick 显示）
        self.colon_visible = False
        self._draw_colon_indicators()

        # 更新时间
        self.update_time()

        # 绑定右键菜单
        self.root.bind('<Button-3>', self.show_menu)

    def _draw_colon(self, x, y, w, h):
        """绘制冒号"""
        dot_r = 5
        gap = 18
        cx = x + w // 2
        cy1 = y + h // 2 - gap
        cy2 = y + h // 2 + gap

        self.colon_top = self.canvas.create_oval(
            cx - dot_r, cy1 - dot_r, cx + dot_r, cy1 + dot_r,
            fill=COLON_COLOR, outline='', tags='colons'
        )
        self.colon_bot = self.canvas.create_oval(
            cx - dot_r, cy2 - dot_r, cx + dot_r, cy2 + dot_r,
            fill=COLON_COLOR, outline='', tags='colons'
        )

    def _draw_colon_indicators(self):
        """引用冒号对象供后续闪烁"""
        colon_tags = self.canvas.find_withtag('colons')
        self.colon_objs = colon_tags

    def _blink_colons(self):
        self.colon_visible = not self.colon_visible
        state = 'normal' if self.colon_visible else 'hidden'
        for obj in self.colon_objs:
            self.canvas.itemconfig(obj, state=state)

    def update_time(self):
        t = time.localtime()
        hh, mm, ss = t.tm_hour, t.tm_min, t.tm_sec

        # 24小时制转为12小时制
        disp_h = hh % 12
        if disp_h == 0:
            disp_h = 12

        time_str = f'{disp_h:02d}{mm:02d}{ss:02d}'
        ampm = 'AM' if hh < 12 else 'PM'

        # 更新每个数字（变化的数字独立翻页动画）
        for i, ch in enumerate(time_str):
            val = int(ch)
            if val != self.digits[i].value:
                self.digits[i].set_value(val, animate=True)

        # 日期
        weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        date_str = f'{t.tm_year}年{t.tm_mon:02d}月{t.tm_mday:02d}日 {weekdays[t.tm_wday]} {ampm}'
        self.canvas.itemconfig(self.date_text, text=date_str)

        # 冒号闪烁
        self._blink_colons()

        # 下一次更新（精确到整秒）
        now = time.time()
        next_sec = math.ceil(now)
        delay = int((next_sec - now) * 1000)
        self.root.after(delay, self.update_time)

    def show_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0, bg='#1c1c1e', fg='#f5f5f7',
                       activebackground='#3a3a3c', activeforeground='#ffffff')
        menu.add_command(label='置顶', command=self.toggle_topmost)
        menu.add_separator()
        menu.add_command(label='退出', command=self.root.quit)
        menu.tk_popup(event.x_root, event.y_root)

    def toggle_topmost(self):
        current = self.root.attributes('-topmost')
        self.root.attributes('-topmost', not current)

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    app = FlipClock()
    app.run()
