import streamlit as st
import pandas as pd
import mysql.connector as db
import matplotlib.pyplot as plt
import seaborn as sns
import io

# Connect to MySQL Database
connection = db.connect(
    host='localhost',
    user='root',
    password='Anbu_0820',
    database='ds'
)
cursor = connection.cursor()

# Streamlit App Configuration
st.set_page_config(layout="wide")
st.markdown("<h2 style='text-align: center; color: #a19d9d;'>💉 DS_Nutrition Paradox 💊🫃</h2>", unsafe_allow_html=True)
st.divider()

# Load data from MySQL
obesity_query = "SELECT * FROM obesity"
malnutrition_query = "SELECT * FROM malnutrition"

obesity_data = pd.read_sql(obesity_query, connection)
malnutrition_data = pd.read_sql(malnutrition_query, connection)

# Sidebar Navigation
st.sidebar.title("Navigation")
section = st.sidebar.selectbox("Select Analysis Section", ["Obesity Analysis", "Malnutrition Analysis", "Combined Analysis"])

# Function to generate downloadable CSV and image

def render_download_buttons(df, filename_prefix):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data as CSV", csv, file_name=f"{filename_prefix}.csv", mime="text/csv")

def render_chart_download(fig, filename):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    st.download_button("Download Chart as PNG", data=buf.getvalue(), file_name=filename, mime="image/png")

# Obesity Queries
def obesity_queries():
    st.header("Obesity Analysis")

    options = [
        "Top 5 regions with highest avg obesity levels in 2022",
        "Top 5 countries with highest obesity estimates",
        "Obesity trend in India over the years",
        "Average obesity by gender",
        "Country count by obesity level and age group",
        "Top 5 least reliable and most consistent countries by CI_Width",
        "Average obesity by age group",
        "Top 10 countries with consistent low obesity",
        "Countries where female obesity exceeds male by large margin",
        "Global average obesity percentage per year"
    ]

    choice = st.sidebar.selectbox("Select an analysis", options)

    if choice == options[0]:
        st.subheader(choice)
        top_regions_2022 = obesity_data[obesity_data['Year'] == 2022].groupby('Region')['Mean_Estimate'].mean().sort_values(ascending=False).head(5)
        st.write(top_regions_2022)
        st.bar_chart(top_regions_2022)

    elif choice == options[1]:
        st.subheader(choice)
        top_countries = obesity_data.groupby('Country')['Mean_Estimate'].mean().sort_values(ascending=False).head(5)
        st.write(top_countries)
        st.bar_chart(top_countries)

    elif choice == options[2]:
        st.subheader(choice)
        india_trend = obesity_data[obesity_data['Country'] == 'India'].groupby('Year')['Mean_Estimate'].mean()
        st.write(india_trend)
        st.line_chart(india_trend)

    elif choice == options[3]:
        st.subheader(choice)
        gender_obesity = obesity_data.groupby('Gender')['Mean_Estimate'].mean()
        st.write(gender_obesity)
        st.bar_chart(gender_obesity)

    elif choice == options[4]:
        st.subheader(choice)
        obesity_data['Category'] = pd.cut(obesity_data['Mean_Estimate'], bins=[0, 10, 20, 30, 100], labels=['Low', 'Moderate', 'High', 'Very High'])
        count_by_category = obesity_data.groupby(['Category', 'age_group']).size().unstack()
        st.write(count_by_category)
        st.bar_chart(count_by_category.T)

    elif choice == options[5]:
        st.subheader(choice)
        top_least_reliable = obesity_data.groupby('Country')['CI_Width'].max().sort_values(ascending=False).head(5)
        top_most_consistent = obesity_data.groupby('Country')['CI_Width'].mean().sort_values().head(5)
        st.write("Top 5 least reliable countries:")
        st.write(top_least_reliable)
        st.write("Top 5 most consistent countries:")
        st.write(top_most_consistent)
        fig, ax = plt.subplots(1, 2, figsize=(12, 5))   
        sns.barplot(x=top_least_reliable.index, y=top_least_reliable.values, ax=ax[0])
        sns.barplot(x=top_most_consistent.index, y=top_most_consistent.values, ax=ax[1])
        ax[0].set_title("Top 5 Least Reliable Countries")
        ax[1].set_title("Top 5 Most Consistent Countries")
        st.pyplot(fig)

    elif choice == options[6]:
        st.subheader(choice)
        age_group_obesity = obesity_data.groupby('age_group')['Mean_Estimate'].mean()
        st.write(age_group_obesity)
        st.bar_chart(age_group_obesity)

    elif choice == options[7]:
        st.subheader(choice)
        consistent_low_obesity = obesity_data.groupby('Country').agg(
            avg_obesity=('Mean_Estimate', 'mean'),
            avg_ci_width=('CI_Width', 'mean')
        )
        consistent_low_obesity = consistent_low_obesity[(consistent_low_obesity['avg_obesity'] < 15) & (consistent_low_obesity['avg_ci_width'] < 5)]
        top_10 = consistent_low_obesity.sort_values(by=['avg_obesity', 'avg_ci_width']).head(10)
        st.write(top_10)
        st.bar_chart(top_10['avg_obesity'])

    elif choice == options[8]:
        st.subheader(choice)
        gender_diff = obesity_data.groupby(['Country', 'Gender'])['Mean_Estimate'].mean().unstack()
        gender_diff['Diff'] = gender_diff['Female'] - gender_diff['Male']
        significant_diff = gender_diff[gender_diff['Diff'] > 5].sort_values('Diff', ascending=False)
        st.write(significant_diff)
        st.bar_chart(significant_diff['Diff'])

    elif choice == options[9]:
        st.subheader(choice)
        global_trend = obesity_data.groupby('Year')['Mean_Estimate'].mean()
        st.write(global_trend)
        st.line_chart(global_trend)

