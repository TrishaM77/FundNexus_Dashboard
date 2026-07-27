import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.graph_objects as go # type: ignore
import plotly.express as px # type: ignore
import matplotlib.pyplot as plt # type: ignore
import streamlit as st # type: ignore

# Sidebar Inputs
st.sidebar.header("Google Sheet Settings")

sheet_id = st.sidebar.text_input(
    "Google Sheet ID",
    value=""
)

sheet_name = st.sidebar.text_input(
    "Sheet Name",
    value="Sheet1"
)

gid = st.sidebar.text_input(
    "GID (Optional)",
    value=""
)
if sheet_id:

    url = (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        f"/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    )

    df = pd.read_csv(url)

    st.success("Google Sheet loaded successfully!")

else:
    st.warning("Please enter the Google Sheet ID.")
    st.stop()
df["Call Date"] = pd.to_datetime(df["Call Date"], errors="coerce")

df["Follow Up Date"] = pd.to_datetime(
    df["Follow Up Date"],
    dayfirst=True,
    errors="coerce"
)

df["Donation Amount"] = pd.to_numeric(
    df["Donation Amount"],
    errors="coerce"
)
st.set_page_config(
    page_title="Fund Nexus Dashboard",
    page_icon="📊",
    layout="wide"
)
st.title("Fund Nexus Dashboard")
st.write("Monitor call performance and donation metrics in real time.")

st.markdown("---")
st.sidebar.title("Filters")
st.sidebar.write("Filters will be added here.")
st.markdown("---")

contacted_status = [
    "interested",
    "callback",
    "declined",
    "declined after follow up"
]

total_calls = len(df)

contacted_calls = df[df["Disposition"].isin(contacted_status)].shape[0]

contact_rate = round((contacted_calls / total_calls) * 100, 2)

converted_calls = df[df["Disposition"] == "interested"].shape[0]

if contacted_calls > 0:
    conversion_rate = round((converted_calls / contacted_calls) * 100, 2)
else:
    conversion_rate = 0

total_donations = df["Donation Amount"].sum()

today = pd.Timestamp.today().normalize()

followups_due = (
    df["Follow Up Date"].dt.normalize() == today
).sum()
col1, col2, col3, col4 = st.columns(4)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Contact Rate",
        value=f"{contact_rate}%"
    )

with col2:
    st.metric(
        label="Conversion Rate",
        value=f"{conversion_rate}%"
    )

with col3:
    st.metric(
        label="Donations Collected",
        value=f"₹{total_donations:,.0f}"
    )

with col4:
    st.metric(
        label="Follow-ups Due Today",
        value=f"{followups_due}"
    )

