"""
Chat module for symptom checker functionality
Provides the backend logic for the symptom checker
"""
import os
import random
import json
import torch
import numpy as np
import logging
from torch.utils.data import Dataset, DataLoader

logger = logging.getLogger(__name__)

# Load intents data from JSON file
try:
    with open('attached_assets/intents.json', 'r') as f:
        intents_data = json.load(f)
        intents = intents_data['intents']
        logger.info(f"Successfully loaded {len(intents)} intents")
except Exception as e:
    logger.error(f"Error loading intents data: {str(e)}")
    intents = []

# Load hospitals data
try:
    with open('attached_assets/hospitals.json', 'r') as f:
        hospitals_data = json.load(f)
        hospitals = hospitals_data
        logger.info(f"Successfully loaded {len(hospitals)} hospitals")
except Exception as e:
    logger.error(f"Error loading hospitals data: {str(e)}")
    hospitals = []

def find_nearby_hospitals(user_location=None, limit=3):
    """
    Find hospitals near the user's location
    If no location provided, returns random hospitals
    
    Args:
        user_location (tuple): (latitude, longitude)
        limit (int): Number of hospitals to return
        
    Returns:
        list: List of hospitals
    """
    if not hospitals:
        return []
    
    # For now, we'll just return random hospitals since we don't have user location
    selected_hospitals = random.sample(hospitals, min(limit, len(hospitals)))
    return selected_hospitals

def find_intent_by_symptoms(symptoms_text):
    """
    Match user symptoms text to an intent
    
    Args:
        symptoms_text (str): Text describing symptoms
        
    Returns:
        dict: Matching intent or None
    """
    if not intents:
        return None
    
    symptoms_lower = symptoms_text.lower()
    
    # First check for emergency keywords
    emergency_keywords = [
        'chest pain', 'heart attack', 'stroke', 'breathing', 'breath',
        'unconscious', 'passed out', 'seizure', 'severe bleeding', 
        'suicide', 'kill myself', 'emergency'
    ]
    
    for keyword in emergency_keywords:
        if keyword in symptoms_lower:
            # Find emergency intent
            for intent in intents:
                if intent.get('tag') == 'emergency':
                    return intent
    
    # Check for exact matches in patterns
    for intent in intents:
        if 'patterns' in intent:
            for pattern in intent['patterns']:
                pattern_terms = [term.strip().lower() for term in pattern.split(',')]
                
                # Count matching terms
                match_count = sum(1 for term in pattern_terms if term in symptoms_lower)
                
                # If most terms match, return this intent
                if match_count >= len(pattern_terms) * 0.6:  # 60% match threshold
                    return intent
    
    # Check for keyword matches in intents
    best_match = None
    best_score = 0
    
    for intent in intents:
        if 'tag' in intent and intent['tag'] not in ['greeting', 'goodbye', 'who']:
            # Simple keyword matching
            tag_lower = intent['tag'].lower()
            score = 0
            
            # Check if the tag appears in the symptoms
            if tag_lower in symptoms_lower:
                score += 3
                
            # Check if any pattern keywords match
            if 'patterns' in intent:
                for pattern in intent['patterns']:
                    pattern_terms = [term.strip().lower() for term in pattern.split(',')]
                    for term in pattern_terms:
                        if term in symptoms_lower:
                            score += 1
            
            if score > best_score:
                best_score = score
                best_match = intent
    
    # Return the best match if score is reasonable
    if best_score >= 2:
        return best_match
        
    # Return a general intent if no good match found
    for intent in intents:
        if intent.get('tag') == 'symptoms':
            return intent
            
    return None

