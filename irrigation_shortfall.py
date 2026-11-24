"""Pakistan irrigation water-shortfall decision-support dashboard.

User-supplied national/provincial claims are explicitly labelled as claims to verify;
this module does not present them as measured national statistics.
"""
from __future__ import annotations

import io
import pandas as pd
import plotly.express as px
import streamlit as st

PAGE_TITLE = "Pakistan Irrigation Water Shortfall: Causes, Provincial Challenges & Solutions"

CAUSES = pd.DataFrame([
    {"Driver": "Conveyance and field losses", "Description": "Aging canals, unlined watercourses, seepage, siltation, uneven fields and inefficient application.", "Evidence status": "User-supplied estimate; quantify locally", "Indicators": "Head-to-tail discharge, watercourse condition, field application efficiency"},
    {"Driver": "Limited storage and siltation", "Description": "Limited carryover storage, sediment accumulation and delayed storage development.", "Evidence status": "User-supplied claims; verify current capacity and sediment surveys", "Indicators": "Live storage, gross storage, sediment survey year, dependable inflow"},
    {"Driver": "Climate variability", "Description": "Changing monsoon timing, drought, glacial-melt variability and flood pulses.", "Evidence status": "Qualitative driver; quantify by basin and period", "Indicators": "Rainfall anomaly, snow/glacier contribution, seasonal river-flow series"},
    {"Driver": "Groundwater over-extraction", "Description": "Tubewell pumping offsets canal shortages but can lower water tables and worsen quality.", "Evidence status": "Regional condition; requires aquifer-specific evidence", "Indicators": "Groundwater level trend, abstraction, recharge, ECw, RSC"},
    {"Driver": "Water-intensive crop patterns", "Description": "Crop mix and planting locations can create high seasonal demand in water-stressed areas.", "Evidence status": "Requires crop-area and crop-water data", "Indicators": "Crop area, ETc, effective rainfall, NIR, GIR"},
    {"Driver": "Rising demand and governance", "Description": "Population, cities, industry, irrigation operations, pricing and allocation institutions compete for water.", "Evidence status": "Policy assessment; use dated official data", "Indicators": "Sector withdrawals, delivery schedules, abiana recovery, telemetry coverage"},
])

PROVINCES = pd.DataFrame([
    {"Province / region": "Punjab", "Key challenge": "Tubewell dependence, tail-end canal shortages, crop demand concentration", "Priority responses": "Watercourse rehabilitation, laser leveling, crop zoning, groundwater monitoring", "District / setting examples": "Southern Punjab tail reaches; canal commands; arid and barani zones"},
    {"Province / region": "Sindh", "Key challenge": "Tail-end delivery vulnerability, brackish groundwater, coastal salinity and intrusion", "Priority responses": "Transparent flow measurement, drainage where feasible, water-quality monitoring, efficient field application", "District / setting examples": "Lower Indus, rice belt, delta and coastal commands"},
    {"Province / region": "Khyber Pakhtunkhwa", "Key challenge": "Steep terrain, rain-fed agriculture and seasonal hill-torrent variability", "Priority responses": "Small storage, spate-irrigation improvement, watershed measures, local conveyance upgrades", "District / setting examples": "D.I. Khan and southern plains; Peshawar valley; upland valleys"},
    {"Province / region": "Balochistan", "Key challenge": "Aridity, flash-runoff losses and groundwater stress in some basins", "Priority responses": "Aquifer accounting, recharge structures where hydrogeologically suitable, efficient irrigation, abstraction management", "District / setting examples": "Nasirabad/Jaffarabad command; upland and coastal basins"},
])

SEASONS = pd.DataFrame([
    {"Season": "Kharif", "Typical period in supplied brief": "April–September", "Crops named": "Cotton, rice, sugarcane", "Shortfall mechanism": "Monsoon onset/timing and river-flow variability; intense rainfall may arrive as damaging flood pulses", "Planning focus": "Planting-window reliability, seasonal allocation, flood capture only where safe and feasible"},
    {"Season": "Rabi", "Typical period in supplied brief": "October–March", "Crops named": "Wheat and winter crops", "Shortfall mechanism": "Lower seasonal river flows and dependence on reservoir carryover and groundwater", "Planning focus": "Reservoir rule curves, crop-water budgeting, groundwater conjunctive use"},
])

