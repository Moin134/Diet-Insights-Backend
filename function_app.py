import azure.functions as func
import json
import pandas as pd
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

def get_data():
    # Load and clean like Person B did
    df = pd.read_csv("All_Diets.csv")
    df = df.dropna()
    for col in ["Protein(g)", "Carbs(g)", "Fat(g)"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna()

@app.route(route="nutritional_insights")
def nutritional_insights(req: func.HttpRequest) -> func.HttpResponse:
    df = get_data()
    # Data for the Bar Chart
    insights = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean().to_dict(orient="index")
    return func.HttpResponse(json.dumps(insights), mimetype="application/json")

@app.route(route="recipes")
def recipes(req: func.HttpRequest) -> func.HttpResponse:
    df = get_data()
    # Send back the top recipes for the UI list
    data = df[['Recipe_name', 'Diet_type', 'Cuisine_type']].head(50).to_dict(orient="records")
    return func.HttpResponse(json.dumps(data), mimetype="application/json")

@app.route(route="clusters")
def clusters(req: func.HttpRequest) -> func.HttpResponse:
    df = get_data()
    # Data for the Scatter Plot (Protein vs Carbs)
    scatter = df[['Protein(g)', 'Carbs(g)', 'Diet_type']].to_dict(orient="records")
    return func.HttpResponse(json.dumps(scatter), mimetype="application/json")