st.markdown("---")
# Tabs for Dashboard Overview and Call Performance
tab1, tab2, tab3 = st.tabs([
    "Daily calls",
    " Call Performance",
    "Fundraising Analytics"
])
with tab1:
    st.subheader("Daily Calls vs Target")
    df["Call Date"] = pd.to_datetime(df["Call Date"])

    daily_calls = (
        df.groupby([df["Call Date"].dt.date, "Master Agent Name"])["Call Id"]
        .count()
        .reset_index(name="Calls Done")
    )

    daily_calls.rename(columns={"Call Date": "Date"}, inplace=True)

    agents = sorted(daily_calls["Master Agent Name"].unique())

    selected_agents = st.multiselect(
        "Select Agent(s)",
        options=agents,
        default=agents
    )

    target = st.number_input(
        "Enter Daily Target",
        min_value=0,
        max_value=500,
        value=100,
        step=5
    )

    if len(selected_agents) > 0:
        fig = go.Figure()

        colors = px.colors.qualitative.Dark24

        for i, agent in enumerate(selected_agents):
            temp = daily_calls[
                daily_calls["Master Agent Name"] == agent
            ].sort_values("Date")

            border_colors = [
                "green" if calls >= target else "black"
                for calls in temp["Calls Done"]
            ]

            fig.add_trace(
                go.Scatter(
                    x=temp["Date"],
                    y=temp["Calls Done"],
                    mode="lines+markers",
                    name=agent,
                    line=dict(
                        color=colors[i % len(colors)],
                        width=3
                    ),
                    marker=dict(
                        size=10,
                        color=colors[i % len(colors)],
                        line=dict(
                            color=border_colors,
                            width=3
                        )
                    ),
                    hovertemplate=
                    "<b>Agent:</b> %{fullData.name}<br>"
                    "<b>Date:</b> %{x}<br>"
                    "<b>Calls:</b> %{y}<extra></extra>"
                )
            )

        fig.add_hline(
            y=target,
            line_dash="dash",
            line_color="red",
            line_width=3,
            annotation_text=f"Target = {target}"
        )

        fig.update_layout(
            title="Daily Calls vs Target",
            xaxis_title="Date",
            yaxis_title="Calls Done",
            template="plotly_white",
            hovermode="closest",
            autosize=True,
            height=650,
            legend_title="Agents"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Please select at least one agent.")

st.markdown("---")
with tab2:
    col1,col2 = st.columns(2)
    with col1:
        st.subheader("Contact Rate")
        df["Disposition"] = (
            df["Disposition"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        contacted = [
            "interested",
            "callback",
            "declined",
            "declined after follow up"
        ]
        total_calls = len(df)
        contacted_calls = df[df["Disposition"].isin(contacted)].shape[0]

        contact_rate = round((contacted_calls / total_calls) * 100, 2)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=contact_rate,
            number={"suffix": "%"},
            title={"text": "<b>Contact Rate</b>"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "royalblue"},
                "steps": [
                    {"range": [0, 40], "color": "#F8CECC"},
                    {"range": [40, 70], "color": "#FFE599"},
                    {"range": [70, 100], "color": "#B6D7A8"}
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "value": 80
                }
            }
        ))

        fig.update_layout(
            autosize=True,
            height=450,
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="contact_rate_chart"
        )
    with col2:
        st.subheader("Conversion Rate")
        df["Disposition"] = (
            df["Disposition"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        contacted_status = [
            "interested",
            "callback",
            "declined",
            "declined after follow up"
        ]

        contacted_calls = df[df["Disposition"].isin(contacted_status)]
        converted_calls = df[df["Disposition"] == "interested"]

        total_contacted = len(contacted_calls)
        total_converted = len(converted_calls)

        if total_contacted > 0:
            conversion_rate = round((total_converted / total_contacted) * 100, 2)
        else:
            conversion_rate = 0

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=conversion_rate,
            number={"suffix": "%"},
            title={"text": "<b>Conversion Rate</b>"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "darkgreen"},
                "steps": [
                    {"range": [0, 30], "color": "#F8CECC"},
                    {"range": [30, 60], "color": "#FFE599"},
                    {"range": [60, 100], "color": "#B6D7A8"}
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "value": 50
                }
            }
        ))

        fig.update_layout(
            autosize=True,
            height=450,
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="conversion_rate_chart"
        )

    col3,col4 = st.columns(2)
    with col3:
        st.subheader("Hot Leads Pending")
        df["Follow Up Date"] = pd.to_datetime(
            df["Follow Up Date"],
            dayfirst=True,
            errors="coerce"
        )
        today = pd.Timestamp.today().normalize()

        hot_leads = df[
            (df["Disposition"] == "interested") &
            (df["Follow Up Date"] >= today)
        ]

        hot_leads_agent = (
            hot_leads.groupby("Master Agent Name")
            .size()
            .reset_index(name="Hot Leads Pending")
        )
        fig = px.bar(
            hot_leads_agent,
            x="Hot Leads Pending",
            y="Master Agent Name",
            orientation="h",
            color="Hot Leads Pending",
            color_continuous_scale="Reds",
            text="Hot Leads Pending",
            title="Hot Leads Pending by Agent"
        )

        fig.update_traces(textposition="outside")

        fig.update_layout(
            template="plotly_white",
            autosize=True,
            height=500,
            title_x=0.5,
            xaxis_title="Number of Hot Leads",
            yaxis_title="Master Agent Name"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="hot_leads_chart"
        )
    with col4:
        st.subheader("Agent Rankings")

        agent_rankings = (
            df.groupby("Master Agent Name")["Call Id"]
            .count()
            .reset_index(name="Total Calls")
        )

        agent_rankings = agent_rankings.sort_values(
            by="Total Calls",
            ascending=False
        )

        agent_rankings["Rank"] = range(1, len(agent_rankings) + 1)
        fig = px.bar(
            agent_rankings,
            x="Total Calls",
            y="Master Agent Name",
            orientation="h",
            color="Total Calls",
            color_continuous_scale="Viridis",
            text="Total Calls",
            hover_data=["Rank"],
            title="Agent Rankings (Based on Total Calls)"
        )

        fig.update_traces(
            textposition="outside"
        )

        fig.update_layout(
            template="plotly_white",
            autosize=True,
            height=600,
            title_x=0.5,
            xaxis_title="Number of Calls",
            yaxis_title="Agent Name",
            yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            key="agent_rankings_chart"
        )
