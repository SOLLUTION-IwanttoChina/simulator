import json
import os
import random
import math
import tkinter as tk
from tkinter import ttk, messagebox

DB_FILE = "database.json"

DEFAULT_DB = {
    "players": {},
    "coaches": {},
    "teams": {},
    "match_history": []
}

# Список ролей
ROLES = ["Капитан", "Снайпер", "Опенер", "Рифлер", "Саппорт", "Капитан-Снайпер", "Люркер"]
PROFICIENCIES = ["Прекрасно", "Отлично", "Хорошо", "Средне", "Плохо"]
ROLE_MULTIPLIERS = {"Прекрасно": 1.20, "Отлично": 1.10, "Хорошо": 1.00, "Средне": 0.85, "Плохо": 0.70}

# Актуальный список карт Standoff 2 (Карта Sakura удалена)
MAPS = ["Sandstone", "Province", "Breeze", "Rust", "Dune", "Hanami", "Prison"]

MAP_DETAILS = {
    "Sandstone": {"type": "Defuse", "desc": "Легендарная песчаная локация с восточным колоритом."},
    "Province": {"type": "Defuse", "desc": "Узкие улочки старинного европейского городка."},
    "Breeze": {"type": "Defuse", "desc": "Тропический порт с контейнерами и морским бризом."},
    "Rust": {"type": "Defuse", "desc": "Заброшенный промышленный завод и строительные леса."},
    "Dune": {"type": "Defuse", "desc": "Военная база в самом сердце раскаленной пустыни."},
    "Hanami": {"type": "Defuse", "desc": "Праздник цветения вишни на улицах японского мегаполиса."},
    "Prison": {"type": "Defuse", "desc": "Тюремный комплекс с множеством коридоров и уровней."}
}

# Цветовая палитра темной темы
COLOR_BG = "#0B0E14"          
COLOR_CARD = "#141822"        
COLOR_CARD_INNER = "#1A1F2C"  
COLOR_BORDER = "#232A3B"      
COLOR_TEXT = "#F1F3F9"        
COLOR_MUTED = "#8C96A8"       
COLOR_GOLD = "#F5C027"        
COLOR_NEON_CYAN = "#00F0FF"   
COLOR_NEON_PINK = "#FF007F"   
COLOR_GREEN = "#10B981"
COLOR_RED = "#EF4444"

def load_db():
    if not os.path.exists(DB_FILE):
        save_db(DEFAULT_DB)
        return DEFAULT_DB
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "match_history" not in data:
                data["match_history"] = []
            return data
    except Exception:
        return DEFAULT_DB

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[Ошибка БД]: {e}")

db = load_db()

# --- Кастомная Неоновая Анимированная Кнопка ---
class NeonButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=180, height=40, 
                 neon_color=COLOR_NEON_CYAN, bg_color=COLOR_CARD_INNER, fg_color=COLOR_TEXT, **kwargs):
        parent_bg = parent.cget("bg") if hasattr(parent, "cget") else COLOR_CARD
        super().__init__(parent, width=width, height=height, bg=parent_bg, highlightthickness=0, bd=0, **kwargs)
        self.command = command
        self.text = text
        self.width = width
        self.height = height
        self.neon_color = neon_color
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.is_hovered = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

        self.draw_button()

    def draw_button(self):
        self.delete("all")
        border_col = self.neon_color if self.is_hovered else COLOR_BORDER
        fill_col = "#222B3E" if self.is_hovered else self.bg_color
        text_col = "#FFFFFF" if self.is_hovered else self.fg_color

        if self.is_hovered:
            self.create_rectangle(1, 1, self.width-1, self.height-1, outline=self.neon_color, width=2)
            self.create_rectangle(3, 3, self.width-3, self.height-3, fill=fill_col, outline="")
        else:
            self.create_rectangle(1, 1, self.width-1, self.height-1, fill=fill_col, outline=border_col, width=1)

        self.create_text(self.width / 2, self.height / 2, text=self.text, fill=text_col, font=("Segoe UI", 9, "bold"))

    def _on_enter(self, e):
        self.is_hovered = True
        self.draw_button()

    def _on_leave(self, e):
        self.is_hovered = False
        self.draw_button()

    def _on_click(self, e):
        if self.command:
            self.command()

# --- Анимированный Холст Сакуры ---
class SakuraCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLOR_BG, highlightthickness=0, bd=0, **kwargs)
        self.petals = []
        self.wind_angle = 0
        self.bind("<Configure>", self._on_resize)
        self._create_petals()
        self.animate()

    def _create_petals(self):
        self.petals = []
        for _ in range(45):
            self.petals.append({
                "x": random.randint(0, 1400),
                "y": random.randint(-100, 900),
                "size": random.uniform(3, 7),
                "speed_y": random.uniform(1.0, 2.5),
                "speed_x": random.uniform(-0.6, 0.6),
                "phase": random.uniform(0, math.pi * 2),
                "color": random.choice(["#FF1493", "#FF69B4", "#FFB6C1", "#FF007F", "#E86F88"])
            })

    def _on_resize(self, event):
        self.draw_sakura_tree()

    def draw_sakura_tree(self):
        self.delete("tree")
        w = self.winfo_width()
        if w < 100: return

        sway = math.sin(self.wind_angle) * 10
        pts = [w + 20, -10, w - 220 + sway, 90, w - 450 + sway*1.4, 180]
        self.create_line(pts, fill="#1F181B", width=12, capstyle="round", smooth=True, tags="tree")
        self.create_line(pts, fill="#3D292D", width=6, capstyle="round", smooth=True, tags="tree")

        self.create_line(w - 220 + sway, 90, w - 320 + sway*1.2, 180, fill="#2A1E22", width=4, smooth=True, tags="tree")
        self.create_line(w - 350 + sway*1.3, 140, w - 430 + sway*1.6, 90, fill="#2A1E22", width=3, smooth=True, tags="tree")

        flower_spots = [
            (w - 150 + sway, 60), (w - 220 + sway, 90), (w - 280 + sway*1.1, 130),
            (w - 350 + sway*1.3, 140), (w - 420 + sway*1.4, 170), (w - 450 + sway*1.4, 180),
            (w - 320 + sway*1.2, 180), (w - 410 + sway*1.5, 95)
        ]

        for fx, fy in flower_spots:
            for angle in range(0, 360, 60):
                rad = math.radians(angle)
                px = fx + math.cos(rad) * 10
                py = fy + math.sin(rad) * 10
                self.create_oval(px-5, py-5, px+5, py+5, fill="#FF69B4", outline="", tags="tree")
            self.create_oval(fx-3, fy-3, fx+3, fy+3, fill="#F5C027", outline="", tags="tree")

    def animate(self):
        self.wind_angle += 0.03
        sway_offset = math.sin(self.wind_angle) * 1.5

        self.delete("petal")

        h = self.winfo_height() or 900
        w = self.winfo_width() or 1400

        for p in self.petals:
            p["y"] += p["speed_y"]
            p["phase"] += 0.03
            p["x"] += p["speed_x"] + math.sin(p["phase"]) * 1.2 + sway_offset * 0.3

            if p["y"] > h + 20:
                p["y"] = random.randint(-50, -10)
                p["x"] = random.randint(0, w)

            s = p["size"]
            self.create_oval(
                p["x"] - s, p["y"] - s * 0.6, p["x"] + s, p["y"] + s * 0.6,
                fill=p["color"], outline="", tags="petal"
            )

        self.after(40, self.animate)

