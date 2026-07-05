# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     https://www.apache.org/licenses/LICENSE-2.0

import sys
import os
import pandas as pd
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("Public Health Knowledge Server")

# Resolve path to the data file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(CURRENT_DIR, "data", "community_health_data.csv")

# Factual Medical Database
DISEASE_DB = {
    "dengue": (
        "**Dengue Fever**\n\n"
        "- **Cause**: Transmission of the dengue virus by female Aedes mosquitoes (primarily Aedes aegypti).\n"
        "- **Symptoms**: High fever (104°F/40°C), severe headache, pain behind the eyes, muscle and joint pain, nausea, vomiting, swollen glands, and a skin rash.\n"
        "- **Prevention**: Avoid mosquito bites by using insect repellent (DEET), wearing protective clothing (long sleeves/pants), eliminating standing water around the house, and installing window screens.\n"
        "- **When to seek medical help**: Seek immediate emergency medical care if warning signs appear, typically 3-7 days after symptoms start. These include severe abdominal pain, persistent vomiting, bleeding gums/nose, extreme fatigue, restlessness, and blood in vomit or stools."
    ),
    "diabetes": (
        "**Diabetes Mellitus**\n\n"
        "- **Cause**: Inability of the body to produce enough insulin (Type 1) or effectively use the insulin it produces (Type 2).\n"
        "- **Symptoms**: Increased thirst, frequent urination, unexplained weight loss, fatigue, blurry vision, slow-healing sores, and frequent infections.\n"
        "- **Prevention**: Type 2 diabetes can be prevented or delayed through lifestyle modifications, including maintaining a healthy weight, staying active (at least 150 minutes of moderate exercise per week), eating a balanced diet rich in fiber and whole grains, and avoiding tobacco.\n"
        "- **When to seek medical help**: Consult a healthcare provider if you experience symptoms like persistent fatigue, excessive thirst, or frequent urination. Seek urgent emergency care for signs of diabetic ketoacidosis (DKA), which include rapid breathing, fruity breath, confusion, and vomiting."
    ),
    "influenza": (
        "**Influenza (Flu)**\n\n"
        "- **Cause**: Infection of the respiratory tract by Influenza A or B viruses.\n"
        "- **Symptoms**: Sudden onset of fever, chills, cough, sore throat, runny or stuffy nose, muscle aches, headache, and severe fatigue.\n"
        "- **Prevention**: The most effective prevention is the annual flu vaccination. Additionally, practice frequent handwashing, avoid close contact with infected individuals, and cover coughs and sneezes.\n"
        "- **When to seek medical help**: Most people recover in a week, but seek immediate emergency care if you experience difficulty breathing, chest pain, persistent dizziness, confusion, or severe muscle weakness."
    ),
    "heat stroke": (
        "**Heat Stroke**\n\n"
        "- **Cause**: Prolonged exposure to high temperatures or strenuous physical activity in hot environments, leading to the body's failure to regulate its temperature (core temperature rises above 104°F/40°C).\n"
        "- **Symptoms**: Altered mental state (confusion, agitation, slurred speech, delirium), hot/dry skin or heavy sweating, high body temperature, nausea, rapid breathing, and a racing heart rate.\n"
        "- **Prevention**: Stay hydrated (drink water frequently), wear lightweight and loose-fitting clothing, avoid strenuous outdoor activities during peak heat hours, and take frequent cooling breaks in shade or air-conditioned environments.\n"
        "- **When to seek medical help**: **Heat stroke is a medical emergency.** Call local emergency services (like 911) immediately. While waiting, move the person to a cool area and apply cool water or wet cloths to lower their body temperature."
    )
}