SOLUTIONS = pd.DataFrame([
    {"Measure": "High-efficiency irrigation systems (HEIS)", "Mechanism": "Apply water nearer to crop demand and reduce avoidable field application", "Planning checks": "Crop suitability, filtration, energy, maintenance, salinity and actual consumptive use"},
    {"Measure": "Laser land leveling", "Mechanism": "Improve field uniformity and reduce ponding/over-application", "Planning checks": "Field survey, soil depth, operator access and before/after measurement"},
    {"Measure": "Canal and watercourse rehabilitation", "Mechanism": "Reduce conveyance losses where seepage is non-beneficial", "Planning checks": "Reach-specific seepage tests, groundwater impacts, cost and downstream return flows"},
    {"Measure": "Crop diversification and zoning", "Mechanism": "Align crop choices with local water availability and agro-ecology", "Planning checks": "Markets, food security, farmer income, soil and crop calendars"},
    {"Measure": "Groundwater governance and recharge", "Mechanism": "Track abstraction and support recharge where aquifers can accept it", "Planning checks": "Aquifer mapping, water quality, recharge rate, contamination risk and licensing"},
    {"Measure": "Telemetry and water-pricing reform", "Mechanism": "Improve measurement, accountability and maintenance funding", "Planning checks": "Calibration, public data access, affordability, legal authority and equity"},
])

INITIATIVES = pd.DataFrame([
    {"Programme / project": "Diamer-Bhasha Dam", "Level": "Federal", "Purpose in supplied brief": "Storage, hydropower and additional irrigation potential", "Status note": "Construction/status and target dates are time-sensitive; verify with WAPDA", "Source": "https://wapda.gov.pk/diamer-basha-dam-project/"},
    {"Programme / project": "Mohmand Dam", "Level": "Federal / KP", "Purpose in supplied brief": "Storage, hydropower and flood mitigation", "Status note": "Verify current construction and commissioning schedule with WAPDA", "Source": "https://wapda.gov.pk/"},
    {"Programme / project": "Indus Basin telemetry and water accounting", "Level": "Federal / provincial", "Purpose in supplied brief": "Real-time measurement and transparent allocation", "Status note": "Separate operational telemetry from proposed/planned coverage", "Source": "https://irsa.gov.pk/"},
    {"Programme / project": "Punjab Resilient and Inclusive Agriculture Transformation (PRIAT)", "Level": "Punjab", "Purpose in supplied brief": "Watercourse improvement, HEIS and on-farm water management", "Status note": "Targets and implementation progress require current Punjab project records", "Source": "https://agripunjab.gov.pk/"},
    {"Programme / project": "Punjab Water Efficient Agriculture programme (2025–2028)", "Level": "Punjab", "Purpose in supplied brief": "Watercourse improvement and laser land leveling", "Status note": "User-supplied programme details; verify approved PC-I/ADP and progress", "Source": "https://agripunjab.gov.pk/"},
    {"Programme / project": "Sindh Water and Agriculture Transformation (SWAT)", "Level": "Sindh", "Purpose in supplied brief": "Watercourse improvement, on-farm storage and water governance", "Status note": "Verify grant terms, districts, milestones and current implementation", "Source": "https://www.worldbank.org/en/country/pakistan"},
    {"Programme / project": "Small dams and hill-torrent management", "Level": "KP / Balochistan", "Purpose in supplied brief": "Capture seasonal runoff, support spate irrigation and recharge", "Status note": "Project-by-project status and hydrological suitability must be checked", "Source": "https://www.pndkp.gov.pk/"},
])


def _csv_download(df: pd.DataFrame, filename: str, key: str) -> None:
    st.download_button("⬇️ Download table as CSV", df.to_csv(index=False).encode("utf-8-sig"), filename, "text/csv", key=key)


