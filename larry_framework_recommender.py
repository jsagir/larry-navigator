#!/usr/bin/env python3
"""
Larry Framework Recommender
Smart framework suggestions based on conversation context, problem type, and persona
"""

from typing import List, Dict, Tuple

# Framework Database (from 2,988 chunk knowledge base)
FRAMEWORKS = {
    'Design Thinking': {
        'mentions': 1996,
        'problem_types': ['ill-defined', 'well-defined'],
        'personas': ['entrepreneur', 'corporate', 'student', 'consultant'],
        'keywords': ['user', 'empathy', 'prototype', 'ideate', 'customer', 'design'],
        'uncertainty_level': 'medium',
        'risk_level': 'medium',
        'description': 'Human-centered innovation process: Empathize → Define → Ideate → Prototype → Test'
    },
    'Disruptive Innovation': {
        'mentions': 1977,
        'problem_types': ['undefined', 'ill-defined'],
        'personas': ['entrepreneur', 'corporate', 'researcher'],
        'keywords': ['disrupt', 'market', 'clayton christensen', 'incumbent', 'new market'],
        'uncertainty_level': 'high',
        'risk_level': 'high',
        'description': 'Creating new markets by serving overlooked customers with simpler, cheaper solutions'
    },
    'Scenario Analysis': {
        'mentions': 1872,
        'problem_types': ['undefined'],
        'personas': ['corporate', 'researcher', 'consultant'],
        'keywords': ['future', 'scenario', 'trend', 'planning', 'forecast', 'uncertainty'],
        'uncertainty_level': 'very-high',
        'risk_level': 'medium',
        'description': 'Exploring multiple futures to prepare for uncertainty (5-20 year horizon)'
    },
    'Jobs-to-be-Done': {
        'mentions': 1862,
        'problem_types': ['ill-defined', 'well-defined'],
        'personas': ['entrepreneur', 'corporate', 'consultant'],
        'keywords': ['customer', 'need', 'job', 'progress', 'hire', 'milkshake'],
        'uncertainty_level': 'low',
        'risk_level': 'low',
        'description': 'Understanding why customers "hire" products to make progress in their lives'
    },
    'Three Box Solution': {
        'mentions': 1856,
        'problem_types': ['undefined', 'ill-defined'],
        'personas': ['corporate', 'consultant'],
        'keywords': ['portfolio', 'now', 'new', 'next', 'manage', 'innovation'],
        'uncertainty_level': 'medium',
        'risk_level': 'medium',
        'description': 'Manage present (Box 1), selectively forget past (Box 2), create future (Box 3)'
    },
    'Blue Ocean Strategy': {
        'mentions': 850,
        'problem_types': ['ill-defined'],
        'personas': ['entrepreneur', 'corporate'],
        'keywords': ['blue ocean', 'red ocean', 'competition', 'value', 'uncontested'],
        'uncertainty_level': 'high',
        'risk_level': 'high',
        'description': 'Create uncontested market space instead of competing in bloody red oceans'
    },
    'TRIZ': {
        'mentions': 720,
        'problem_types': ['well-defined'],
        'personas': ['corporate', 'researcher', 'consultant'],
        'keywords': ['contradiction', 'technical', 'inventive', 'principles', 'systematic'],
        'uncertainty_level': 'low',
        'risk_level': 'low',
        'description': 'Systematic innovation using 40 inventive principles to resolve contradictions'
    },
    'Value Migration': {
        'mentions': 680,
        'problem_types': ['undefined', 'ill-defined'],
        'personas': ['corporate', 'consultant'],
        'keywords': ['value', 'shift', 'migration', 'business model', 'market'],
        'uncertainty_level': 'high',
        'risk_level': 'medium',
        'description': 'Tracking where economic value flows in industry to anticipate shifts'
    },
    'MECE Trees': {
        'mentions': 620,
        'problem_types': ['well-defined'],
        'personas': ['consultant', 'corporate', 'student'],
        'keywords': ['mece', 'mutually exclusive', 'collectively exhaustive', 'structure', 'breakdown'],
        'uncertainty_level': 'low',
        'risk_level': 'low',
        'description': 'Mutually Exclusive, Collectively Exhaustive problem decomposition'
    },
    '5 Whys': {
        'mentions': 580,
        'problem_types': ['well-defined'],
        'personas': ['entrepreneur', 'corporate', 'student'],
        'keywords': ['root cause', 'why', 'problem', 'diagnosis', 'toyota'],
        'uncertainty_level': 'low',
        'risk_level': 'low',
        'description': 'Root cause analysis by asking "why" five times'
    },
    'Lean Startup': {
        'mentions': 520,
        'problem_types': ['ill-defined', 'well-defined'],
        'personas': ['entrepreneur', 'corporate'],
        'keywords': ['mvp', 'pivot', 'validate', 'build measure learn', 'eric ries'],
        'uncertainty_level': 'medium',
        'risk_level': 'medium',
        'description': 'Build-Measure-Learn cycle to validate assumptions quickly'
    },
    'Customer Development': {
        'mentions': 480,
        'problem_types': ['ill-defined'],
        'personas': ['entrepreneur', 'corporate'],
        'keywords': ['customer discovery', 'validation', 'steve blank', 'get out'],
        'uncertainty_level': 'medium',
        'risk_level': 'low',
        'description': 'Get out of the building to discover and validate customer needs'
    }
}