with tab3:

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Donations Collected")
        df["Call Date"] = pd.to_datetime(df["Call Date"], errors="coerce")

        df["Donation Amount"] = pd.to_numeric(
            df["Donation Amount"],
            errors="coerce"
        )
        donation_df = df.dropna(subset=["Donation Amount"])
        daily_donations = (
            donation_df.groupby("Call Date")["Donation Amount"]
            .sum()
            .reset_index()
        )
        fig = px.line(
            daily_donations,
            x="Call Date",
            y="Donation Amount",
            title="Daily Donations Collected",
            markers=True,
            labels={
                "Call Date": "Date",
                "Donation Amount": "Donation Amount (₹)"
            }
        )

        fig.update_traces(
            line=dict(color="green", width=3),
            marker=dict(size=8, color="darkgreen")
        )

        fig.update_layout(
            template="plotly_white",
            autosize=True,
            height=500,
            hovermode="x unified",
            xaxis_title="Call Date",
            yaxis_title="Donation Amount (₹)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="donations_chart"
        )

    with col2:
        st.subheader("Disposition Trends")
        disposition_count = (
            df["Disposition"]
            .value_counts()
            .reset_index()
        )
        disposition_count.columns = ["Disposition", "Count"]

        fig = px.pie(
            disposition_count,
            names="Disposition",
            values="Count",
            hole=0.5,
            title="Disposition Trends",
            color="Disposition",
            color_discrete_map={
                "interested": "#2E8B57",
                "callback": "#1F77B4",
                "wrong number": "#D62728",
                "no answer": "#FF7F0E",
                "declined": "#9467BD",
                "declined after follow up": "#8C564B"
                }
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
        )
        fig.update_layout(
            template="plotly_white",
            autosize=True,
            height=600,
            title_x=0.5,
            legend_title="Disposition"
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            key="disposition_trends_chart"
        )

    st.subheader("Follow-ups Due Today")
    today = pd.Timestamp.today().normalize()
    followups_today = df[df["Follow Up Date"].dt.normalize() == today]
    agent_followups = (
        followups_today.groupby("Master Agent Name")
        .size()
        .reset_index(name="Follow Ups Due")
        )
    if not agent_followups.empty:
        fig = px.bar(
            agent_followups,
            x="Follow Ups Due",
            y="Master Agent Name",
            orientation="h",
            color="Follow Ups Due",
            color_continuous_scale="Blues",
            text="Follow Ups Due",
            title="Follow-ups Due Today by Agent"
        )

        fig.update_traces(
            textposition="outside"
        )
        fig.update_layout(
            template="plotly_white",
            autosize=True,
            height=500,
            title_x=0.5,
            xaxis_title="Number of Follow-ups",
            yaxis_title="Master Agent Name"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="followups_today_chart"
        )

    else:
        st.success("No follow-ups due today!")
    