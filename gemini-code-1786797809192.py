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

MAP_DETAILS = {
    "Sandstone": {"type": "Defuse", "desc": "Легендарная песчаная локация с восточным колоритом."},
    "Province": {"type": "Defuse", "desc": "Узкие улочки старинного европейского городка."},
    "Breeze": {"type": "Defuse", "desc": "Тропический порт с контейнерами и морским бризом."},
    "Rust": {"type": "Defuse", "desc": "Заброшенный промышленный завод и строительные леса."},
    "Dune": {"type": "Defuse", "desc": "Военная база в самом сердце раскаленной пустыни."},
    "Hanami": {"type": "Defuse", "desc": "Праздник цветения вишни на улицах японского мегаполиса."},
    "Prison": {"type": "Defuse", "desc": "Тюремный комплекс с множеством коридоров и уровней."}
}

st.set_page_config(page_title="Standoff 2 Esports Hub", layout="wide", page_icon="🎮")

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

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🎮 STANDOFF 2 — ESPORTS HUB")
with col_h2:
    if st.button("🔄 Импортировать команды", type="primary"):
        load_preset_teams()
        st.success("Базовые команды и игроки загружены!")
        st.rerun()

tab_match, tab_players, tab_teams, tab_coaches = st.tabs(["⚔️ Матч-Центр", "👤 Игроки", "🛡️ Команды", "📋 Тренеры"])

# ==================== МАТЧ-ЦЕНТР ====================
with tab_match:
    st.header("Симулятор Киберспортивных Матчей")
    teams_list = list(db["teams"].keys())

    if len(teams_list) < 2:
        st.warning("Нажмите кнопку 'Импортировать команды' вверху справа, чтобы загрузить список команд!")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1: team_a = st.selectbox("Команда A", teams_list, index=0)
        with col2: team_b = st.selectbox("Команда B", teams_list, index=min(1, len(teams_list)-1))
        with col3: match_fmt = st.selectbox("Формат", ["BO1", "BO2", "BO3"], index=2)
        with col4: selected_map = st.selectbox("Локация", ["🎲 Автовыбор"] + MAPS)

        if st.button("🚀 НАЧАТЬ СИМУЛЯЦИЮ", type="primary", use_container_width=True):
            if team_a == team_b:
                st.error("Выберите две разные команды!")
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
                    map_results.append((f"Карта {idx+1}: {m_name}", s_a, s_b))

                    for p, st_data in st_a.items():
                        if p not in total_stats[team_a]: total_stats[team_a][p] = {"K": 0, "A": 0, "D": 0, "damage": 0, "kast": 0, "imp": 0.0}
                        for k in st_data: total_stats[team_a][p][k] += st_data[k]

                    for p, st_data in st_b.items():
                        if p not in total_stats[team_b]: total_stats[team_b][p] = {"K": 0, "A": 0, "D": 0, "damage": 0, "kast": 0, "imp": 0.0}
                        for k in st_data: total_stats[team_b][p][k] += st_data[k]

                st.markdown("---")
                st.subheader(f"🏆 Результат: {team_a} {maps_won_a} : {maps_won_b} {team_b}")
                st.caption(" | ".join([f"{m}: {sa}-{sb}" for m, sa, sb in map_results]))

                col_ta, col_tb = st.columns(2)
                for idx, (t_name, col_t) in enumerate([(team_a, col_ta), (team_b, col_tb)]):
                    with col_t:
                        st.markdown(f"### {t_name}")
                        rows = []
                        for p_name, st_data in total_stats[t_name].items():
                            kd = round(st_data["K"] / max(1, st_data["D"]), 2)
                            adr = int(st_data["damage"] / max(1, total_rounds))
                            rating = round(0.40 + (kd * 0.35) + (adr / 130.0) * 0.35, 2)
                            rows.append({
                                "Игрок": p_name,
                                "K/A/D": f"{st_data['K']}/{st_data['A']}/{st_data['D']}",
                                "K/D": kd,
                                "ADR": adr,
                                "Рейтинг": rating
                            })
                        st.dataframe(rows, use_container_width=True)

