# Import required packages
import streamlit as st
from snowflake.snowpark.functions import col

# App Title and Description
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom smoothie!
    """
)

# Establish Snowflake Session
cnx = st.connection("snowflake")
session = cnx.session()

# Query the FRUIT_OPTIONS table and select only the FRUIT_NAME column
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Display the fruit options as a dataframe
st.dataframe(data=my_dataframe, use_container_width=True)

# Multi-select widget to choose ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',  # Widget label
    my_dataframe                    # Data source for multi-select
)

# Display the selected ingredients
if ingredients_list:
    # Combine selected ingredients into a single string
    ingredients_string = ', '.join(ingredients_list)  # Use comma as a separator

    # Create the SQL insert statement
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders(ingredients)
    VALUES ('{ingredients_string}')
    """

    # Button to trigger the insertion
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # Execute the insert statement
        session.sql(my_insert_stmt).collect()

        # Display success message
        st.success('Your Smoothie is ordered!', icon="✅")
