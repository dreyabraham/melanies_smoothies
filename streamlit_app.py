# Import required packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# App Title and Description
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom smoothie!
    """
)

# Input field to get the name for the smoothie
name_on_order = st.text_input("Name On Smoothie:")
st.write(f"The name on your smoothie will be **{name_on_order}**")

# Establish Snowflake Session
cnx = st.connection("snowflake")
session = cnx.session()

# Query the FRUIT_OPTIONS table and select only the FRUIT_NAME column
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))

pd_df = my_dataframe.to_pandas()

# Multi-select widget to choose ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',   # Widget label
    pd_df['FRUIT_NAME'].tolist(),    # Data source for multi-select
    max_selections=5                 # Limit the number of selections to 5
)

# Display the selected ingredients and allow submission
if ingredients_list:
    # Initialize an empty string to store selected ingredients
    ingredients_string = ', '.join(ingredients_list)  # Create a comma-separated list of ingredients
    
    # Display nutrition information for each selected fruit
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        st.subheader(f"{fruit_chosen} Nutrition Information")
        
        # Make the API request
        try:
            smoothiefroot_response = requests.get("https://www.smoothiefroot.com/api/fruit/" + search_on)
            smoothiefroot_response.raise_for_status()  # Will raise an HTTPError for bad responses
            data = smoothiefroot_response.json()  # Extract JSON data

            # Display data in a dataframe
            st.write(f"Nutrition information for {fruit_chosen}:")
            st.dataframe(data, use_container_width=True)
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")

    # SQL insert statement to save the order in the database
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Button to submit the order
    if st.button('Submit Order'):
        # Execute the insert statement in Snowflake
        session.sql(my_insert_stmt).collect()
        st.success(f"Thank you, **{name_on_order}**! Your Smoothie is ordered!", icon="✅")
