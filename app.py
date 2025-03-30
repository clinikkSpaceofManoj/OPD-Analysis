import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


st.markdown(
    """
    <style>
    html, body, [data-testid="stApp"] {
        background-color: #FED2E2;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <style>
    div[data-baseweb="select"] > div {
        background-color: #C68EFD !important;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    /* Title (st.title) */
    h1 {
        color: #8F87F1 !important; /* Change title color */
        text-align: center;
    }

    /* Subheader (st.subheader) */
    h2 {
        color: #E9A5F1 !important; /* Change subheader color */
        font-weight: bold;
    }

    /* Button (st.button) */
    div.stButton > button {
        color: #FF8989 !important; /* Change button text color */
        background-color: #F8ED8C !important; /* Green button */
        border-radius: 10px;
        font-weight: bold;
    }

    /* Button hover effect */
    div.stButton > button:hover {
        background-color: #89AC46 !important;
        color: #FFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)



def load_data(file):
    data = file
    
    data["Sum of Total OPD MRP"] = data["Sum of Total OPD MRP"].fillna(0)
    data["Sum of Refund_Amount"] = data["Sum of Refund_Amount"].fillna(0)
    
    data["Total OPD Used"] = data["Sum of Total OPD MRP"] + data["Sum of Refund_Amount"]
    
    data = data[data["Sum of OPD Limit"] != 0]
    
    data.loc[:, "Opd Perc"] = np.where(
        data["Total OPD Used"] > 0, 
        round(((data["Total OPD Used"] / data["Sum of OPD Limit"]) * 100), 1), 
        0
    )
    return data

def process_data(data, ren_types, policy_years, planTypes, FamilyStructure, AgeBand):
    filtered_data = data[(data["ren_type"].isin(ren_types)) & (data["Sum of Policy start Year"].isin(policy_years))
                        & (data["Plan Type"].isin(planTypes)) & (data["Family Structure"].isin(FamilyStructure))
                        & (data["Age Band"].isin(AgeBand))]
    
    grouped_data = filtered_data.groupby("Age").agg({
        "Total OPD Used": "sum",
        "Sum of OPD Limit": "sum",
        "Sum of Total OPD MRP":"sum",
        "Sum of Refund_Amount":"sum"
    }).reset_index()

    st.divider()
    opd_assigned = sum(grouped_data["Sum of OPD Limit"])
    opd_exhausted = sum(grouped_data["Total OPD Used"])
    TotalCustomers = len(grouped_data)
    inopdUsed = sum(grouped_data["Sum of Total OPD MRP"])
    reimbursementsUsed = sum(grouped_data["Sum of Refund_Amount"])

    st.markdown(
        f"""
        <div style="background-color: #F1EFEC; border-radius: 10px; border: 2px solid #D4C9BE">
            <div style="display: flex; justify-content: space-evenly; align-items: center; width: 100%; padding: 5px 0;">
                <h4 style="color: #F7374F; text-align: center;">OPD Assigned: {opd_assigned:.2f}</h4>
                <h4 style="color: #88304E; text-align: center;">OPD Exhausted: {opd_exhausted:.2f}</h4>
            </div>
            <div style="display: flex; justify-content: space-evenly; align-items: center; width: 100%; padding: 5px 0;">
                <h4 style="color: #F7374F; text-align: center;">Clinikk OPD @MRP: {inopdUsed:.2f}</h4>
                <h4 style="color: #88304E; text-align: center;">Reimbursements: {reimbursementsUsed:.2f}</h4>
            </div>
            <div style="display: flex; justify-content: center; align-items: center; width: 100%; padding: 5px 0;">
                <h4 style="color: #F7374F; text-align: center;">Total Customers: {TotalCustomers}</h4>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

    #st.markdown(f'<h4 style="color: #F7374F;">OPD assigned: {sum(grouped_data["Sum of OPD Limit"]):.2f}</h4>', unsafe_allow_html=True)
    #st.markdown(f'<h4 style="color: #88304E;">OPD Exhausted: {sum(grouped_data["Total OPD Used"]):.2f}</h3>', unsafe_allow_html=True)
    st.divider()

    grouped_data["Opd Used Perc"] = np.where(
        grouped_data["Sum of OPD Limit"] > 0, 
        grouped_data["Total OPD Used"] / grouped_data["Sum of OPD Limit"], 
        0
    )
    
    bins = [-float("inf"), 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, float("inf")]
    labels = ["<0%", "1-10%", "11-20%", "21-30%", "31-40%", "41-50%", "51-60%", "61-70%", "71-80%", "81-90%", "91-100%", ">100%"]
    grouped_data["OPD Slab"] = pd.cut(grouped_data["Opd Used Perc"], bins=bins, labels=labels)
    
    slab_counts = grouped_data["OPD Slab"].value_counts().sort_index().reset_index()
    slab_counts.columns = ["OPD Slab", "Count"]
    
    return slab_counts

def main():
    st.title("OPD Usage Analysis App")
    
    uploaded_file = pd.read_csv("data1.csv")
    if uploaded_file is not None:
        data = load_data(uploaded_file)
        
        ren_types = st.multiselect("Select Renewal Types", options=data["ren_type"].unique().tolist(), default=data["ren_type"].unique().tolist())
        policy_years = st.multiselect("Select Policy Year", options=sorted(data["Sum of Policy start Year"].unique()), default=sorted(data["Sum of Policy start Year"].unique()))
        planTypes = st.multiselect("Select Plan Types", options=data["Plan Type"].unique().tolist(), default=data["Plan Type"].unique().tolist())
        FamilyStructure = st.multiselect("Select Family Structure", options=data["Family Structure"].unique().tolist(), default=data["Family Structure"].unique().tolist())
        AgeBand = st.multiselect("Select Age Band", options=data["Age Band"].unique().tolist(), default=data["Age Band"].unique().tolist())

        if st.button("Analyze Data"):
            slab_counts = process_data(data, ren_types, policy_years, planTypes, FamilyStructure, AgeBand)
            
            st.markdown(
                    f"""
                    <h3 style="
                        font-family: 'Arial, sans-serif'; 
                        color: #F7374F; 
                        text-align: center; 
                        font-size: 24px; 
                        font-weight: bold; 
                        padding: 10px;">
                        OPD Usage Distribution
                    </h3>
                    """, 
                    unsafe_allow_html=True
                )
            st.divider()

            st.dataframe(
                slab_counts.style.set_properties(
                    **{
                        'background-color': '#8AB2A6',  # Light Yellow Background
                        'color': '#3E3F5B',  # Black Text
                        'border': '1px solid #F6F1DE',  # Red Border
                        'text-align': 'center',  # Center Align Text
                        'font-size': '16px',  # Adjust Font Size
                        'font-family': 'Arial, sans-serif'  # Change Font
                    }
                ),
                hide_index=True,  
                column_config={
                    "OPD Slab": {"alignment": "center"},  
                    "Count": {"alignment": "center"}  # Ensure the correct column name
                }
            )
            
            fig = px.bar(
                slab_counts, 
                x="OPD Slab", 
                y="Count", 
                color="OPD Slab",
                color_discrete_sequence=["#034C53", "#007074", "#F38C79", "#FFC1B4"]
            )

            st.plotly_chart(fig)

if __name__ == "__main__":
    main()
