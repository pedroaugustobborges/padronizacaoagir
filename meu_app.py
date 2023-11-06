import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")
url = "https://docs.google.com/spreadsheets/d/1CGypJWn35SFD6oYeLmFU1HjMhxJRBpuuVuVeP7y86wo/edit#gid=0"

conn = st.experimental_connection("gsheets", type=GSheetsConnection)

df = conn.read(spreadsheet=url, usecols=list(range(22)))
df1 = conn.read(spreadsheet=url, usecols=list(range(22)))
df = df.sort_values("DATA DE ATRIBUIÇÃO:")

# Convert the "DATA DE ATRIBUIÇÃO:" column to datetime with errors='coerce'
df["DATA DE ATRIBUIÇÃO:"] = pd.to_datetime(df["DATA DE ATRIBUIÇÃO:"], format='%d/%m/%Y', errors='coerce')

# Filter out rows where the date could not be parsed (NaT)
df = df.dropna(subset=["DATA DE ATRIBUIÇÃO:"])

# Extract year, month, and quarter
df["Year"] = df["DATA DE ATRIBUIÇÃO:"].dt.year
df["Month"] = df["DATA DE ATRIBUIÇÃO:"].dt.month
df["Quarter"] = df["DATA DE ATRIBUIÇÃO:"].dt.quarter

# Create a "Year-Quarter" column
df["Year-Quarter"] = df["Year"].astype(str) + "-T" + df["Quarter"].astype(str)

# If you want to create a "Year-Month" column, you can use the following line
df["Year-Month"] = df["DATA DE ATRIBUIÇÃO:"].dt.strftime("%Y-%m")


#----------------------- CREATING THE COLUMN TO DATA DE CONCLUSÃO ------


df = df.sort_values("DATA DE CONCLUSÃO:")
# Convert the "DATA DE ATRIBUIÇÃO:" column to datetime with errors='coerce'
df["DATA DE CONCLUSÃO:"] = pd.to_datetime(df["DATA DE CONCLUSÃO:"], format='%d/%m/%Y', errors='coerce')
# Filter out rows where the date could not be parsed (NaT)
df = df.dropna(subset=["DATA DE CONCLUSÃO:"])

df["Year conclusion"] = df["DATA DE CONCLUSÃO:"].dt.year
df["Month conclusion"] = df["DATA DE CONCLUSÃO:"].dt.month
df["Quarter conclusion"] = df["DATA DE CONCLUSÃO:"].dt.quarter

# Create a "Year-Quarter" column
df["Year-Quarter conclusion"] = df["Year conclusion"].astype(str) + "-T" + df["Quarter conclusion"].astype(str)

# If you want to create a "Year-Month" column, you can use the following line
df["Year-Month conclusion"] = df["DATA DE CONCLUSÃO:"].dt.strftime("%Y-%m")


#--------------------------------------


# Sort the unique values in ascending order
unique_year_month = sorted(df["Year-Month"].unique())
unique_year_quarter = sorted(df["Year-Quarter"].unique())

# Add "All" as an option for both filters
unique_year_month.insert(0, "Todos")
unique_year_quarter.insert(0, "Todos")

# Create a sidebar for selecting filters
month = st.sidebar.selectbox("Mês", unique_year_month)
quarter = st.sidebar.selectbox("Trimestre", unique_year_quarter)

# Define the list of "UNIDADE:" values and add "Todos" as an option
desired_unidades = ["CRER", "HECAD", "HUGOL", "HDS", "AGIR", "TEIA", "CED"]
desired_unidades.insert(0, "Todos")

# Create a filter for selecting "UNIDADE:"
unidade = st.sidebar.selectbox("Unidade:", desired_unidades)

# Check if "All" is selected for the "Year-Month" filter
if month == "Todos":
    month_filtered = df
else:
    month_filtered = df[df["Year-Month"] == month]

# Check if "All" is selected for the "Year-Quarter" filter
if quarter == "Todos":
    filtered_df = month_filtered
else:
    filtered_df = month_filtered[month_filtered["Year-Quarter"] == quarter]

# Check if "Todos" is selected for the "UNIDADE:" filter
if unidade != "Todos":
    filtered_df = filtered_df[filtered_df["UNIDADE:"] == unidade]

# Display the filtered DataFrame
st.write("Filtered Data:")
st.dataframe(filtered_df)


col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
col5, col7 = st.columns(2)
col6 = st.columns(1)