MYTH_DB = {
    "antibiotics cure viral infections": (
        "**Myth Verification: Antibiotics cure viral infections**\n\n"
        "- **Status**: **FALSE**\n"
        "- **Explanation**: Antibiotics are designed to target and kill **bacteria**, not viruses. Common colds, influenza, COVID-19, and dengue are caused by viruses, meaning antibiotics will not cure them, reduce symptoms, or speed up recovery. Overusing antibiotics for viral illnesses leads to the development of antibiotic-resistant bacteria, which is a major global health threat."
    ),
    "vaccines cause autism": (
        "**Myth Verification: Vaccines cause autism**\n\n"
        "- **Status**: **FALSE**\n"
        "- **Explanation**: Extensive scientific research involving millions of children worldwide has repeatedly demonstrated that there is **no link** between vaccines (such as the MMR vaccine) and autism. The original claim was based on a small, fraudulent 1998 study that was subsequently fully retracted, and its author's medical license was revoked due to misconduct."
    ),
    "cold weather causes flu": (
        "**Myth Verification: Cold weather causes the flu**\n\n"
        "- **Status**: **FALSE**\n"
        "- **Explanation**: The flu is caused by the influenza **virus**, not cold weather itself. Cold temperatures do not make you sick. However, in winter, people spend more time indoors in close proximity to one another, making transmission easier. Additionally, low humidity indoors helps the influenza virus remain stable and suspended in the air longer."
    ),
    "drinking water cures diabetes": (
        "**Myth Verification: Drinking water cures diabetes**\n\n"
        "- **Status**: **FALSE**\n"
        "- **Explanation**: While drinking sufficient water is crucial for overall health and helps flush excess glucose from the kidneys in diabetics, it **cannot cure** diabetes. Diabetes is a chronic metabolic disorder that requires clinical management, which may include insulin therapy, oral glucose-lowering medications, dietary changes, and regular physical activity."
    ),
    "vitamin c prevents colds": (
        "**Myth Verification: Vitamin C prevents colds**\n\n"
        "- **Status**: **PARTIALLY TRUE / MISLEADING**\n"
        "- **Explanation**: Standard daily supplementation of Vitamin C does not reduce the risk of contracting a cold for the general population. However, it has been shown to slightly reduce the duration (by about 8% in adults) and severity of colds once they develop. It is best obtained through a balanced diet rich in citrus fruits, bell peppers, and leafy greens."
    )
}

VACCINE_DB = {
    "child": (
        "**Recommended Child Vaccination Schedule (Ages 0-6 Years)**\n\n"
        "1. **Birth**: Hepatitis B (HepB) dose 1.\n"
        "2. **2 Months**: HepB dose 2, DTaP (Diphtheria, Tetanus, Pertussis), Hib (Haemophilus influenzae type b), PCV (Pneumococcal), IPV (Inactivated Poliovirus), Rotavirus (RV).\n"
        "3. **4 Months**: DTaP, Hib, PCV, IPV, RV (second doses).\n"
        "4. **6 Months**: HepB dose 3, DTaP, Hib, PCV, IPV, RV (third doses), and Annual Influenza vaccine.\n"
        "5. **12-15 Months**: MMR (Measles, Mumps, Rubella), Varicella (Chickenpox), Hib, PCV, and Hepatitis A (HepA).\n"
        "6. **4-6 Years**: DTaP, IPV, MMR, Varicella booster doses."
    ),
    "adult": (
        "**Recommended Adult Vaccination Schedule**\n\n"
        "1. **Every Year**: Influenza (Flu) vaccine.\n"
        "2. **Every 10 Years**: Tetanus-Diphtheria-Pertussis (Td/Tdap) booster.\n"
        "3. **Ages 50+**: Zoster (Shingles) vaccine (2 doses, 2-6 months apart).\n"
        "4. **Ages 65+**: Pneumococcal vaccine (PCV15/PCV20) to protect against pneumonia.\n"
        "5. **Any Age**: COVID-19 updated vaccinations as recommended by local authorities."
    )
}

RESOURCES_DB = {
    "hand hygiene": (
        "**Public Health Guideline: Hand Hygiene**\n\n"
        "- **Instructions**: Wash hands thoroughly with soap and clean water for at least 20 seconds. Ensure you scrub the backs of your hands, between your fingers, and under your nails.\n"
        "- **Key times to wash**: Before preparing food or eating, after using the restroom, after blowing your nose/coughing/sneezing, and after touching garbage.\n"
        "- **Alternative**: Use an alcohol-based hand sanitizer containing at least 60% alcohol if soap and water are not immediately available."
    ),
    "nutrition": (
        "**Public Health Guideline: Healthy Nutrition**\n\n"
        "- **Core Recommendations**: Build your meals around nutrient-dense foods. Fill half your plate with colorful fruits and vegetables, one-quarter with whole grains (brown rice, oats, whole wheat), and one-quarter with lean proteins (poultry, fish, beans, tofu).\n"
        "- **Hydration**: Drink plenty of water throughout the day. Limit sugary beverages, sodas, and juices.\n"
        "- **Limits**: Restrict intake of sodium (less than 2,300 mg/day), saturated fats, and added sugars."
    ),
    "heat stroke prevention": (
        "**Public Health Guideline: Preventing Heat Stroke**\n\n"
        "- **Hydrate**: Drink plenty of fluids (water, electrolyte drinks) even if you don't feel thirsty. Avoid caffeine and alcohol as they dehydrate the body.\n"
        "- **Dress**: Wear lightweight, light-colored, and loose-fitting clothing.\n"
        "- **Environment**: Keep indoor environments cool. Use fans or air conditioning. Stay out of direct sunlight during peak ultraviolet hours (10 AM to 4 PM).\n"
        "- **Safety**: Never leave children, elderly individuals, or pets in a parked car, even with the windows cracked."
    )
}


