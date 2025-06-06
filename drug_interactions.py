import logging
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def get_severity_description(level):
    """
    Get description for severity level
    
    Args:
        level (str): Severity level (Major, Moderate, Minor)
        
    Returns:
        tuple: (description, recommendations)
    """
    if level == "Major":
        return (
            "Major interactions are highly clinically significant. Avoid combinations; the risk of the interaction outweighs the benefit.",
            "Strongly consider changing medication therapy and be alert for severe adverse events."
        )
    elif level == "Moderate":
        return (
            "Moderate interactions have moderate clinical significance. Usually avoid combinations; use only under special circumstances.",
            "Consider therapy modification and monitor closely for adverse effects."
        )
    elif level == "Minor":
        return (
            "Minor interactions have minimal clinical significance. Minimize risk; assess risk and consider alternative medication.",
            "Consider monitoring therapy and observe for any adverse effects."
        )
    else:
        return (
            "Interaction severity is not well documented.",
            "Exercise caution and consult your healthcare provider."
        )

def find_interaction(df, drug1, drug2):
    """
    Find interaction between two drugs in the dataset
    
    Args:
        df (pandas.DataFrame): DataFrame containing drug interaction data
        drug1 (str): Name of first drug
        drug2 (str): Name of second drug
        
    Returns:
        dict: Dictionary containing interaction information
    """
    if df is None:
        logger.error("Drug database is not available")
        return {'error': 'Drug database is not available'}
    
    try:
        # Convert drug names to lowercase for case-insensitive comparison
        drug1_lower = drug1.lower()
        drug2_lower = drug2.lower()
        
        # Check if drugs exist in dataset
        drug1_exists = any(df['Drug_A'].str.lower() == drug1_lower) or any(df['Drug_B'].str.lower() == drug1_lower)
        drug2_exists = any(df['Drug_A'].str.lower() == drug2_lower) or any(df['Drug_B'].str.lower() == drug2_lower)
        
        if not drug1_exists:
            logger.warning(f"Drug '{drug1}' not found in database")
            return {'error': f"Drug '{drug1}' not found in our database"}
        
        if not drug2_exists:
            logger.warning(f"Drug '{drug2}' not found in database")
            return {'error': f"Drug '{drug2}' not found in our database"}
        
        # Search for interaction in both directions (drug1-drug2 and drug2-drug1)
        interaction1 = df[(df['Drug_A'].str.lower() == drug1_lower) & 
                          (df['Drug_B'].str.lower() == drug2_lower)]
        
        interaction2 = df[(df['Drug_A'].str.lower() == drug2_lower) & 
                          (df['Drug_B'].str.lower() == drug1_lower)]
        
        # Combine results
        interaction = pd.concat([interaction1, interaction2])
        
        # If interaction found
        if not interaction.empty:
            # Get the first interaction record
            first_interaction = interaction.iloc[0]
            
            # Get severity level
            severity = first_interaction.get('Level', 'Unknown')
            
            # Get description and recommendations
            severity_description, recommendations = get_severity_description(severity)
            
            result = {
                'drug1': drug1,
                'drug2': drug2,
                'interaction': True,
                'severity': severity,
                'description': severity_description,
                'recommendations': recommendations
            }
            
            logger.info(f"Found {severity} interaction between {drug1} and {drug2}")
            return result
        else:
            # No interaction found
            logger.info(f"No interaction found between {drug1} and {drug2}")
            return {
                'drug1': drug1,
                'drug2': drug2,
                'interaction': False,
                'message': f"No known interactions found between {drug1} and {drug2}."
            }
    
    except Exception as e:
        logger.error(f"Error finding interaction: {str(e)}")
        return {'error': f"An error occurred: {str(e)}"}

def get_severity_level(severity_text):
    """
    Normalize severity level text to a standard format
    
    Args:
        severity_text (str): The severity text from the dataset
        
    Returns:
        str: Normalized severity level (Major, Moderate, Minor, or Unknown)
    """
    if not severity_text or not isinstance(severity_text, str):
        return "Unknown"
    
    severity_lower = severity_text.lower()
    
    if any(term in severity_lower for term in ['major', 'severe', 'contraindicated']):
        return "Major"
    elif any(term in severity_lower for term in ['moderate', 'significant']):
        return "Moderate"
    elif any(term in severity_lower for term in ['minor', 'mild', 'minimal']):
        return "Minor"
    else:
        return "Unknown"