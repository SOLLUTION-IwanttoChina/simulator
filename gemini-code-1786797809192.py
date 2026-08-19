import json
import random
import streamlit as st
from upstash_redis import Redis

# Подключение к Upstash Redis
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
TIERS_OPTIONS = ["Авторасчет", "Tier 1", "Tier 2", "Tier 3"]

MAPS = ["Sandstone", "Province", "Breeze", "Rust", "Dune", "Hanami", "Prison"]

st.set_page_config(
    page_title="Standoff 2 Esports Hub",
    layout="wide",
    page_icon="🎮",
    initial_sidebar_state="collapsed"
)

# Инициализация темы (по умолчанию - тёмная)
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

CAT_IMG_URL = "https://i.ibb.co/Ld35P0v/cat-hat.png"

# ==========================================
# ДИНАМИЧЕСКИЕ СТИЛИ
# ==========================================
if st.session_state.theme == "light":
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: #f5f3ff;
            color: #2e1065;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }}
        
        [data-testid="stSidebar"] {{ display: none; }}
        
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        input, select, textarea {{
            background-color: #ffffff !important;
            color: #1e1b4b !important;
            border: 1px solid #ddd6fe !important;
            border-radius: 8px !important;
        }}

        .stButton > button {{
            background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%) !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            border: 1px solid #c084fc !important;
            box-shadow: 0 4px 14px rgba(124, 58, 237, 0.25) !important;
        }}

        .cat-corner-wrapper {{
            position: fixed;
            top: 15px;
            right: 25px;
            z-index: 999999;
        }}
        
        .cat-corner-wrapper button {{
            width: 65px !important;
            height: 65px !important;
            border-radius: 50% !important;
            background-image: url('{CAT_IMG_URL}') !important;
            background-size: cover !important;
            background-position: center !important;
            border: 3px solid #8b5cf6 !important;
            box-shadow: 0 0 20px rgba(139, 92, 246, 0.5) !important;
            color: transparent !important;
            cursor: pointer !important;
        }}

        /* LvUp style Match Nodes */
        .bracket-node {{
            background: #ffffff;
            border: 2px solid #ddd6fe;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 15px;
            box-shadow: 0 4px 12px rgba(124, 58, 237, 0.08);
        }}
        .bracket-header {{
            font-size: 0.72rem;
            font-weight: 800;
            color: #7c3aed;
            text-transform: uppercase;
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
        }}
        .bracket-team {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 8px;
            border-radius: 6px;
            background: #f5f3ff;
            margin-bottom: 4px;
            font-weight: 700;
            color: #2e1065;
            font-size: 0.85rem;
        }}
        .bracket-team.winner {{
            background: #d8b4fe;
            color: #3b0764;
            border-left: 4px solid #7c3aed;
        }}
        
        .jp-match-card {{
            background-color: #ffffff;
            border: 1px solid #e9d5ff;
            border-top: 4px solid #8b5cf6;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 18px;
            box-shadow: 0 8px 30px rgba(124, 58, 237, 0.08);
        }}
        .jp-status-bar {{
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 0.72rem;
            font-weight: 800;
            color: #6d28d9;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}
        .jp-score-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            text-align: center;
            padding: 12px 16px;
            background: linear-gradient(90deg, #f3e8ff 0%, #faf5ff 50%, #f3e8ff 100%);
            border-radius: 10px;
            border-left: 4px solid #8b5cf6;
            border-right: 4px solid #8b5cf6;
        }}
        .jp-team-title {{ font-size: 1.25rem; font-weight: 800; color: #3b0764; width: 38%; }}
        .jp-score-main {{ font-size: 1.85rem; font-weight: 900; color: #6d28d9; width: 24%; }}
        .jp-winner-tag {{ text-align: center; margin-top: 8px; font-size: 0.88rem; font-weight: 800; color: #7e22ce; text-transform: uppercase; }}
        .jp-mvp-box {{ background: linear-gradient(90deg, #f3e8ff 0%, #ffffff 100%); border: 1px solid #c084fc; border-radius: 8px; padding: 8px 12px; font-size: 0.82rem; color: #581c87; margin-top: 10px; }}
        .jp-section-title {{ font-size: 0.75rem; font-weight: 800; color: #6b21a8; margin: 14px 0 6px 0; text-transform: uppercase; }}
        .jp-maps-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; }}
        .jp-map-item {{ background: #f5f3ff; border: 1px solid #ddd6fe; border-radius: 8px; padding: 7px; text-align: center; }}
        .jp-map-name {{ font-size: 0.7rem; font-weight: 700; color: #581c87; text-transform: uppercase; }}
        .jp-map-score {{ font-size: 0.75rem; font-weight: 600; color: #4c1d95; }}
        .jp-map-score.winner {{ color: #7c3aed; font-weight: 800; }}
        .jp-table-wrapper {{ overflow-x: auto; border-radius: 8px; border: 1px solid #ddd6fe; margin-bottom: 8px; }}
        .jp-table {{ width: 100%; border-collapse: collapse; font-size: 0.73rem; background: #ffffff; }}
        .jp-table th {{ background: #f3e8ff; color: #581c87; font-weight: 800; padding: 7px; text-align: center; border-bottom: 1px solid #ddd6fe; text-transform: uppercase; }}
        .jp-table td {{ padding: 6px; text-align: center; color: #334155; border-bottom: 1px solid #f5f3ff; }}
        .jp-table tr.mvp-row {{ background: #f3e8ff !important; }}
        .jp-table td.player-cell {{ text-align: left; font-weight: 800; color: #3b0764; }}
        .jp-table td.rating-cell {{ font-weight: 900; color: #6d28d9; }}
        
        .team-card-box {{ background: linear-gradient(145deg, #ffffff 0%, #f3e8ff 100%); border: 2px solid #ddd6fe; border-radius: 14px; padding: 18px 20px; margin-bottom: 10px; }}
        .team-card-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e9d5ff; padding-bottom: 12px; margin-bottom: 12px; }}
        .team-card-title {{ font-size: 1.4rem; font-weight: 900; color: #3b0764; display: flex; align-items: center; gap: 10px; }}
        .team-ovr-badge {{ background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%); color: #ffffff; padding: 6px 14px; border-radius: 8px; font-weight: 900; font-size: 1.1rem; text-align: center; }}
        .team-stats-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 14px; background: #f5f3ff; padding: 10px; border-radius: 8px; border: 1px solid #ddd6fe; }}
        .team-stat-item {{ font-size: 0.78rem; color: #6b21a8; }}
        .roster-grid {{ display: flex; flex-direction: column; gap: 6px; }}
        .roster-slot-card {{ display: flex; justify-content: space-between; align-items: center; background: #ffffff; border: 1px solid #e9d5ff; border-left: 3px solid #8b5cf6; padding: 6px 12px; border-radius: 6px; font-size: 0.8rem; color: #2e1065; }}
        .role-badge {{ background: rgba(139, 92, 246, 0.15); color: #6d28d9; border: 1px solid rgba(139, 92, 246, 0.3); padding: 2px 8px; border-radius: 4px; font-size: 0.68rem; font-weight: 800; text-transform: uppercase; }}
    </style>
    """, unsafe_allow_html=True)

else:
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: #0b0c10;
            color: #e2e8f0;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }}
        
        [data-testid="stSidebar"] {{ display: none; }}
        
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        input, select, textarea {{
            background-color: #12141c !important;
            color: #ffffff !important;
            border: 1px solid #2a2e3d !important;
            border-radius: 6px !important;
        }}

        .stButton > button {{
            background: linear-gradient(135deg, #991b1b 0%, #dc2626 100%) !important;
            color: #ffffff !important;
            border-radius: 6px !important;
            font-weight: 700 !important;
            border: 1px solid #f87171 !important;
        }}

        .cat-corner-wrapper {{
            position: fixed;
            top: 15px;
            right: 25px;
            z-index: 999999;
        }}
        
        .cat-corner-wrapper button {{
            width: 65px !important;
            height: 65px !important;
            border-radius: 50% !important;
            background-image: url('{CAT_IMG_URL}') !important;
            background-size: cover !important;
            background-position: center !important;
            border: 3px solid #dc2626 !important;
            box-shadow: 0 4px 18px rgba(220, 38, 38, 0.5) !important;
            color: transparent !important;
            cursor: pointer !important;
        }}

        /* LvUp style Match Nodes */
        .bracket-node {{
            background: #12141e;
            border: 1px solid #232736;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 15px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.5);
        }}
        .bracket-header {{
            font-size: 0.72rem;
            font-weight: 800;
            color: #f87171;
            text-transform: uppercase;
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
        }}
        .bracket-team {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 8px;
            border-radius: 5px;
            background: #181b28;
            margin-bottom: 4px;
            font-weight: 700;
            color: #cbd5e1;
            font-size: 0.85rem;
        }}
        .bracket-team.winner {{
            background: #281013;
            color: #fca5a5;
            border-left: 3px solid #dc2626;
        }}

        .jp-match-card {{ background-color: #0f1118; border: 1px solid #222634; border-radius: 10px; padding: 14px; margin-bottom: 15px; }}
        .jp-status-bar {{ background: rgba(234, 179, 8, 0.08); border: 1px solid rgba(234, 179, 8, 0.25); border-radius: 5px; padding: 4px 8px; font-size: 0.72rem; font-weight: 700; color: #eab308; text-transform: uppercase; margin-bottom: 8px; }}
        .jp-score-header {{ display: flex; justify-content: space-between; align-items: center; text-align: center; padding: 10px 14px; background: #141722; border-radius: 8px; border-left: 3px solid #dc2626; border-right: 3px solid #dc2626; }}
        .jp-team-title {{ font-size: 1.2rem; font-weight: 800; color: #f8fafc; width: 38%; }}
        .jp-score-main {{ font-size: 1.8rem; font-weight: 900; color: #ffffff; width: 24%; }}
        .jp-winner-tag {{ text-align: center; margin-top: 6px; font-size: 0.85rem; font-weight: 800; color: #eab308; text-transform: uppercase; }}
        .jp-mvp-box {{ background: linear-gradient(90deg, rgba(234, 179, 8, 0.12) 0%, rgba(15, 17, 24, 0.8) 100%); border: 1px solid rgba(234, 179, 8, 0.3); border-radius: 6px; padding: 6px 10px; font-size: 0.8rem; color: #fef08a; margin-top: 8px; }}
        .jp-section-title {{ font-size: 0.75rem; font-weight: 800; color: #94a3b8; margin: 12px 0 6px 0; text-transform: uppercase; }}
        .jp-maps-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; }}
        .jp-map-item {{ background: #141722; border: 1px solid #232736; border-radius: 6px; padding: 6px; text-align: center; }}
        .jp-map-name {{ font-size: 0.7rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; }}
        .jp-map-score {{ font-size: 0.75rem; font-weight: 600; color: #cbd5e1; }}
        .jp-map-score.winner {{ color: #eab308; font-weight: 800; }}
        .jp-table-wrapper {{ overflow-x: auto; border-radius: 6px; border: 1px solid #202433; margin-bottom: 8px; }}
        .jp-table {{ width: 100%; border-collapse: collapse; font-size: 0.73rem; background: #12141e; }}
        .jp-table th {{ background: #181b28; color: #64748b; font-weight: 700; padding: 6px; text-align: center; border-bottom: 1px solid #232736; text-transform: uppercase; }}
        .jp-table td {{ padding: 5px 6px; text-align: center; color: #cbd5e1; border-bottom: 1px solid #1a1d2b; }}
        .jp-table tr.mvp-row {{ background: rgba(234, 179, 8, 0.08) !important; }}
        .jp-table td.player-cell {{ text-align: left; font-weight: 700; color: #ffffff; }}
        .jp-table td.rating-cell {{ font-weight: 800; color: #eab308; }}
        
        .team-card-box {{ background: linear-gradient(145deg, #121520 0%, #0a0b10 100%); border: 2px solid #2a2e3d; border-radius: 14px; padding: 18px 20px; margin-bottom: 10px; }}
        .team-card-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #232736; padding-bottom: 12px; margin-bottom: 12px; }}
        .team-card-title {{ font-size: 1.4rem; font-weight: 900; color: #ffffff; display: flex; align-items: center; gap: 10px; }}
        .team-ovr-badge {{ background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); color: #ffffff; padding: 6px 14px; border-radius: 8px; font-weight: 900; font-size: 1.1rem; text-align: center; }}
        .team-stats-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 14px; background: #161925; padding: 10px; border-radius: 8px; }}
        .team-stat-item {{ font-size: 0.78rem; color: #94a3b8; }}
        .roster-grid {{ display: flex; flex-direction: column; gap: 6px; }}
        .roster-slot-card {{ display: flex; justify-content: space-between; align-items: center; background: #141722; border: 1px solid #202433; border-left: 3px solid #dc2626; padding: 6px 12px; border-radius: 6px; font-size: 0.8rem; color: #ffffff; }}
        .role-badge {{ background: rgba(220, 38, 38, 0.15); color: #f87171; border: 1px solid rgba(220, 38, 38, 0.3); padding: 2px 8px; border-radius: 4px; font-size: 0.68rem; font-weight: 800; text-transform: uppercase; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
    .jp-col-player { width: 30%; }
    .jp-col-k      { width: 8%; }
    .jp-col-a      { width: 8%; }
    .jp-col-d      { width: 8%; }
    .jp-col-kd     { width: 9%; }
    .jp-col-adr    { width: 11%; }
    .jp-col-kast   { width: 13%; }
    .jp-col-imp    { width: 13%; }
    .jp-col-rating { width: 10%; }
</style>
""", unsafe_allow_html=True)

# 🐱 КНОПКА-КОТИК В ПРАВОМ ВЕРХНЕМ УГЛУ
st.markdown('<div class="cat-corner-wrapper">', unsafe_allow_html=True)
if st.button("🐱", key="cat_toggle_btn", help="Нажмите на котика, чтобы сменить стиль!"):
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

def save_db(data):
    try:
        redis.set(DB_KEY, json.dumps(data, ensure_ascii=False))
    except Exception as e:
        st.error(f"Сбой сети при сохранении: {e}")

def load_preset_teams(db_data):
    db_data["players"].clear()
    db_data["coaches"].clear()
    db_data["teams"].clear()

    preset_coaches = {
        "Kuba": 99, "inverness": 99, "dstr": 99, "postanova": 98,
        "TOSS": 95, "JOHNY": 94, "Pronyx": 92, "hellmxre": 90
    }

    for c_name, c_rating in preset_coaches.items():
        db_data["coaches"][c_name] = {"rating": c_rating}

    preset_teams = {
        "Virtus Pro": {
            "best": "Prison", "worst": "Hanami", "tier": "Авторасчет",
            "roster": [("Hi-Lo", "Рифлер"), ("Lunax", "Опенер"), ("Reason", "Снайпер"), ("Arventy", "Капитан-Снайпер"), ("chipaa", "Рифлер")],
            "ratings": {"Hi-Lo": 99, "Lunax": 98, "Reason": 97, "Arventy": 95, "chipaa": 90}
        },
        "CyberHero": {
            "best": "Breeze", "worst": "Rust", "tier": "Авторасчет",
            "roster": [("cxtleta", "Рифлер"), ("Enough", "Снайпер"), ("Nekr0", "Капитан"), ("FLACSYS", "Опенер"), ("scndoom", "Саппорт")],
            "ratings": {"cxtleta": 99, "Enough": 96, "Nekr0": 96, "FLACSYS": 93, "scndoom": 91}
        },
        "STRICT": {
            "best": "Sandstone", "worst": "Dune", "tier": "Авторасчет",
            "roster": [("st1ck", "Капитан"), ("Swoop", "Снайпер"), ("k3nny", "Опенер"), ("fLek", "Рифлер"), ("Zero", "Саппорт")],
            "ratings": {"st1ck": 92, "Swoop": 91, "k3nny": 89, "fLek": 88, "Zero": 85}
        },
        "Horizon": {
            "best": "Province", "worst": "Prison", "tier": "Авторасчет",
            "roster": [("Skyline", "Рифлер"), ("Vortex", "Снайпер"), ("Spark", "Опенер"), ("Nova", "Капитан"), ("Blade", "Саппорт")],
            "ratings": {"Skyline": 90, "Vortex": 91, "Spark": 87, "Nova": 88, "Blade": 84}
        }
    }

    for t_name, data in preset_teams.items():
        roster_dict = {}
        for idx, (p_name, p_role) in enumerate(data["roster"], 1):
            role_skills = {role: ("Прекрасно" if role == p_role else random.choice(["Отлично", "Хорошо"])) for role in ROLES}
            db_data["players"][p_name] = {"base_rating": data["ratings"][p_name], "roles": role_skills}
            roster_dict[f"Slot_{idx}"] = {"player": p_name, "role": p_role}

        db_data["teams"][t_name] = {
            "chemistry": 90, "coach": "Kuba", "tier": data["tier"],
            "best_map": data["best"], "worst_map": data["worst"],
            "roster": roster_dict
        }

    save_db(db_data)

def load_db():
    try:
        raw_data = redis.get(DB_KEY)
        if raw_data:
            data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
            if "match_history" not in data:
                data["match_history"] = []
            
            if not data.get("teams") and not data.get("players"):
                load_preset_teams(data)
            return data

        new_db = DEFAULT_DB.copy()
        load_preset_teams(new_db)
        return new_db
    except Exception as e:
        st.error(f"Ошибка загрузки из Upstash: {e}")
        return DEFAULT_DB

if "db" not in st.session_state:
    st.session_state.db = load_db()

db = st.session_state.db

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
                win_roster, lose_roster, win_stats, lose_stats = roster_b, roster_a, stats_a, stats_b

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

            for st_dict in [stats_a, stats_b]:
                for p in st_dict:
                    if random.random() < 0.80: st_dict[p]["kast"] += 1

            if (score_a >= 13 or score_b >= 13) and abs(score_a - score_b) >= 2: break

        return score_a, score_b, stats_a, stats_b, rounds_played


# ==================== ШАПКА ====================
if st.session_state.theme == "light":
    st.title("🪻 STANDOFF 2 — ESPORTS HUB")
    st.caption("Фиолетовая сакура • Glow Violet Edition")
else:
    st.title("⛩️ STANDOFF 2 — ESPORTS HUB")
    st.caption("Обычный темный киберспортивный режим")

st.markdown("---")

tab_match, tab_players, tab_teams, tab_coaches, tab_brackets = st.tabs([
    "⚔️ Матч-Центр", 
    "👤 Игроки", 
    "🛡️ Команды", 
    "📋 Тренеры",
    "🏆 Конструктор (LvUp)"
])

# ==================== МАТЧ-ЦЕНТР ====================
with tab_match:
    st.subheader("⚔️ Симуляция Поединка")
    teams_list = list(db["teams"].keys())

    if len(teams_list) < 2:
        st.info("💡 Создайте минимум 2 команды во вкладке 'Команды', чтобы начать матч!")
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

                table_header_html = '<thead><tr><th class="jp-col-player" style="text-align:left;">ИГРОК / РОЛЬ</th><th class="jp-col-k">K</th><th class="jp-col-a">A</th><th class="jp-col-d">D</th><th class="jp-col-kd">K/D</th><th class="jp-col-adr">ADR</th><th class="jp-col-kast">KAST</th><th class="jp-col-imp">IMP</th><th class="jp-col-rating">РЕЙТИНГ</th></tr></thead>'

                icon_title = "🪻" if st.session_state.theme == "light" else "⛩️"

                full_card_html = f'<div class="jp-match-card"><div class="jp-status-bar">{icon_title} МАТЧ СИМУЛИРОВАН • ФОРМАТ: {match_fmt}</div><div class="jp-score-header"><div class="jp-team-title">{team_a}</div><div class="jp-score-main">{maps_won_a} : {maps_won_b}</div><div class="jp-team-title">{team_b}</div></div><div class="jp-winner-tag">🏆 {winner_team} ПОБЕДА!</div>{mvp_banner_html}<div class="jp-section-title"><span>|</span> КАРТЫ МАТЧА</div><div class="jp-maps-grid">{maps_html}</div><div class="jp-section-title"><span>|</span> {team_a}</div><div class="jp-table-wrapper"><table class="jp-table">{table_header_html}<tbody>{table_rows_a}</tbody></table></div><div class="jp-section-title"><span>|</span> {team_b}</div><div class="jp-table-wrapper"><table class="jp-table">{table_header_html}<tbody>{table_rows_b}</tbody></table></div></div>'

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
    st.subheader("🛡️ Профили и Составы Команд")
    t_col1, t_col2 = st.columns([1, 1])

    with t_col1:
        st.markdown("##### ✏️ Редактор команды")
        team_options = ["➕ Создать новую"] + list(db["teams"].keys())
        selected_team = st.selectbox("Выберите команду:", team_options, key="team_select_box")

        if selected_team != "➕ Создать новую":
            t_data = db["teams"][selected_team]
            default_t_name = selected_team
            default_chem = t_data.get("chemistry", 50)
            default_coach = t_data.get("coach", "Нет")
            default_best = t_data.get("best_map", MAPS[0])
            default_worst = t_data.get("worst_map", MAPS[1])
            default_tier = t_data.get("tier", "Авторасчет")
            default_roster = t_data.get("roster", {})
        else:
            default_t_name, default_chem, default_coach, default_best, default_worst, default_tier, default_roster = "", 50, "Нет", MAPS[0], MAPS[1], "Авторасчет", {}

        t_name = st.text_input("Название команды", value=default_t_name, key=f"t_name_{selected_team}")
        
        c_t1, c_t2 = st.columns(2)
        with c_t1:
            t_chem = st.slider("Сыгранность состава (%)", 0, 100, default_chem, key=f"t_chem_{selected_team}")
        with c_t2:
            tier_index = TIERS_OPTIONS.index(default_tier) if default_tier in TIERS_OPTIONS else 0
            t_tier = st.selectbox("Тир команды", TIERS_OPTIONS, index=tier_index, key=f"t_tier_{selected_team}")
            
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
                db["teams"][t_name] = {
                    "chemistry": t_chem,
                    "coach": t_coach,
                    "best_map": t_best,
                    "worst_map": t_worst,
                    "tier": t_tier,
                    "roster": roster_data
                }
                save_db(db)
                st.success(f"Команда '{t_name}' сохранена!")
                st.rerun()

    with t_col2:
        st.markdown("##### 📸 Паспорта Команд")
        for tm, data in db["teams"].items():
            roster = data.get("roster", {})
            player_ratings = []
            roster_html = ""

            for i in range(1, 6):
                slot_info = roster.get(f"Slot_{i}", {})
                p_name = slot_info.get("player", "Нет") if isinstance(slot_info, dict) else "Нет"
                p_role = slot_info.get("role", "Рифлер") if isinstance(slot_info, dict) else "Рифлер"
                
                p_rating = db["players"].get(p_name, {}).get("base_rating", 0) if p_name != "Нет" else 0
                if p_rating > 0: player_ratings.append(p_rating)

                p_rating_display = f"{p_rating} OVR" if p_rating > 0 else "—"
                roster_html += f'<div class="roster-slot-card"><div><b>{p_name}</b></div><div><span class="role-badge">{p_role}</span> <span style="font-weight:700; margin-left:6px; opacity:0.8;">{p_rating_display}</span></div></div>'

            avg_p_rating = sum(player_ratings) / max(1, len(player_ratings)) if player_ratings else 0
            coach_r = db["coaches"].get(data.get("coach"), {}).get("rating", 0)
            team_ovr = round((avg_p_rating * 0.75) + (data.get("chemistry", 0) * 0.15) + (coach_r * 0.10))

            saved_tier = data.get("tier", "Авторасчет")
            if saved_tier == "Авторасчет":
                tier_tag = "TIER 1" if team_ovr >= 88 else ("TIER 2" if team_ovr >= 75 else "TIER 3")
            else:
                tier_tag = saved_tier.upper()

            team_card_html = f'<div class="team-card-box"><div class="team-card-header"><div class="team-card-title">🛡️ {tm} <span class="role-badge">{tier_tag}</span></div><div class="team-ovr-badge">{team_ovr}</div></div><div class="team-stats-grid"><div class="team-stat-item">👔 Тренер: <b>{data.get("coach", "Нет")}</b></div><div class="team-stat-item">🧩 Сыгранность: <b>{data.get("chemistry", 0)}%</b></div><div class="team-stat-item">🟢 Пик: <b>{data.get("best_map", "Sandstone")}</b></div></div><div class="roster-grid">{roster_html}</div></div>'

            with st.expander(f"🛡️ Паспорт команды: {tm}", expanded=False):
                st.markdown(team_card_html, unsafe_allow_html=True)

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


# =========================================================================
# ==================== 🏆 КОНСТРУКТОР СЕТОК (LVUP.GG STYLE) =============
# =========================================================================
with tab_brackets:
    st.subheader("🏆 Конструктор Турниров и Сеток (LvUp.gg Style)")

    if "tourney" not in st.session_state:
        st.session_state.tourney = None

    # --- ФОРМА СОЗДАНИЯ ТУРНИРА ---
    with st.expander("⚡ Панель организатора: Создание нового турнира", expanded=(st.session_state.tourney is None)):
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            t_title = st.text_input("Название турнира", value="Standoff 2 Major Cup")
            t_format = st.selectbox("Формат сетки", ["Single Elimination (4 команды)", "Single Elimination (8 команд)", "Double Elimination (4 команды)"])
        with t_col2:
            t_map_fmt = st.selectbox("Формат матчей", ["BO1", "BO3"])
            shuffle_teams = st.checkbox("🎲 Случайный сидинг (Жеребьевка)", value=True)
        with t_col3:
            all_teams = list(db["teams"].keys())
            req_count = 8 if "8" in t_format else 4
            selected_participants = st.multiselect(
                f"Участники ({req_count} команд):",
                options=all_teams,
                default=all_teams[:min(req_count, len(all_teams))]
            )

        if st.button("🚀 СФОРМИРОВАТЬ ТУРНИРНУЮ СЕТКУ", type="primary", use_container_width=True):
            if len(selected_participants) < req_count:
                st.error(f"Необходимо выбрать минимум {req_count} команд! У вас создано: {len(all_teams)}.")
            else:
                participants = selected_participants[:req_count]
                if shuffle_teams:
                    random.shuffle(participants)

                matches = {}
                if t_format == "Single Elimination (4 команды)":
                    matches = {
                        "M1": {"round": "1/2 Финала", "team_a": participants[0], "team_b": participants[1], "score_a": 0, "score_b": 0, "winner": None, "next_match": "M3", "slot": "team_a"},
                        "M2": {"round": "1/2 Финала", "team_a": participants[2], "team_b": participants[3], "score_a": 0, "score_b": 0, "winner": None, "next_match": "M3", "slot": "team_b"},
                        "M3": {"round": "🏆 Гранд-Финал", "team_a": "TBD", "team_b": "TBD", "score_a": 0, "score_b": 0, "winner": None, "next_match": None, "slot": None}
                    }
                elif t_format == "Single Elimination (8 команд)":
                    matches = {
                        "M1": {"round": "1/4 Финала", "team_a": participants[0], "team_b": participants[1], "score_a": 0, "score_b": 0, "winner": None, "next_match": "M5", "slot": "team_a"},
                        "M2": {"round": "1/4 Финала", "team_a": participants[2], "team_b": participants[3], "score_a": 0, "score_b": 0, "winner": None, "next_match": "M5", "slot": "team_b"},
                        "M3": {"round": "1/4 Финала", "team_a": participants[4], "team_b": participants[5], "score_a": 0, "score_b": 0, "winner": None, "next_match": "M6", "slot": "team_a"},
                        "M4": {"round": "1/4 Финала", "team_a": participants[6], "team_b": participants[7], "score_a": 0, "score_b": 0, "winner": None, "next_match": "M6", "slot": "team_b"},
                        "M5": {"round": "1/2 Финала", "team_a": "TBD", "team_b": "TBD", "score_a": 0, "score_b": 0, "winner": None, "next_match": "M7", "slot": "team_a"},
                        "M6": {"round": "1/2 Финала", "team_a": "TBD", "team_b": "TBD", "score_a": 0, "score_b": 0, "winner": None, "next_match": "M7", "slot": "team_b"},
                        "M7": {"round": "🏆 Гранд-Финал", "team_a": "TBD", "team_b": "TBD", "score_a": 0, "score_b": 0, "winner": None, "next_match": None, "slot": None}
                    }
                elif t_format == "Double Elimination (4 команды)":
                    matches = {
                        "M1": {"round": "Верхняя Сетка R1", "team_a": participants[0], "team_b": participants[1], "score_a": 0, "score_b": 0, "winner": None, "loser": None, "next_win": "M3", "win_slot": "team_a", "next_lose": "M4", "lose_slot": "team_a"},
                        "M2": {"round": "Верхняя Сетка R1", "team_a": participants[2], "team_b": participants[3], "score_a": 0, "score_b": 0, "winner": None, "loser": None, "next_win": "M3", "win_slot": "team_b", "next_lose": "M4", "lose_slot": "team_b"},
                        "M3": {"round": "Финал Верхней Сетки", "team_a": "TBD", "team_b": "TBD", "score_a": 0, "score_b": 0, "winner": None, "loser": None, "next_win": "M6", "win_slot": "team_a", "next_lose": "M5", "lose_slot": "team_b"},
                        "M4": {"round": "Нижняя Сетка R1", "team_a": "TBD", "team_b": "TBD", "score_a": 0, "score_b": 0, "winner": None, "next_match": "M5", "slot": "team_a"},
                        "M5": {"round": "Финал Нижней Сетки", "team_a": "TBD", "team_b": "TBD", "score_a": 0, "score_b": 0, "winner": None, "next_match": "M6", "slot": "team_b"},
                        "M6": {"round": "🏆 Гранд-Финал", "team_a": "TBD", "team_b": "TBD", "score_a": 0, "score_b": 0, "winner": None, "next_match": None, "slot": None}
                    }

                st.session_state.tourney = {
                    "title": t_title,
                    "format": t_format,
                    "map_fmt": t_map_fmt,
                    "matches": matches
                }
                st.rerun()

    # --- ИНТЕРАКТИВНОЕ ОТОБРАЖЕНИЕ И УПРАВЛЕНИЕ СЕТКОЙ ---
    if st.session_state.tourney:
        tourney = st.session_state.tourney
        st.markdown(f"### 🎮 {tourney['title']} — `{tourney['format']}`")

        # Функция для проброса победителя по сетке
        def advance_winner(m_id, winner_name, score_a, score_b):
            m = tourney["matches"][m_id]
            m["winner"] = winner_name
            m["score_a"] = score_a
            m["score_b"] = score_b

            loser_name = m["team_b"] if winner_name == m["team_a"] else m["team_a"]
            if "loser" in m: m["loser"] = loser_name

            # Проброс победителя
            next_m_id = m.get("next_match") or m.get("next_win")
            slot = m.get("slot") or m.get("win_slot")
            if next_m_id and next_m_id in tourney["matches"]:
                tourney["matches"][next_m_id][slot] = winner_name

            # Проброс проигравшего (Double Elimination)
            lose_m_id = m.get("next_lose")
            lose_slot = m.get("lose_slot")
            if lose_m_id and lose_m_id in tourney["matches"]:
                tourney["matches"][lose_m_id][lose_slot] = loser_name

        # РЕНДЕР КАРТОЧКИ МАТЧА В СТИЛЕ LVUP
        def render_lvup_card(m_id):
            m = tourney["matches"][m_id]
            st.markdown(f'<div class="bracket-node"><div class="bracket-header"><span>{m["round"]}</span><span>ID: {m_id}</span></div>', unsafe_allow_html=True)

            cls_a = "winner" if m["winner"] == m["team_a"] and m["team_a"] != "TBD" else ""
            cls_b = "winner" if m["winner"] == m["team_b"] and m["team_b"] != "TBD" else ""

            st.markdown(
                f'<div class="bracket-team {cls_a}"><span>{m["team_a"]}</span><span>{m["score_a"]}</span></div>'
                f'<div class="bracket-team {cls_b}"><span>{m["team_b"]}</span><span>{m["score_b"]}</span></div></div>',
                unsafe_allow_html=True
            )

            # Элементы управления (Симуляция / Ввод)
            if m["team_a"] != "TBD" and m["team_b"] != "TBD" and not m["winner"]:
                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button("🎲 Играть", key=f"btn_sim_{m_id}", use_container_width=True):
                        needed_wins = 1 if tourney["map_fmt"] == "BO1" else 2
                        sa, sb = 0, 0
                        while sa < needed_wins and sb < needed_wins:
                            res_a, res_b, _, _, _ = MatchEngine.simulate_map(m["team_a"], m["team_b"], random.choice(MAPS))
                            if res_a > res_b: sa += 1
                            else: sb += 1
                        winner = m["team_a"] if sa > sb else m["team_b"]
                        advance_winner(m_id, winner, sa, sb)
                        st.rerun()

                with c2:
                    with st.popover("✏️ Ввод"):
                        sa_in = st.number_input("Счет A", min_value=0, max_value=3, value=0, key=f"sa_{m_id}")
                        sb_in = st.number_input("Счет B", min_value=0, max_value=3, value=0, key=f"sb_{m_id}")
                        if st.button("OK", key=f"save_{m_id}"):
                            if sa_in != sb_in:
                                win_t = m["team_a"] if sa_in > sb_in else m["team_b"]
                                advance_winner(m_id, win_t, sa_in, sb_in)
                                st.rerun()

        # РАСПРЕДЕЛЕНИЕ МАТЧЕЙ ПО КОЛОНКАМ (СТАДИЯМ СЕТКИ)
        if tourney["format"] == "Single Elimination (4 команды)":
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.markdown("#### 1/2 Финала")
                render_lvup_card("M1")
                render_lvup_card("M2")
            with col_r2:
                st.markdown("#### Гранд-Финал")
                render_lvup_card("M3")

        elif tourney["format"] == "Single Elimination (8 команд)":
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.markdown("#### 1/4 Финала")
                render_lvup_card("M1")
                render_lvup_card("M2")
                render_lvup_card("M3")
                render_lvup_card("M4")
            with col_r2:
                st.markdown("#### 1/2 Финала")
                render_lvup_card("M5")
                render_lvup_card("M6")
            with col_r3:
                st.markdown("#### Гранд-Финал")
                render_lvup_card("M7")

        elif tourney["format"] == "Double Elimination (4 команды)":
            col_ub, col_lb, col_gf = st.columns(3)
            with col_ub:
                st.markdown("#### Верхняя Сетка")
                render_lvup_card("M1")
                render_lvup_card("M2")
                render_lvup_card("M3")
            with col_lb:
                st.markdown("#### Нижняя Сетка")
                render_lvup_card("M4")
                render_lvup_card("M5")
            with col_gf:
                st.markdown("#### Гранд-Финал")
                render_lvup_card("M6")

        # ВЫВОД ЧЕМПИОНА
        final_match_key = "M3" if "4 команды" in tourney["format"] and "Double" not in tourney["format"] else ("M7" if "8" in tourney["format"] else "M6")
        champion = tourney["matches"][final_match_key]["winner"]

        if champion:
            st.balloons()
            st.success(f"👑 **ЧЕМПИОН ТУРНИРА:** **{champion}**!")

        st.markdown("---")
        if st.button("🗑️ Сбросить сетку и создать новый турнир"):
            st.session_state.tourney = None
            st.rerun()
