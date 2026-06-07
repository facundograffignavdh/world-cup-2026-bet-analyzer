import pandas as pd # type: ignore
import streamlit as st # type: ignore
import plotly.graph_objects as go # type: ignore

EQUIPOS_MUNDIAL_2026 = {
    # nombre en español: (bandera, nombre exacto en dataset GitHub)
    "Argentina": ("🇦🇷", "Argentina"),
    "Brasil": ("🇧🇷", "Brazil"),
    "Uruguay": ("🇺🇾", "Uruguay"),
    "Colombia": ("🇨🇴", "Colombia"),
    "Ecuador": ("🇪🇨", "Ecuador"),
    "Paraguay": ("🇵🇾", "Paraguay"),

    "Francia": ("🇫🇷", "France"),
    "España": ("🇪🇸", "Spain"),
    "Inglaterra": ("🏴󠁧󠁢󠁥󠁮󠁧󠁿", "England"),
    "Alemania": ("🇩🇪", "Germany"),
    "Portugal": ("🇵🇹", "Portugal"),
    "Países Bajos": ("🇳🇱", "Netherlands"),
    "Bélgica": ("🇧🇪", "Belgium"),
    "Croacia": ("🇭🇷", "Croatia"),
    "Dinamarca": ("🇩🇰", "Denmark"),
    "Austria": ("🇦🇹", "Austria"),
    "Suiza": ("🇨🇭", "Switzerland"),
    "Serbia": ("🇷🇸", "Serbia"),
    "Polonia": ("🇵🇱", "Poland"),
    "Hungría": ("🇭🇺", "Hungary"),
    "Chequia": ("🇨🇿", "Czech Republic"),
    "Escocia": ("🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Scotland"),
    "Turquía": ("🇹🇷", "Turkey"),
    "Noruega": ("🇳🇴", "Norway"),
    "Suecia": ("🇸🇪", "Sweden"),
    "Bosnia y Herzegovina": ("🇧🇦", "Bosnia and Herzegovina"),

    "Estados Unidos": ("🇺🇸", "United States"),
    "México": ("🇲🇽", "Mexico"),
    "Canadá": ("🇨🇦", "Canada"),
    "Panamá": ("🇵🇦", "Panama"),
    "Haití": ("🇭🇹", "Haiti"),
    "Curazao": ("🇨🇼", "Curacao"),

    "Japón": ("🇯🇵", "Japan"),
    "Corea del Sur": ("🇰🇷", "South Korea"),
    "Irán": ("🇮🇷", "Iran"),
    "Australia": ("🇦🇺", "Australia"),
    "Arabia Saudita": ("🇸🇦", "Saudi Arabia"),
    "Irak": ("🇮🇶", "Iraq"),
    "Jordania": ("🇯🇴", "Jordan"),
    "Uzbekistán": ("🇺🇿", "Uzbekistan"),
    "Catar": ("🇶🇦", "Qatar"),

    "Marruecos": ("🇲🇦", "Morocco"),
    "Senegal": ("🇸🇳", "Senegal"),
    "Egipto": ("🇪🇬", "Egypt"),
    "Nigeria": ("🇳🇬", "Nigeria"),
    "Sudáfrica": ("🇿🇦", "South Africa"),
    "Argelia": ("🇩🇿", "Algeria"),
    "Túnez": ("🇹🇳", "Tunisia"),
    "Ghana": ("🇬🇭", "Ghana"),
    "Costa de Marfil": ("🇨🇮", "Ivory Coast"),
    "Rep. Democrática del Congo": ("🇨🇩", "DR Congo"),
    "Cabo Verde": ("🇨🇻", "Cabo Verde"),

    "Nueva Zelanda": ("🇳🇿", "New Zealand"),
}

def main():
    st.title("⚽ World Cup 2026")
    st.markdown("Analizá estadísticas históricas de las 48 selecciones del Mundial 2026 y encontrá los eventos con mayor probabilidad.")
    st.divider()
    qatar2022, goles, partidos, bookings = load_data()
    equipos = sorted(EQUIPOS_MUNDIAL_2026.keys())
    team_a_es = st.selectbox("Equipo 1", equipos)
    team_b_es = st.selectbox("Equipo 2", equipos)

    bandera_a, team_a = EQUIPOS_MUNDIAL_2026[team_a_es]
    bandera_b, team_b = EQUIPOS_MUNDIAL_2026[team_b_es]

    if st.button("Analizar"):
        stats_a = get_team_stats(team_a, partidos, goles, bookings, qatar2022)
        stats_b = get_team_stats(team_b, partidos, goles, bookings, qatar2022)
        markets = calculate_markets(stats_a, stats_b)
        generate_report(team_a, team_b, bandera_a, bandera_b, stats_a, stats_b, markets)