@mcp.tool()
def retrieve_disease_info(disease: str) -> str:
    """Retrieve trusted public health information for a specific disease.

    Args:
        disease: The name of the disease (e.g., dengue, diabetes, influenza, heat stroke).
    """
    cleaned = disease.lower().strip()
    # Fuzzy match
    for k, v in DISEASE_DB.items():
        if k in cleaned or cleaned in k:
            return v
    
    return (
        f"No direct match found for '{disease}'. Here is a general notice: "
        "Maintain proper hygiene, seek physician advice, and stay updated on local health advisories."
    )


@mcp.tool()
def verify_health_myth(claim: str) -> str:
    """Verify common health claims, rumors, or myths against trusted clinical data.

    Args:
        claim: The health claim to verify (e.g., 'antibiotics cure viral infections', 'vaccines cause autism').
    """
    cleaned = claim.lower().strip()
    for k, v in MYTH_DB.items():
        if k in cleaned or cleaned in k:
            return v
            
    # Generic myth response
    return (
        f"Verification results for query: '{claim}'\n\n"
        "Status: UNVERIFIED\n"
        "Explanation: This claim does not match our current database of validated medical myths. "
        "Always consult certified healthcare practitioners or official bodies (such as the WHO or CDC) before believing medical claims found online."
    )


@mcp.tool()
def get_vaccination_schedule(age_group: str) -> str:
    """Retrieve recommended vaccination schedule for children (infants) or adults.

    Args:
        age_group: Either 'child' (or 'infant') or 'adult'.
    """
    cleaned = age_group.lower().strip()
    if "child" in cleaned or "infant" in cleaned or "kid" in cleaned:
        return VACCINE_DB["child"]
    elif "adult" in cleaned:
        return VACCINE_DB["adult"]
    else:
        return (
            "Please specify either 'child' or 'adult' to get the appropriate vaccination schedule. "
            "Example: get_vaccination_schedule(age_group='child')"
        )


@mcp.tool()
def get_preventive_guidelines(topic: str) -> str:
    """Retrieve public health resources and preventive guidelines on hygiene, nutrition, or heat stroke.

    Args:
        topic: The topic of interest (e.g., 'hand hygiene', 'nutrition', 'heat stroke prevention').
    """
    cleaned = topic.lower().strip()
    for k, v in RESOURCES_DB.items():
        if k in cleaned or cleaned in k:
            return v
            
    return (
        f"No specific guidelines found for '{topic}'. General recommendation: "
        "Wash hands frequently, consume a balanced diet, exercise regularly, stay hydrated, and sleep 7-8 hours daily."
    )


@mcp.tool()
def analyze_health_trends() -> str:
    """Analyze community health data to find total cases, highest-risk regions, and trend summaries.
    """
    if not os.path.exists(CSV_PATH):
        return "Community health dataset is not available."
        
    try:
        df = pd.read_csv(CSV_PATH)
        total_cases = int(df['cases'].sum())
        region_cases = df.groupby('region')['cases'].sum()
        highest_risk_region = region_cases.idxmax()
        highest_cases = int(region_cases.max())
        
        # Calculate trends comparing latest month (June) to previous month (May)
        dates = sorted(df['date'].unique())
        trend_report = []
        if len(dates) >= 2:
            latest_date = dates[-1]
            prev_date = dates[-2]
            latest_df = df[df['date'] == latest_date]
            prev_df = df[df['date'] == prev_date]
            
            for disease in df['disease'].unique():
                latest_cases = latest_df[latest_df['disease'] == disease]['cases'].sum()
                prev_cases = prev_df[prev_df['disease'] == disease]['cases'].sum()
                
                if prev_cases > 0:
                    pct_change = (latest_cases - prev_cases) / prev_cases * 100
                    if pct_change > 0:
                        trend_report.append(f"{disease}: +{pct_change:.1f}% ({prev_cases} -> {latest_cases} cases)")
                    elif pct_change < 0:
                        trend_report.append(f"{disease}: -{abs(pct_change):.1f}% ({prev_cases} -> {latest_cases} cases)")
                    else:
                        trend_report.append(f"{disease}: Stable ({latest_cases} cases)")
                else:
                    if latest_cases > 0:
                        trend_report.append(f"{disease}: New cases reported ({latest_cases} cases)")
                        
        trend_summary = ", ".join(trend_report) if trend_report else "No historical trends calculated."
        
        return (
            f"**Community Health Trends Summary**\n\n"
            f"- **Total Cases**: {total_cases}\n"
            f"- **Highest Risk Region**: {highest_risk_region} ({highest_cases} total cases)\n"
            f"- **Trends (Latest MoM)**: {trend_summary}"
        )
    except Exception as e:
        return f"Error analyzing health trends: {str(e)}"


