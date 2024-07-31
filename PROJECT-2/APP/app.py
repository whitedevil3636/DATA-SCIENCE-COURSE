import streamlit as st
import pandas as pd
from helpers import *

summer,winter = data_preprocessor()

summer,winter = duplicate_rows_remover(summer,winter)

summer.dropna(subset=["region"] , inplace=True)
winter.dropna(subset=["region"] , inplace=True)

st.sidebar.title("MENU")
season = st.sidebar.radio("Choose Season : " ,("Summer","Winter"))
options = st.sidebar.radio("Options" , ("Medal-Tally" , "Country-Wise","Year-Wise","Year-Wise Progress"))

### MEDAL TALLY

if season=="Summer" and options=="Medal-Tally":
    st.subheader("Summer Olymmpics Medal Tally")
    medal_pivot_summer = medal_tally_calculator(summer)
    medal_pivot_summer = medal_pivot_summer.sort_values(by=["Gold","Silver","Bronze"] , ascending=False)
    st.dataframe(medal_pivot_summer , width=700)

elif season=="Winter" and options=="Medal-Tally":
    st.subheader("Winter Olymmpics Medal Tally")
    medal_pivot_winter = medal_tally_calculator(winter)
    medal_pivot_winter = medal_pivot_winter.sort_values(by=["Gold","Silver","Bronze"] , ascending=False)
    st.dataframe(medal_pivot_winter , width=700)


### Country-Wise
elif season=="Summer" and options=="Country-Wise":
    st.subheader("Summer Country-Wise Search")
    medal_pivot_summer = medal_tally_calculator(summer)
    noc = st.selectbox("Select NOC : " , medal_pivot_summer.index.tolist())
    details = country_wise_search(noc , medal_pivot_summer)
    table = pd.DataFrame.from_dict(details , orient="index" , columns=["Value"])
    st.dataframe(table)

elif season=="Winter" and options=="Country-Wise":
    st.subheader("Winter Country-Wise Search")
    medal_pivot_winter = medal_tally_calculator(winter)
    noc = st.selectbox("Select NOC : " , medal_pivot_winter.index.tolist())
    details = country_wise_search(noc , medal_pivot_winter)
    table = pd.DataFrame.from_dict(details , orient="index" , columns=["Value"])
    st.dataframe(table)


### YEAR-WISE
elif season=="Summer" and options=="Year-Wise":
    st.subheader("Summer Year-Wise Search")

    years = sorted(summer["Year"].unique())
    selected_year = st.selectbox("Select Year" , years)

    countries = sorted(summer[summer["Year"]==selected_year]["region"].unique())
    selected_country = st.selectbox("Select Country :" , countries)

    plot_medals(selected_year,selected_country,summer)

elif season=="Winter" and options=="Year-Wise":
    st.subheader("Winter Year-Wise Search")

    years = sorted(winter["Year"].unique())
    selected_year = st.selectbox("Select Year" , years)

    countries = sorted(winter[winter["Year"]==selected_year]["region"].unique())
    selected_country = st.selectbox("Select Country :" , countries)

    plot_medals(selected_year,selected_country,winter)

### YEAR WISE ANALYSIS

elif season=="Summer" and options=="Year-Wise Progress":
    st.subheader("OVERALL ANALYSIS OF A COUNTRY")

    countries = sorted(summer["region"].unique())
    selected_country = st.selectbox("Choose country : ",countries)

    year_analysis(selected_country,summer)

else:

    st.subheader("OVERALL ANALYSIS OF A COUNTRY")

    countries = sorted(winter["region"].unique())
    selected_country = st.selectbox("Choose country : ",countries)

    year_analysis(selected_country,winter)