def load_data():
    qatar2022 = pd.read_csv("data/Fifa_world_cup_matches.csv")
    for col in ["possession team1", "possession team2"]:
        qatar2022[col] = qatar2022[col].str.replace("%", "").astype(float)
    goles = pd.read_csv("data/goals.csv")
    partidos = pd.read_csv("data/matches.csv")
    bookings = pd.read_csv("data/bookings.csv")
    return qatar2022, goles, partidos, bookings

def get_team_stats(team, partidos, goles, bookings, qatar2022):
    team_matches = partidos[(partidos["home_team_name"] == team) | (partidos["away_team_name"] == team)]
    match_ids = team_matches["match_id"]
    total_matches = len(team_matches)
    if total_matches >= 20:
        confianza = "alta"
    elif total_matches >= 10:
        confianza = "media"
    else:
        confianza = "baja"
    
    team_goals_data = goles[goles["team_name"] == team]
    team_goals = team_goals_data.shape[0]
    goals_by_minute = team_goals_data.groupby("minute_regulation").size()
    prob_goal_by_minute = goals_by_minute / total_matches if total_matches > 0 else goals_by_minute * 0
    goals_conceded_by_minute = goles[(goles["match_id"].isin(match_ids)) & (goles["team_name"] != team)].groupby("minute_regulation").size()
    prob_goals_conceded_by_minute = goals_conceded_by_minute / total_matches if total_matches > 0 else goals_conceded_by_minute * 0
    goals_first_half = goles[(goles["match_id"].isin(match_ids)) & (goles["team_name"] == team) & (goles["match_period"] == "first half")].shape[0]
    goals_second_half = goles[(goles["match_id"].isin(match_ids)) & (goles["team_name"] == team) & (goles["match_period"] == "second half")].shape[0]
    goals_extra_time = goles[(goles["match_id"].isin(match_ids)) & (goles["team_name"] == team) & (goles["match_period"].str.contains("extra time"))].shape[0]
    goals_penalty = goles[(goles["match_id"].isin(match_ids)) & (goles["team_name"] == team) & (goles["penalty"] == 1)].shape[0]
    goals_0_30 = goles[(goles["match_id"].isin(match_ids)) & (goles["team_name"] == team) & (goles["minute_regulation"] <= 30)].shape[0]
    goals_31_60 = goles[(goles["match_id"].isin(match_ids)) & (goles["team_name"] == team) & (goles["minute_regulation"] > 30) & (goles["minute_regulation"] <= 60)].shape[0]
    goals_61_90 = goles[(goles["match_id"].isin(match_ids)) & (goles["team_name"] == team) & (goles["minute_regulation"] > 60) & (goles["minute_regulation"] <= 90)].shape[0]
    goals_91_120 = goles[(goles["match_id"].isin(match_ids)) & (goles["team_name"] == team) & (goles["minute_regulation"] > 90)].shape[0]
    prob_goals_0_30_per_match = goals_0_30 / total_matches if total_matches > 0 else 0
    prob_goals_31_60_per_match = goals_31_60 / total_matches if total_matches > 0 else 0
    prob_goals_61_90_per_match = goals_61_90 / total_matches if total_matches > 0 else 0
    matches_extra_time = team_matches[team_matches["extra_time"] == 1].shape[0]
    prob_goals_91_120_per_extra_time = min(goals_91_120 / matches_extra_time, 1.0) if matches_extra_time > 0 else 0
    goals_conceded_0_30 = goles[(goles["match_id"].isin(match_ids)) & (goles["team_name"] != team) & (goles["minute_regulation"] <= 30)].shape[0]
    goals_conceded_31_60 = goles[(goles["match_id"].isin(match_ids)) & (goles["team_name"] != team) & (goles["minute_regulation"] > 30) & (goles["minute_regulation"] <= 60)].shape[0]
    goals_conceded_61_90 = goles[(goles["match_id"].isin(match_ids)) & (goles["team_name"] != team) & (goles["minute_regulation"] > 60) & (goles["minute_regulation"] <= 90)].shape[0]
    goals_conceded_91_120 = goles[(goles["match_id"].isin(match_ids)) & (goles["team_name"] != team) & (goles["minute_regulation"] > 90)].shape[0]
    prob_goals_conceded_0_30_per_match = goals_conceded_0_30 / total_matches if total_matches > 0 else 0
    prob_goals_conceded_31_60_per_match = goals_conceded_31_60 / total_matches if total_matches > 0 else 0
    prob_goals_conceded_61_90_per_match = goals_conceded_61_90 / total_matches if total_matches > 0 else 0
    prob_goals_conceded_91_120_per_extra_time = min(goals_conceded_91_120 / matches_extra_time, 1.0) if matches_extra_time > 0 else 0

    goals_conceded = goles[(goles["match_id"].isin(match_ids)) & (goles["team_name"] != team)]
    total_goals_conceded = len(goals_conceded)
    own_goals = goles[(goles["match_id"].isin(match_ids)) & (goles["team_name"] == team) & (goles["own_goal"] == 1)].shape[0]

    avg_own_goals = own_goals / total_matches if total_matches > 0 else 0
    avg_goals_scored = team_goals / total_matches if total_matches > 0 else 0
    avg_goals_conceded = total_goals_conceded / total_matches if total_matches > 0 else 0
    matches_with_goals = goles[(goles["match_id"].isin(match_ids)) & (goles["team_name"] == team)]["match_id"].nunique()
    prob_scoring_per_match = matches_with_goals / total_matches if total_matches > 0 else 0

    matches_with_yellow = bookings[(bookings["match_id"].isin(match_ids)) & (bookings["team_name"] == team) & (bookings["yellow_card"] == 1)]["match_id"].nunique()
    yellow_cards = bookings[(bookings["match_id"].isin(match_ids)) & (bookings["team_name"] == team) & (bookings["yellow_card"] == 1)].shape[0]
    yellow_cards_first_half = bookings[(bookings["match_id"].isin(match_ids)) & (bookings["team_name"] == team) & (bookings["yellow_card"] == 1) & (bookings["match_period"] == "first half")].shape[0]
    yellow_cards_second_half = bookings[(bookings["match_id"].isin(match_ids)) & (bookings["team_name"] == team) & (bookings["yellow_card"] == 1) & (bookings["match_period"] == "second half")].shape[0]
    yellow_cards_extra_time = bookings[(bookings["match_id"].isin(match_ids)) & (bookings["team_name"] == team) & (bookings["yellow_card"] == 1) & (bookings["match_period"].str.contains("extra time"))].shape[0]
    second_yellow_cards = bookings[(bookings["match_id"].isin(match_ids)) & (bookings["team_name"] == team) & (bookings["second_yellow_card"] == 1)].shape[0]
    direct_red_cards = bookings[(bookings["match_id"].isin(match_ids)) & (bookings["team_name"] == team) & (bookings["red_card"] == 1) & (bookings["second_yellow_card"] == 0)].shape[0]
    red_cards = bookings[(bookings["match_id"].isin(match_ids)) & (bookings["team_name"] == team) & (bookings["red_card"] == 1)].shape[0]
    
    avg_yellow_cards = yellow_cards / total_matches if total_matches > 0 else 0
    avg_red_cards = red_cards / total_matches if total_matches > 0 else 0

    prob_second_yellow_card = second_yellow_cards / matches_with_yellow if matches_with_yellow > 0 else 0
    prob_direct_red_card = direct_red_cards / total_matches if total_matches > 0 else 0

    # QATAR 2022
    as_team1 = qatar2022[qatar2022["team1"] == team.upper()]
    as_team2 = qatar2022[qatar2022["team2"] == team.upper()]

    total_qatar_matches = len(as_team1) + len(as_team2)
    corners = as_team1["corners team1"].sum() + as_team2["corners team2"].sum()
    avg_corners = corners / total_qatar_matches if total_qatar_matches > 0 else 0
    possession = as_team1["possession team1"].sum() + as_team2["possession team2"].sum()
    avg_possession = possession / total_qatar_matches if total_qatar_matches > 0 else 0
    goals_in_area = as_team1["goal inside the penalty area team1"].sum() + as_team2["goal inside the penalty area team2"].sum()
    avg_goals_in_area = goals_in_area / total_qatar_matches if total_qatar_matches > 0 else 0
    goals_out_area = as_team1["goal outside the penalty area team1"].sum() + as_team2["goal outside the penalty area team2"].sum()
    avg_goals_out_area = goals_out_area / total_qatar_matches if total_qatar_matches > 0 else 0
    on_target_attempts = as_team1["on target attempts team1"].sum() + as_team2["on target attempts team2"].sum()
    avg_on_target_attempts = on_target_attempts / total_qatar_matches if total_qatar_matches > 0 else 0
    off_target_attempts = as_team1["off target attempts team1"].sum() + as_team2["off target attempts team2"].sum()
    avg_off_target_attempts = off_target_attempts / total_qatar_matches if total_qatar_matches > 0 else 0
    offsides = as_team1["offsides team1"].sum() + as_team2["offsides team2"].sum()
    avg_offsides = offsides / total_qatar_matches if total_qatar_matches > 0 else 0
    fouls_committed = as_team1["fouls against team2"].sum() + as_team2["fouls against team1"].sum()
    avg_fouls_committed = fouls_committed / total_qatar_matches if total_qatar_matches > 0 else 0
    fouls_suffered = as_team1["fouls against team1"].sum() + as_team2["fouls against team2"].sum()
    avg_fouls_suffered = fouls_suffered / total_qatar_matches if total_qatar_matches > 0 else 0
    free_kicks = as_team1["free kicks team1"].sum() + as_team2["free kicks team2"].sum()
    avg_free_kicks = free_kicks / total_qatar_matches if total_qatar_matches > 0 else 0

    return {
        "total_matches": total_matches,
        "confianza": confianza,
        "team_goals": team_goals,
        "goals_by_minute": goals_by_minute,
        "prob_goal_by_minute": prob_goal_by_minute,
        "goals_conceded_by_minute": goals_conceded_by_minute,
        "prob_goals_conceded_by_minute": prob_goals_conceded_by_minute,
        "goals_first_half": goals_first_half,
        "goals_second_half": goals_second_half,
        "goals_extra_time": goals_extra_time,
        "goals_0_30": goals_0_30,
        "goals_31_60": goals_31_60,
        "goals_61_90": goals_61_90,
        "goals_91_120": goals_91_120,
        "prob_goals_0_30_per_match": prob_goals_0_30_per_match,
        "prob_goals_31_60_per_match": prob_goals_31_60_per_match,
        "prob_goals_61_90_per_match": prob_goals_61_90_per_match,
        "prob_goals_91_120_per_extra_time": prob_goals_91_120_per_extra_time,
        "goals_conceded_0_30": goals_conceded_0_30,
        "goals_conceded_31_60": goals_conceded_31_60,
        "goals_conceded_61_90": goals_conceded_61_90,
        "goals_conceded_91_120": goals_conceded_91_120,
        "prob_goals_conceded_0_30_per_match": prob_goals_conceded_0_30_per_match,
        "prob_goals_conceded_31_60_per_match": prob_goals_conceded_31_60_per_match, 
        "prob_goals_conceded_61_90_per_match": prob_goals_conceded_61_90_per_match,
        "prob_goals_conceded_91_120_per_extra_time": prob_goals_conceded_91_120_per_extra_time,
        "total_goals_conceded": total_goals_conceded,
        "own_goals": own_goals,
        "avg_own_goals": avg_own_goals,
        "avg_goals_scored": avg_goals_scored,
        "avg_goals_conceded": avg_goals_conceded,
        "yellow_cards": yellow_cards,
        "yellow_cards_first_half": yellow_cards_first_half,
        "yellow_cards_second_half": yellow_cards_second_half,
        "yellow_cards_extra_time": yellow_cards_extra_time,
        "red_cards": red_cards,
        "total_qatar_matches": total_qatar_matches,
        "avg_yellow_cards": avg_yellow_cards,
        "avg_red_cards": avg_red_cards,
        "prob_second_yellow_card": prob_second_yellow_card,
        "prob_direct_red_card": prob_direct_red_card,
        "avg_corners": avg_corners,
        "avg_possession": avg_possession,
        "avg_goals_in_area": avg_goals_in_area,
        "avg_goals_out_area": avg_goals_out_area,
        "avg_on_target_attempts": avg_on_target_attempts,
        "avg_off_target_attempts": avg_off_target_attempts,
        "avg_offsides": avg_offsides,
        "avg_fouls_committed": avg_fouls_committed,
        "avg_fouls_suffered": avg_fouls_suffered,
        "avg_free_kicks": avg_free_kicks,
        "prob_scoring_per_match": prob_scoring_per_match,
        "matches_with_goals": matches_with_goals
    }