# Function to render malnutrition-related queries
def malnutrition_queries():
    st.header("Malnutrition Analysis")

    options = [
        "Avg. malnutrition by age group",
        "Top 5 countries with highest malnutrition",
        "Malnutrition trend in African region over the years",
        "Gender-based average malnutrition",
        "Malnutrition level-wise (average CI_Width by age group)",
        "Yearly malnutrition change in India, Nigeria, Brazil",
        "Regions with lowest malnutrition averages",
        "Countries with increasing malnutrition",
        "Min/Max malnutrition levels year-wise comparison",
        "High CI_Width flags for monitoring (CI_Width > 5)"
    ]

    choice = st.sidebar.selectbox("Select an analysis", options)

    if choice == options[0]:
        st.subheader(choice)
        age_group_malnutrition = malnutrition_data.groupby('age_group')['Mean_Estimate'].mean()
        st.write(age_group_malnutrition)
        st.bar_chart(age_group_malnutrition)

    elif choice == options[1]:
        st.subheader(choice)
        top_countries_malnutrition = malnutrition_data.groupby('Country')['Mean_Estimate'].mean().sort_values(ascending=False).head(5)
        st.write(top_countries_malnutrition)
        st.bar_chart(top_countries_malnutrition)

    elif choice == options[2]:
        st.subheader(choice)
        africa_trend = malnutrition_data[malnutrition_data['Region'] == 'Africa'].groupby('Year')['Mean_Estimate'].mean()
        st.write(africa_trend)
        st.line_chart(africa_trend)

    elif choice == options[3]:
        st.subheader(choice)
        gender_malnutrition = malnutrition_data.groupby('Gender')['Mean_Estimate'].mean()
        st.write(gender_malnutrition)
        st.bar_chart(gender_malnutrition)

    elif choice == options[4]:
        st.subheader(choice)
        malnutrition_data['Level'] = pd.cut(malnutrition_data['Mean_Estimate'], bins=[0, 10, 20, 30, 100], labels=['Low', 'Moderate', 'High', 'Very High'])
        avg_ci_by_level = malnutrition_data.groupby(['Level', 'age_group'])['CI_Width'].mean().unstack()
        st.write(avg_ci_by_level)
        st.bar_chart(avg_ci_by_level.T)

    elif choice == options[5]:
        st.subheader(choice)
        countries = ['India', 'Nigeria', 'Brazil']
        yearly_change = malnutrition_data[malnutrition_data['Country'].isin(countries)].groupby(['Country', 'Year'])['Mean_Estimate'].mean().unstack()
        st.write(yearly_change)
        st.line_chart(yearly_change.T)

    elif choice == options[6]:
        st.subheader(choice)
        low_regions = malnutrition_data.groupby('Region')['Mean_Estimate'].mean().sort_values().head(5)
        st.write(low_regions)
        st.bar_chart(low_regions)

    elif choice == options[7]:
        st.subheader(choice)
        change_df = malnutrition_data.groupby('Country')['Mean_Estimate'].agg(['min', 'max'])
        increase_df = change_df[change_df['max'] > change_df['min']]
        st.write(increase_df.sort_values(by='max', ascending=False))
        st.bar_chart(increase_df['max'])


    elif choice == options[8]:
        st.subheader(choice)
        yearly_minmax = malnutrition_data.groupby('Year')['Mean_Estimate'].agg(['min', 'max'])
        st.write(yearly_minmax)
        st.line_chart(yearly_minmax)

    elif choice == options[9]:
        st.subheader(choice)
        flagged_data = malnutrition_data[malnutrition_data['CI_Width'] > 5]
        st.write(flagged_data)
        st.bar_chart(flagged_data.groupby('Country')['CI_Width'].mean())
        render_download_buttons(flagged_data, "high_ci_width_flags")