def get_response(msg):
    """
    Generate a response for the symptom checker
    
    Args:
        msg (str): User's message/symptom description
        
    Returns:
        str: Generated response
    """
    try:
        if not msg.strip():
            return "Please describe your symptoms so I can help you better."
        
        # Check for greetings
        greeting_words = ['hi', 'hello', 'hey', 'greetings', 'good day']
        if any(word == msg.lower().strip() for word in greeting_words):
            greeting_responses = [
                "Hello! How can I help you with your health concerns today?",
                "Hi there! Please describe your symptoms, and I'll do my best to assist you.",
                "Welcome to the symptom checker! What symptoms are you experiencing?"
            ]
            return random.choice(greeting_responses)
        
        # Check for emergency keywords first
        emergency_keywords = [
            'chest pain', 'heart attack', 'stroke', 'breathing', 'breath',
            'unconscious', 'passed out', 'seizure', 'severe bleeding', 
            'suicide', 'kill myself', 'emergency'
        ]
        
        msg_lower = msg.lower()
        for keyword in emergency_keywords:
            if keyword in msg_lower:
                emergency_response = (
                    "<div class='alert alert-danger'><strong>EMERGENCY DETECTED</strong>: "
                    "The symptoms you've described could indicate a serious medical emergency. "
                    "Please seek immediate medical attention by calling emergency services "
                    "or going to the nearest emergency room.</div>"
                    "<p>Do not wait to see if symptoms improve on their own.</p>"
                )
                
                # Add nearby hospitals if available
                nearby_hospitals = find_nearby_hospitals(limit=3)
                if nearby_hospitals:
                    emergency_response += "<div class='mt-3'><h5>Nearby Medical Facilities:</h5><ul>"
                    for hospital in nearby_hospitals:
                        emergency_response += f"<li><strong>{hospital['Name of the hospital '].strip()}</strong><br>{hospital.get('Address', 'No address available')}<br>Phone: {hospital.get('Contact Number', 'N/A')}</li>"
                    emergency_response += "</ul></div>"
                
                return emergency_response
        
        # Try to match intent
        matched_intent = find_intent_by_symptoms(msg)
        
        if matched_intent:
            # Get response from matched intent
            if isinstance(matched_intent.get('responses'), list):
                response_text = random.choice(matched_intent['responses'])
            else:
                response_text = matched_intent.get('responses', "")
            
            # Format response with precautions if available
            formatted_response = f"<h5>{matched_intent.get('tag', 'Health Analysis')}</h5><p>{response_text}</p>"
            
            if 'Precaution' in matched_intent:
                if isinstance(matched_intent['Precaution'], list):
                    precaution_text = "<ul>" + "".join([f"<li>{p}</li>" for p in matched_intent['Precaution']]) + "</ul>"
                else:
                    precaution_text = matched_intent['Precaution']
                
                formatted_response += f"<div class='alert alert-info mt-3'><h6>Precautions:</h6>{precaution_text}</div>"
            
            # Add nearby hospitals if it's a more serious condition
            if matched_intent.get('tag') not in ['greeting', 'goodbye', 'who', 'Common Cold', 'Allergies']:
                nearby_hospitals = find_nearby_hospitals(limit=3)
                if nearby_hospitals:
                    formatted_response += "<div class='mt-3'><h6>Medical Facilities Near You:</h6><ul>"
                    for hospital in nearby_hospitals:
                        formatted_response += f"<li><strong>{hospital['Name of the hospital '].strip()}</strong><br>{hospital.get('Address', 'No address available')}<br>Phone: {hospital.get('Contact Number', 'N/A')}</li>"
                    formatted_response += "</ul></div>"
            
            return formatted_response
        
        # Default responses if no intent matched
        general_responses = [
            "Based on the symptoms you've described, I recommend monitoring your condition and consulting a healthcare provider if symptoms persist or worsen.",
            "Thank you for sharing your symptoms. For a more accurate assessment, please provide more details about your symptoms including duration and severity.",
            "It's important to consult with a healthcare professional for an accurate diagnosis. The information I provide is not a substitute for professional medical advice."
        ]
        
        response = random.choice(general_responses) + "\n\n"
        response += "Please provide more specific details about your symptoms, including:\n"
        response += "- When they started\n"
        response += "- Severity (mild, moderate, severe)\n"
        response += "- Any other symptoms you're experiencing\n"
        response += "- Any medications you're currently taking"
        
        return response
    
    except Exception as e:
        logger.error(f"Error in get_response: {str(e)}")
        return "I'm sorry, but I encountered an error while processing your symptoms. Please try describing them again or consult with a healthcare professional directly."
