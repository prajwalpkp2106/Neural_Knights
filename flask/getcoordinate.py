def get_coordinates(location=None):
    prompt = f"""
    You are an AI assistant that provides accurate geographical coordinates.

    ### **Task:**  
    Generate a **random or specific latitude and longitude** {f"for {location}" if location else ""}.  

    ### **Output Format:**  
    The output should **only** contain two numeric values representing latitude and longitude in decimal degrees, formatted as a **JSON object**.

    **Example Output:**  
    json
    {{"latitude": 37.7749, "longitude": -122.4194}}
    ```
    Do not include any additional text, explanations, or direction indicators (N, S, E, W)—just the numeric values.
    """
    return prompt   
