import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

title = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", title)

# Get the active Snowflake session
session = get_active_session()

# Fetch fruit options from the Snowflake table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert the Snowpark DataFrame to a Pandas DataFrame to use the `loc` function
pd_df = my_dataframe.to_pandas()

# Display multi-select widget for ingredients
Ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'],
    max_selections=5
)

if Ingredients_list:
    ingredients_string = ''

    for fruit_chosen in Ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get the 'SEARCH_ON' value for the chosen fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for', fruit_chosen, 'is', search_on, '.')

        # Fetch and display nutrition information from the Fruityvice API
        st.subheader(f'{fruit_chosen} Nutrition Information')
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
        if fruityvice_response.status_code == 200:
            fv_data = fruityvice_response.json()
            fv_df = pd.DataFrame([fv_data])
            st.dataframe(fv_df, use_container_width=True)
        else:
            st.write(f"Could not fetch data for {fruit_chosen}.")

    # Prepare the SQL insert statement
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER) 
    VALUES ('{ingredients_string.strip()}', '{title}');
    """

    # Button to submit the order
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # Execute the SQL insert statement
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {title}!', icon="✅")
