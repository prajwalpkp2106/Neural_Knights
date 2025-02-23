def get_fertilizer_dosage(crop_type, growth_stage, fertilizer_name, plot_size):
    prompt=f'''You are an expert agricultural AI assistant. Your task is to predict how a given crop disease will progress over time based on essential farming factors and recommend the required quantity of treatment or fertilizer.  

### *Input Parameters:*  
- Crop Type:{crop_type} [e.g., Wheat, Rice, Corn]  
- *Growth Stage:{growth_stage} [e.g., Germination, Vegetative,  , Fruiting]  
- *Fertilizer Name:*{fertilizer_name} [e.g., Urea, NPK, DAP]  
- *Plot Size:*{plot_size} [Value in hectares or acres]  

### *Task:*  
Analyze the potential disease impact and progression based on the given parameters. Consider how growth stage, fertilizer application, and plot size influence disease spread and severity.  

### *Output Format:*  
Provide a *numeric value* for the recommended quantity of treatment or fertilizer.  

### *Example Output (JSON format):* 
# json
{{"fertilizer": "Urea", "quantity": "50 kg"}}
'''

    return prompt