def calculate_markets(stats_a, stats_b):
    prob_goal_by_minute_a = stats_a["prob_goal_by_minute"]
    prob_goal_by_minute_b = stats_b["prob_goal_by_minute"]
    prob_goals_conceded_by_minute_a = stats_a["prob_goals_conceded_by_minute"]
    prob_goals_conceded_by_minute_b = stats_b["prob_goals_conceded_by_minute"]
    expected_goals = stats_a["avg_goals_scored"] + stats_b["avg_goals_scored"]
    over_1_5 = expected_goals > 1.5
    over_2_5 = expected_goals > 2.5
    over_3_5 = expected_goals > 3.5
    expected_corners = stats_a["avg_corners"] + stats_b["avg_corners"]
    over_9_5_corners = expected_corners > 9.5
    over_10_5_corners = expected_corners > 10.5
    over_11_5_corners = expected_corners > 11.5
    expected_yellow_cards = stats_a["avg_yellow_cards"] + stats_b["avg_yellow_cards"]
    over_3_5_yellow_cards = expected_yellow_cards > 3.5
    over_4_5_yellow_cards = expected_yellow_cards > 4.5
    over_5_5_yellow_cards = expected_yellow_cards > 5.5
    expected_red_cards = stats_a["avg_red_cards"] + stats_b["avg_red_cards"]
    over_0_5_red_cards = expected_red_cards > 0.5
    btts = stats_a["prob_scoring_per_match"] > 0.5 and stats_b["prob_scoring_per_match"] > 0.5

    prob_goal_a_0_30 = (stats_a["prob_goals_0_30_per_match"] + stats_b["prob_goals_conceded_0_30_per_match"]) / 2
    prob_goal_a_31_60 = (stats_a["prob_goals_31_60_per_match"] + stats_b["prob_goals_conceded_31_60_per_match"]) / 2
    prob_goal_a_61_90 = (stats_a["prob_goals_61_90_per_match"] + stats_b["prob_goals_conceded_61_90_per_match"]) / 2
    prob_goal_a_91_120 = (stats_a["prob_goals_91_120_per_extra_time"] + stats_b["prob_goals_conceded_91_120_per_extra_time"]) / 2
    prob_goal_b_0_30 = (stats_b["prob_goals_0_30_per_match"] + stats_a["prob_goals_conceded_0_30_per_match"]) / 2
    prob_goal_b_31_60 = (stats_b["prob_goals_31_60_per_match"] + stats_a["prob_goals_conceded_31_60_per_match"]) / 2
    prob_goal_b_61_90 = (stats_b["prob_goals_61_90_per_match"] + stats_a["prob_goals_conceded_61_90_per_match"]) / 2
    prob_goal_b_91_120 = (stats_b["prob_goals_91_120_per_extra_time"] + stats_a["prob_goals_conceded_91_120_per_extra_time"]) / 2

    qatar_available = stats_a["total_qatar_matches"] > 0 and stats_b["total_qatar_matches"] > 0
    expected_corners = (stats_a["avg_corners"] + stats_b["avg_corners"]) if qatar_available else None
    over_9_5_corners = expected_corners is not None and expected_corners > 9.5
    over_10_5_corners = expected_corners is not None and expected_corners > 10.5
    over_11_5_corners = expected_corners is not None and expected_corners > 11.5
    expected_possession = (stats_a["avg_possession"] + stats_b["avg_possession"]) / 2 if qatar_available else None
    expected_goals_in_area = (stats_a["avg_goals_in_area"] + stats_b["avg_goals_in_area"]) / 2 if qatar_available else None
    expected_goals_out_area = (stats_a["avg_goals_out_area"] + stats_b["avg_goals_out_area"]) / 2 if qatar_available else None
    expected_on_target_attempts = (stats_a["avg_on_target_attempts"] + stats_b["avg_on_target_attempts"]) / 2 if qatar_available else None
    expected_off_target_attempts = (stats_a["avg_off_target_attempts"] + stats_b["avg_off_target_attempts"]) / 2 if qatar_available else None
    expected_offsides = (stats_a["avg_offsides"] + stats_b["avg_offsides"]) / 2 if qatar_available else None
    expected_fouls_committed = (stats_a["avg_fouls_committed"] + stats_b["avg_fouls_committed"]) / 2 if qatar_available else None
    expected_fouls_suffered = (stats_a["avg_fouls_suffered"] + stats_b["avg_fouls_suffered"]) / 2 if qatar_available else None
    expected_free_kicks = (stats_a["avg_free_kicks"] + stats_b["avg_free_kicks"]) / 2 if qatar_available else None
    
    return {
        "expected_goals": expected_goals,
        "over_1_5": over_1_5,
        "over_2_5": over_2_5,
        "over_3_5": over_3_5,
        "expected_corners": expected_corners,
        "over_9_5_corners": over_9_5_corners,
        "over_10_5_corners": over_10_5_corners,
        "over_11_5_corners": over_11_5_corners,
        "expected_yellow_cards": expected_yellow_cards,
        "over_3_5_yellow_cards": over_3_5_yellow_cards,
        "over_4_5_yellow_cards": over_4_5_yellow_cards,
        "over_5_5_yellow_cards": over_5_5_yellow_cards,
        "expected_red_cards": expected_red_cards,
        "over_0_5_red_cards": over_0_5_red_cards,
        "btts": btts,
        "prob_goal_by_minute_a": prob_goal_by_minute_a,
        "prob_goal_by_minute_b": prob_goal_by_minute_b,
        "prob_goals_conceded_by_minute_a": prob_goals_conceded_by_minute_a,
        "prob_goals_conceded_by_minute_b": prob_goals_conceded_by_minute_b,
        "prob_goal_a_0_30": prob_goal_a_0_30,
        "prob_goal_a_31_60": prob_goal_a_31_60,
        "prob_goal_a_61_90": prob_goal_a_61_90,
        "prob_goal_a_91_120": prob_goal_a_91_120,
        "prob_goal_b_0_30": prob_goal_b_0_30,
        "prob_goal_b_31_60": prob_goal_b_31_60,
        "prob_goal_b_61_90": prob_goal_b_61_90,
        "prob_goal_b_91_120": prob_goal_b_91_120,
        "expected_possession": expected_possession,
        "expected_goals_in_area": expected_goals_in_area,
        "expected_goals_out_area": expected_goals_out_area,
        "expected_on_target_attempts": expected_on_target_attempts,
        "expected_off_target_attempts": expected_off_target_attempts,
        "expected_offsides": expected_offsides,
        "expected_fouls_committed": expected_fouls_committed,
        "expected_fouls_suffered": expected_fouls_suffered,
        "fouls_committed_a": stats_a["avg_fouls_committed"],
        "fouls_committed_b": stats_b["avg_fouls_committed"],
        "fouls_suffered_a": stats_a["avg_fouls_suffered"],
        "fouls_suffered_b": stats_b["avg_fouls_suffered"],
        "expected_free_kicks": expected_free_kicks
    }

