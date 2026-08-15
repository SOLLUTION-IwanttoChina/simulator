import json
import os
import random
import streamlit as st

DB_FILE = "database.json"

DEFAULT_DB = {
    "players": {},
    "coaches": {},
    "teams": {},
    "match_history": []
}

ROLES = ["Капитан", "Снайпер", "Опенер", "Рифлер", "Саппорт", "Капитан-Снайпер", "Люркер"]
PROFICIENCIES = ["Прекрасно", "Отлично", "Хорошо", "Средне", "Плохо"]
ROLE_MULTIPLIERS = {"Прекрасно": 1.20, "Отлично": 1.10, "Хорошо": 1.00, "Средне": 0.85, "Плохо": 0.70}

MAPS = ["Sandstone", "Province", "Breeze", "Rust", "Dune", "Hanami", "Prison"]

st.set_page_config(
    page_title="Standoff 2 Esports Hub",
    layout="wide",
    page_icon="🎮",
    initial_sidebar_state="collapsed"
)

# Custom CSS styling with Mobile Screenshot Match Card & Dark Cyberpunk Theme
st.markdown("""
<style>
    /* Dark Theme Base */
    .stApp {
        background-color: #0b0e14;
        color: #f1f5f9;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Global Input & Select Contrast Fixes */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    input, select, textarea {
        background-color: #161f30 !important;
        color: #ffffff !important;
        border-color: #2b3952 !important;
    }
    
    /* Dropdown text readability */
    div[data-baseweb="popover"] div, div[data-baseweb="menu"] * {
        background-color: #161f30 !important;
        color: #ffffff !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease-in-out !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
    }

    /* ==========================================
       SQUARE MOBILE SCREENSHOT MATCH CARD
       ========================================== */
    .match-card-container {
        max-width: 480px;
        margin: 0 auto 20px auto;
        background: linear-gradient(145deg, #0d1322 0%, #151d30 100%);
        border: 2px solid #3b82f6;
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.7);
        color: #ffffff;
        box-sizing: border-box;
    }
    
    .match-card-header {
        text-align: center;
        font-size: 0.75rem;
        font-weight: 700;
        color: #38bdf8;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    
    .match-teams-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .team-box-side {
        width: 38%;
        text-align: center;
    }
    
    .team-box-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.2;
        word-wrap: break-word;
    }
    
    .score-center-box {
        width: 24%;
        text-align: center;
        font-size: 2.1rem;
        font-weight: 900;
        color: #60a5fa;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 10px;
        padding: 2px 0;
        text-shadow: 0 0 12px rgba(96, 165, 250, 0.6);
    }
    
    .maps-chips-wrapper {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 4px;
        margin: 10px 0;
    }
    
    .map-chip-item {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 6px;
        padding: 3px 8px;
        font-size: 0.72rem;
        color: #cbd5e1;
    }
    
    .stats-split-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .mini-team-heading {
        font-size: 0.8rem;
        font-weight: 700;
        color: #93c5fd;
        text-align: center;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .mini-stats-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.7rem;
    }
    
    .mini-stats-table th {
        color: #64748b;
        font-weight: 600;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 2px;
        text-align: center;
    }
    
    .mini-stats-table td {
        padding: 3px 1px;
        text-align: center;
        color: #e2e8f0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }

    .mini-stats-table td.player-col {
        text-align: left;
        font-weight: 600;
        max-width: 65px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Cards / Expanders Contrast Fix */
    div[data-testid="stExpander"] {
        background: #131822 !important;
        border: 1px solid #222c3d !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }
    
    div[data-testid="stExpander"] summary {
        color: #38bdf8 !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

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
        st.error(f"Ошибка сохранения базы данных: {e}")

if "db" not in st.session_state:
    st.session_state.db = load_db()

db = st.session_state.db

def load_preset_teams():
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
            role_skills = {role: ("Прекрасно" if role == p_role else random.choice(["Отлично", "Хорошо"])) for role in ROLES}
            db["players"][p_name] = {"base_rating": data["ratings"][p_name], "roles": role_skills}
            roster_dict[f"Slot_{idx}"] = {"player": p_name, "role": p_role}

        db["teams"][t_name] = {
            "chemistry": 0, "coach": "Нет",
            "best_map": data["best"], "worst_map": data["worst"],
            "roster": roster_dict
        }

    save_db(db)

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
                elif v and v != "Нет": roster_items.append((k, v))

        players_power = sum(MatchEngine.get_player_power(p_name, role) for role, p_name in roster_items)
        if not roster_items or len(roster_items) < 5: players_power = max(players_power, 350)

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
                    elif v and v != "Нет": res.append(v)
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
                win_roster, lose_roster, win_stats, lose_stats = roster_a, roster_b, stats_a, stats_b
            else:
                score_b += 1
                win_roster, lose_roster, win_stats, lose_stats = roster_b, roster_a, stats_b, stats_a

            if win_roster and lose_roster:
                for _ in range(5):
                    killer, victim = pick_weighted_player(win_roster), random.choice(lose_roster)
                    win_stats[killer]["K"] += 1
                    win_stats[killer]["damage"] += random.randint(80, 140)
                    win_stats[killer]["imp"] += 0.08
                    if random.random() < 0.42: win_stats[killer]["hs"] += 1
                    lose_stats[victim]["D"] += 1
                    if len(win_roster) > 1 and random.random() < 0.55:
                        assist = random.choice([p for p in win_roster if p != killer])
                        win_stats[assist]["A"] += 1

                for _ in range(random.randint(1, 4) if random.random() < 0.85 else 0):
                    killer, victim = pick_weighted_player(lose_roster), random.choice(win_roster)
                    lose_stats[killer]["K"] += 1
                    lose_stats[killer]["damage"] += random.randint(80, 140)
                    lose_stats[killer]["imp"] += 0.08
                    if random.random() < 0.42: lose_stats[killer]["hs"] += 1
                    win_stats[victim]["D"] += 1
                    if len(lose_roster) > 1 and random.random() < 0.55:
                        assist = random.choice([p for p in lose_roster if p != killer])
                        lose_stats[assist]["A"] += 1

            for st in [stats_a, stats_b]:
                for p in st:
                    if random.random() < 0.75: st[p]["kast"] += 1

            if (score_a >= 13 or score_b >= 13) and abs(score_a - score_b) >= 2: break

        return score_a, score_b, stats_a, stats_b, rounds_played

# Header Section
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("🎮 STANDOFF 2 — ESPORTS HUB")
    st.caption("Профессиональный менеджер команд, игроков и симулятор матчей")
with header_col2:
    if st.button("🔄 Импортировать пресеты", type="primary", use_container_width=True):
        load_preset_teams()
        st.success("Базовые команды и игроки загружены!")
        st.rerun()

st.markdown("---")

tab_match, tab_players, tab_teams, tab_coaches = st.tabs([
    "⚔️ Матч-Центр", 
    "👤 Игроки", 
    "🛡️ Команды / Кланы", 
    "📋 Тренеры"
])

# ==================== МАТЧ-ЦЕНТР ====================
with tab_match:
    st.subheader("⚡ Симуляция Киберспортивного Поединка")
    teams_list = list(db["teams"].keys())

    if len(teams_list) < 2:
        st.info("💡 Нажмите кнопку **'Импортировать пресеты'** вверху справа, чтобы загрузить команды по умолчанию!")
    else:
        col1, col2 = st.columns(2)
        with col1: team_a = st.selectbox("Команда A (Хозяева)", teams_list, index=0)
        with col2: team_b = st.selectbox("Команда B (Гости)", teams_list, index=min(1, len(teams_list)-1))

        col3, col4 = st.columns(2)
        with col3: match_fmt = st.selectbox("Формат серии", ["BO1", "BO2", "BO3"], index=2)
        with col4: selected_map = st.selectbox("Карта проведения", ["🎲 Автовыбор"] + MAPS)

        if st.button("🚀 НАЧАТЬ СИМУЛЯЦИЮ МАТЧА", type="primary", use_container_width=True):
            if team_a == team_b:
                st.error("Ошибка: Выберите две разные команды для симуляции!")
            else:
                maps_pool = [selected_map] if selected_map != "🎲 Автовыбор" else random.sample(MAPS, 1 if match_fmt == "BO1" else (2 if match_fmt == "BO2" else 3))
                maps_won_a, maps_won_b = 0, 0
                total_stats = {team_a: {}, team_b: {}}
                map_results = []
                total_rounds = 0

                for idx, m_name in enumerate(maps_pool):
                    if match_fmt == "BO3" and (maps_won_a == 2 or maps_won_b == 2): break
                    s_a, s_b, st_a, st_b, r_played = MatchEngine.simulate_map(team_a, team_b, m_name)
                    total_rounds += r_played
                    if s_a > s_b: maps_won_a += 1
                    else: maps_won_b += 1
                    map_results.append((f"{m_name}", s_a, s_b))

                    for p, st_data in st_a.items():
                        if p not in total_stats[team_a]:
                            total_stats[team_a][p] = {}
                        for k, v in st_data.items():
                            total_stats[team_a][p][k] = total_stats[team_a][p].get(k, 0) + v

                    for p, st_data in st_b.items():
                        if p not in total_stats[team_b]:
                            total_stats[team_b][p] = {}
                        for k, v in st_data.items():
                            total_stats[team_b][p][k] = total_stats[team_b][p].get(k, 0) + v

                # HTML генерация чипов карт
                map_chips_html = "".join([f'<span class="map-chip-item">{m}: <b>{sa}-{sb}</b></span>' for m, sa, sb in map_results])

                # HTML генерация мини-таблиц статистики для идеального мобильного скрина
                def build_mini_rows(t_name):
                    rows_html = ""
                    sorted_players = sorted(
                        total_stats[t_name].items(), 
                        key=lambda x: round(0.40 + ((x[1].get('K', 0)/max(1, x[1].get('D', 0))) * 0.35) + ((int(x[1].get('damage', 0)/max(1, total_rounds))) / 130.0) * 0.35, 2), 
                        reverse=True
                    )
                    for p_name, st_data in sorted_players:
                        k = st_data.get("K", 0)
                        d = st_data.get("D", 0)
                        kd = round(k / max(1, d), 2)
                        adr = int(st_data.get("damage", 0) / max(1, total_rounds))
                        rating = round(0.40 + (kd * 0.35) + (adr / 130.0) * 0.35, 2)
                        rows_html += f"""
                        <tr>
                            <td class="player-col">{p_name}</td>
                            <td>{k}/{d}</td>
                            <td><b>{rating}</b></td>
                        </tr>
                        """
                    return rows_html

                rows_team_a = build_mini_rows(team_a)
                rows_team_b = build_mini_rows(team_b)

                # Идеальная квадратная карточка для скриншота (Square Screenshot Card)
                st.markdown(f"""
                <div class="match-card-container">
                    <div class="match-card-header">⚔️ Standoff 2 Esports Match</div>
                    <div class="match-teams-row">
                        <div class="team-box-side">
                            <div class="team-box-title">{team_a}</div>
                        </div>
                        <div class="score-center-box">{maps_won_a} : {maps_won_b}</div>
                        <div class="team-box-side">
                            <div class="team-box-title">{team_b}</div>
                        </div>
                    </div>
                    <div class="maps-chips-wrapper">
                        {map_chips_html}
                    </div>
                    <div class="stats-split-grid">
                        <div>
                            <div class="mini-team-heading">{team_a}</div>
                            <table class="mini-stats-table">
                                <thead>
                                    <tr>
                                        <th style="text-align:left;">Игрок</th>
                                        <th>K/D</th>
                                        <th>RTG</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {rows_team_a}
                                </tbody>
                            </table>
                        </div>
                        <div>
                            <div class="mini-team-heading">{team_b}</div>
                            <table class="mini-stats-table">
                                <thead>
                                    <tr>
                                        <th style="text-align:left;">Игрок</th>
                                        <th>K/D</th>
                                        <th>RTG</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {rows_team_b}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Полная развернутая таблица ниже для подробного анализа
                with st.expander("🔍 Детальная статистика по всем показателям (ADR, Ассисты, Урон)"):
                    col_ta, col_tb = st.columns(2)
                    for idx, (t_name, col_t) in enumerate([(team_a, col_ta), (team_b, col_tb)]):
                        with col_t:
                            st.markdown(f"#### 📊 {t_name}")
                            rows = []
                            for p_name, st_data in total_stats[t_name].items():
                                kd = round(st_data.get("K", 0) / max(1, st_data.get("D", 0)), 2)
                                adr = int(st_data.get("damage", 0) / max(1, total_rounds))
                                rating = round(0.40 + (kd * 0.35) + (adr / 130.0) * 0.35, 2)
                                rows.append({
                                    "Игрок": p_name,
                                    "K/A/D": f"{st_data.get('K', 0)}/{st_data.get('A', 0)}/{st_data.get('D', 0)}",
                                    "K/D": kd,
                                    "ADR": adr,
                                    "Рейтинг": rating
                                })
                            st.dataframe(rows, use_container_width=True)

# ==================== ИГРОКИ ====================
with tab_players:
    st.subheader("Управление и Редактирование Игроков")
    p_col1, p_col2 = st.columns([1, 1])

    with p_col1:
        st.markdown("##### ✏️ Редактор характеристик игрока")
        
        player_options = ["➕ Создать нового"] + list(db["players"].keys())
        selected_player = st.selectbox("Выберите игрока для изменения:", player_options, key="player_select_box")

        if selected_player != "➕ Создать нового":
            p_data = db["players"][selected_player]
            default_name = selected_player
            default_rating = p_data.get("base_rating", 85)
            default_roles = p_data.get("roles", {})
        else:
            default_name = ""
            default_rating = 85
            default_roles = {}

        p_name = st.text_input("Никнейм игрока", value=default_name, placeholder="Например: Reason", key=f"p_name_{selected_player}")
        p_rating = st.number_input("Базовый skill-рейтинг (1-100)", min_value=1, max_value=100, value=default_rating, key=f"p_rating_{selected_player}")

        st.markdown("**Эффективность и навыки по ролям:**")
        p_roles = {}
        role_cols = st.columns(2)
        for idx, role in enumerate(ROLES):
            cur_proficiency = default_roles.get(role, "Хорошо")
            cur_index = PROFICIENCIES.index(cur_proficiency) if cur_proficiency in PROFICIENCIES else 2
            with role_cols[idx % 2]:
                p_roles[role] = st.selectbox(
                    f"Роль: {role}", 
                    PROFICIENCIES, 
                    index=cur_index, 
                    key=f"p_edit_role_{selected_player}_{role}"
                )

        if st.button("💾 Сохранить изменения игрока", use_container_width=True):
            if p_name:
                db["players"][p_name] = {"base_rating": p_rating, "roles": p_roles}
                save_db(db)
                st.success(f"Характеристики игрока '{p_name}' успешно обновлены!")
                st.rerun()

    with p_col2:
        st.markdown("##### 📜 Зарегистрированные Киберспортсмены")
        p_list = [{"Игрок": k, "Рейтинг": v.get("base_rating", 75)} for k, v in db["players"].items()]
        st.dataframe(p_list, use_container_width=True, height=520)

# ==================== КОМАНДЫ / КЛАНЫ ====================
with tab_teams:
    st.subheader("Управление Командами и Кланами")
    t_col1, t_col2 = st.columns([1, 1])

    with t_col1:
        st.markdown("##### 🛡️ Редактор характеристик клана")

        team_options = ["➕ Создать новую"] + list(db["teams"].keys())
        selected_team = st.selectbox("Выберите клан / команду для редактирования:", team_options, key="team_select_box")

        if selected_team != "➕ Создать новую":
            t_data = db["teams"][selected_team]
            default_t_name = selected_team
            default_chem = t_data.get("chemistry", 50)
            default_coach = t_data.get("coach", "Нет")
            default_best = t_data.get("best_map", MAPS[0])
            default_worst = t_data.get("worst_map", MAPS[1])
            default_roster = t_data.get("roster", {})
        else:
            default_t_name = ""
            default_chem = 50
            default_coach = "Нет"
            default_best = MAPS[0]
            default_worst = MAPS[1]
            default_roster = {}

        t_name = st.text_input("Название команды", value=default_t_name, placeholder="Например: Virtus Pro", key=f"t_name_{selected_team}")
        t_chem = st.slider("Сыгранность состава (%)", 0, 100, default_chem, key=f"t_chem_{selected_team}")
        
        coaches_list = ["Нет"] + list(db["coaches"].keys())
        coach_idx = coaches_list.index(default_coach) if default_coach in coaches_list else 0
        t_coach = st.selectbox("Главный тренер", coaches_list, index=coach_idx, key=f"t_coach_{selected_team}")

        best_idx = MAPS.index(default_best) if default_best in MAPS else 0
        worst_idx = MAPS.index(default_worst) if default_worst in MAPS else 1

        map_c1, map_c2 = st.columns(2)
        with map_c1: t_best = st.selectbox("Лучшая карта", MAPS, index=best_idx, key=f"t_best_{selected_team}")
        with map_c2: t_worst = st.selectbox("Худшая карта", MAPS, index=worst_idx, key=f"t_worst_{selected_team}")

        st.markdown("**Состав (5 Слотов & Роли):**")
        all_p = ["Нет"] + list(db["players"].keys())
        roster_data = {}
        
        for i in range(1, 6):
            slot_key = f"Slot_{i}"
            slot_info = default_roster.get(slot_key, {})
            cur_player = slot_info.get("player", "Нет") if isinstance(slot_info, dict) else "Нет"
            cur_role = slot_info.get("role", "Рифлер") if isinstance(slot_info, dict) else "Рифлер"

            p_idx = all_p.index(cur_player) if cur_player in all_p else 0
            r_idx = ROLES.index(cur_role) if cur_role in ROLES else 0

            c1, c2 = st.columns(2)
            with c1: 
                p_sel = st.selectbox(
                    f"Слот {i} (Игрок)", 
                    all_p, 
                    index=p_idx, 
                    key=f"t_edit_slot_{selected_team}_{i}"
                )
            with c2: 
                r_sel = st.selectbox(
                    f"Роль {i}", 
                    ROLES, 
                    index=r_idx, 
                    key=f"t_edit_role_{selected_team}_{i}"
                )
            roster_data[f"Slot_{i}"] = {"player": p_sel, "role": r_sel}

        if st.button("💾 Сохранить изменения клана", use_container_width=True):
            if t_name:
                db["teams"][t_name] = {
                    "chemistry": t_chem, "coach": t_coach,
                    "best_map": t_best, "worst_map": t_worst,
                    "roster": roster_data
                }
                save_db(db)
                st.success(f"Команда / Клан '{t_name}' сохранен!")
                st.rerun()

    with t_col2:
        st.markdown("##### 📋 Активные Команды и Составы")
        for tm, data in db["teams"].items():
            with st.expander(f"🛡️ {tm}"):
                st.write(f"**Тренер:** {data.get('coach', 'Нет')} | **Сыгранность:** {data.get('chemistry', 0)}%")
                st.write(f"**Карты:** 🟢 {data.get('best_map')} | 🔴 {data.get('worst_map')}")
                st.markdown("---")
                roster = data.get("roster", {})
                for slot, info in roster.items():
                    if isinstance(info, dict):
                        st.write(f"• **{info.get('role', 'Рифлер')}:** {info.get('player', 'Нет')}")

# ==================== ТРЕНЕРЫ ====================
with tab_coaches:
    st.subheader("Штаб Тренеров")
    c_col1, c_col2 = st.columns([1, 1])

    with c_col1:
        st.markdown("##### 👔 Зарегистрировать / Изменить тренера")
        
        coach_options = ["➕ Новый тренер"] + list(db["coaches"].keys())
        selected_c = st.selectbox("Выберите тренера:", coach_options, key="coach_select_box")

        if selected_c != "➕ Новый тренер":
            def_c_name = selected_c
            def_c_rating = db["coaches"][selected_c].get("rating", 80)
        else:
            def_c_name = ""
            def_c_rating = 80

        c_name = st.text_input("Имя / Никнейм тренера", value=def_c_name, placeholder="Например: dstr", key=f"c_name_{selected_c}")
        c_rating = st.number_input("Рейтинг тренерского штаба (0-100)", min_value=0, max_value=100, value=def_c_rating, key=f"c_rating_{selected_c}")
        
        if st.button("💾 Сохранить тренера", use_container_width=True):
            if c_name:
                db["coaches"][c_name] = {"rating": c_rating}
                save_db(db)
                st.success(f"Тренер '{c_name}' сохранен!")
                st.rerun()

    with c_col2:
        st.markdown("##### 📜 Список Тренеров")
        c_list = [{"Тренер": k, "Рейтинг": v.get("rating", 0)} for k, v in db["coaches"].items()]
        st.dataframe(c_list, use_container_width=True, height=400)