# Function to render combined obesity and malnutrition queries
def combined_queries():
    st.header("Combined Analysis: Obesity vs Malnutrition")

    options = [
        "Obesity vs malnutrition comparison by country (any 5 countries)",
        "Gender-based disparity in both obesity and malnutrition",
        "Region-wise avg estimates side-by-side (Africa and America)",
        "Countries with obesity up & malnutrition down",
        "Age-wise trend analysis"
    ]

    choice = st.sidebar.selectbox("Select an analysis", options)

    if choice == options[0]:
        st.subheader(choice)
        countries = st.multiselect("Select countries", obesity_data['Country'].unique())
        if countries:
            comparison_data = obesity_data[obesity_data['Country'].isin(countries)].merge(
                malnutrition_data[malnutrition_data['Country'].isin(countries)],
                on=['Country', 'Year']
            )
            st.write(comparison_data)

    elif choice == options[1]:
        st.subheader(choice)
        gender_comparison = obesity_data.groupby('Gender')['Mean_Estimate'].mean().to_frame(name='Obesity')
        gender_comparison['Malnutrition'] = malnutrition_data.groupby('Gender')['Mean_Estimate'].mean()
        st.write(gender_comparison)

    elif choice == options[2]:
        st.subheader(choice)
        
        # Get average obesity and malnutrition by region
        obesity_region = obesity_data[obesity_data['Region'].isin(['Africa', 'America'])].groupby('Region')['Mean_Estimate'].mean().rename('Obesity')
        malnutrition_region = malnutrition_data[malnutrition_data['Region'].isin(['Africa', 'America'])].groupby('Region')['Mean_Estimate'].mean().rename('Malnutrition')
        
        # Merge with outer join to include all regions
        regions_comparison = pd.merge(obesity_region, malnutrition_region, left_index=True, right_index=True, how='outer')
        
        st.write(regions_comparison)
        st.bar_chart(regions_comparison)

    elif choice == options[3]:
        st.subheader(choice)

        # Step 1: Group and get min/max for both datasets
        obesity_change = obesity_data.groupby('Country')['Mean_Estimate'].agg(['min', 'max'])
        malnutrition_change = malnutrition_data.groupby('Country')['Mean_Estimate'].agg(['min', 'max'])

        # Debug print
        st.write("📊 Obesity Change (min & max):")
        st.dataframe(obesity_change)

        st.write("📊 Malnutrition Change (min & max):")
        st.dataframe(malnutrition_change)

        # Step 2: Merge both into one DataFrame on Country
        combined = pd.merge(
            obesity_change, 
            malnutrition_change, 
            left_index=True, 
            right_index=True, 
            suffixes=('_obesity', '_malnutrition')
        )

        # Debug print
        st.write("🔗 Combined Obesity & Malnutrition Changes:")
        st.dataframe(combined)

        # Step 3: Filter for increasing obesity and decreasing malnutrition
        filtered = combined[
            (combined['max_obesity'] > combined['min_obesity']) & 
            (combined['max_malnutrition'] < combined['min_malnutrition'])
        ]

        # Step 4: Show result or warning
        if filtered.empty:
            st.warning("⚠️ No countries found with increasing obesity and decreasing malnutrition.")
        else:
            st.success("✅ Countries with increasing obesity and decreasing malnutrition:")
            st.dataframe(filtered)

            # Optional Bar Chart
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(14, 6))
            x = range(len(filtered))
            ax.bar(x, filtered['max_obesity'] - filtered['min_obesity'], width=0.4, label='Obesity Increase')
            ax.bar([i + 0.4 for i in x], filtered['min_malnutrition'] - filtered['max_malnutrition'], width=0.4, label='Malnutrition Decrease', color='orange')
            ax.set_xticks([i + 0.2 for i in x])
            ax.set_xticklabels(filtered.index, rotation=90)
            ax.set_ylabel("Change in Mean Estimate")
            ax.set_title("Countries: Obesity ↑ and Malnutrition ↓")
            ax.legend()
            st.pyplot(fig)


    elif choice == options[4]:
        st.subheader("Obesity Age-wise Trend")
        obesity_trend = obesity_data.groupby(['Year', 'age_group'])['Mean_Estimate'].mean().unstack()
        st.write(obesity_trend)
        st.line_chart(obesity_trend)

        st.subheader("Malnutrition Age-wise Trend")
        malnutrition_trend = malnutrition_data.groupby(['Year', 'age_group'])['Mean_Estimate'].mean().unstack()
        st.write(malnutrition_trend)
        st.line_chart(malnutrition_trend)

# Run the selected query group
if section == "Obesity Analysis":
    obesity_queries()
elif section == "Malnutrition Analysis":
    malnutrition_queries()
elif section == "Combined Analysis":
    combined_queries()

