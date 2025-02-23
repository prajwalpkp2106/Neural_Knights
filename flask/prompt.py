def Disease_Predictor(
    disease: str,
    crop: str,
    longitude: float = None,
    latitude: float = None,
    location: str = ""
):
    # Define the basic prompt structure
    base_prompt = f"""
*Prompt:*  
*"Given the crop name {crop}, disease {disease},"""

    # Include latitude and longitude if provided
    if latitude is not None and longitude is not None:
        base_prompt += f" and location (latitude: {latitude}, longitude: {longitude})"

    base_prompt += """ provide the following details in a structured format:  

1. *Pesticides & Fungicides:* List effective chemical solutions.  
2. *Fertilizers:* Recommend suitable fertilizers.  
3. *Organic Solutions:* Suggest natural treatments.  
4. *Hybrid Crops:* Mention disease-resistant hybrid varieties.  

Format the output as follows (without extra lines or explanations):  

*Pesticides & Fungicides:* {list}  
*Fertilizers:* {list}  
*Organic Solutions:* {list}  
*Hybrid Crops:* {list}  

ensure a structured, region-specific, and concise response without unnecessary text.
Dont provide any suggestions(Like -Specific regional varieties needed for accurate response) just list them in the respective categories.
Provide output in key - value pairs in json and remove '\','*' and '\n'.
"""

    # If a location is provided, append it
    if location:
        base_prompt += f"\n\n## Location in which the crop is being cultivated: {location}"

    return base_prompt