# Calculate the Quantity of "ATRIBUÍDO" (total number of rows in filtered_df)
quantity_atribuido = len(filtered_df["Year-Month"])
quantity_residual = (df1["FORMULA 1"] == 2).sum()
# Calculate the Quantity of "FINALIZADO"
if quarter == "Todos" and month == "Todos":
    # When both "Trimestre" and "Mês" are "Todos", quantity_finalizado is the count of values in "FORMULA 1" in df
    quantity_finalizado = quantity_atribuido - quantity_residual
else:
    # When at least one of "Trimestre" or "Mês" is not "Todos"
    if quarter == "Todos":
        # When only "Trimestre" is "Todos", use the first value in "Year-Month" of filtered_df
        first_year_month = filtered_df["Year-Month"].iloc[0]
        quantity_finalizado = (df["Year-Month conclusion"] == first_year_month).sum()
    else:
        if month == "Todos":
            # When only "Mês" is "Todos", use the first value in "Year-Quarter" of filtered_df
            first_year_quarter = filtered_df["Year-Quarter"].iloc[0]
            quantity_finalizado = (df["Year-Quarter conclusion"] == first_year_quarter).sum()
        else:
            # When both "Trimestre" and "Mês" are not "Todos", quantity_finalizado is 0
            quantity_finalizado = 0

# Calculate the Quantity of "RESIDUAL"
quantity_residual = quantity_atribuido - quantity_finalizado







# Create a dictionary to hold the values
data = {
    'Category': ['RESIDUAL', 'ATRIBUÍDO', 'FINALIZADO'],
    'Quantity': [quantity_residual, quantity_atribuido, quantity_finalizado]
}


# You can also display the values as text in the sidebar
st.sidebar.markdown(f"**RESIDUAL:** {quantity_residual}")
st.sidebar.markdown(f"**ATRIBUÍDO:** {quantity_atribuido}")
st.sidebar.markdown(f"**FINALIZADO:** {quantity_finalizado}")

# Standardize the names and capitalize the first letter
filtered_df["ANALISTA:"] = filtered_df["ANALISTA:"].str.strip().str.lower().str.capitalize()
filtered_df["ANALISTA:"].replace({"Renato": "Renato", "Ingrid": "Ingrid", "Naiani": "Naiani", "Yasmine ": "Yasmine"}, inplace=True)

counts = filtered_df["ANALISTA:"].value_counts().reset_index()
counts.columns = ["ANALISTA", "Quantidade"]

fig_date = px.bar(counts, x="ANALISTA", y="Quantidade", title="Quantidade de processos atribuídos a cada analista")
col1.plotly_chart(fig_date)

# Assuming filtered_df is your DataFrame
avg_lead_time = filtered_df.groupby("ANALISTA:")["LEAD TIME DO PROCESSO:"].mean().reset_index()
avg_lead_time = avg_lead_time.sort_values(by="LEAD TIME DO PROCESSO:", ascending=False)

fig_avg_lead_time = px.bar(avg_lead_time, x="ANALISTA:", y="LEAD TIME DO PROCESSO:", title="Lead Time Médio por Analista")
col2.plotly_chart(fig_avg_lead_time)

#   TERCEIRO GRÁFICO
# Calculate the "Taxa de assertividade" for each month
assertividade_data = filtered_df.groupby(["Year-Month"])["ANDAMENTO:"].apply(lambda x: (x == "FINALIZADO").sum() / x.count() * 100).reset_index()
assertividade_data.columns = ["Year-Month", "Taxa de assertividade"]

# Create a line chart
fig_assertividade = px.line(assertividade_data, x="Year-Month", y="Taxa de assertividade", title="Taxa de assertividade dos processos recebidos (%)")

# Add a horizontal line at 90%
fig_assertividade.add_hline(y=90, line_dash="dash", line_color="green", annotation_text="90%", annotation_position="bottom right")

# Add the "target" annotation
fig_assertividade.add_annotation(text="META", xref="paper", yref="y", x=0.999, y=91, showarrow=False)

# Show the line chart
col4.plotly_chart(fig_assertividade)

# QUARTO GRÁFICOOO -------------------

# Define the list of "UNIDADE:" values you want to include
desired_unidades = ["CRER", "HECAD", "HUGOL", "HDS", "AGIR", "TEIA", "CED"]

# Filter the DataFrame to include only the desired "UNIDADE:" values and where "INCONFORMIDADE 1:" is not equal to "-"
filtered_df = filtered_df[(filtered_df["UNIDADE:"].isin(desired_unidades)) & (filtered_df["INCONFORMIDADE 1:"] != "-")]

