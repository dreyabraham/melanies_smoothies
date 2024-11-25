# Import required packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas

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
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col("SEARCH_ON"))

# Display the fruit options as a dataframe
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

pd_df = my_dataframe.to_pandas()

# Multi-select widget to choose ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',   # Widget label
    my_dataframe,                    # Data source for multi-select
    max_selections=5                 # Limit the number of selections to 5
)

# Display the selected ingredients and allow submission
if ingredients_list:
    # Initialize an empty string to store selected ingredients
    ingredients_string = ' '.join(ingredients_list)  # Concatenate fruits into a single string with spaces

    # Display nutrition information for each selected fruit
    for fruit_chosen in ingredients_list:
        

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        # Fetch nutrition information for the selected fruit from the SmoothieFroot API
        
        st.subheader(f"{fruit_chosen} Nutrition Information")  
        smoothiefroot_response = requests.get ("https://www.smoothiefroot.com/api/fruit/all" + search_on)
       
        # Display the API response in a Streamlit dataframe
        # st.write(f"Nutrition information for **{fruit_chosen}**:")
            
        fv_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

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
