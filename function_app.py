import azure.functions as func
import json
import pandas as pd
import logging
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

def get_data():
    # Use absolute path to ensure Azure can find the CSV file in the same folder
    base_path = os.path.dirname(os.path.realpath(__file__))
    csv_path = os.path.join(base_path, "All_Diets.csv")
    
    try:
        df = pd.read_csv(csv_path)
        # Cleaning like Person B: Remove empty rows and fix numeric columns
        df = df.dropna()
        for col in ["Protein(g)", "Carbs(g)", "Fat(g)"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        return df.dropna()
    except Exception as e:
        logging.error(f"Error reading CSV: {str(e)}")
        return pd.DataFrame()

@app.route(route="nutritional_insights")
def nutritional_insights(req: func.HttpRequest) -> func.HttpResponse:
    df = get_data()
    if df.empty:
        return func.HttpResponse("Error loading data", status_code=500)
        
    # Data for the Bar Chart: Average macros per Diet Type
    insights = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean().to_dict(orient="index")
    return func.HttpResponse(json.dumps(insights), mimetype="application/json")

@app.route(route="recipes")
def recipes(req: func.HttpRequest) -> func.HttpResponse:
    df = get_data()
    if df.empty:
        return func.HttpResponse("Error loading data", status_code=500)
        
    # Send back the top 50 recipes for the UI list
    data = df[['Recipe_name', 'Diet_type', 'Cuisine_type']].head(50).to_dict(orient="records")
    return func.HttpResponse(json.dumps(data), mimetype="application/json")

@app.route(route="clusters")
def clusters(req: func.HttpRequest) -> func.HttpResponse:
    df = get_data()
    if df.empty:
        return func.HttpResponse("Error loading data", status_code=500)
        
    # Data for the Scatter Plot (Protein vs Carbs)
    scatter = df[['Protein(g)', 'Carbs(g)', 'Diet_type']].to_dict(orient="records")
    return func.HttpResponse(json.dumps(scatter), mimetype="application/json")