import tkinter as tk
import requests
import threading
import time
import numpy as np

# ================= CONFIG =================
CONTROL_IP = "http://192.168.1.10/cmd"
TEMP_IP = "http://192.168.1.10/temp"
CAMERA_STREAM = "http://192.168.1.11:81/stream"
REQUEST_TIMEOUT = 2
TURN_TOTAL_DEGREE = 25  # degrees per turn command


class SpiderBotSystem:

    def __init__(self, root):
        self.root = root
        self.root.title("SpiderBot Control Station")
        self.root.geometry("1300x750")
        self.root.configure(bg="#111111")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Status flags
        self.running = True
        self.connected = False
        self.camera_connected = False
        self.manual_mode = False
        self.current_command = "S"
        self.current_mode = None

        # Auto/task mode
        self.command_queue = []
        self.auto_sequence_running = False
        self.selected_direction = None
        self.selected_duration = 5

        # Map
        self.path_window = None
        self.path_canvas = None
        self.robot_x = 400
        self.robot_y = 400
        self.robot_angle = 0
        self.robot_marker = None

        # Status labels
        self.control_status_label = None
        self.camera_status_label = None

        self.root.bind("<Escape>", lambda e: self.go_back())

        self.build_main_screen()

    # ================= BASIC =================
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def go_back(self):
        self.stop_all_modes()
        self.build_main_screen()

    def stop_all_modes(self):
        self.manual_mode = False
        self.auto_sequence_running = False
        self.command_queue.clear()
        self.send_command("S")

    # ================= MAIN MENU =================
    def build_main_screen(self):
        self.clear_screen()

        tk.Label(self.root,
                 text="SPIDERBOT CONTROL SYSTEM",
                 font=("Arial", 26, "bold"),
                 fg="white", bg="#111111").pack(pady=80)

        tk.Button(self.root, text="AUTO MODE",
                  width=20, height=2,
                  command=self.build_auto_screen).pack(pady=15)

        tk.Button(self.root, text="REMOTE CONTROL",
                  width=20, height=2,
                  command=self.build_remote_screen).pack(pady=15)

        tk.Button(self.root, text="AUTOMATED TASK",
                  width=20, height=2,
                  command=self.build_task_screen).pack(pady=15)

        tk.Button(self.root, text="EXIT",
                  width=20, height=2,
                  bg="red", fg="white",
                  command=self.on_close).pack(pady=40)

    # ================= COMMON LAYOUT =================
    def build_common_layout(self, title):
        self.clear_screen()
        main = tk.Frame(self.root, bg="#111111")
        main.pack(fill="both", expand=True)

        self.video_label = tk.Label(main, bg="black")
        self.video_label.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        panel = tk.Frame(main, bg="#1c1c1c", width=350)
        panel.pack(side="right", fill="y", padx=15, pady=15)

        tk.Label(panel, text=title,
                 fg="white", bg="#1c1c1c",
                 font=("Arial", 14, "bold")).pack(pady=10)

        tk.Button(panel, text="ESC",
                  bg="red", fg="white",
                  command=self.go_back).pack(pady=5)

        tk.Label(panel, text="CONTROL STATUS", bg="#1c1c1c", fg="white").pack(pady=(20, 3))
        self.control_status_label = tk.Label(panel, text="Checking...", bg="#1c1c1c", fg="yellow")
        self.control_status_label.pack()

        tk.Label(panel, text="CAMERA STATUS", bg="#1c1c1c", fg="white").pack(pady=(20, 3))
        self.camera_status_label = tk.Label(panel, text="Checking...", bg="#1c1c1c", fg="yellow")
        self.camera_status_label.pack()

        self.start_connection_monitor()
        return panel

    # ================= CONNECTION MONITOR =================
    def start_connection_monitor(self):
        threading.Thread(target=self.check_connection_loop, daemon=True).start()

    def check_connection_loop(self):
        while self.running:
            try:
                requests.get(CONTROL_IP, timeout=2)
                self.connected = True
            except:
                self.connected = False

            try:
                requests.get(CAMERA_STREAM, timeout=2)
                self.camera_connected = True
            except:
                self.camera_connected = False

            self.root.after(0, self.update_connection_label)
            time.sleep(2)

    def update_connection_label(self):
        if self.control_status_label:
            self.control_status_label.config(
                text="🟢 CONNECTED" if self.connected else "🔴 DISCONNECTED",
                fg="lime" if self.connected else "red"
            )
        if self.camera_status_label:
            self.camera_status_label.config(
                text="🟢 CONNECTED" if self.camera_connected else "🔴 DISCONNECTED",
                fg="lime" if self.camera_connected else "red"
            )

    # ================= AUTO MODE =================
    def build_auto_screen(self):
        self.stop_all_modes()
        panel = self.build_common_layout("AUTO MODE")
        self.current_mode = "AUTO"
        self.send_command("AUTO")

    # ================= REMOTE CONTROL =================
    def build_remote_screen(self):
        self.stop_all_modes()
        panel = self.build_common_layout("REMOTE MODE")
        self.current_mode = "REMOTE"
        self.manual_mode = True
        self.current_command = "S"
        self.send_command("MANUAL")

        pad = tk.Frame(panel, bg="#1c1c1c")
        pad.pack(pady=40)
        style = {"width": 6, "height": 2}

        self.btn_w = tk.Button(pad, text="▲", **style)
        self.btn_w.grid(row=0, column=1)
        self.btn_a = tk.Button(pad, text="◀", **style)
        self.btn_a.grid(row=1, column=0)
        self.btn_s = tk.Button(pad, text="■", **style)
        self.btn_s.grid(row=1, column=1)
        self.btn_d = tk.Button(pad, text="▶", **style)
        self.btn_d.grid(row=1, column=2)

        self.btn_w.bind("<ButtonPress>", lambda e: self.press("F"))
        self.btn_w.bind("<ButtonRelease>", self.release)
        self.btn_s.bind("<ButtonPress>", lambda e: self.press("B"))
        self.btn_s.bind("<ButtonRelease>", self.release)
        self.btn_a.bind("<ButtonPress>", lambda e: self.press("L"))
        self.btn_a.bind("<ButtonRelease>", self.release)
        self.btn_d.bind("<ButtonPress>", lambda e: self.press("R"))
        self.btn_d.bind("<ButtonRelease>", self.release)

        threading.Thread(target=self.remote_control_loop, daemon=True).start()

    def remote_control_loop(self):
        while self.running:
            if self.manual_mode and self.current_command:
                self.send_command(self.current_command)
            time.sleep(0.05)

    def press(self, cmd):
        if self.manual_mode:
            self.current_command = cmd

    def release(self, event=None):
        self.current_command = "S"

    # ================= TASK MODE =================
    def build_task_screen(self):
        self.stop_all_modes()
        panel = self.build_common_layout("AUTOMATED TASK MODE")

        dir_frame = tk.Frame(panel, bg="#1c1c1c")
        dir_frame.pack(pady=10)

        for i, d in enumerate(["F", "B", "L", "R", "STAY"]):
            tk.Button(dir_frame, text=d, command=lambda x=d: self.select_direction(x)).grid(row=0, column=i, padx=3)

        tk.Label(panel, text="Duration (sec)", bg="#1c1c1c", fg="white").pack()
        for t in [3, 5, 10]:
            tk.Button(panel, text=str(t), command=lambda x=t: self.select_duration(x)).pack()

        tk.Button(panel, text="ADD STEP", command=self.add_step).pack(pady=5)
        self.mission_box = tk.Listbox(panel, height=6)
        self.mission_box.pack(pady=5)
        tk.Button(panel, text="START", bg="green", command=self.start_sequence).pack(pady=5)

    def select_direction(self, d):
        self.selected_direction = "S" if d == "STAY" else d

    def select_duration(self, t):
        self.selected_duration = t

    def add_step(self):
        if self.selected_direction:
            self.command_queue.append((self.selected_direction, self.selected_duration))
            self.mission_box.insert(tk.END, f"{self.selected_direction} for {self.selected_duration}s")

    def start_sequence(self):
        if not self.auto_sequence_running and self.command_queue:
            self.auto_sequence_running = True
            self.open_path_window()
            threading.Thread(target=self.run_sequence, daemon=True).start()

    def run_sequence(self):
        while self.command_queue and self.auto_sequence_running:
            cmd, duration = self.command_queue.pop(0)
            self.execute_path_logic(cmd, duration)
            time.sleep(0.3)
        self.auto_sequence_running = False
        self.send_command("S")

    # ================= MOVEMENT =================
    def execute_path_logic(self, cmd, duration):
        if cmd == "S":
            self.send_command("S")
            time.sleep(duration)
            return

        if cmd in ["L", "R"]:
            self.send_command(cmd)
            total_angle = TURN_TOTAL_DEGREE
            if cmd == "L":
                total_angle *= -1
            self.turn_exact(total_angle, duration)
            self.send_command("S")

        elif cmd in ["F", "B"]:
            self.send_command(cmd)
            step_distance = 20 if cmd == "F" else -20
            steps = duration * 20  # smoother movement, 20 updates/sec
            for _ in range(steps):
                self.move_robot(step_distance / 20)
                time.sleep(duration / steps)
            self.send_command("S")

    def turn_exact(self, total_angle, duration=1):
        steps = int(duration * 20)  # 20 updates per second
        angle_per_step = total_angle / steps
        for _ in range(steps):
            self.robot_angle += angle_per_step
            self.update_robot_marker()
            if self.path_canvas:
                self.path_canvas.update()
            time.sleep(duration / steps)

    def move_robot(self, step):
        if not self.path_canvas:
            return
        rad = np.radians(self.robot_angle)
        new_x = self.robot_x + step * np.cos(rad)
        new_y = self.robot_y + step * np.sin(rad)
        self.path_canvas.create_line(self.robot_x, self.robot_y, new_x, new_y, fill="#00FFFF", width=3)
        self.robot_x = new_x
        self.robot_y = new_y
        self.update_robot_marker()

    # ================= MAP =================
    def open_path_window(self):
        if self.path_window and self.path_window.winfo_exists():
            return
        self.path_window = tk.Toplevel(self.root)
        self.path_window.title("Live Robot Map")
        self.path_window.geometry("800x800")
        self.path_canvas = tk.Canvas(self.path_window, width=800, height=800, bg="#0f0f0f")
        self.path_canvas.pack(fill="both", expand=True)
        for i in range(0, 800, 50):
            self.path_canvas.create_line(i, 0, i, 800, fill="#1f1f1f")
            self.path_canvas.create_line(0, i, 800, i, fill="#1f1f1f")
        self.robot_x = 400
        self.robot_y = 400
        self.robot_angle = 0
        self.update_robot_marker()

    def update_robot_marker(self):
        if not self.path_canvas:
            return
        if self.robot_marker:
            self.path_canvas.delete(self.robot_marker)
        size = 14
        rad = np.radians(self.robot_angle)
        x1 = self.robot_x + size * np.cos(rad)
        y1 = self.robot_y + size * np.sin(rad)
        x2 = self.robot_x + size * np.cos(rad + 2.5)
        y2 = self.robot_y + size * np.sin(rad + 2.5)
        x3 = self.robot_x + size * np.cos(rad - 2.5)
        y3 = self.robot_y + size * np.sin(rad - 2.5)
        self.robot_marker = self.path_canvas.create_polygon(x1, y1, x2, y2, x3, y3, fill="lime", outline="white")

    # ================= NETWORK =================
    def send_command(self, cmd):
        try:
            requests.get(CONTROL_IP, params={"move": cmd}, timeout=REQUEST_TIMEOUT)
        except:
            pass

    # ================= CLOSE =================
    def on_close(self):
        self.running = False
        self.send_command("S")
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SpiderBotSystem(root)
    root.mainloop()
