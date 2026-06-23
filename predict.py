import cv2
import numpy as np
from PIL import Image
import os

def analyze_image(image_path):
    """
    Analyze image using OpenCV and Pillow to detect potential AI-generated characteristics
    """
    results = {
        'is_ai_generated': False,
        'confidence': 0,
        'analysis_details': [],
        'error': None
    }
    
    try:
        # Open image with PIL
        pil_image = Image.open(image_path)
        
        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert PIL image to OpenCV format
        open_cv_image = np.array(pil_image)
        open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
        
        # Analysis 1: Check image metadata
        metadata_analysis = analyze_metadata(pil_image)
        results['analysis_details'].append(metadata_analysis)
        
        # Analysis 2: Check for noise patterns
        noise_analysis = analyze_noise_pattern(open_cv_image)
        results['analysis_details'].append(noise_analysis)
        
        # Analysis 3: Check color distribution
        color_analysis = analyze_color_distribution(open_cv_image)
        results['analysis_details'].append(color_analysis)
        
        # Analysis 4: Check for artifacts
        artifact_analysis = analyze_artifacts(open_cv_image)
        results['analysis_details'].append(artifact_analysis)
        
        # Calculate overall confidence
        confidence_score = calculate_confidence(results['analysis_details'])
        results['confidence'] = confidence_score
        results['is_ai_generated'] = confidence_score > 60
        
    except Exception as e:
        results['error'] = str(e)
    
    return results

def analyze_metadata(pil_image):
    """Analyze image metadata for AI generation clues"""
    analysis = {
        'test_name': 'Metadata Analysis',
        'score': 0,
        'details': []
    }
    
    try:
        # Check if image has metadata
        if pil_image.info:
            analysis['details'].append("Image contains metadata")
            
            # Check for common AI generator tags
            ai_indicators = ['AI', 'Generated', 'Stable Diffusion', 'DALL-E', 'Midjourney']
            info_str = str(pil_image.info).lower()
            
            for indicator in ai_indicators:
                if indicator.lower() in info_str:
                    analysis['score'] += 30
                    analysis['details'].append(f"Found AI indicator: {indicator}")
        else:
            analysis['details'].append("No metadata found - could indicate AI generation")
            analysis['score'] += 20
            
    except Exception as e:
        analysis['details'].append(f"Error in metadata analysis: {str(e)}")
    
    return analysis

def analyze_noise_pattern(image):
    """Analyze noise patterns in the image"""
    analysis = {
        'test_name': 'Noise Pattern Analysis',
        'score': 0,
        'details': []
    }
    
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate noise level using Laplacian
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        noise_level = np.var(laplacian)
        
        analysis['details'].append(f"Noise variance: {noise_level:.2f}")
        
        # AI-generated images often have different noise patterns
        if noise_level < 100:
            analysis['score'] += 15
            analysis['details'].append("Low noise level - possible AI generation")
        elif noise_level > 500:
            analysis['score'] += 5
            analysis['details'].append("High noise level - more likely natural")
        else:
            analysis['score'] += 10
            analysis['details'].append("Moderate noise level")
            
    except Exception as e:
        analysis['details'].append(f"Error in noise analysis: {str(e)}")
    
    return analysis

def analyze_color_distribution(image):
    """Analyze color distribution patterns"""
    analysis = {
        'test_name': 'Color Distribution Analysis',
        'score': 0,
        'details': []
    }
    
    try:
        # Calculate color histogram
        color_means = []
        for i in range(3):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            color_means.append(np.mean(hist))
        
        # Check color distribution uniformity
        color_variation = np.std(color_means)
        analysis['details'].append(f"Color variation: {color_variation:.2f}")
        
        # AI images often have unusual color distributions
        if color_variation < 100:
            analysis['score'] += 15
            analysis['details'].append("Unusual color distribution detected")
        else:
            analysis['score'] += 5
            analysis['details'].append("Natural color distribution")
            
    except Exception as e:
        analysis['details'].append(f"Error in color analysis: {str(e)}")
    
    return analysis

def analyze_artifacts(image):
    """Check for common AI generation artifacts"""
    analysis = {
        'test_name': 'Artifact Detection',
        'score': 0,
        'details': []
    }
    
    try:
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect edges
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        analysis['details'].append(f"Edge density: {edge_density:.4f}")
        
        # Check for unnatural smoothness or patterns
        if edge_density < 0.05:
            analysis['score'] += 20
            analysis['details'].append("Very smooth - possible AI generation")
        elif edge_density > 0.2:
            analysis['score'] += 5
            analysis['details'].append("High detail - more likely natural")
        else:
            analysis['score'] += 10
            analysis['details'].append("Normal detail level")
            
    except Exception as e:
        analysis['details'].append(f"Error in artifact analysis: {str(e)}")
    
    return analysis

def calculate_confidence(analysis_details):
    """Calculate overall confidence score"""
    if not analysis_details:
        return 0
    
    total_score = sum(detail.get('score', 0) for detail in analysis_details)
    max_possible_score = 80  # 20 points max per test * 4 tests
    
    confidence = (total_score / max_possible_score) * 100
    return min(round(confidence, 1), 99)  # Cap at 99%