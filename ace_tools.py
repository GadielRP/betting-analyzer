import pandas as pd

def display_dataframe_to_user(name, dataframe):
    """
    Display a pandas DataFrame in a formatted way
    """
    print(f"\n{name}")
    print("-" * 50)
    print(dataframe)
    print("-" * 50) 