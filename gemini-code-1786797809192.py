import json
import random
import streamlit as st
from upstash_redis import Redis

# Подключение к Upstash Redis через Streamlit Secrets
redis = Redis(
    url=st.secrets["UPSTASH_REDIS_REST_URL"],
    token=st.secrets["UPSTASH_REDIS_REST_TOKEN"]
)

DB_KEY = "simulator_standoff_db"

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
    page_title="Standoff 2 Esports Hub — 侍",
    layout="wide",
    page_icon="⚔️",
    initial_sidebar_state="collapsed"
)

# ==========================================
# ЯПОНСКИЙ ТЕМНЫЙ СТИЛЬ (JAPANESE CYBER/SAMURAI THEME)
# ==========================================
st.markdown("""
<style>
    .stApp {
        background-color: #0b0c10;
        color: #e2e8f0;
        font-family: 'Inter', system-ui, sans-serif;
    }
    
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    input, select, textarea {
        background-color: #12141c !important;
        color: #ffffff !important;
        border: 1px solid #2a2e3d !important;
        border-radius: 6px !important;
    }
    
    div[data-baseweb="popover"] div, div[data-baseweb="menu"] * {
        background-color: #12141c !important;
        color: #ffffff !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #991b1b 0%, #dc2626 100%) !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        border: 1px solid #f87171 !important;
        transition: all 0.25s ease-in-out !important;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 18px rgba(220, 38, 38, 0.5) !important;
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%) !important;
    }

    .jp-match-card {
        background-color: #10121a;
        border: 1px solid #232736;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
    }

    .jp-status-bar {
        background: rgba(234, 179, 8, 0.08);
        border: 1px solid rgba(234, 179, 8, 0.3);
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 0.78rem;
        font-weight: 700;
        color: #eab308;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 16px;
    }

    .jp-score-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        text-align: center;
        padding: 15px 10px;
        background: #151824;
        border-radius: 10px;
        border-left: 4px solid #dc2626;
        border-right: 4px solid #dc2626;
    }

    .jp-team-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #f8fafc;
        width: 38%;
    }

    .jp-score-main {
        font-size: 2.3rem;
        font-weight: 900;
        color: #ffffff;
        width: 24%;
        letter-spacing: 2px;
    }

    .jp-winner-tag {
        text-align: center;
        margin-top: 10px;
        font-size: 0.95rem;
        font-weight: 800;
        color: #eab308;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }

    .jp-section-title {
        font-size: 0.9rem;
        font-weight: 800;
        color: #cbd5e1;
        margin: 18px 0 10px 0;
        display: flex;
        align-items: center;
        gap: 8px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    .jp-section-title span {
        color: #dc2626;
        font-size: 1.2rem;
    }

    .jp-mvp-box {
        background: linear-gradient(90deg, rgba(234, 179, 8, 0.12) 0%, rgba(16, 18, 26, 0.8) 100%);
        border: 1px solid rgba(234, 179, 8, 0.35);
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 0.88rem;
        color: #fef08a;
        margin-top: 12px;
    }

    .jp-maps-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 12px;
    }

    .jp-map-item {
        background: #161926;
        border: 1px solid #282d40;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
    }

    .jp-map-name {
        font-size: 0.82rem;
        font-weight: 700;
        color: #94a3b8;
        margin-bottom: 4px;
        text-transform: uppercase;
    }

    .jp-map-score {
        font-size: 0.85rem;
        font-weight: 600;
        color: #e2e8f0;
    }

    .jp-map-score.winner {
        color: #eab308;
        font-weight: 800;
    }

    .jp-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.8rem;
        margin-bottom: 20px;
        background: #141722;
        border-radius: 8px;
        overflow: hidden;
    }

    .jp-table th {
        background: #1a1e2c;
        color: #64748b;
        font-weight: 700;
        padding: 10px 8px;
        text-align: center;
        border-bottom: 1px solid #272c3e;
        text-transform: uppercase;
        font-size: 0.72rem;
    }

    .jp-table td {
        padding: 9px 8px;
        text-align: center;
        color: #cbd5e1;
        border-bottom: 1px solid #1f2333;
    }

    .jp-table tr.mvp-row {
        background: rgba(234, 179, 8, 0.08) !important;
    }

    .jp-table td.player-cell {
        text-align: left;
        font-weight: 700;
        color: #ffffff;
    }

    .jp-table td.player-cell small {
        color: #64748b;
        font-weight: 400;
        margin-left: 5px;
    }

    .jp-table td.rating-cell {
        font-weight: 800;
        color: #eab308;
    }

    div[data-testid="stExpander"] {
        background: #12141d !important;
        border: 1px solid #232736 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

def load_db():
    try:
        raw_data = redis.get(DB_KEY)
        if raw_data:
            data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
            if "match_history" not in data:
                data["match_history"] = []
            return data
        return DEFAULT_DB
    except Exception as e:
        st.error(f"Ошибка загрузки из Upstash: {e}")
        return DEFAULT_DB

def save_db(data):
    try:
        redis.set(DB_KEY, json.dumps(data, ensure_ascii=False))
    except Exception as e:
        st.error(f"Сбой сети при сохранении: {e}")

if "db" not in st.session_state:
    st.session_state.db = load_db()

db = st.session_state.db

def load_preset_teams():
    db["players"].clear()
    db["coaches"].clear()
    db["teams"].clear()

    preset_coaches = {
        "Kuba": 99, "inverness": 99, "dstr": 99, "postanova": 98,
        "TOSS": 95, "JOHNY": 94, "Pronyx": 92, "hellmxre": 90
    }

    for c_name, c_rating in preset_coaches.items():
        db["coaches"][c_name] = {"rating": c_rating}

    preset_teams = {
        "Shadow Tigers": {
            "best": "Sandstone", "worst": "Dune",
            "roster": [("Krong", "Люркер"), ("Lunax", "Опенер"), ("PorcelaiN", "Капитан"), ("scndoom", "Снайпер"), ("FilArmonia", "Рифлер")],
            "ratings": {"Krong": 88, "Lunax": 99, "PorcelaiN": 95, "scndoom": 97, "FilArmonia": 92}
        },
        "Lycoris": {
            "best": "Province", "worst": "Rust",
            "roster": [("shadow", "Люркер"), ("vortex", "Опенер"), ("dimasik", "Капитан"), ("sneak", "Снайпер"), ("k1nG", "Рифлер")],
            "ratings": {"shadow": 91, "vortex": 93, "dimasik": 90, "sneak": 98, "k1nG": 94}
        },
        "Virtus Pro": {
            "best": "Prison", "worst": "Hanami",
            "roster": [("Reason", "Снайпер"), ("Hi-Lo", "Рифлер"), ("Arventy", "Капитан"), ("chipaa", "Рифлер"), ("Ping", "Саппорт")],
            "ratings": {"Reason": 97, "Hi-Lo": 99, "Arventy": 95, "chipaa": 96, "Ping": 89}
        },
        "CyberHero": {
            "best": "Sandstone", "worst": "Rust",
            "roster": [("FLACSYS", "Опенер"), ("cxtleta", "Рифлер"), ("Nekr0", "Капитан"), ("Enough", "Снайпер"), ("Horts", "Опенер")],
            "ratings": {"FLACSYS": 93, "cxtleta": 97, "Nekr0": 96, "Enough": 96, "Horts": 90}
        }
    }

    for t_name, data in preset_teams.items():
        roster_dict = {}
        for idx, (p_name, p_role) in enumerate(data["roster"], 1):
            role_skills = {role: ("Прекрасно" if role == p_role else random.choice(["Отлично", "Хорошо"])) for role in ROLES}
            db["players"][p_name] = {"base_rating": data["ratings"][p_name], "roles": role_skills}
            roster_dict[f"Slot_{idx}"] = {"player": p_name, "role": p_role}

        db["teams"][t_name] = {
            "chemistry": 85, "coach": "Kuba",
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
                        p, role = v.get("player"), v.get("role", "Рифлер")
                        if p and p != "Нет": res.append((p, role))
            return res

        roster_a = get_roster_players(team_a)
        roster_b = get_roster_players(team_b)

        stats_a = {p[0]: {"role": p[1], "K": 0, "A": 0, "D": 0, "damage": 0, "kast": 0, "imp": 0} for p in roster_a}
        stats_b = {p[0]: {"role": p[1], "K": 0, "A": 0, "D": 0, "damage": 0, "kast": 0, "imp": 0} for p in roster_b}

        prob_a = power_a / max(1, (power_a + power_b))

        def pick_weighted_player(roster_pairs):
            if not roster_pairs: return None
            weights = [MatchEngine.get_player_power(p, r) for p, r in roster_pairs]
            return random.choices([p for p, r in roster_pairs], weights=weights, k=1)[0]

        while True:
            rounds_played += 1
            win_prob = prob_a * 0.94 + random.uniform(-0.06, 0.06)
            winner = team_a if random.random() < win_prob else team_b

            if winner == team_a:
                score_a += 1
                win_roster, lose_roster, win_stats, lose_stats = roster_a, roster_b, stats_a, stats_b
            else:
                score_b += 1
                win_roster, lose_roster, win_stats, lose_stats = roster_b, roster_a, stats_b, stats_a

            if win_roster and lose_roster:
                for _ in range(5):
                    killer = pick_weighted_player(win_roster)
                    victim = random.choice([p for p, r in lose_roster])
                    win_stats[killer]["K"] += 1
                    win_stats[killer]["damage"] += random.randint(80, 150)
                    win_stats[killer]["imp"] += random.randint(1, 2)
                    lose_stats[victim]["D"] += 1
                    if len(win_roster) > 1 and random.random() < 0.55:
                        assist = random.choice([p for p, r in win_roster if p != killer])
                        win_stats[assist]["A"] += 1

                for _ in range(random.randint(1, 4)):
                    killer = pick_weighted_player(lose_roster)
                    victim = random.choice([p for p, r in win_roster])
                    lose_stats[killer]["K"] += 1
                    lose_stats[killer]["damage"] += random.randint(80, 140)
                    lose_stats[killer]["imp"] += random.randint(1, 2)
                    win_stats[victim]["D"] += 1
                    if len(lose_roster) > 1 and random.random() < 0.55:
                        assist = random.choice([p for p, r in lose_roster if p != killer])
                        lose_stats[assist]["A"] += 1

            for st in [stats_a, stats_b]:
                for p in st:
                    if random.random() < 0.80: st[p]["kast"] += 1

            if (score_a >= 13 or score_b >= 13) and abs(score_a - score_b) >= 2: break

        return score_a, score_b, stats_a, stats_b, rounds_played

# Header
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("⛩️ STANDOFF 2 — ESPORTS HUB")
    st.caption("武士道 • Профессиональный менеджер команд и симулятор киберспорта")
with header_col2:
    if st.button("🔄 Загрузить пресеты", type="primary", use_container_width=True):
        load_preset_teams()
        st.success("Базовые данные успешно загружены!")
        st.rerun()

st.markdown("---")

tab_match, tab_players, tab_teams, tab_coaches = st.tabs([
    "⚔️ Матч-Центр", 
    "👤 Игроки", 
    "🛡️ Команды", 
    "📋 Тренеры"
])

# ==================== МАТЧ-ЦЕНТР ====================
with tab_match:
    st.subheader("⚔️ Симуляция Поединка")
    teams_list = list(db["teams"].keys())

    if len(teams_list) < 2:
        st.info("💡 Нажмите кнопку **'Загрузить пресеты'** вверху справа для быстрой загрузки команд!")
    else:
        col1, col2 = st.columns(2)
        with col1: team_a = st.selectbox("Команда A", teams_list, index=0)
        with col2: team_b = st.selectbox("Команда B", teams_list, index=min(1, len(teams_list)-1))

        col3, col4 = st.columns(2)
        with col3: match_fmt = st.selectbox("Формат серии", ["BO1", "BO2", "BO3"], index=2)
        with col4: selected_map = st.selectbox("Карта проведения", ["🎲 Автовыбор"] + MAPS)

        if st.button("🔥 НАЧАТЬ СРАЖЕНИЕ", type="primary", use_container_width=True):
            if team_a == team_b:
                st.error("Ошибка: Выберите две разные команды!")
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
                    map_results.append((m_name, s_a, s_b))

                    for p, st_data in st_a.items():
                        if p not in total_stats[team_a]:
                            total_stats[team_a][p] = {"role": st_data["role"], "K": 0, "A": 0, "D": 0, "damage": 0, "kast": 0, "imp": 0}
                        for k in ["K", "A", "D", "damage", "kast", "imp"]:
                            total_stats[team_a][p][k] += st_data[k]

                    for p, st_data in st_b.items():
                        if p not in total_stats[team_b]:
                            total_stats[team_b][p] = {"role": st_data["role"], "K": 0, "A": 0, "D": 0, "damage": 0, "kast": 0, "imp": 0}
                        for k in ["K", "A", "D", "damage", "kast", "imp"]:
                            total_stats[team_b][p][k] += st_data[k]

                winner_team = team_a if maps_won_a > maps_won_b else (team_b if maps_won_b > maps_won_a else "Ничья")

                all_processed_players = []
                for t_name in [team_a, team_b]:
                    for p_name, st_data in total_stats[t_name].items():
                        k, a, d = st_data["K"], st_data["A"], st_data["D"]
                        kd = round(k / max(1, d), 2)
                        adr = round(st_data["damage"] / max(1, total_rounds), 1)
                        kast_pct = min(98.0, round((st_data["kast"] / max(1, total_rounds)) * 100, 1))
                        imp_pct = min(99.0, round((st_data["imp"] / max(1, total_rounds)) * 50, 1))
                        rating = round(0.35 + (kd * 0.35) + (adr / 110.0) * 0.30 + (kast_pct / 200.0) * 0.10, 2)

                        item = {
                            "team": t_name, "player": p_name, "role": st_data["role"],
                            "K": k, "A": a, "D": d, "KD": kd, "ADR": adr,
                            "KAST": f"{kast_pct}%", "IMP": f"{imp_pct}%", "Rating": rating
                        }
                        all_processed_players.append(item)

                mvp_player = max(all_processed_players, key=lambda x: x["Rating"]) if all_processed_players else None

                maps_html = ""
                for m_name, sa, sb in map_results:
                    win_a_cls = "winner" if sa > sb else ""
                    win_b_cls = "winner" if sb > sa else ""
                    maps_html += f'<div class="jp-map-item"><div class="jp-map-name">{m_name}</div><div class="jp-map-score {win_a_cls}">{team_a} {sa}</div><div class="jp-map-score {win_b_cls}">{team_b} {sb}</div></div>'

                def render_team_table(t_name):
                    rows_html = ""
                    t_players = [p for p in all_processed_players if p["team"] == t_name]
                    t_players.sort(key=lambda x: x["Rating"], reverse=True)
                    
                    for p in t_players:
                        is_mvp = (mvp_player and p["player"] == mvp_player["player"])
                        mvp_cls = "mvp-row" if is_mvp else ""
                        mvp_star = "⭐ " if is_mvp else ""
                        
                        rows_html += f'<tr class="{mvp_cls}"><td class="player-cell">{mvp_star}{p["player"]}<small>{p["role"]}</small></td><td>{p["K"]}</td><td>{p["A"]}</td><td>{p["D"]}</td><td>{p["KD"]}</td><td>{p["ADR"]}</td><td>{p["KAST"]}</td><td>{p["IMP"]}</td><td class="rating-cell">{p["Rating"]:.2f}</td></tr>'
                    return rows_html

                table_rows_a = render_team_table(team_a)
                table_rows_b = render_team_table(team_b)

                mvp_banner_html = f'<div class="jp-mvp-box">⭐ <b>MVP матча</b> — <b>{mvp_player["player"]}</b> ({mvp_player["team"]}) &nbsp;|&nbsp; Рейтинг: <b>{mvp_player["Rating"]:.2f}</b></div>' if mvp_player else ''

                full_card_html = f'<div class="jp-match-card"><div class="jp-status-bar">⛩️ МАТЧ СИМУЛИРОВАН • ФОРМАТ: {match_fmt}</div><div class="jp-score-header"><div class="jp-team-title">{team_a}</div><div class="jp-score-main">{maps_won_a} : {maps_won_b}</div><div class="jp-team-title">{team_b}</div></div><div class="jp-winner-tag">🏆 {winner_team} ПОБЕДА!</div>{mvp_banner_html}<div class="jp-section-title"><span>|</span> КАРТЫ МАТЧА</div><div class="jp-maps-grid">{maps_html}</div><div class="jp-section-title"><span>|</span> {team_a}</div><table class="jp-table"><thead><tr><th style="text-align:left;">ИГРОК / РОЛЬ</th><th>K</th><th>A</th><th>D</th><th>K/D</th><th>ADR</th><th>KAST</th><th>IMP</th><th>РЕЙТИНГ</th></tr></thead><tbody>{table_rows_a}</tbody></table><div class="jp-section-title"><span>|</span> {team_b}</div><table class="jp-table"><thead><tr><th style="text-align:left;">ИГРОК / РОЛЬ</th><th>K</th><th>A</th><th>D</th><th>K/D</th><th>ADR</th><th>KAST</th><th>IMP</th><th>РЕЙТИНГ</th></tr></thead><tbody>{table_rows_b}</tbody></table></div>'

                st.markdown(full_card_html, unsafe_allow_html=True)

# ==================== ИГРОКИ ====================
with tab_players:
    st.subheader("Управление Игроками")
    p_col1, p_col2 = st.columns([1, 1])

    with p_col1:
        st.markdown("##### ✏️ Редактор характеристик")
        player_options = ["➕ Создать нового"] + list(db["players"].keys())
        selected_player = st.selectbox("Выберите игрока:", player_options, key="player_select_box")

        if selected_player != "➕ Создать нового":
            p_data = db["players"][selected_player]
            default_name = selected_player
            default_rating = p_data.get("base_rating", 85)
            default_roles = p_data.get("roles", {})
        else:
            default_name, default_rating, default_roles = "", 85, {}

        p_name = st.text_input("Никнейм игрока", value=default_name, key=f"p_name_{selected_player}")
        p_rating = st.number_input("Базовый skill-рейтинг (1-100)", min_value=1, max_value=100, value=default_rating, key=f"p_rating_{selected_player}")

        p_roles = {}
        role_cols = st.columns(2)
        for idx, role in enumerate(ROLES):
            cur_proficiency = default_roles.get(role, "Хорошо")
            cur_index = PROFICIENCIES.index(cur_proficiency) if cur_proficiency in PROFICIENCIES else 2
            with role_cols[idx % 2]:
                p_roles[role] = st.selectbox(f"{role}:", PROFICIENCIES, index=cur_index, key=f"p_edit_role_{selected_player}_{role}")

        if st.button("💾 Сохранить игрока", use_container_width=True):
            if p_name:
                db["players"][p_name] = {"base_rating": p_rating, "roles": p_roles}
                save_db(db)
                st.success(f"Игрок '{p_name}' обновлен!")
                st.rerun()

    with p_col2:
        st.markdown("##### 📜 Зарегистрированные Игроки")
        p_list = [{"Игрок": k, "Рейтинг": v.get("base_rating", 75)} for k, v in db["players"].items()]
        st.dataframe(p_list, use_container_width=True, height=500)

# ==================== КОМАНДЫ ====================
with tab_teams:
    st.subheader("Управление Командами")
    t_col1, t_col2 = st.columns([1, 1])

    with t_col1:
        st.markdown("##### 🛡️ Редактор команды")
        team_options = ["➕ Создать новую"] + list(db["teams"].keys())
        selected_team = st.selectbox("Выберите команду:", team_options, key="team_select_box")

        if selected_team != "➕ Создать новую":
            t_data = db["teams"][selected_team]
            default_t_name = selected_team
            default_chem = t_data.get("chemistry", 50)
            default_coach = t_data.get("coach", "Нет")
            default_best = t_data.get("best_map", MAPS[0])
            default_worst = t_data.get("worst_map", MAPS[1])
            default_roster = t_data.get("roster", {})
        else:
            default_t_name, default_chem, default_coach, default_best, default_worst, default_roster = "", 50, "Нет", MAPS[0], MAPS[1], {}

        t_name = st.text_input("Название команды", value=default_t_name, key=f"t_name_{selected_team}")
        t_chem = st.slider("Сыгранность состава (%)", 0, 100, default_chem, key=f"t_chem_{selected_team}")
        
        coaches_list = ["Нет"] + list(db["coaches"].keys())
        coach_idx = coaches_list.index(default_coach) if default_coach in coaches_list else 0
        t_coach = st.selectbox("Главный тренер", coaches_list, index=coach_idx, key=f"t_coach_{selected_team}")

        map_c1, map_c2 = st.columns(2)
        with map_c1: t_best = st.selectbox("Лучшая карта", MAPS, index=MAPS.index(default_best) if default_best in MAPS else 0, key=f"t_best_{selected_team}")
        with map_c2: t_worst = st.selectbox("Худшая карта", MAPS, index=MAPS.index(default_worst) if default_worst in MAPS else 1, key=f"t_worst_{selected_team}")

        all_p = ["Нет"] + list(db["players"].keys())
        roster_data = {}
        
        for i in range(1, 6):
            slot_key = f"Slot_{i}"
            slot_info = default_roster.get(slot_key, {})
            cur_player = slot_info.get("player", "Нет") if isinstance(slot_info, dict) else "Нет"
            cur_role = slot_info.get("role", "Рифлер") if isinstance(slot_info, dict) else "Рифлер"

            c1, c2 = st.columns(2)
            with c1: p_sel = st.selectbox(f"Слот {i}", all_p, index=all_p.index(cur_player) if cur_player in all_p else 0, key=f"t_edit_slot_{selected_team}_{i}")
            with c2: r_sel = st.selectbox(f"Роль {i}", ROLES, index=ROLES.index(cur_role) if cur_role in ROLES else 0, key=f"t_edit_role_{selected_team}_{i}")
            roster_data[f"Slot_{i}"] = {"player": p_sel, "role": r_sel}

        if st.button("💾 Сохранить команду", use_container_width=True):
            if t_name:
                db["teams"][t_name] = {"chemistry": t_chem, "coach": t_coach, "best_map": t_best, "worst_map": t_worst, "roster": roster_data}
                save_db(db)
                st.success(f"Команда '{t_name}' сохранена!")
                st.rerun()

    with t_col2:
        st.markdown("##### 📋 Составы Команд")
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
        st.markdown("##### 👔 Редактор тренера")
        coach_options = ["➕ Новый тренер"] + list(db["coaches"].keys())
        selected_c = st.selectbox("Выберите тренера:", coach_options, key="coach_select_box")

        if selected_c != "➕ Новый тренер":
            def_c_name, def_c_rating = selected_c, db["coaches"][selected_c].get("rating", 80)
        else:
            def_c_name, def_c_rating = "", 80

        c_name = st.text_input("Имя / Никнейм тренера", value=def_c_name, key=f"c_name_{selected_c}")
        c_rating = st.number_input("Рейтинг (0-100)", min_value=0, max_value=100, value=def_c_rating, key=f"c_rating_{selected_c}")
        
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
