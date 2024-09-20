
# Import python packages
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

session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#Convert the Snowpark Dataframe to a Pandas Dataframe so we can use the LOC function
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

Ingredients_list = st.multiselect(
    'Choose upto 5 ingredients:'
    , my_dataframe
    , max_selections = 5
    )

#st.write(Ingredients_list)


if Ingredients_list:
    ingredients_string = ''

    for fruit_chosen in Ingredients_list:
            ingredients_string += fruit_chosen + ' '

            search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
            st.subheader(fruit_chosen + ' Nutrition Information')
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
            fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
    #st.write(ingredients_string)
    
    my_insert_stmt = """ insert into smoothies.public.orders(INGREDIENTS, NAME_ON_ORDER) 
            values ('""" + ingredients_string + "'"+',' + "'"+ title + "'"+ ');'

    time_to_insert = st.button('Submit Order')
    
    #st.write(my_insert_stmt)
    #st.stop()
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
    
        st.success(f'Your Smoothie is ordered,{title}!', icon="✅")
