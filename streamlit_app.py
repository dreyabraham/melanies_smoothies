# Import required package
import streamlit as st
from snowflake.snowpark.functions import col

# App Title and Description
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom smoothie!
    """
)

name_on_order = st.text_input("Name On Smoothie:")
st.write("The name on your smoothie will be", name_on_order)

# Establish Snowflake Session
cnx = st.connection("snowflake")
session = cnx.session()

# Query the FRUIT_OPTIONS table and select only the FRUIT_NAME column
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Display the fruit options as a dataframe
st.dataframe(data=my_dataframe, use_container_width=True)

# Multi-select widget to choose ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'  # Widget label
    ,my_dataframe     
    ,max_selections=5 # Data source for multi-select
)

# Display the selected ingredients
if ingredients_list:

  ingredients_string = ''
 
  for fruit_chosen in ingredients_list:
      ingredients_string += fruit_chosen + ''

  # st.write(ingredients_string)

  my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""
  # st.write(my_insert_stmt)
  # st.stop()  
  time_to_insert = st.button('Submit Order')


  if time_to_insert:
     session.sql(my_insert_stmt).collect()
     st.success(f"Thank you, {name_on_order}! Your Smoothie is ordered!", icon="✅")

# New section to display SmoothieFroot nutrition information
import requests

# Make a GET request to retrieve nutritional information for watermelon
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

# Optionally, you can display the raw JSON response (commented out for now)
# st.text(smoothiefroot_response.json())
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