@mcp.tool()
def predict_health_risk(disease: str, region: str) -> str:
    """Predict risk level (Low Risk, Medium Risk, High Risk) for a disease in a specific region.
    
    Args:
        disease: Name of the disease (e.g. Dengue, Influenza).
        region: Name of the region/ward (e.g. Ward 1).
    """
    if not os.path.exists(CSV_PATH):
        return "Community health dataset is not available."
        
    try:
        cleaned_disease = disease.lower().strip()
        cleaned_region = region.lower().strip()
        
        df = pd.read_csv(CSV_PATH)
        matching_diseases = [d for d in df['disease'].unique() if cleaned_disease in d.lower()]
        matching_regions = [r for r in df['region'].unique() if cleaned_region in r.lower()]
        
        if not matching_diseases or not matching_regions:
            return f"Could not find data for disease '{disease}' in region '{region}'."
            
        tgt_disease = matching_diseases[0]
        tgt_region = matching_regions[0]
        
        sub = df[(df['disease'] == tgt_disease) & (df['region'] == tgt_region)].sort_values('date')
        if len(sub) < 2:
            return f"Insufficient historical data to predict risk for {tgt_disease} in {tgt_region}."
            
        latest_row = sub.iloc[-1]
        prev_row = sub.iloc[-2]
        
        latest_cases = int(latest_row['cases'])
        prev_cases = int(prev_row['cases'])
        
        if prev_cases == 0:
            change_pct = 100.0 if latest_cases > 0 else 0.0
        else:
            change_pct = (latest_cases - prev_cases) / prev_cases * 100.0
            
        if change_pct > 25.0:
            risk = "High Risk"
        elif change_pct > 0.0:
            risk = "Medium Risk"
        else:
            risk = "Low Risk"
            
        return (
            f"**Risk Prediction for {tgt_disease} in {tgt_region}**\n\n"
            f"- **Previous Cases**: {prev_cases}\n"
            f"- **Latest Cases**: {latest_cases}\n"
            f"- **Percentage Change**: {change_pct:+.1f}%\n"
            f"- **Calculated Risk Level**: **{risk}**\n"
            f"- **Vaccination Rate**: {latest_row['vaccination_rate']*100:.1f}%"
        )
    except Exception as e:
        return f"Error predicting risk: {str(e)}"


@mcp.tool()
def generate_health_recommendations(disease: str, risk_level: str) -> str:
    """Generate public health recommendations based on a disease and risk level.
    
    Args:
        disease: Name of the disease (e.g. Dengue, Heat Stroke).
        risk_level: Risk level (e.g. Low Risk, Medium Risk, High Risk).
    """
    cleaned_disease = disease.lower().strip()
    cleaned_risk = risk_level.lower().strip()
    
    recs = []
    if "dengue" in cleaned_disease:
        recs.extend([
            "Conduct mosquito breeding site inspections and eliminate standing water.",
            "Deploy mosquito control measures (larvicides and fogging) in high-risk zones.",
            "Distribute insect repellents and raise community awareness on wearing long sleeves/pants."
        ])
    elif "influenza" in cleaned_disease or "flu" in cleaned_disease:
        recs.extend([
            "Initiate immediate community vaccination drives, focusing on infants and elderly.",
            "Distribute personal hygiene kits (masks, hand sanitizers) to local schools and community centers.",
            "Advise individuals to stay home if showing symptoms and practice respiratory etiquette."
        ])
    elif "heat stroke" in cleaned_disease or "heat" in cleaned_disease:
        recs.extend([
            "Set up public cooling shelters and hydration stations across the region.",
            "Issue high-temperature health alerts advising residents to avoid outdoor activity from 10 AM to 4 PM.",
            "Promote frequent hydration and check-in programs for elderly/isolated residents."
        ])
    elif "diabetes" in cleaned_disease:
        recs.extend([
            "Organize community health screening camps for blood glucose monitoring.",
            "Launch public awareness campaigns focusing on balanced nutrition and regular exercise.",
            "Promote active lifestyle programs and counseling services in community centers."
        ])
    else:
        recs.extend([
            "Promote general hygiene guidelines, handwashing, and routine health checks.",
            "Advise consulting local healthcare facilities if symptoms develop."
        ])
        
    if "high" in cleaned_risk:
        priority = "CRITICAL / IMMEDIATE ACTION REQUIRED"
        recs = [r + " (Priority: Urgent)" for r in recs]
    elif "medium" in cleaned_risk:
        priority = "MODERATE / PREVENTIVE INTERVENTION"
    else:
        priority = "ROUTINE MONITORING"
        
    result = f"**Public Health Recommendations for {disease.title()} ({priority})**\n\n"
    for r in recs:
        result += f"- {r}\n"
    return result


if __name__ == "__main__":
    mcp.run()