# ==================== ИГРОКИ ====================
with tab_players:
    st.header("Управление Игроками")
    p_col1, p_col2 = st.columns([1, 2])

    with p_col1:
        st.subheader("Редактор")
        p_name = st.text_input("Никнейм игрока")
        p_rating = st.number_input("Базовый рейтинг (1-100)", min_value=1, max_value=100, value=85)
        
        st.write("**Эффективность ролей:**")
        p_roles = {}
        for role in ROLES:
            p_roles[role] = st.selectbox(role, PROFICIENCIES, index=2, key=f"role_{role}")

        if st.button("Сохранить Игрока"):
            if p_name:
                db["players"][p_name] = {"base_rating": p_rating, "roles": p_roles}
                save_db(db)
                st.success(f"Игрок {p_name} сохранен!")
                st.rerun()

    with p_col2:
        st.subheader("Список Игроков")
        p_list = [{"Игрок": k, "Рейтинг": v.get("base_rating", 75)} for k, v in db["players"].items()]
        st.dataframe(p_list, use_container_width=True)

# ==================== КОМАНДЫ ====================
with tab_teams:
    st.header("Управление Командами")
    t_col1, t_col2 = st.columns([1, 1])

    with t_col1:
        st.subheader("Параметры команды")
        t_name = st.text_input("Название команды")
        t_chem = st.slider("Сыгранность (%)", 0, 100, 0)
        t_coach = st.selectbox("Тренер", ["Нет"] + list(db["coaches"].keys()))
        t_best = st.selectbox("Лучшая карта", MAPS, index=0)
        t_worst = st.selectbox("Худшая карта", MAPS, index=1)

        st.write("**Состав (5 игроков):**")
        all_p = ["Нет"] + list(db["players"].keys())
        roster_data = {}
        for i in range(1, 6):
            c1, c2 = st.columns(2)
            with c1: p_sel = st.selectbox(f"Слот {i}", all_p, key=f"t_slot_{i}")
            with c2: r_sel = st.selectbox(f"Роль {i}", ROLES, key=f"t_role_{i}")
            roster_data[f"Slot_{i}"] = {"player": p_sel, "role": r_sel}

        if st.button("Сохранить Команду"):
            if t_name:
                db["teams"][t_name] = {
                    "chemistry": t_chem, "coach": t_coach,
                    "best_map": t_best, "worst_map": t_worst,
                    "roster": roster_data
                }
                save_db(db)
                st.success(f"Команда {t_name} сохранена!")
                st.rerun()

    with t_col2:
        st.subheader("Существующие Команды")
        for tm, data in db["teams"].items():
            with st.expander(f"🛡️ {tm}"):
                st.write(f"**Тренер:** {data.get('coach', 'Нет')} | **Сыгранность:** {data.get('chemistry', 0)}%")
                st.write(f"**Карты:** Лучшая ({data.get('best_map')}) / Худшая ({data.get('worst_map')})")
                roster = data.get("roster", {})
                for slot, info in roster.items():
                    if isinstance(info, dict):
                        st.write(f"• {info.get('role', 'Рифлер')}: {info.get('player', 'Нет')}")

# ==================== ТРЕНЕРЫ ====================
with tab_coaches:
    st.header("Управление Тренерами")
    c_col1, c_col2 = st.columns([1, 2])

    with c_col1:
        c_name = st.text_input("Имя тренера")
        c_rating = st.number_input("Рейтинг тренера (0-100)", min_value=0, max_value=100, value=80)
        if st.button("Сохранить Тренера"):
            if c_name:
                db["coaches"][c_name] = {"rating": c_rating}
                save_db(db)
                st.success(f"Тренер {c_name} сохранен!")
                st.rerun()

    with c_col2:
        c_list = [{"Тренер": k, "Рейтинг": v.get("rating", 0)} for k, v in db["coaches"].items()]
        st.dataframe(c_list, use_container_width=True)