def render_irrigation_shortfall_page() -> None:
    st.title("🇵🇰 Pakistan Irrigation Water Shortfall: Causes, Provincial Challenges & Solutions")
    st.caption("National decision-support overview | Integrates infrastructure, crop-water demand, climate, groundwater and governance")
    st.warning("Evidence note: several numerical statements in the supplied brief (including 50–60% losses, 30 days of storage, reservoir capacity loss, tubewell counts, seasonal deficit percentages and programme targets) are not independently verified here. They are not displayed as established national measurements. Use current official records and dated studies before policy or engineering use.")

    tabs = st.tabs(["National causes", "Provincial challenges", "Kharif & Rabi", "Solutions & scenarios", "Government initiatives", "Agentic assessment brief"])

    with tabs[0]:
        st.subheader("Six interacting drivers of irrigation shortfall")
        st.dataframe(CAUSES, use_container_width=True, hide_index=True)
        st.plotly_chart(px.bar(CAUSES, x="Driver", y=[1]*len(CAUSES), title="Cause categories (classification only — not a quantitative ranking)"), use_container_width=True)
        st.caption("The chart counts categories only. It does not estimate the share of national water shortage attributable to each cause.")
        st.markdown("#### How to quantify the shortfall")
        st.latex(r"\text{Seasonal deficit} = \text{crop demand} - \text{dependable delivered supply}")
        st.markdown("Measure demand and supply over the same command area, time step and unit. Record headworks diversion, canal delivery, farm-gate delivery, effective rainfall, groundwater contribution and environmental/other releases separately. Avoid treating all conveyance seepage as a basin-scale loss: some seepage may return to usable groundwater or downstream flows.")
        _csv_download(CAUSES, "pakistan_irrigation_shortfall_causes.csv", "shortfall_causes_csv")

    with tabs[1]:
        st.subheader("Provincial and regional challenge comparison")
        st.dataframe(PROVINCES, use_container_width=True, hide_index=True)
        selected = st.selectbox("Explore a province / region", PROVINCES["Province / region"].tolist(), key="shortfall_province")
        row = PROVINCES.loc[PROVINCES["Province / region"] == selected].iloc[0]
        st.info(f"**Key challenge:** {row['Key challenge']}\n\n**Priority responses:** {row['Priority responses']}\n\n**Illustrative settings:** {row['District / setting examples']}")
        st.caption("These are broad regional patterns, not exhaustive district diagnoses. A district may contain multiple canal, groundwater, soil and rainfall settings.")
        _csv_download(PROVINCES, "pakistan_provincial_water_challenges.csv", "provincial_challenges_csv")

    with tabs[2]:
        st.subheader("Seasonal supply-demand context")
        st.dataframe(SEASONS, use_container_width=True, hide_index=True)
        st.markdown("#### Editable seasonal water-shortfall screening")
        c1, c2, c3 = st.columns(3)
        with c1:
            season = st.selectbox("Season", ["Kharif", "Rabi"], key="shortfall_season_calc")
            demand = st.number_input("Estimated seasonal irrigation demand (MAF)", min_value=0.0, value=35.0 if season == "Kharif" else 30.0, step=0.5, key="shortfall_demand")
        with c2:
            supply = st.number_input("Dependable available supply (MAF)", min_value=0.0, value=32.0 if season == "Kharif" else 27.0, step=0.5, key="shortfall_supply")
        with c3:
            reserve = st.number_input("Operational / environmental reserve (MAF)", min_value=0.0, value=0.0, step=0.5, key="shortfall_reserve")
        available = max(0.0, supply - reserve)
        deficit = max(0.0, demand - available)
        surplus = max(0.0, available - demand)
        m1, m2, m3 = st.columns(3)
        m1.metric("Screened deficit", f"{deficit:.2f} MAF")
        m2.metric("Deficit as demand share", f"{(deficit/demand*100 if demand else 0):.1f}%")
        m3.metric("Screened surplus", f"{surplus:.2f} MAF")
        st.caption("Illustrative defaults only, not official IRSA seasonal allocations or measured national demand. Replace them with same-period official records. This simple calculator does not model monthly timing, reservoir routing, return flows or inter-provincial allocation rules.")
        comparison = pd.DataFrame({"Component": ["Demand", "Supply after reserve"], "Volume (MAF)": [demand, available]})
        st.plotly_chart(px.bar(comparison, x="Component", y="Volume (MAF)", title=f"{season} screening balance — editable assumptions"), use_container_width=True)

    with tabs[3]:
        st.subheader("Practical interventions")
        st.dataframe(SOLUTIONS, use_container_width=True, hide_index=True)
        st.markdown("#### Compare assumed delivery-efficiency scenarios")
        c1, c2 = st.columns(2)
        with c1:
            field_demand = st.number_input("Net field requirement (AF)", min_value=0.0, value=1000.0, step=50.0, key="shortfall_net_field")
            conveyance = st.slider("Conveyance efficiency (%)", 30, 100, 75, key="shortfall_conveyance")
        with c2:
            application = st.slider("Field application efficiency (%)", 30, 100, 70, key="shortfall_application")
            scenario_eff = st.slider("Alternative overall efficiency (%)", 30, 100, 85, key="shortfall_alt_eff")
        base_eff = (conveyance / 100) * (application / 100)
        alt_eff = scenario_eff / 100
        baseline_gross = field_demand / base_eff if base_eff else 0.0
        alternative_gross = field_demand / alt_eff if alt_eff else 0.0
        saving = max(0.0, baseline_gross - alternative_gross)
        st.metric("Illustrative gross diversion avoided under alternative assumption", f"{saving:,.1f} AF", delta=f"{(saving/baseline_gross*100 if baseline_gross else 0):.1f}% of baseline gross diversion")
        st.caption("Efficiency improvements reduce gross diversion needed to meet a fixed net field requirement in this simplified calculation. They do not automatically create basin-scale water savings if farmers expand irrigated area or increase consumptive use. Confirm return-flow effects and crop ET.")
        scenario_df = pd.DataFrame([{"Scenario": "Current assumed conveyance × field efficiency", "Overall efficiency (%)": base_eff*100, "Gross requirement (AF)": baseline_gross}, {"Scenario": "Alternative overall efficiency", "Overall efficiency (%)": alt_eff*100, "Gross requirement (AF)": alternative_gross}])
        st.plotly_chart(px.bar(scenario_df, x="Scenario", y="Gross requirement (AF)", title="Gross diversion requirement under editable efficiency assumptions"), use_container_width=True)
        _csv_download(scenario_df, "irrigation_efficiency_scenarios.csv", "efficiency_scenarios_csv")

    with tabs[4]:
        st.subheader("Federal and provincial initiatives mentioned in the supplied brief")
        st.dataframe(INITIATIVES, use_container_width=True, hide_index=True)
        st.caption("Programme inclusion does not confirm current implementation, approved scope, financing, target completion or benefits. Open the linked institution and check the latest dated project documents.")
        for _, item in INITIATIVES.iterrows():
            st.markdown(f"- **{item['Programme / project']}** — [{item['Level']}]({item['Source']})")
        _csv_download(INITIATIVES, "pakistan_water_initiatives_register.csv", "water_initiatives_csv")

    with tabs[5]:
        st.subheader("Decision-question workspace for the CrewAI Command Centre")
        questions = [
            "Which interventions could reduce irrigation delivery deficits in tail-end commands, and what measurements are needed to rank them?",
            "How should Kharif and Rabi reservoir operations be assessed under variable inflows and competing demands?",
            "Which districts need groundwater abstraction monitoring and water-quality assessment first?",
            "How can crop zoning and HEIS be evaluated without overstating basin-scale water savings?",
            "What telemetry, governance and maintenance reforms would improve transparent water accounting?",
        ]
        suggested = st.selectbox("Suggested decision question", questions, key="shortfall_suggested_question")
        custom = st.text_area("Or enter your own question", height=100, key="shortfall_custom_question")
        context = st.text_area("Add local data, district, time period or constraints (optional)", height=90, key="shortfall_agent_context")
        task = "Assess Pakistan irrigation water shortfall using the supplied project context. Separate observed data, user-supplied claims, assumptions and missing evidence. Compare structural, agricultural, seasonal, provincial, climate, groundwater and governance drivers. Recommend measurable, equitable interventions and identify verification requirements. Do not invent national statistics, project status or citations."
        if st.button("Prepare this task for the Agentic AI Command Centre", type="primary", key="shortfall_prepare_agentic"):
            st.session_state["agentic_goal_v2"] = task
            st.session_state["agentic_custom_question_v1"] = custom.strip() or suggested
            st.session_state["agentic_context_v2"] = "\n\n".join(["Source context: user-provided irrigation water shortfall brief.", context.strip()])
            st.success("Decision task prepared in this session. Open ‘Agentic AI Command Centre (CrewAI)’ from the sidebar; select ‘Irrigation, canals and groundwater’ and run the reviewed workflow.")
        st.markdown("**Suggested agent sector:** Irrigation, canals and groundwater. You can add integrated water resources, climate, agriculture, disaster risk and governance sectors in the existing agent centre.")
        st.code(task, language="text")

    st.divider()
    st.markdown("### Sources and verification register")
    source_rows = [
        ("Indus River System Authority (IRSA)", "https://irsa.gov.pk/", "Seasonal allocations, system operation and water accounting"),
        ("Water and Power Development Authority (WAPDA)", "https://wapda.gov.pk/", "Reservoir projects, storage and hydropower project status"),
        ("Punjab Irrigation Department", "https://irrigation.punjab.gov.pk/", "Canal operations, irrigation infrastructure and provincial records"),
        ("Punjab Agriculture Department", "https://agripunjab.gov.pk/", "Agriculture, water management and programme information"),
        ("World Bank Pakistan", "https://www.worldbank.org/en/country/pakistan", "Development programme documentation and project status"),
    ]
    for name, url, purpose in source_rows:
        st.markdown(f"- [{name}]({url}) — {purpose}")
    st.info("This dashboard is an analytical framework populated with the claims and programme references supplied for the project. It is not a live national water-accounting feed. Record publication date, geographic coverage, units, method and source for every numeric update.")