def plot_goal_probability(team_a, team_b, markets):
    
    minutos = list(range(1, 91))
    prob_a = [markets["prob_goal_by_minute_a"].get(m, 0) for m in minutos]
    prob_b = [markets["prob_goal_by_minute_b"].get(m, 0) for m in minutos]
    prob_conceded_a = [markets["prob_goals_conceded_by_minute_a"].get(m, 0) for m in minutos]
    prob_conceded_b = [markets["prob_goals_conceded_by_minute_b"].get(m, 0) for m in minutos]

    prob_a_smooth = pd.Series(prob_a).rolling(window=7, center=True, min_periods=1).mean()
    prob_b_smooth = pd.Series(prob_b).rolling(window=7, center=True, min_periods=1).mean()
    prob_conceded_a_smooth = pd.Series(prob_conceded_a).rolling(window=7, center=True, min_periods=1).mean()
    prob_conceded_b_smooth = pd.Series(prob_conceded_b).rolling(window=7, center=True, min_periods=1).mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=minutos, y=prob_a_smooth, name=f"{team_a} anota", mode="lines", line=dict(color="#1E90FF", width=2.5, shape="spline", smoothing=1.3)))
    fig.add_trace(go.Scatter(x=minutos, y=prob_conceded_a_smooth, name=f"{team_a} concede", mode="lines", line=dict(color="#87CEEB", width=1.5, shape="spline", smoothing=1.3)))
    fig.add_trace(go.Scatter(x=minutos, y=prob_b_smooth, name=f"{team_b} anota", mode="lines", line=dict(color="#FF6B35", width=2.5, shape="spline", smoothing=1.3)))
    fig.add_trace(go.Scatter(x=minutos, y=prob_conceded_b_smooth, name=f"{team_b} concede", mode="lines", line=dict(color="#FFAA80", width=1.5, shape="spline", smoothing=1.3)))

    # Anotaciones en márgenes derechos
    fig.add_annotation(x=91, y=prob_a_smooth.iloc[-1], text=f"{prob_a_smooth.iloc[-1]:.1%}", showarrow=False, xanchor="left", font=dict(color="#1E90FF", size=11))
    fig.add_annotation(x=91, y=prob_conceded_a_smooth.iloc[-1], text=f"{prob_conceded_a_smooth.iloc[-1]:.1%}", showarrow=False, xanchor="left", font=dict(color="#87CEEB", size=11))
    fig.add_annotation(x=91, y=prob_b_smooth.iloc[-1], text=f"{prob_b_smooth.iloc[-1]:.1%}", showarrow=False, xanchor="left", font=dict(color="#FF6B35", size=11))
    fig.add_annotation(x=91, y=prob_conceded_b_smooth.iloc[-1], text=f"{prob_conceded_b_smooth.iloc[-1]:.1%}", showarrow=False, xanchor="left", font=dict(color="#FFAA80", size=11))

    # Probabilidad promedio por zona centrada
    avg_a_0_30 = sum(prob_a_smooth[:30]) / 30
    avg_b_0_30 = sum(prob_b_smooth[:30]) / 30
    avg_a_31_60 = sum(prob_a_smooth[30:60]) / 30
    avg_b_31_60 = sum(prob_b_smooth[30:60]) / 30
    avg_a_61_90 = sum(prob_a_smooth[60:]) / 30
    avg_b_61_90 = sum(prob_b_smooth[60:]) / 30

    ymax = max(prob_a_smooth.max(), prob_b_smooth.max()) * 1.15

    fig.add_annotation(x=15, y=ymax, text=f"{team_a}: {markets['prob_goal_a_0_30']:.0%} · {team_b}: {markets['prob_goal_b_0_30']:.0%}", showarrow=False, font=dict(size=11, color="white"))
    fig.add_annotation(x=45, y=ymax, text=f"{team_a}: {markets['prob_goal_a_31_60']:.0%} · {team_b}: {markets['prob_goal_b_31_60']:.0%}", showarrow=False, font=dict(size=11, color="white"))
    fig.add_annotation(x=75, y=ymax, text=f"{team_a}: {markets['prob_goal_a_61_90']:.0%} · {team_b}: {markets['prob_goal_b_61_90']:.0%}", showarrow=False, font=dict(size=11, color="white"))
    
    fig.add_vrect(x0=0, x1=30, fillcolor="blue", opacity=0.03, line_width=0, annotation_text="0-30'")
    fig.add_vrect(x0=30, x1=60, fillcolor="green", opacity=0.03, line_width=0, annotation_text="31-60'")
    fig.add_vrect(x0=60, x1=90, fillcolor="red", opacity=0.03, line_width=0, annotation_text="61-90'")

    fig.update_layout(
        title="Probabilidad de gol por minuto",
        xaxis_title="Minuto",
        yaxis_title="Probabilidad",
        yaxis_tickformat=".0%",
        margin=dict(r=80, t=80),
        yaxis=dict(range=[0, ymax * 1.2])
    )

    st.plotly_chart(fig, use_container_width=True)