# --- Окно ХАРАКТЕРИСТИКИ КОМАНДЫ ---
class TeamStatsWindow(tk.Toplevel):
    def __init__(self, parent, team_name):
        super().__init__(parent)
        self.title(f"Характеристики: {team_name}")
        self.geometry("920x550")
        self.configure(bg="#0D1017")
        self.team_name = team_name

        self.transient(parent)
        self.grab_set()

        self.build_ui()

    def build_ui(self):
        t_data = db["teams"].get(self.team_name, {})
        coach_name = t_data.get("coach", "Нет")
        chem = t_data.get("chemistry", 0)
        worst_map = t_data.get("worst_map", "Prison")
        best_map = t_data.get("best_map", "Sandstone")

        main_box = tk.Frame(self, bg="#131722", bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        main_box.pack(fill="both", expand=True, padx=20, pady=20)

        # 1. Шапка Команды
        header_frame = tk.Frame(main_box, bg="#131722")
        header_frame.pack(fill="x", padx=25, pady=(20, 15))

        logo_lbl = tk.Label(header_frame, text="🛡️", font=("Segoe UI", 32), bg="#131722", fg=COLOR_GOLD)
        logo_lbl.pack(side="left", padx=(0, 15))

        info_title_box = tk.Frame(header_frame, bg="#131722")
        info_title_box.pack(side="left")

        tk.Label(info_title_box, text=self.team_name, font=("Segoe UI", 20, "bold"), bg="#131722", fg=COLOR_GOLD).pack(anchor="w")
        tk.Label(info_title_box, text=f"👤 Тренер: {coach_name}", font=("Segoe UI", 10), bg="#131722", fg=COLOR_MUTED).pack(anchor="w")

        close_btn = tk.Label(header_frame, text="✕", font=("Segoe UI", 14, "bold"), bg="#131722", fg=COLOR_MUTED, cursor="hand2")
        close_btn.pack(side="right", anchor="n")
        close_btn.bind("<Button-1>", lambda e: self.destroy())

        # 2. Плашка показателей
        meta_row = tk.Frame(main_box, bg="#131722")
        meta_row.pack(fill="x", padx=25, pady=(0, 20))

        roster_dict = t_data.get("roster", {})
        roster_items = []
        if isinstance(roster_dict, dict):
            for k, v in roster_dict.items():
                if isinstance(v, dict):
                    p_name, p_role = v.get("player"), v.get("role", "Рифлер")
                    if p_name and p_name != "Нет": roster_items.append((p_role, p_name))
                elif v and v != "Нет":
                    roster_items.append((k, v))

        roster_players = [p for _, p in roster_items]
        
        avg_rating = 0
        if roster_players:
            tot_r = sum(db["players"].get(p, {}).get("base_rating", 75) for p in roster_players)
            avg_rating = int(tot_r / len(roster_players))

        p1 = tk.Frame(meta_row, bg="#1A1F2C", bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        p1.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=8)
        tk.Label(p1, text=f"🤝 Сыгранность: {chem}%", font=("Segoe UI", 10, "bold"), bg="#1A1F2C", fg=COLOR_TEXT).pack()

        p2 = tk.Frame(meta_row, bg="#1A1F2C", bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        p2.pack(side="left", fill="x", expand=True, padx=5, ipady=8)
        tk.Label(p2, text=f"★ Ср. рейтинг: {avg_rating}", font=("Segoe UI", 10, "bold"), bg="#1A1F2C", fg=COLOR_TEXT).pack()

        p3 = tk.Frame(meta_row, bg="#1A1F2C", bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        p3.pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=8)
        tk.Label(p3, text=f"🗺 {worst_map} / {best_map}", font=("Segoe UI", 10, "bold"), bg="#1A1F2C", fg=COLOR_TEXT).pack()

        # 3. Состав
        tk.Label(main_box, text="👥 СОСТАВ КОМАНДЫ", font=("Segoe UI", 10, "bold"), bg="#131722", fg=COLOR_MUTED).pack(anchor="w", padx=25, pady=(5, 8))

        table_frame = tk.Frame(main_box, bg="#131722")
        table_frame.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        headers = [("Игрок", 18, "w"), ("Роль", 18, "w"), ("Рейт", 6, "center"), ("K/D", 8, "center"), ("ADR", 8, "center"), ("KAST", 8, "center"), ("IMP", 8, "center"), ("Рейтинг", 8, "center")]
        
        h_row = tk.Frame(table_frame, bg="#1A1F2C")
        h_row.pack(fill="x", pady=(0, 5))
        for h_text, w, align in headers:
            tk.Label(h_row, text=h_text, font=("Segoe UI", 8, "bold"), bg="#1A1F2C", fg=COLOR_MUTED, width=w, anchor=align).pack(side="left", padx=2, pady=5)

        for role_title, p_name in roster_items:
            p_data = db["players"].get(p_name, {})
            base_r = p_data.get("base_rating", 75)

            # Детерминированный расчет без вмешательства в random.seed()
            r_seed = sum(ord(c) for c in p_name)
            kd = round(0.85 + (base_r / 100.0) * 0.4 + ((r_seed % 13) - 6) * 0.01, 2)
            adr = int(70 + (base_r / 100.0) * 35 + ((r_seed % 15) - 7))
            kast = int(65 + (base_r / 100.0) * 15 + ((r_seed % 9) - 4))
            imp = round(0.80 + (base_r / 100.0) * 0.4 + ((r_seed % 11) - 5) * 0.01, 2)
            perf_rating = round(0.50 + (kd * 0.3) + (adr / 150.0) * 0.3, 2)

            row = tk.Frame(table_frame, bg="#131722")
            row.pack(fill="x", pady=2)

            tk.Label(row, text=p_name, font=("Segoe UI", 9, "bold"), bg="#131722", fg=COLOR_TEXT, width=18, anchor="w").pack(side="left", padx=2)
            tk.Label(row, text=role_title, font=("Segoe UI", 9), bg="#131722", fg=COLOR_MUTED, width=18, anchor="w").pack(side="left", padx=2)
            tk.Label(row, text=str(base_r), font=("Segoe UI", 9, "bold"), bg="#131722", fg=COLOR_GOLD, width=6, anchor="center").pack(side="left", padx=2)
            tk.Label(row, text=f"{kd:.2f}", font=("Segoe UI", 9), bg="#131722", fg=COLOR_TEXT, width=8, anchor="center").pack(side="left", padx=2)
            tk.Label(row, text=str(adr), font=("Segoe UI", 9), bg="#131722", fg=COLOR_TEXT, width=8, anchor="center").pack(side="left", padx=2)
            tk.Label(row, text=f"{kast}%", font=("Segoe UI", 9), bg="#131722", fg=COLOR_TEXT, width=8, anchor="center").pack(side="left", padx=2)
            tk.Label(row, text=f"{imp:.2f}", font=("Segoe UI", 9), bg="#131722", fg=COLOR_TEXT, width=8, anchor="center").pack(side="left", padx=2)
            tk.Label(row, text=f"{perf_rating:.2f}", font=("Segoe UI", 9, "bold"), bg="#131722", fg=COLOR_GOLD if perf_rating >= 1.15 else COLOR_TEXT, width=8, anchor="center").pack(side="left", padx=2)

# --- Окно выбора карты ---
class MapSelectorWindow(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Выбор Локации [Neon Edition]")
        self.geometry("950x650")
        self.configure(bg=COLOR_BG)
        self.callback = callback
        
        self.transient(parent)
        self.grab_set()

        self.create_ui()

    def create_ui(self):
        top_bar = tk.Frame(self, bg=COLOR_BG)
        top_bar.pack(fill="x", padx=20, pady=15)

        header = tk.Label(top_bar, text="ВЫБОР ЛОКАЦИИ", font=("Impact", 22), bg=COLOR_BG, fg=COLOR_NEON_CYAN)
        header.pack(side="left")

        btn_auto = NeonButton(top_bar, text="🎲 Автовыбор", width=140, height=34, neon_color=COLOR_GOLD, command=lambda: self.select_map(None))
        btn_auto.pack(side="right")

        canvas = tk.Canvas(self, bg=COLOR_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg=COLOR_BG)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        cols = 3
        for index, map_name in enumerate(MAPS):
            row = index // cols
            col = index % cols
            
            card = self.build_map_card(scrollable_frame, map_name)
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

    def build_map_card(self, parent, map_name):
        data = MAP_DETAILS.get(map_name, {"type": "Unknown", "desc": "Описание отсутствует."})
        
        frame = tk.Frame(parent, bg=COLOR_CARD, bd=2, relief="flat", highlightbackground=COLOR_BORDER, highlightthickness=2)
        frame.bind("<Enter>", lambda e, f=frame: f.config(highlightbackground=COLOR_NEON_CYAN))
        frame.bind("<Leave>", lambda e, f=frame: f.config(highlightbackground=COLOR_BORDER))

        top_bar = tk.Frame(frame, bg=COLOR_CARD)
        top_bar.pack(fill="x", padx=15, pady=(15, 5))
        
        tk.Label(top_bar, text=map_name, font=("Segoe UI", 16, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT).pack(side="left")
        tk.Label(top_bar, text=data["type"].upper(), font=("Segoe UI", 8, "bold"), bg=COLOR_NEON_PINK, fg="#FFFFFF").pack(side="right")

        desc_lbl = tk.Label(frame, text=data["desc"], font=("Segoe UI", 10), bg=COLOR_CARD, fg=COLOR_MUTED, wraplength=220, justify="left")
        desc_lbl.pack(fill="x", padx=15, pady=10)

        btn_frame = tk.Frame(frame, bg=COLOR_CARD)
        btn_frame.pack(fill="x", side="bottom", pady=15)
        
        NeonButton(btn_frame, text="ВЫБРАТЬ", width=120, height=30, neon_color=COLOR_NEON_CYAN, 
                   command=lambda m=map_name: self.select_map(m)).pack()

        return frame

    def select_map(self, map_name):
        self.callback(map_name)
        self.destroy()

# --- Движок Симуляции ---
class MatchEngine:
    @staticmethod
    def get_player_power(player_name, role):
        p_data = db["players"].get(player_name, {})
        base = p_data.get("base_rating", 75)
        prof = p_data.get("roles", {}).get(role, "Хорошо")
        return base * ROLE_MULTIPLIERS.get(prof, 1.0)

    @staticmethod
    def calculate_team_map_power(team_name, map_name):
        t_data = db["teams"].get(team_name, {})
        roster = t_data.get("roster", {})
        
        roster_items = []
        if isinstance(roster, dict):
            for k, v in roster.items():
                if isinstance(v, dict):
                    p_name, p_role = v.get("player"), v.get("role", "Рифлер")
                    if p_name and p_name != "Нет": roster_items.append((p_role, p_name))
                elif v and v != "Нет":
                    roster_items.append((k, v))

        players_power = sum(
            MatchEngine.get_player_power(p_name, role)
            for role, p_name in roster_items
        )
        if not roster_items or len(roster_items) < 5:
            players_power = max(players_power, 350)

        chem = t_data.get("chemistry", 0)
        chem_factor = 0.85 + (chem / 100.0) * 0.30

        coach_name = t_data.get("coach", "Нет")
        coach_rating = db["coaches"].get(coach_name, {}).get("rating", 0) if coach_name != "Нет" else 0
        coach_factor = 1.0 + (coach_rating / 100.0) * 0.08

        map_factor = 1.10 if map_name == t_data.get("best_map") else (0.90 if map_name == t_data.get("worst_map") else 1.0)
        return players_power * chem_factor * coach_factor * map_factor

    @staticmethod
    def simulate_map(team_a, team_b, map_name):
        power_a = MatchEngine.calculate_team_map_power(team_a, map_name)
        power_b = MatchEngine.calculate_team_map_power(team_b, map_name)

        score_a, score_b, rounds_played = 0, 0, 0
        
        def get_roster_players(t_name):
            r = db["teams"].get(t_name, {}).get("roster", {})
            res = []
            if isinstance(r, dict):
                for k, v in r.items():
                    if isinstance(v, dict):
                        p = v.get("player")
                        if p and p != "Нет": res.append(p)
                    elif v and v != "Нет":
                        res.append(v)
            return res

        roster_a = get_roster_players(team_a)
        roster_b = get_roster_players(team_b)

        stats_a = {p: {"K": 0, "A": 0, "D": 0, "damage": 0, "hs": 0, "kast": 0, "imp": 0.0} for p in roster_a}
        stats_b = {p: {"K": 0, "A": 0, "D": 0, "damage": 0, "hs": 0, "kast": 0, "imp": 0.0} for p in roster_b}

        prob_a = power_a / max(1, (power_a + power_b))

        def pick_weighted_player(roster):
            if not roster: return None
            weights = [MatchEngine.get_player_power(p, "Рифлер") for p in roster]
            return random.choices(roster, weights=weights, k=1)[0]

        while True:
            rounds_played += 1
            win_prob = prob_a * 0.94 + random.uniform(-0.06, 0.06) if rounds_played in [1, 13] else prob_a
            winner = team_a if random.random() < win_prob else team_b

            if winner == team_a:
                score_a += 1
                win_roster, lose_roster = roster_a, roster_b
                win_stats, lose_stats = stats_a, stats_b
            else:
                score_b += 1
                win_roster, lose_roster = roster_b, roster_a
                win_stats, lose_stats = stats_b, stats_a

            if win_roster and lose_roster:
                for _ in range(5):
                    killer = pick_weighted_player(win_roster)
                    victim = random.choice(lose_roster)
                    win_stats[killer]["K"] += 1
                    win_stats[killer]["damage"] += random.randint(80, 140)
                    win_stats[killer]["imp"] += 0.08
                    if random.random() < 0.42:
                        win_stats[killer]["hs"] += 1
                    lose_stats[victim]["D"] += 1

                    if len(win_roster) > 1 and random.random() < 0.55:
                        assist_candidates = [p for p in win_roster if p != killer]
                        if assist_candidates:
                            assist = random.choice(assist_candidates)
                            win_stats[assist]["A"] += 1

                lose_kills = random.randint(1, 4) if random.random() < 0.85 else 0
                for _ in range(lose_kills):
                    killer = pick_weighted_player(lose_roster)
                    victim = random.choice(win_roster)
                    lose_stats[killer]["K"] += 1
                    lose_stats[killer]["damage"] += random.randint(80, 140)
                    lose_stats[killer]["imp"] += 0.08
                    if random.random() < 0.42:
                        lose_stats[killer]["hs"] += 1
                    win_stats[victim]["D"] += 1

                    if len(lose_roster) > 1 and random.random() < 0.55:
                        assist_candidates = [p for p in lose_roster if p != killer]
                        if assist_candidates:
                            assist = random.choice(assist_candidates)
                            lose_stats[assist]["A"] += 1

            for st in [stats_a, stats_b]:
                for p in st:
                    if random.random() < 0.75:
                        st[p]["kast"] += 1

            if (score_a >= 13 or score_b >= 13) and abs(score_a - score_b) >= 2:
                break

        return score_a, score_b, stats_a, stats_b, rounds_played

# --- Главное Приложение ---
class StandoffApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Standoff 2 Esports Hub")
        self.geometry("1400x900")
        self.configure(bg=COLOR_BG)

        self.manual_map = None 

        self.setup_styles()
        
        self.bg_canvas = SakuraCanvas(self)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self.main_container = tk.Frame(self, bg=COLOR_BG)
        self.main_container.pack(fill="both", expand=True, padx=30, pady=20)

        self.create_header()
        self.create_tabs()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(".", background=COLOR_BG, foreground=COLOR_TEXT, fieldbackground=COLOR_CARD_INNER)
        style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=COLOR_CARD, foreground=COLOR_MUTED, padding=[24, 10], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", COLOR_CARD_INNER)], foreground=[("selected", COLOR_GOLD)])
        
        style.configure("TCombobox", 
                        fieldbackground=COLOR_CARD_INNER, 
                        background=COLOR_BORDER, 
                        foreground=COLOR_TEXT, 
                        darkcolor=COLOR_BORDER,
                        lightcolor=COLOR_BORDER,
                        arrowcolor=COLOR_GOLD,
                        bordercolor=COLOR_BORDER,
                        insertcolor=COLOR_TEXT)
        
        style.map("TCombobox", 
                  fieldbackground=[("readonly", COLOR_CARD_INNER), ("focus", COLOR_CARD_INNER), ("!disabled", COLOR_CARD_INNER)],
                  foreground=[("readonly", COLOR_TEXT), ("focus", COLOR_TEXT), ("!disabled", COLOR_TEXT)],
                  background=[("readonly", COLOR_BORDER), ("focus", COLOR_BORDER), ("!disabled", COLOR_BORDER)],
                  selectbackground=[("readonly", COLOR_NEON_CYAN), ("focus", COLOR_NEON_CYAN)],
                  selectforeground=[("readonly", "#000000"), ("focus", "#000000")])
        
        self.option_add('*TCombobox*Listbox.background', COLOR_CARD_INNER)
        self.option_add('*TCombobox*Listbox.foreground', COLOR_TEXT)
        self.option_add('*TCombobox*Listbox.selectBackground', COLOR_NEON_CYAN)
        self.option_add('*TCombobox*Listbox.selectForeground', '#000000')
        self.option_add('*TCombobox*Listbox.borderWidth', 1)
        self.option_add('*TCombobox*Listbox.relief', 'solid')

    def create_header(self):
        header = tk.Frame(self.main_container, bg=COLOR_CARD, bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        header.pack(fill="x", pady=(0, 15))

        title_frame = tk.Frame(header, bg=COLOR_CARD)
        title_frame.pack(side="left", padx=20, pady=12)

        tk.Label(title_frame, text="STANDOFF 2", font=("Impact", 22), bg=COLOR_CARD, fg=COLOR_GOLD).pack(side="left")
        tk.Label(title_frame, text="  │  ESPORTS HUB", font=("Segoe UI", 11, "bold"), bg=COLOR_CARD, fg=COLOR_MUTED).pack(side="left")

        btn_import = NeonButton(
            header, text="Импортировать команды", command=self.load_preset_teams,
            width=200, height=36, neon_color=COLOR_NEON_CYAN
        )
        btn_import.pack(side="right", padx=15, pady=8)

    def create_tabs(self):
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill="both", expand=True)

        self.tab_match = ttk.Frame(self.notebook)
        self.tab_players = ttk.Frame(self.notebook)
        self.tab_teams = ttk.Frame(self.notebook)
        self.tab_coaches = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_match, text="Матч-Центр")
        self.notebook.add(self.tab_players, text="Игроки")
        self.notebook.add(self.tab_teams, text="Команды")
        self.notebook.add(self.tab_coaches, text="Тренеры")

        self.build_match_tab()
        self.build_players_tab()
        self.build_teams_tab()
        self.build_coaches_tab()

    def create_card(self, parent):
        return tk.Frame(parent, bg=COLOR_CARD, bd=1, relief="solid", highlightbackground=COLOR_BORDER)

    def create_entry(self, parent):
        return tk.Entry(
            parent, bg=COLOR_CARD_INNER, fg=COLOR_TEXT, insertbackground="#FFF",
            bd=1, relief="solid", selectbackground=COLOR_NEON_CYAN, selectforeground="#000000",
            highlightthickness=1, highlightbackground=COLOR_BORDER, highlightcolor=COLOR_NEON_CYAN
        )

    def create_listbox(self, parent):
        return tk.Listbox(
            parent, bg=COLOR_CARD_INNER, fg=COLOR_TEXT, selectbackground=COLOR_NEON_CYAN,
            selectforeground="#000000", bd=0, highlightthickness=1, highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_NEON_CYAN, activestyle="none"
        )

    # --- ИМПОРТИРОВАНИЕ КОМАНД С МНОЖЕСТВЕННЫМИ РОЛЯМИ И БЕЗ SAKURA ---
    def load_preset_teams(self):
        if not messagebox.askyesno("Подтверждение", "Загрузка базовых команд перезапишет текущие данные команд и игроков.\nПродолжить?"):
            return

        db["players"].clear()
        db["coaches"].clear()
        db["teams"].clear()

        preset_coaches = {
            "Kuba": 99, "inverness": 99, "dstr": 99, "postanova": 98,
            "TOSS": 95, "JOHNY": 94, "Pronyx": 92, "hellmxre": 90,
            "SiD": 90, "4ambi": 89, "deserve": 87, "Apart": 84,
            "karuseel": 83, "payback": 83, "ins1der": 81, "Relax": 81,
            "FLAFFY": 80, "befoRe": 79, "sab1t": 78, "uspik": 75,
            "Shame": 73, "n1kson": 70, "Nonstxp": 69, "Paydeck": 65
        }

        for c_name, c_rating in preset_coaches.items():
            db["coaches"][c_name] = {"rating": c_rating}

        preset_teams = {
            "Virtus Pro": {
                "best": "Prison", "worst": "Hanami",
                "roster": [("Reason", "Снайпер"), ("Hi-Lo", "Рифлер"), ("Lunax", "Люркер"), ("Arventy", "Капитан"), ("chipaa", "Рифлер")],
                "ratings": {"Reason": 97, "Hi-Lo": 99, "Lunax": 99, "Arventy": 95, "chipaa": 96}
            },
            "CyberHero": {
                "best": "Sandstone", "worst": "Rust",
                "roster": [("scndoom", "Саппорт"), ("FLACSYS", "Опенер"), ("cxtleta", "Рифлер"), ("Nekr0", "Капитан"), ("Enough", "Снайпер")],
                "ratings": {"scndoom": 97, "FLACSYS": 93, "cxtleta": 97, "Nekr0": 96, "Enough": 96}
            },
            "VozWooden": {
                "best": "Province", "worst": "Breeze",
                "roster": [("qu1ns3", "Капитан-Снайпер"), ("Ping", "Саппорт"), ("n2say", "Люркер"), ("Horts", "Опенер"), ("Kot", "Рифлер")],
                "ratings": {"qu1ns3": 90, "Ping": 89, "n2say": 85, "Horts": 90, "Kot": 94}
            },
            "Alpha 7": {
                "best": "Breeze", "worst": "Dune",
                "roster": [("Kyten", "Капитан"), ("Metal", "Рифлер"), ("Jabbi", "Опенер"), ("GSN", "Саппорт"), ("Ale", "Снайпер")],
                "ratings": {"Kyten": 88, "Metal": 91, "Jabbi": 90, "GSN": 88, "Ale": 90}
            },
            "CyberTeam": {
                "best": "Rust", "worst": "Dune",
                "roster": [("molodoy", "Опенер"), ("PariS", "Рифлер"), ("volex", "Люркер"), ("street", "Саппорт"), ("tapochek", "Капитан-Снайпер")],
                "ratings": {"molodoy": 87, "PariS": 86, "volex": 85, "street": 84, "tapochek": 87}
            },
            "Maverick": {
                "best": "Sandstone", "worst": "Hanami",
                "roster": [("Kuba", "Капитан"), ("blaster", "Опенер"), ("Relayx", "Рифлер"), ("l1rkuzz", "Опенер"), ("Relax1on", "Люркер")],
                "ratings": {"Kuba": 88, "blaster": 85, "Relayx": 89, "l1rkuzz": 88, "Relax1on": 85}
            },
            "Gen X": {
                "best": "Dune", "worst": "Prison",
                "roster": [("Pla1nt", "Опенер"), ("dzin", "Капитан"), ("nvy", "Саппорт"), ("packo", "Рифлер"), ("Dazzik", "Люркер")],
                "ratings": {"Pla1nt": 87, "dzin": 85, "nvy": 84, "packo": 85, "Dazzik": 78}
            },
            "CyberShoke": {
                "best": "Hanami", "worst": "Breeze",
                "roster": [("Hlp", "Опенер"), ("Y9do", "Рифлер"), ("Dazz", "Капитан"), ("S1ndy", "Опенер"), ("R6ght", "Рифлер")],
                "ratings": {"Hlp": 95, "Y9do": 97, "Dazz": 95, "S1ndy": 98, "R6ght": 96}
            },
            "Shadow Tigers": {
                "best": "Sandstone", "worst": "Dune",
                "roster": [("Krong", "Капитан"), ("Toose", "Рифлер"), ("nights", "Опенер"), ("Hopyx", "Снайпер"), ("Vetrol", "Люркер")],
                "ratings": {"Krong": 88, "Toose": 86, "nights": 91, "Hopyx": 87, "Vetrol": 90}
            },
            "Madbulls": {
                "best": "Province", "worst": "Rust",
                "roster": [("FANT1M", "Опенер"), ("ck", "Саппорт"), ("nia", "Люркер"), ("D3Fence", "Рифлер"), ("Franker", "Рифлер")],
                "ratings": {"FANT1M": 85, "ck": 84, "nia": 85, "D3Fence": 86, "Franker": 92}
            },
            "Esize Team": {
                "best": "Breeze", "worst": "Province",
                "roster": [("XZise", "Капитан"), ("Wyrdin", "Рифлер"), ("Zarvan", "Снайпер"), ("z1der", "Опенер"), ("naoto", "Саппорт")],
                "ratings": {"XZise": 94, "Wyrdin": 86, "Zarvan": 85, "z1der": 85, "naoto": 84}
            },
            "Mafiozy Esports": {
                "best": "Rust", "worst": "Sandstone",
                "roster": [("incleas", "Капитан"), ("ezio", "Рифлер"), ("dress", "Саппорт"), ("ReNiTe", "Опенер"), ("strezu", "Люркер")],
                "ratings": {"incleas": 85, "ezio": 86, "dress": 85, "ReNiTe": 86, "strezu": 88}
            }
        }

        for t_name, data in preset_teams.items():
            roster_dict = {}
            for idx, (p_name, p_role) in enumerate(data["roster"], 1):
                role_skills = {}
                for role in ROLES:
                    role_skills[role] = "Прекрасно" if role == p_role else random.choice(["Отлично", "Хорошо"])
                
                db["players"][p_name] = {
                    "base_rating": data["ratings"][p_name],
                    "roles": role_skills
                }

                roster_dict[f"Slot_{idx}"] = {"player": p_name, "role": p_role}

            db["teams"][t_name] = {
                "chemistry": 0,       
                "coach": "Нет",       
                "best_map": data["best"],
                "worst_map": data["worst"],
                "roster": roster_dict
            }

        save_db(db)
        self.refresh_all_views()
        messagebox.showinfo("Успешно!", "Команды успешно загружены!\n\n• Карта Sakura удалена\n• В составах разрешено несколько игроков одной роли (например, 2 Рифлера)\n• У всех сыгранность 0%, тренеры не экипированы")

    def refresh_all_views(self):
        self.refresh_players_list()
        self.refresh_coaches_list()
        self.refresh_teams_list()
        self.refresh_team_dropdowns()
        self.refresh_match_team_combos()

    # ==================== MATCH CENTER ====================
    def build_match_tab(self):
        card = self.create_card(self.tab_match)
        card.pack(fill="both", expand=True, padx=5, pady=5)

        top_ctrl = tk.Frame(card, bg=COLOR_CARD, bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        top_ctrl.pack(fill="x", padx=15, pady=15)

        ctrl_inner = tk.Frame(top_ctrl, bg=COLOR_CARD)
        ctrl_inner.pack(pady=10)

        tk.Label(ctrl_inner, text="КОМАНДА A:", font=("Segoe UI", 9, "bold"), bg=COLOR_CARD, fg=COLOR_MUTED).grid(row=0, column=0, padx=5)
        self.m_team_a_cb = ttk.Combobox(ctrl_inner, state="readonly", width=18)
        self.m_team_a_cb.grid(row=0, column=1, padx=5)

        tk.Label(ctrl_inner, text="VS", font=("Impact", 14), bg=COLOR_CARD, fg=COLOR_GOLD).grid(row=0, column=2, padx=15)

        tk.Label(ctrl_inner, text="КОМАНДА B:", font=("Segoe UI", 9, "bold"), bg=COLOR_CARD, fg=COLOR_MUTED).grid(row=0, column=3, padx=5)
        self.m_team_b_cb = ttk.Combobox(ctrl_inner, state="readonly", width=18)
        self.m_team_b_cb.grid(row=0, column=4, padx=5)

        tk.Label(ctrl_inner, text="ФОРМАТ:", font=("Segoe UI", 9, "bold"), bg=COLOR_CARD, fg=COLOR_MUTED).grid(row=0, column=5, padx=10)
        self.m_format_cb = ttk.Combobox(ctrl_inner, values=["BO1", "BO2", "BO3"], state="readonly", width=6)
        self.m_format_cb.set("BO3")
        self.m_format_cb.grid(row=0, column=6, padx=5)

        btn_sim = NeonButton(ctrl_inner, text="СИМУЛИРОВАТЬ", command=self.run_simulation, width=150, height=36, neon_color=COLOR_GOLD)
        btn_sim.grid(row=0, column=7, padx=15)

        btn_map = NeonButton(ctrl_inner, text="ВЫБРАТЬ КАРТУ", command=self.open_map_selector, width=150, height=36, neon_color=COLOR_NEON_PINK)
        btn_map.grid(row=0, column=8, padx=5)

        self.selected_map_label = tk.Label(ctrl_inner, text="Карта: Авто", font=("Segoe UI", 9, "bold"), bg=COLOR_CARD, fg=COLOR_NEON_CYAN)
        self.selected_map_label.grid(row=0, column=9, padx=10)

        self.match_result_frame = tk.Frame(card, bg=COLOR_BG)
        self.match_result_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.refresh_match_team_combos()

    def refresh_match_team_combos(self):
        teams = list(db["teams"].keys())
        self.m_team_a_cb["values"] = teams
        self.m_team_b_cb["values"] = teams
        if len(teams) >= 2:
            self.m_team_a_cb.set(teams[0])
            self.m_team_b_cb.set(teams[1])

    def open_map_selector(self):
        def on_map_chosen(map_name):
            self.manual_map = map_name
            if map_name:
                self.selected_map_label.config(text=f"Карта: {map_name}")
            else:
                self.selected_map_label.config(text="Карта: Авто")
            
        MapSelectorWindow(self, on_map_chosen)

    def run_simulation(self):
        team_a = self.m_team_a_cb.get()
        team_b = self.m_team_b_cb.get()
        fmt = self.m_format_cb.get()

        if not team_a or not team_b or team_a == team_b:
            messagebox.showerror("Ошибка", "Выберите две разные команды!")
            return

        for widget in self.match_result_frame.winfo_children():
            widget.destroy()

        if self.manual_map:
            if fmt == "BO1":
                maps_pool = [self.manual_map]
            elif fmt == "BO2":
                other_maps = [m for m in MAPS if m != self.manual_map]
                maps_pool = [self.manual_map] + random.sample(other_maps, 1)
            else:
                other_maps = [m for m in MAPS if m != self.manual_map]
                maps_pool = [self.manual_map] + random.sample(other_maps, 2)
        else:
            maps_count = 1 if fmt == "BO1" else (2 if fmt == "BO2" else 3)
            maps_pool = random.sample(MAPS, maps_count)

        maps_won_a, maps_won_b = 0, 0
        total_rounds_a, total_rounds_b = 0, 0
        total_stats = {team_a: {}, team_b: {}}
        map_results = []

        for idx, m_name in enumerate(maps_pool):
            if fmt == "BO3" and (maps_won_a == 2 or maps_won_b == 2):
                break

            s_a, s_b, st_a, st_b, r_played = MatchEngine.simulate_map(team_a, team_b, m_name)
            total_rounds_a += s_a
            total_rounds_b += s_b
            
            winner_m = team_a if s_a > s_b else team_b
            if s_a > s_b: maps_won_a += 1
            else: maps_won_b += 1

            map_results.append((f"{idx+1}. {m_name}", s_a, s_b, winner_m))

            for p, st in st_a.items():
                if p not in total_stats[team_a]:
                    total_stats[team_a][p] = {"K": 0, "A": 0, "D": 0, "damage": 0, "hs": 0, "kast": 0, "imp": 0.0}
                for k in st: total_stats[team_a][p][k] += st[k]

            for p, st in st_b.items():
                if p not in total_stats[team_b]:
                    total_stats[team_b][p] = {"K": 0, "A": 0, "D": 0, "damage": 0, "hs": 0, "kast": 0, "imp": 0.0}
                for k in st: total_stats[team_b][p][k] += st[k]

        if maps_won_a > maps_won_b:
            final_winner = team_a
        elif maps_won_b > maps_won_a:
            final_winner = team_b
        else:
            final_winner = "НИЧЬЯ"

        db["match_history"].append({
            "team_a": team_a, "team_b": team_b,
            "score_a": maps_won_a, "score_b": maps_won_b,
            "winner": final_winner
        })
        save_db(db)

        all_players_eval = []
        tot_rounds = max(1, total_rounds_a + total_rounds_b)

        for t_name, p_dict in total_stats.items():
            for p_name, st in p_dict.items():
                if not p_name: continue
                kd = st["K"] / max(1, st["D"])
                adr = int(st["damage"] / tot_rounds)
                kast_pct = min(100, int((st["kast"] / tot_rounds) * 100))
                imp_val = round(0.80 + (st["imp"] / tot_rounds), 2)
                rating = round(0.40 + (kd * 0.35) + (adr / 130.0) * 0.35 + (kast_pct / 200.0), 2)
                
                role_str = "Игрок"
                t_roster = db["teams"].get(t_name, {}).get("roster", {})
                if isinstance(t_roster, dict):
                    for k, v in t_roster.items():
                        if isinstance(v, dict) and v.get("player") == p_name:
                            role_str = v.get("role", "Игрок")
                            break
                        elif v == p_name:
                            role_str = k
                            break

                all_players_eval.append({
                    "name": p_name, "team": t_name, "role": role_str,
                    "k": st["K"], "a": st["A"], "d": st["D"],
                    "kd": f"{kd:.2f}", "adr": adr, "kast": f"{kast_pct}%",
                    "imp": f"{imp_val:.2f}", "rating": f"{rating:.2f}", "raw_rating": rating
                })

        all_players_eval.sort(key=lambda x: x["raw_rating"], reverse=True)
        mvp = all_players_eval[0] if all_players_eval else None

        self.render_match_view(
            team_a, team_b, maps_won_a, maps_won_b, final_winner,
            maps_pool[:len(map_results)], map_results, mvp, all_players_eval
        )

    def render_match_view(self, team_a, team_b, score_a, score_b, winner, maps_list, map_results, mvp, players_stats):
        container = self.match_result_frame

        center_frame = tk.Frame(container, bg=COLOR_BG)
        center_frame.pack(expand=True, fill="both", padx=10, pady=5)

        head_lbl = tk.Label(center_frame, text="🎮 ИТОГИ МАТЧА", font=("Segoe UI", 14, "bold"), bg=COLOR_BG, fg=COLOR_GOLD)
        head_lbl.pack(pady=(2, 8))

        score_card = tk.Frame(center_frame, bg=COLOR_CARD, bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        score_card.pack(fill="x", pady=(0, 8), ipadx=10, ipady=6)

        score_box = tk.Frame(score_card, bg=COLOR_CARD)
        score_box.pack()

        tk.Label(score_box, text=f"{team_a}   ", font=("Segoe UI", 14, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT).pack(side="left")
        tk.Label(score_box, text=f"{score_a}", font=("Impact", 24), bg=COLOR_CARD, fg=COLOR_GOLD if winner == team_a else COLOR_TEXT).pack(side="left")
        tk.Label(score_box, text="  :  ", font=("Segoe UI", 14, "bold"), bg=COLOR_CARD, fg=COLOR_MUTED).pack(side="left")
        tk.Label(score_box, text=f"{score_b}", font=("Impact", 24), bg=COLOR_CARD, fg=COLOR_GOLD if winner == team_b else COLOR_TEXT).pack(side="left")
        tk.Label(score_box, text=f"   {team_b}", font=("Segoe UI", 14, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT).pack(side="left")

        meta_box = tk.Frame(score_card, bg=COLOR_CARD)
        meta_box.pack(pady=(4, 0))

        w_text = f"  [{winner.upper()} ПОБЕДА!]  " if winner != "НИЧЬЯ" else "  [НИЧЬЯ 1 : 1]  "
        w_bg = COLOR_GOLD if winner != "НИЧЬЯ" else COLOR_NEON_CYAN
        badge = tk.Label(meta_box, text=w_text, font=("Segoe UI", 8, "bold"), bg=w_bg, fg="#000000")
        badge.pack(side="left", padx=(0, 10))

        maps_str = ", ".join(maps_list)
        tk.Label(meta_box, text=f"Карты: {maps_str}", font=("Segoe UI", 8), bg=COLOR_CARD, fg=COLOR_MUTED).pack(side="left")

        row_info = tk.Frame(center_frame, bg=COLOR_BG)
        row_info.pack(fill="x", pady=(0, 8))

        if mvp:
            mvp_card = tk.Frame(row_info, bg=COLOR_CARD, bd=1, relief="solid", highlightbackground=COLOR_GOLD)
            mvp_card.pack(side="left", fill="both", expand=True, padx=(0, 5), ipady=4)
            mvp_text = f"★ MVP: {mvp['name']} ({mvp['team']})  |  Рейт: {mvp['rating']}  |  K/D: {mvp['kd']}  |  ADR: {mvp['adr']}"
            tk.Label(mvp_card, text=mvp_text, font=("Segoe UI", 9, "bold"), bg=COLOR_CARD, fg=COLOR_GOLD).pack(expand=True)

        res_str = " | ".join([f"{m_title.split('.')[1].strip()}: {sa}:{sb}" for m_title, sa, sb, _ in map_results])
        maps_card = tk.Frame(row_info, bg=COLOR_CARD, bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        maps_card.pack(side="right", fill="both", expand=True, padx=(5, 0), ipady=4)
        tk.Label(maps_card, text=f"🗺 Карты: {res_str}", font=("Segoe UI", 9, "bold"), bg=COLOR_CARD, fg=COLOR_NEON_CYAN).pack(expand=True)

        tables_frame = tk.Frame(center_frame, bg=COLOR_BG)
        tables_frame.pack(fill="both", expand=True)
        tables_frame.columnconfigure((0, 1), weight=1, uniform="team_tables")

        cols = [("Игрок", 11, "w"), ("K/A/D", 7, "center"), ("K/D", 5, "center"), ("ADR", 5, "center"), ("KAST", 5, "center"), ("Рейт", 5, "center")]

        for idx, t_name in enumerate([team_a, team_b]):
            t_card = tk.Frame(tables_frame, bg=COLOR_CARD, bd=1, relief="solid", highlightbackground=COLOR_BORDER)
            t_card.grid(row=0, column=idx, padx=4 if idx == 0 else 4, sticky="nsew", ipady=5)

            tk.Label(t_card, text=t_name, font=("Segoe UI", 10, "bold"), bg=COLOR_CARD, fg=COLOR_GOLD).pack(pady=(4, 4))

            h_frame = tk.Frame(t_card, bg=COLOR_CARD_INNER)
            h_frame.pack(fill="x", padx=6, pady=(0, 2))

            for title, w, align in cols:
                tk.Label(h_frame, text=title, font=("Segoe UI", 7, "bold"), bg=COLOR_CARD_INNER, fg=COLOR_MUTED, width=w, anchor=align).pack(side="left", padx=1, pady=2)

            team_players = [p for p in players_stats if p["team"] == t_name]
            for p in team_players:
                r_frame = tk.Frame(t_card, bg=COLOR_CARD)
                r_frame.pack(fill="x", padx=6, pady=1)

                is_mvp = mvp and p["name"] == mvp["name"]
                p_color = COLOR_GOLD if is_mvp else COLOR_TEXT
                font_style = ("Segoe UI", 8, "bold") if is_mvp else ("Segoe UI", 8)

                tk.Label(r_frame, text=p['name'], font=font_style, bg=COLOR_CARD, fg=p_color, width=11, anchor="w").pack(side="left", padx=1)
                tk.Label(r_frame, text=f"{p['k']}/{p['a']}/{p['d']}", font=("Segoe UI", 8), bg=COLOR_CARD, fg=COLOR_MUTED, width=7, anchor="center").pack(side="left", padx=1)
                tk.Label(r_frame, text=p["kd"], font=("Segoe UI", 8, "bold"), bg=COLOR_CARD, fg=COLOR_GOLD if float(p["kd"]) >= 1.1 else COLOR_TEXT, width=5, anchor="center").pack(side="left", padx=1)
                tk.Label(r_frame, text=p["adr"], font=("Segoe UI", 8), bg=COLOR_CARD, fg=COLOR_TEXT, width=5, anchor="center").pack(side="left", padx=1)
                tk.Label(r_frame, text=p["kast"], font=("Segoe UI", 8), bg=COLOR_CARD, fg=COLOR_TEXT, width=5, anchor="center").pack(side="left", padx=1)
                tk.Label(r_frame, text=p["rating"], font=("Segoe UI", 8, "bold"), bg=COLOR_CARD, fg=COLOR_GOLD, width=5, anchor="center").pack(side="left", padx=1)

    # ==================== ИГРОКИ ====================
    def build_players_tab(self):
        card = self.create_card(self.tab_players)
        card.pack(fill="both", expand=True, padx=5, pady=5)

        center_box = tk.Frame(card, bg=COLOR_CARD)
        center_box.pack(expand=True, fill="both", padx=40, pady=20)

        form_frame = tk.Frame(center_box, bg=COLOR_CARD)
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

        tk.Label(form_frame, text="ПРОФИЛЬ ИГРОКА", font=("Segoe UI", 12, "bold"), bg=COLOR_CARD, fg=COLOR_GOLD).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        tk.Label(form_frame, text="Никнейм:", bg=COLOR_CARD, fg=COLOR_TEXT).grid(row=1, column=0, sticky="w", pady=3)
        self.p_name_entry = self.create_entry(form_frame)
        self.p_name_entry.grid(row=1, column=1, sticky="ew", pady=3)

        tk.Label(form_frame, text="Базовый rating (1-100):", bg=COLOR_CARD, fg=COLOR_TEXT).grid(row=2, column=0, sticky="w", pady=3)
        self.p_rating_entry = self.create_entry(form_frame)
        self.p_rating_entry.insert(0, "85")
        self.p_rating_entry.grid(row=2, column=1, sticky="ew", pady=3)

        tk.Label(form_frame, text="ЭФФЕКТИВНОСТЬ РОЛЕЙ", font=("Segoe UI", 10, "bold"), bg=COLOR_CARD, fg=COLOR_MUTED).grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 5))

        self.role_combos = {}
        for idx, role in enumerate(ROLES):
            tk.Label(form_frame, text=f"{role}:", bg=COLOR_CARD, fg=COLOR_TEXT).grid(row=4 + idx, column=0, sticky="w", pady=2)
            cb = ttk.Combobox(form_frame, values=PROFICIENCIES, state="readonly")
            cb.set("Хорошо")
            cb.grid(row=4 + idx, column=1, sticky="ew", pady=2)
            self.role_combos[role] = cb

        btn_box = tk.Frame(form_frame, bg=COLOR_CARD)
        btn_box.grid(row=5 + len(ROLES), column=0, columnspan=2, pady=15, sticky="w")

        NeonButton(btn_box, text="Сохранить", command=self.save_player, width=120, height=34, neon_color=COLOR_GREEN).pack(side="left", padx=(0, 10))
        NeonButton(btn_box, text="Удалить", command=self.delete_player, width=120, height=34, neon_color=COLOR_RED).pack(side="left", padx=(0, 10))
        NeonButton(btn_box, text="Сброс", command=self.clear_player_form, width=100, height=34, neon_color=COLOR_NEON_CYAN).pack(side="left")

        list_frame = tk.Frame(center_box, bg=COLOR_CARD)
        list_frame.pack(side="right", fill="both", expand=True)

        tk.Label(list_frame, text="СПИСОК ИГРОКОВ", font=("Segoe UI", 10, "bold"), bg=COLOR_CARD, fg=COLOR_MUTED).pack(anchor="w", pady=(0, 10))
        self.players_listbox = self.create_listbox(list_frame)
        self.players_listbox.pack(fill="both", expand=True)
        self.players_listbox.bind("<<ListboxSelect>>", self.on_select_player)

        self.refresh_players_list()

    def clear_player_form(self):
        self.p_name_entry.delete(0, tk.END)
        self.p_rating_entry.delete(0, tk.END)
        self.p_rating_entry.insert(0, "85")
        for cb in self.role_combos.values():
            cb.set("Хорошо")

    def on_select_player(self, event):
        sel = self.players_listbox.curselection()
        if not sel: return
        item = self.players_listbox.get(sel[0])
        p_name = item.split(" [")[0].strip()
        data = db["players"].get(p_name)
        if not data: return

        self.p_name_entry.delete(0, tk.END)
        self.p_name_entry.insert(0, p_name)
        self.p_rating_entry.delete(0, tk.END)
        self.p_rating_entry.insert(0, str(data.get("base_rating", 75)))

        for role, cb in self.role_combos.items():
            cb.set(data.get("roles", {}).get(role, "Хорошо"))

    def save_player(self):
        name = self.p_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите имя игрока!")
            return
        try: rating = int(self.p_rating_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом!")
            return

        db["players"][name] = {
            "base_rating": rating,
            "roles": {role: cb.get() for role, cb in self.role_combos.items()}
        }
        save_db(db)
        self.refresh_all_views()
        messagebox.showinfo("Успех", f"Игрок {name} сохранен!")

    def delete_player(self):
        name = self.p_name_entry.get().strip()
        if name in db["players"]:
            del db["players"][name]
            save_db(db)
            self.clear_player_form()
            self.refresh_all_views()
            messagebox.showinfo("Успех", "Игрок удален!")

    def refresh_players_list(self):
        self.players_listbox.delete(0, tk.END)
        for p, d in db["players"].items():
            self.players_listbox.insert(tk.END, f"{p}  [Рейтинг: {d.get('base_rating', 75)}]")

    # ==================== ТРЕНЕРЫ ====================
    def build_coaches_tab(self):
        card = self.create_card(self.tab_coaches)
        card.pack(fill="both", expand=True, padx=5, pady=5)

        center_box = tk.Frame(card, bg=COLOR_CARD)
        center_box.pack(expand=True, fill="both", padx=40, pady=20)

        form_frame = tk.Frame(center_box, bg=COLOR_CARD)
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

        tk.Label(form_frame, text="ПРОФИЛЬ ТРЕНЕРА", font=("Segoe UI", 12, "bold"), bg=COLOR_CARD, fg=COLOR_GOLD).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        tk.Label(form_frame, text="Никнейм:", bg=COLOR_CARD, fg=COLOR_TEXT).grid(row=1, column=0, sticky="w", pady=5)
        self.c_name_entry = self.create_entry(form_frame)
        self.c_name_entry.grid(row=1, column=1, sticky="ew", pady=5)

        tk.Label(form_frame, text="Рейтинг (0-100):", bg=COLOR_CARD, fg=COLOR_TEXT).grid(row=2, column=0, sticky="w", pady=5)
        self.c_rating_entry = self.create_entry(form_frame)
        self.c_rating_entry.insert(0, "80")
        self.c_rating_entry.grid(row=2, column=1, sticky="ew", pady=5)

        btn_box = tk.Frame(form_frame, bg=COLOR_CARD)
        btn_box.grid(row=3, column=0, columnspan=2, pady=20, sticky="w")

        NeonButton(btn_box, text="Сохранить", command=self.save_coach, width=120, height=34, neon_color=COLOR_GREEN).pack(side="left", padx=(0, 10))
        NeonButton(btn_box, text="Удалить", command=self.delete_coach, width=120, height=34, neon_color=COLOR_RED).pack(side="left", padx=(0, 10))
        NeonButton(btn_box, text="Сброс", command=self.clear_coach_form, width=100, height=34, neon_color=COLOR_NEON_CYAN).pack(side="left")

        list_frame = tk.Frame(center_box, bg=COLOR_CARD)
        list_frame.pack(side="right", fill="both", expand=True)

        tk.Label(list_frame, text="СПИСОК ТРЕНЕРОВ", font=("Segoe UI", 10, "bold"), bg=COLOR_CARD, fg=COLOR_MUTED).pack(anchor="w", pady=(0, 10))
        self.coaches_listbox = self.create_listbox(list_frame)
        self.coaches_listbox.pack(fill="both", expand=True)
        self.coaches_listbox.bind("<<ListboxSelect>>", self.on_select_coach)

        self.refresh_coaches_list()

    def clear_coach_form(self):
        self.c_name_entry.delete(0, tk.END)
        self.c_rating_entry.delete(0, tk.END)
        self.c_rating_entry.insert(0, "80")

    def on_select_coach(self, event):
        sel = self.coaches_listbox.curselection()
        if not sel: return
        item = self.coaches_listbox.get(sel[0])
        c_name = item.split("  [")[0].strip()
        data = db["coaches"].get(c_name)
        if not data: return

        self.c_name_entry.delete(0, tk.END)
        self.c_name_entry.insert(0, c_name)
        self.c_rating_entry.delete(0, tk.END)
        self.c_rating_entry.insert(0, str(data.get("rating", 75)))

    def save_coach(self):
        name = self.c_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите имя тренера!")
            return
        try: rating = int(self.c_rating_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом!")
            return

        db["coaches"][name] = {"rating": rating}
        save_db(db)
        self.refresh_all_views()
        messagebox.showinfo("Успех", f"Тренер {name} сохранен!")

    def delete_coach(self):
        name = self.c_name_entry.get().strip()
        if name in db["coaches"]:
            del db["coaches"][name]
            save_db(db)
            self.clear_coach_form()
            self.refresh_all_views()
            messagebox.showinfo("Успех", "Тренер удален!")

    def refresh_coaches_list(self):
        self.coaches_listbox.delete(0, tk.END)
        for c, d in db["coaches"].items():
            self.coaches_listbox.insert(tk.END, f"{c}  [Рейтинг: {d.get('rating', 0)}]")

    # ==================== КОМАНДЫ (СЛОТЫ СВОБОДНЫХ РОЛЕЙ) ====================
    def build_teams_tab(self):
        card = self.create_card(self.tab_teams)
        card.pack(fill="both", expand=True, padx=5, pady=5)

        center_box = tk.Frame(card, bg=COLOR_CARD)
        center_box.pack(expand=True, fill="both", padx=40, pady=20)

        form_frame = tk.Frame(center_box, bg=COLOR_CARD)
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

        tk.Label(form_frame, text="НАСТРОЙКА КОМАНДЫ", font=("Segoe UI", 12, "bold"), bg=COLOR_CARD, fg=COLOR_GOLD).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        tk.Label(form_frame, text="Название:", bg=COLOR_CARD, fg=COLOR_TEXT).grid(row=1, column=0, sticky="w", pady=3)
        self.t_name_entry = self.create_entry(form_frame)
        self.t_name_entry.grid(row=1, column=1, sticky="ew", pady=3)

        tk.Label(form_frame, text="Сыгранность (%):", bg=COLOR_CARD, fg=COLOR_TEXT).grid(row=2, column=0, sticky="w", pady=3)
        self.t_chem_entry = self.create_entry(form_frame)
        self.t_chem_entry.insert(0, "0")
        self.t_chem_entry.grid(row=2, column=1, sticky="ew", pady=3)

        tk.Label(form_frame, text="Тренер:", bg=COLOR_CARD, fg=COLOR_TEXT).grid(row=3, column=0, sticky="w", pady=3)
        self.t_coach_cb = ttk.Combobox(form_frame, state="readonly")
        self.t_coach_cb.grid(row=3, column=1, sticky="ew", pady=3)

        tk.Label(form_frame, text="Лучшая карта:", bg=COLOR_CARD, fg=COLOR_TEXT).grid(row=4, column=0, sticky="w", pady=3)
        self.t_best_cb = ttk.Combobox(form_frame, values=MAPS, state="readonly")
        self.t_best_cb.set(MAPS[0])
        self.t_best_cb.grid(row=4, column=1, sticky="ew", pady=3)

        tk.Label(form_frame, text="Худшая карта:", bg=COLOR_CARD, fg=COLOR_TEXT).grid(row=5, column=0, sticky="w", pady=3)
        self.t_worst_cb = ttk.Combobox(form_frame, values=MAPS, state="readonly")
        self.t_worst_cb.set(MAPS[1])
        self.t_worst_cb.grid(row=5, column=1, sticky="ew", pady=3)

        tk.Label(form_frame, text="СОСТАВ КОМАНДЫ (5 ИГРОКОВ)", font=("Segoe UI", 10, "bold"), bg=COLOR_CARD, fg=COLOR_MUTED).grid(row=6, column=0, columnspan=2, sticky="w", pady=(8, 4))

        # Создаем 5 слотов с возможностью выбирать Игрока и его Роль отдельно
        self.team_roster_widgets = []
        for idx in range(5):
            slot_num = idx + 1
            tk.Label(form_frame, text=f"Игрок {slot_num}:", bg=COLOR_CARD, fg=COLOR_TEXT).grid(row=7 + idx, column=0, sticky="w", pady=2)
            
            slot_frame = tk.Frame(form_frame, bg=COLOR_CARD)
            slot_frame.grid(row=7 + idx, column=1, sticky="ew", pady=2)
            
            cb_player = ttk.Combobox(slot_frame, state="readonly", width=14)
            cb_player.pack(side="left", padx=(0, 5))
            
            cb_role = ttk.Combobox(slot_frame, values=ROLES, state="readonly", width=12)
            cb_role.pack(side="left")
            cb_role.set("Рифлер")
            
            self.team_roster_widgets.append((cb_player, cb_role))

        btn_box = tk.Frame(form_frame, bg=COLOR_CARD)
        btn_box.grid(row=12, column=0, columnspan=2, pady=12, sticky="w")

        NeonButton(btn_box, text="Сохранить", command=self.save_team, width=110, height=34, neon_color=COLOR_GREEN).pack(side="left", padx=(0, 6))
        NeonButton(btn_box, text="Удалить", command=self.delete_team, width=100, height=34, neon_color=COLOR_RED).pack(side="left", padx=(0, 6))
        NeonButton(btn_box, text="КАРТОЧКА КОМАНДЫ", command=self.open_selected_team_card, width=160, height=34, neon_color=COLOR_GOLD).pack(side="left")

        list_frame = tk.Frame(center_box, bg=COLOR_CARD)
        list_frame.pack(side="right", fill="both", expand=True)

        tk.Label(list_frame, text="СПИСОК КОМАНД (Клик - Выбор, 2-клик - Карточка)", font=("Segoe UI", 9, "bold"), bg=COLOR_CARD, fg=COLOR_MUTED).pack(anchor="w", pady=(0, 10))
        self.teams_listbox = self.create_listbox(list_frame)
        self.teams_listbox.pack(fill="both", expand=True)
        self.teams_listbox.bind("<<ListboxSelect>>", self.on_select_team)
        self.teams_listbox.bind("<Double-Button-1>", lambda e: self.open_selected_team_card())

        self.refresh_teams_list()

    def open_selected_team_card(self):
        t_name = self.t_name_entry.get().strip()
        if not t_name or t_name not in db["teams"]:
            messagebox.showwarning("Внимание", "Выберите или сохраните команду для просмотра карточки!")
            return
        TeamStatsWindow(self, t_name)

    def clear_team_form(self):
        self.t_name_entry.delete(0, tk.END)
        self.t_chem_entry.delete(0, tk.END)
        self.t_chem_entry.insert(0, "0")
        self.t_coach_cb.set("Нет")
        self.t_best_cb.set(MAPS[0])
        self.t_worst_cb.set(MAPS[1])
        for cb_p, cb_r in self.team_roster_widgets:
            cb_p.set("Нет")
            cb_r.set("Рифлер")

    def on_select_team(self, event):
        sel = self.teams_listbox.curselection()
        if not sel: return
        t_name = self.teams_listbox.get(sel[0]).strip()
        data = db["teams"].get(t_name)
        if not data: return

        self.t_name_entry.delete(0, tk.END)
        self.t_name_entry.insert(0, t_name)
        self.t_chem_entry.delete(0, tk.END)
        self.t_chem_entry.insert(0, str(data.get("chemistry", 0)))

        self.t_coach_cb.set(data.get("coach", "Нет"))
        self.t_best_cb.set(data.get("best_map", MAPS[0]))
        self.t_worst_cb.set(data.get("worst_map", MAPS[1]))

        roster = data.get("roster", {})
        if isinstance(roster, dict):
            slots = list(roster.values()) if any(isinstance(v, dict) for v in roster.values()) else []
            if slots:
                for idx, (cb_p, cb_r) in enumerate(self.team_roster_widgets):
                    if idx < len(slots):
                        cb_p.set(slots[idx].get("player", "Нет"))
                        cb_r.set(slots[idx].get("role", "Рифлер"))
                    else:
                        cb_p.set("Нет")
                        cb_r.set("Рифлер")
            else:
                idx = 0
                for r_title, p_name in roster.items():
                    if idx < 5:
                        self.team_roster_widgets[idx][0].set(p_name if p_name else "Нет")
                        self.team_roster_widgets[idx][1].set(r_title if r_title in ROLES else "Рифлер")
                        idx += 1
                while idx < 5:
                    self.team_roster_widgets[idx][0].set("Нет")
                    self.team_roster_widgets[idx][1].set("Рифлер")
                    idx += 1

    def save_team(self):
        name = self.t_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите название команды!")
            return
        try: chem = int(self.t_chem_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Сыгранность должна быть числом!")
            return

        roster_data = {}
        for idx, (cb_p, cb_r) in enumerate(self.team_roster_widgets, 1):
            roster_data[f"Slot_{idx}"] = {
                "player": cb_p.get(),
                "role": cb_r.get()
            }

        db["teams"][name] = {
            "chemistry": chem,
            "coach": self.t_coach_cb.get(),
            "best_map": self.t_best_cb.get(),
            "worst_map": self.t_worst_cb.get(),
            "roster": roster_data
        }
        save_db(db)
        self.refresh_all_views()
        messagebox.showinfo("Успех", f"Команда {name} сохранена!")

    def delete_team(self):
        name = self.t_name_entry.get().strip()
        if name in db["teams"]:
            del db["teams"][name]
            save_db(db)
            self.clear_team_form()
            self.refresh_all_views()
            messagebox.showinfo("Успех", "Команда удалена!")

    def refresh_team_dropdowns(self):
        coaches = ["Нет"] + list(db["coaches"].keys())
        self.t_coach_cb["values"] = coaches

        players = ["Нет"] + list(db["players"].keys())
        for cb_p, cb_r in self.team_roster_widgets:
            cb_p["values"] = players
            cb_r["values"] = ROLES

    def refresh_teams_list(self):
        self.teams_listbox.delete(0, tk.END)
        for t in db["teams"]:
            self.teams_listbox.insert(tk.END, t)

if __name__ == "__main__":
    app = StandoffApp()
    app.mainloop()