# Group the data by "UNIDADE:" and "INCONFORMIDADE 1:" and count the occurrences
grouped_data = filtered_df.groupby(["UNIDADE:", "INCONFORMIDADE 1:"]).size().reset_index(name="Quantidade")

# Sort the grouped_data DataFrame in descending order based on the "Quantidade" column
grouped_data = grouped_data.sort_values(by="Quantidade", ascending=False)

# Create a bar chart
fig_inconformidade = px.bar(grouped_data, x="UNIDADE:", y="Quantidade", color="INCONFORMIDADE 1:", title="Quantidade de Inconformidades por Unidade")

# Show the bar chart
col5.plotly_chart(fig_inconformidade)

#QUINTO GRÁFICO --------------------------------------

# Filter out rows with "-" values in "INCONFORMIDADE 1:"
inconformidade_data = filtered_df[filtered_df["INCONFORMIDADE 1:"] != "-"]

# Group the data by "Year-Month" and "INCONFORMIDADE 1:" and count the occurrences
inconformidade_grouped = inconformidade_data.groupby(["Year-Month", "INCONFORMIDADE 1:"]).size().reset_index(name="Quantidade")

# Create a line chart with multiple lines, one for each value in "INCONFORMIDADE 1:"
fig_inconformidade_lines = px.line(inconformidade_grouped, x="Year-Month", y="Quantidade", color="INCONFORMIDADE 1:", title="Comportamento das Inconformidades por Mês")

# Show the line chart
col7.plotly_chart(fig_inconformidade_lines)

#SEXTO GRÁFICO ---------------------------------

# Filter the DataFrame to include only rows with "FINALIZADO" or "DEVOLVIDO A UNIDADE" in "ANDAMENTO:"
completed_jobs = filtered_df[filtered_df["ANDAMENTO:"].isin(["FINALIZADO", "DEVOLVIDO A UNIDADE"])]

# Group the data by "ANALISTA:" and count the occurrences
analista_counts = completed_jobs["ANALISTA:"].value_counts().reset_index()
analista_counts.columns = ["ANALISTA:", "Quantidade"]

# Create a donut chart
fig_donut = px.pie(
    analista_counts,
    names="ANALISTA:",
    values="Quantidade",
    title="Porcentagem de Produtividade da Equipe",
    hole=0.4  # Adjust the hole size (0.4 represents 40% of the inner hole)
)

# Show the donut chart
col3.plotly_chart(fig_donut)





#ULTIMO GRAFICO


import plotly.express as px

# Calculate the Quantity of "ATRIBUÍDO" (total number of rows in filtered_df)
quantity_atribuido = len(filtered_df)

# Calculate the Quantity of "FINALIZADO"
if quarter == "Todos" and month == "Todos":
    # When both "Trimestre" and "Mês" are "Todos", quantity_finalizado is the count of values in "FORMULA 1" in df
    quantity_finalizado = quantity_atribuido - quantity_residual
else:
    # When at least one of "Trimestre" or "Mês" is not "Todos"
    if quarter == "Todos":
        # When only "Trimestre" is "Todos", use the first value in "Year-Month" of filtered_df
        first_year_month = filtered_df["Year-Month"].iloc[0]
        quantity_finalizado = (df["Year-Month conclusion"] == first_year_month).sum()
    else:
        if month == "Todos":
            # When only "Mês" is "Todos", use the first value in "Year-Quarter" of filtered_df
            first_year_quarter = filtered_df["Year-Quarter"].iloc[0]
            quantity_finalizado = (df["Year-Quarter conclusion"] == first_year_quarter).sum()
        else:
            # When both "Trimestre" and "Mês" are not "Todos", quantity_finalizado is 0
            quantity_finalizado = 0

# Calculate the Quantity of "RESIDUAL"
quantity_residual = quantity_atribuido - quantity_finalizado

# Create a DataFrame to hold the values
residual_data = pd.DataFrame({
    "Year-Month": filtered_df["Year-Month"].unique(),
    "quantity_residual": quantity_residual
})

# Create a line chart
fig_residual = px.line(residual_data, x="Year-Month", y="quantity_residual", title="Quantity Residual por Mês")

# Show the line chart
st.plotly_chart(fig_residual)





#atribuídos x realizados x residual
#meta de conformidade que é 90% e qual a % atual
#processos devolvidos e quais as suas inconformidades
#lead time por analista
#meta prevista de 100% e meta realizada
#quantidade de recebidos, de realziados e de inconformidades
#% de produtividade da equipe
#inconformidades por unidade
