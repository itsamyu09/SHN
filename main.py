"""
Drug Interaction Checker Web Application
Flask server that provides a web interface for checking drug interactions
"""
import os
from flask import Flask, render_template, request, jsonify
import pandas as pd
import drug_interactions as di
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask("Drug Interaction")
app.secret_key = os.environ.get("SESSION_SECRET", "dev_key")

# Load drug interaction data
try:
    logger.info("Loading drug interaction database...")
    interactions_df = pd.read_csv('attached_assets/Druginteractions.csv')
    unique_drugs = sorted(list(set(interactions_df['Drug_A'].unique()) | set(interactions_df['Drug_B'].unique())))
    example_drugs = ['Paroxetine', 'Tramadol', 'Ibuprofen', 'Aspirin', 'Amoxicillin', 
                    'Metformin', 'Lisinopril', 'Atorvastatin', 'Omeprazole', 'Prednisone']
    logger.info(f"Successfully loaded {len(unique_drugs)} unique drugs")
except Exception as e:
    logger.error(f"Error loading drug data: {str(e)}")
    interactions_df = None
    unique_drugs = []
    example_drugs = []

@app.route('/')
def index():
    """Render the main page with example drugs"""
    return render_template('index.html', example_drugs=example_drugs)

@app.route('/check_interaction', methods=['POST'])
def check_interaction():
    """
    Check for interactions between two drugs
    Expects form data with 'drug1' and 'drug2' fields
    """
    try:
        drug1 = request.form.get('drug1', '').strip()
        drug2 = request.form.get('drug2', '').strip()

        if not drug1 or not drug2:
            return jsonify({'error': 'Please enter both drugs'})

        if interactions_df is None:
            return jsonify({'error': 'Drug database is not available'})

        logger.debug(f"Checking interaction between {drug1} and {drug2}")
        interaction = di.find_interaction(interactions_df, drug1, drug2)
        return jsonify(interaction)

    except Exception as e:
        logger.error(f"Error checking interaction: {str(e)}")
        return jsonify({'error': 'An error occurred while checking drug interaction'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