def calculate_uncertainty_risk(problem_type: str, user_message: str) -> Tuple[str, str, int, int]:
    """
    Calculate uncertainty and risk levels based on problem type and context

    Returns: (uncertainty_level, risk_level, uncertainty_score, risk_score)
    uncertainty_score and risk_score are 0-100
    """

    # Base levels from problem type
    base_mapping = {
        'undefined': ('very-high', 'medium', 85, 60),
        'ill-defined': ('high', 'medium', 65, 55),
        'well-defined': ('low', 'low', 25, 30),
        'general': ('medium', 'medium', 50, 50)
    }

    base = base_mapping.get(problem_type, base_mapping['general'])
    uncertainty_level, risk_level, uncertainty_score, risk_score = base

    # Adjust based on keywords in message
    message_lower = user_message.lower()

    # High uncertainty indicators
    if any(word in message_lower for word in ['future', 'trend', 'unknown', 'uncertain', 'predict']):
        uncertainty_score = min(100, uncertainty_score + 15)

    # High risk indicators
    if any(word in message_lower for word in ['invest', 'bet', 'risk', 'failure', 'expensive']):
        risk_score = min(100, risk_score + 15)

    # Low uncertainty indicators
    if any(word in message_lower for word in ['proven', 'known', 'established', 'clear', 'defined']):
        uncertainty_score = max(0, uncertainty_score - 15)

    # Low risk indicators
    if any(word in message_lower for word in ['safe', 'tested', 'validated', 'low cost', 'prototype']):
        risk_score = max(0, risk_score - 15)

    # Update level labels based on final scores
    if uncertainty_score > 75:
        uncertainty_level = 'very-high'
    elif uncertainty_score > 50:
        uncertainty_level = 'high'
    elif uncertainty_score > 30:
        uncertainty_level = 'medium'
    else:
        uncertainty_level = 'low'

    if risk_score > 70:
        risk_level = 'high'
    elif risk_score > 40:
        risk_level = 'medium'
    else:
        risk_level = 'low'

    return uncertainty_level, risk_level, uncertainty_score, risk_score

def recommend_frameworks(
    problem_type: str,
    persona: str,
    user_message: str,
    max_recommendations: int = 3
) -> List[Dict]:
    """
    Recommend frameworks based on context

    Returns list of recommended frameworks with scores
    """

    message_lower = user_message.lower()
    recommendations = []

    for framework_name, framework_data in FRAMEWORKS.items():
        score = 0

        # Problem type match (40 points)
        if problem_type in framework_data['problem_types']:
            score += 40

        # Persona match (30 points)
        if persona in framework_data['personas']:
            score += 30

        # Keyword match (30 points max, 5 per keyword)
        keyword_matches = sum(1 for keyword in framework_data['keywords'] if keyword in message_lower)
        score += min(30, keyword_matches * 5)

        if score > 0:
            recommendations.append({
                'name': framework_name,
                'score': score,
                'mentions': framework_data['mentions'],
                'description': framework_data['description'],
                'uncertainty_level': framework_data['uncertainty_level'],
                'risk_level': framework_data['risk_level']
            })

    # Sort by score and return top N
    recommendations.sort(key=lambda x: (-x['score'], -x['mentions']))
    return recommendations[:max_recommendations]

def get_framework_notification(recommended_frameworks: List[Dict]) -> str:
    """
    Generate gentle notification about relevant frameworks
    """

    if not recommended_frameworks:
        return ""

    if len(recommended_frameworks) == 1:
        framework = recommended_frameworks[0]
        return f"💡 **Relevant Framework**: {framework['name']} might help here"
    elif len(recommended_frameworks) == 2:
        names = " and ".join([f['name'] for f in recommended_frameworks])
        return f"💡 **Relevant Frameworks**: {names} could be useful"
    else:
        names = ", ".join([f['name'] for f in recommended_frameworks[:2]])
        return f"💡 **Relevant Frameworks**: {names}, and others could apply here"

def get_all_frameworks_sorted() -> List[Dict]:
    """Get all frameworks sorted by mentions for display"""
    frameworks = []
    for name, data in FRAMEWORKS.items():
        frameworks.append({
            'name': name,
            'mentions': data['mentions'],
            'description': data['description']
        })
    frameworks.sort(key=lambda x: -x['mentions'])
    return frameworks
