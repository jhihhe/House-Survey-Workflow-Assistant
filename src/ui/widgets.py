import tkinter as tk
from ..utils.config import Config

class CatRunner(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.colors = Config.COLORS
        self.cat_items = []
        self.cat_prev_x = 0
        self.cat_prev_y = 0
        self.cat_phase = 0
        self.cat_running = False
        self.cat_anim_id = None

    def reset(self):
        w = self.winfo_width() or 1
        h = self.winfo_height() or 24
        self.delete("all")
        self.cat_items = []
        
        base_y = h//2 - 10
        body = self.create_rectangle(10, base_y+6, 30, base_y+18, fill=self.colors['pink'], outline="")
        head = self.create_oval(30, base_y+6, 42, base_y+18, fill=self.colors['pink'], outline="")
        ear1 = self.create_polygon(34, base_y+6, 36, base_y+0, 38, base_y+6, fill=self.colors['pink'], outline="")
        ear2 = self.create_polygon(39, base_y+6, 41, base_y+0, 43, base_y+6, fill=self.colors['pink'], outline="")
        eye1 = self.create_oval(33, base_y+10, 35, base_y+12, fill=self.colors['bg'], outline="")
        eye2 = self.create_oval(36, base_y+10, 38, base_y+12, fill=self.colors['bg'], outline="")
        whisker1 = self.create_line(42, base_y+12, 44, base_y+12, fill=self.colors['pink'])
        whisker2 = self.create_line(42, base_y+14, 44, base_y+15, fill=self.colors['pink'])
        leg1 = self.create_rectangle(14, base_y+18, 18, base_y+22, fill=self.colors['pink'], outline="")
        leg2 = self.create_rectangle(22, base_y+18, 26, base_y+22, fill=self.colors['pink'], outline="")
        leg3 = self.create_rectangle(14, base_y+18, 18, base_y+22, fill=self.colors['pink'], outline="")
        leg4 = self.create_rectangle(22, base_y+18, 26, base_y+22, fill=self.colors['pink'], outline="")
        tail = self.create_polygon(10, base_y+14, 2, base_y+12, 5, base_y+16, fill=self.colors['pink'], outline="")
        
        self.cat_items = [body, head, ear1, ear2, eye1, eye2, whisker1, whisker2, leg1, leg2, leg3, leg4, tail]
        for i in self.cat_items:
            self.addtag_withtag("cat", i)
            
        self.cat_prev_x = 0
        self.cat_prev_y = 0
        self.cat_phase = 0
        self.cat_running = True
        self._set_pos(0, 0)
        self._start_anim()

    def update_progress(self, current, total):
        if total <= 0 or not self.cat_items:
            return
        w = self.winfo_width() or 1
        frac = max(0.0, min(1.0, current / total))
        x = int(frac * (w - 60))
        y = 0
        self._set_pos(x, y)

    def complete(self):
        if not self.cat_items:
            return
        self.cat_running = False
        if self.cat_anim_id:
            self.after_cancel(self.cat_anim_id)
            
        cx = self.cat_prev_x
        cy = self.cat_prev_y
        steps = 24
        radius = 6
        
        def step(i=0):
            if i <= steps:
                x = cx + int(radius * 0.8 * (i/steps))
                y = cy
                self._set_pos(x, y)
                self.after(60, step, i+1)
            else:
                for it in self.cat_items:
                    self.itemconfigure(it, state="hidden")
        step()

    def _start_anim(self):
        def tick():
            if not self.cat_running:
                return
            self._anim_step()
            self.cat_anim_id = self.after(120, tick)
        if self.cat_anim_id:
            self.after_cancel(self.cat_anim_id)
        self.cat_anim_id = self.after(120, tick)

    def _anim_step(self):
        if not self.cat_items:
            return
        body = self.cat_items[0]
        head = self.cat_items[1]
        legs = self.cat_items[8:12]
        tail = self.cat_items[12]
        amp = 4
        
        if self.cat_phase == 0:
            for i, leg in enumerate(legs):
                self.move(leg, 0, -amp if i % 2 == 0 else amp)
            x1, y1, x2, y2, x3, y3 = self.coords(tail)
            self.coords(tail, x1, y1-2, x2, y2-2, x3, y3-2)
            self.move(body, 0, -1)
            self.move(head, 0, -1)
            self.cat_phase = 1
        else:
            for i, leg in enumerate(legs):
                self.move(leg, 0, amp if i % 2 == 0 else -amp)
            x1, y1, x2, y2, x3, y3 = self.coords(tail)
            self.coords(tail, x1, y1+2, x2, y2+2, x3, y3+2)
            self.move(body, 0, 1)
            self.move(head, 0, 1)
            self.cat_phase = 0

    def _set_pos(self, x, y):
        dx = x - self.cat_prev_x
        dy = y - self.cat_prev_y
        self.move("cat", dx, dy)
        self.cat_prev_x = x
        self.cat_prev_y = y