def generate_report(team_a, team_b, bandera_a, bandera_b, stats_a, stats_b, markets):   

    st.title(f"⚽ {team_a} vs {team_b}")
    st.caption("Análisis estadístico basado en historial mundialista (1930–2022) y datos de Qatar 2022.")

    st.divider()

    # --- RESUMEN DEL PARTIDO ---
    st.header("Resumen del partido")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Goles esperados", f"{markets['expected_goals']:.2f}", help="Suma de promedios de goles anotados por ambos equipos")
    with col2:
        if markets['expected_corners'] is not None:
            st.metric("Corners esperados", f"{markets['expected_corners']:.1f}", help="Basado en Qatar 2022")
        else:
            st.metric("Corners esperados", "Sin datos")
    with col3:
        st.metric("Amarillas esperadas", f"{markets['expected_yellow_cards']:.2f}", help="Suma de promedios de ambos equipos")
    with col4:
        st.metric("BTTS", "Sí" if markets['btts'] else "No", help="Ambos equipos anotan")

    st.divider()

    # --- ESTADÍSTICAS DE LOS EQUIPOS ---
    st.header("Estadísticas históricas")
    st.caption("Datos basados en el historial completo de cada selección en Copas del Mundo.")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader(f"{team_a}")
        st.caption(f"Confianza: **{stats_a['confianza']}** · {stats_a['total_matches']} partidos mundialistas")
        st.metric("Goles por partido", f"{stats_a['avg_goals_scored']:.2f}")
        st.metric("Goles concedidos por partido", f"{stats_a['avg_goals_conceded']:.2f}")
        st.metric("Amarillas por partido", f"{stats_a['avg_yellow_cards']:.2f}")
        st.metric("Rojas por partido", f"{stats_a['avg_red_cards']:.2f}")
        st.metric("Prob. 2ª amarilla (si tiene 1ª)", f"{stats_a['prob_second_yellow_card']:.0%}")
        st.metric("Prob. roja directa", f"{stats_a['prob_direct_red_card']:.0%}")

    with col_b:
        st.subheader(f"{team_b}")
        st.caption(f"Confianza: **{stats_b['confianza']}** · {stats_b['total_matches']} partidos mundialistas")
        st.metric("Goles por partido", f"{stats_b['avg_goals_scored']:.2f}")
        st.metric("Goles concedidos por partido", f"{stats_b['avg_goals_conceded']:.2f}")
        st.metric("Amarillas por partido", f"{stats_b['avg_yellow_cards']:.2f}")
        st.metric("Rojas por partido", f"{stats_b['avg_red_cards']:.2f}")
        st.metric("Prob. 2ª amarilla (si tiene 1ª)", f"{stats_b['prob_second_yellow_card']:.0%}")
        st.metric("Prob. roja directa", f"{stats_b['prob_direct_red_card']:.0%}")

    st.divider()

    # --- MERCADOS DE GOLES ---
    st.header("Mercados de goles")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Over 1.5", "✅ Sí" if markets['over_1_5'] else "❌ No")
    with col2:
        st.metric("Over 2.5", "✅ Sí" if markets['over_2_5'] else "❌ No")
    with col3:
        st.metric("Over 3.5", "✅ Sí" if markets['over_3_5'] else "❌ No")

    st.divider()

    # --- PROBABILIDAD DE GOL POR PERÍODO ---
    st.header("Probabilidad de gol por período")
    st.caption("Combina el ataque de cada equipo con la defensa del rival en cada franja de minutos.")
    
    plot_goal_probability(team_a, team_b, markets)

    st.subheader("Probabilidad de anotar al menos un gol en cada período")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader(f"{team_a} anota")
        st.metric("Minuto 0–30", f"{markets['prob_goal_a_0_30']:.0%}")
        st.metric("Minuto 31–60", f"{markets['prob_goal_a_31_60']:.0%}")
        st.metric("Minuto 61–90", f"{markets['prob_goal_a_61_90']:.0%}")
        st.metric("Tiempo extra (91–120)", f"{markets['prob_goal_a_91_120']:.0%}")

    with col_b:
        st.subheader(f"{team_b} anota")
        st.metric("Minuto 0–30", f"{markets['prob_goal_b_0_30']:.0%}")
        st.metric("Minuto 31–60", f"{markets['prob_goal_b_31_60']:.0%}")
        st.metric("Minuto 61–90", f"{markets['prob_goal_b_61_90']:.0%}")
        st.metric("Tiempo extra (91–120)", f"{markets['prob_goal_b_91_120']:.0%}")

    st.divider()

    # --- MERCADOS DE TARJETAS ---
    st.header("Mercados de tarjetas")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Over 3.5 amarillas", "✅ Sí" if markets['over_3_5_yellow_cards'] else "❌ No")
    with col2:
        st.metric("Over 4.5 amarillas", "✅ Sí" if markets['over_4_5_yellow_cards'] else "❌ No")
    with col3:
        st.metric("Over 5.5 amarillas", "✅ Sí" if markets['over_5_5_yellow_cards'] else "❌ No")

    st.metric("Over 0.5 rojas", "✅ Sí" if markets['over_0_5_red_cards'] else "❌ No")

    st.divider()

    # --- DATOS DE QATAR 2022 ---
    if markets['expected_corners'] is not None:
        st.header("Datos de Qatar 2022")
        st.caption("Muestra reducida — solo los partidos de ambos equipos en Qatar 2022. Usar como referencia complementaria.")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Corners esperados", f"{markets['expected_corners']:.1f}")
            st.metric("Over 9.5 corners", "✅ Sí" if markets['over_9_5_corners'] else "❌ No")
            st.metric("Over 10.5 corners", "✅ Sí" if markets['over_10_5_corners'] else "❌ No")
            st.metric("Over 11.5 corners", "✅ Sí" if markets['over_11_5_corners'] else "❌ No")
        with col2:
            st.metric("Remates al arco", f"{markets['expected_on_target_attempts']:.1f}", help="Qatar 2022")
            st.metric("Remates fuera", f"{markets['expected_off_target_attempts']:.1f}", help="Qatar 2022")
            st.metric("Offsides esperados", f"{markets['expected_offsides']:.1f}", help="Qatar 2022")
        with col3:
            st.metric(f"Faltas cometidas {team_a}", f"{markets['fouls_committed_a']:.1f}")
            st.metric(f"Faltas cometidas {team_b}", f"{markets['fouls_committed_b']:.1f}")
            st.metric(f"Faltas sufridas {team_a}", f"{markets['fouls_suffered_a']:.1f}")
            st.metric(f"Faltas sufridas {team_b}", f"{markets['fouls_suffered_b']:.1f}")
            st.metric("Tiros libres", f"{markets['expected_free_kicks']:.1f}", help="Qatar 2022")
    else:
        st.info("Sin datos de Qatar 2022 para uno o ambos equipos. Los mercados de corners y estadísticas avanzadas no están disponibles.")

    st.divider()

if __name__ == "__main__":
    main()
