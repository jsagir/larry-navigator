#!/usr/bin/env python3
"""
Metadata Enrichment Service
Builds rich metadata for PWS knowledge base chunks
- Simulates graph relationships as metadata
- Lecture-specific learning objectives
- Framework and tool tagging
- Cross-references between content
"""

from typing import Dict, List, Any, Optional
import re


class MetadataEnricher:
    """
    Enriches chunks with comprehensive metadata

    Simulates Neo4j graph relationships as metadata for File Search:
    - Problem types (relationships → metadata fields)
    - Frameworks mentioned (MENTIONS → list in metadata)
    - Tools introduced (INTRODUCES → list in metadata)
    - Related lectures (RELATED_TO → list in metadata)
    - Prerequisites (REQUIRES → list in metadata)
    """

    # Lecture configurations with complete metadata
    LECTURE_CONFIGS = {
        'N01': {
            'title': 'Framework for Innovation',
            'module': 'introduction',
            'week': 1,
            'difficulty': 'foundational',
            'problem_types': ['all'],
            'frameworks_mentioned': [
                'creative_destruction',
                'innovation_types',
                'entrepreneurship',
                'schumpeter_theory'
            ],
            'tools_introduced': [],
            'related_lectures': ['N02', 'N03', 'N04'],
            'prerequisites': [],
            'learning_objectives': [
                'Understand creative destruction',
                'Define innovation vs invention',
                'Identify entrepreneurial opportunities',
                'Analyze disruption patterns'
            ],
            'cognitive_level': 'understanding',
            'estimated_minutes': 45,
            'has_examples': True,
            'has_definitions': True,
            'has_diagrams': False,
            'keywords': [
                'innovation', 'entrepreneurship', 'creative destruction',
                'schumpeter', 'capitalism', 'disruption'
            ],
            'concepts': [
                'Creative Destruction', 'Innovation', 'Invention',
                'Entrepreneurship', 'Economic Change'
            ]
        },
        'N02': {
            'title': 'Un-defined Problems',
            'module': 'problem_types',
            'week': 2,
            'difficulty': 'foundational',
            'problem_types': ['un-defined'],
            'frameworks_mentioned': [
                'strategic_foresight',
                'scenario_analysis',
                'futures_studies'
            ],
            'tools_introduced': [
                'trending_to_absurd',
                'scenario_analysis',
                'nested_hierarchies',
                'red_teaming',
                'beautiful_questions'
            ],
            'related_lectures': ['N01', 'N03', 'N04'],
            'prerequisites': ['N01'],
            'learning_objectives': [
                'Identify un-defined problems',
                'Apply scenario analysis methodology',
                'Use trending to absurd technique',
                'Develop nested hierarchies',
                'Practice red teaming'
            ],
            'cognitive_level': 'applying',
            'estimated_minutes': 60,
            'has_examples': True,
            'has_diagrams': True,
            'has_definitions': True,
            'keywords': [
                'un-defined', 'scenario analysis', 'future', 'uncertainty',
                'weak signals', 'trends', 'foresight'
            ],
            'concepts': [
                'Un-defined Problems', 'Scenario Analysis',
                'Trending to Absurd', 'Red Teaming',
                'Nested Hierarchies', 'Strategic Foresight'
            ]
        },
        'N03': {
            'title': 'Ill-defined Problems',
            'module': 'problem_types',
            'week': 3,
            'difficulty': 'intermediate',
            'problem_types': ['ill-defined'],
            'frameworks_mentioned': [
                'diffusion_theory',
                'jobs_to_be_done',
                'innovation_diffusion',
                'rogers_adoption_curve'
            ],
            'tools_introduced': [
                'extensive_searching',
                'intensive_searching',
                'trend_analysis',
                'needs_finding'
            ],
            'related_lectures': ['N02', 'N04', 'N05', 'N07'],
            'prerequisites': ['N01', 'N02'],
            'learning_objectives': [
                'Distinguish ill-defined problems',
                'Apply extensive and intensive searching',
                'Identify market opportunities',
                'Use diffusion theory for analysis',
                'Apply jobs-to-be-done framework'
            ],
            'cognitive_level': 'analyzing',
            'estimated_minutes': 60,
            'has_examples': True,
            'has_diagrams': True,
            'has_definitions': True,
            'keywords': [
                'ill-defined', 'searching', 'trends', 'opportunities',
                'needs', 'diffusion', 'adoption', 'market'
            ],
            'concepts': [
                'Ill-defined Problems', 'Extensive Searching',
                'Intensive Searching', 'Diffusion Theory',
                'Jobs-to-be-Done', 'Innovation Adoption'
            ]
        },
        'N04': {
            'title': 'Wicked Problems',
            'module': 'problem_types',
            'week': 4,
            'difficulty': 'advanced',
            'problem_types': ['wicked'],
            'frameworks_mentioned': [
                'wicked_problem_theory',
                'design_thinking',
                'systems_thinking'
            ],
            'tools_introduced': [],
            'related_lectures': ['N02', 'N03', 'N05'],
            'prerequisites': ['N01', 'N02'],
            'learning_objectives': [
                'Define wicked problems',
                'Understand problem complexity',
                'Apply wicked problem frameworks',
                'Recognize wicked problem characteristics'
            ],
            'cognitive_level': 'analyzing',
            'estimated_minutes': 60,
            'has_examples': True,
            'has_diagrams': False,
            'has_definitions': True,
            'keywords': [
                'wicked problems', 'complexity', 'rittel', 'webber',
                'social problems', 'unsolvable', 'systems'
            ],
            'concepts': [
                'Wicked Problems', 'Problem Complexity',
                'Rittel and Webber', 'Social Systems',
                'Problem Formulation'
            ]
        },
        'N05': {
            'title': 'Innovation Domains',
            'module': 'application',
            'week': 5,
            'difficulty': 'intermediate',
            'problem_types': ['all'],
            'frameworks_mentioned': [
                'domain_analysis',
                'sector_analysis'
            ],
            'tools_introduced': [],
            'related_lectures': ['N01', 'N02', 'N03', 'N06'],
            'prerequisites': ['N01', 'N02', 'N03'],
            'learning_objectives': [
                'Apply frameworks to specific domains',
                'Analyze industry-specific challenges',
                'Transfer methodologies across domains',
                'Understand sector dynamics'
            ],
            'cognitive_level': 'applying',
            'estimated_minutes': 60,
            'has_examples': True,
            'has_diagrams': False,
            'keywords': [
                'domains', 'industries', 'application', 'sectors',
                'verticals', 'markets'
            ],
            'concepts': [
                'Innovation Domains', 'Sector Analysis',
                'Domain Transfer', 'Industry Dynamics'
            ]
        },
        'N06': {
            'title': 'Portfolio Management',
            'module': 'strategy',
            'week': 6,
            'difficulty': 'advanced',
            'problem_types': ['all'],
            'frameworks_mentioned': [
                'portfolio_approach',
                'three_box_solution',
                'innovation_portfolio',
                'ambidextrous_organization'
            ],
            'tools_introduced': [
                'portfolio_mapping',
                'resource_allocation'
            ],
            'related_lectures': ['N05', 'N07'],
            'prerequisites': ['N01', 'N02', 'N03'],
            'learning_objectives': [
                'Build innovation portfolios',
                'Balance risk and opportunity',
                'Apply three box solution',
                'Manage organizational ambidexterity'
            ],
            'cognitive_level': 'evaluating',
            'estimated_minutes': 60,
            'has_examples': True,
            'has_diagrams': True,
            'keywords': [
                'portfolio', 'strategy', 'allocation', 'balance',
                'three box', 'govindarajan', 'trimble'
            ],
            'concepts': [
                'Portfolio Management', 'Three Box Solution',
                'Resource Allocation', 'Strategic Balance',
                'Ambidextrous Organization'
            ]
        },
        'N07': {
            'title': 'Well-defined Problems',
            'module': 'problem_types',
            'week': 7,
            'difficulty': 'intermediate',
            'problem_types': ['well-defined'],
            'frameworks_mentioned': [
                'lean_startup',
                'running_lean',
                'customer_development'
            ],
            'tools_introduced': [
                'mvp',
                'validation_board',
                'pirate_metrics',
                'mom_test'
            ],
            'related_lectures': ['N03', 'N06', 'N08'],
            'prerequisites': ['N01', 'N02', 'N03'],
            'learning_objectives': [
                'Identify well-defined problems',
                'Apply lean methodologies',
                'Validate solutions quickly',
                'Build MVPs effectively',
                'Use mom test for validation'
            ],
            'cognitive_level': 'applying',
            'estimated_minutes': 60,
            'has_examples': True,
            'has_diagrams': True,
            'keywords': [
                'well-defined', 'lean', 'validation', 'mvp',
                'execution', 'customer', 'testing'
            ],
            'concepts': [
                'Well-defined Problems', 'Lean Startup',
                'MVP', 'Customer Validation',
                'Mom Test', 'Pirate Metrics'
            ]
        },
        'N08': {
            'title': 'Prior Art & Research',
            'module': 'research',
            'week': 8,
            'difficulty': 'intermediate',
            'problem_types': ['all'],
            'frameworks_mentioned': [
                'literature_review',
                'systematic_review'
            ],
            'tools_introduced': [
                'patent_search',
                'academic_databases',
                'citation_analysis'
            ],
            'related_lectures': ['N07', 'N09'],
            'prerequisites': ['N01'],
            'learning_objectives': [
                'Conduct prior art searches',
                'Review academic literature',
                'Identify existing solutions',
                'Analyze patent landscapes'
            ],
            'cognitive_level': 'analyzing',
            'estimated_minutes': 45,
            'has_examples': True,
            'keywords': [
                'prior art', 'research', 'patents', 'literature',
                'existing solutions', 'search', 'review'
            ],
            'concepts': [
                'Prior Art', 'Literature Review',
                'Patent Search', 'Existing Solutions',
                'Research Methods'
            ]
        },
        'N09': {
            'title': 'Term Report Guidelines',
            'module': 'assessment',
            'week': 9,
            'difficulty': 'intermediate',
            'problem_types': ['all'],
            'frameworks_mentioned': [],
            'tools_introduced': [],
            'related_lectures': ['N01', 'N08'],
            'prerequisites': ['N01', 'N02', 'N03', 'N07'],
            'learning_objectives': [
                'Structure innovation reports',
                'Document methodology',
                'Present findings effectively',
                'Follow academic conventions'
            ],
            'cognitive_level': 'creating',
            'estimated_minutes': 30,
            'has_assignments': True,
            'keywords': [
                'report', 'documentation', 'assignment',
                'deliverable', 'writing', 'presentation'
            ],
            'concepts': [
                'Report Structure', 'Documentation',
                'Methodology', 'Academic Writing'
            ]
        },
        'N10': {
            'title': 'January Term Project',
            'module': 'capstone',
            'week': 10,
            'difficulty': 'advanced',
            'problem_types': ['all'],
            'frameworks_mentioned': [],
            'tools_introduced': [],
            'related_lectures': ['N09'],
            'prerequisites': ['N01', 'N02', 'N03', 'N06', 'N07'],
            'learning_objectives': [
                'Apply complete PWS methodology',
                'Execute capstone project',
                'Demonstrate mastery',
                'Integrate all frameworks'
            ],
            'cognitive_level': 'creating',
            'estimated_minutes': 45,
            'has_assignments': True,
            'keywords': [
                'capstone', 'project', 'integration',
                'application', 'synthesis'
            ],
            'concepts': [
                'Capstone Project', 'Methodology Integration',
                'Problem Solving', 'Application'
            ]
        }
    }

    def enrich_lecture(self, file_name: str, content: str) -> Dict[str, Any]:
        """
        Build rich metadata for lecture chunks

        Args:
            file_name: Lecture filename (e.g., 'N02_UnDefined_Problems')
            content: Lecture content (for keyword extraction)

        Returns:
            Complete metadata dictionary
        """
        # Extract lecture number
        lecture_match = re.match(r'N(\d+)', file_name)
        if not lecture_match:
            return self._get_default_metadata(file_name)

        lecture_num = lecture_match.group(0)  # e.g., 'N02'

        # Get configured metadata
        config = self.LECTURE_CONFIGS.get(lecture_num, {})

        # Extract additional keywords from content
        extracted_keywords = self._extract_keywords(content)

        # Combine configured + extracted keywords
        all_keywords = list(set(
            config.get('keywords', []) + extracted_keywords[:10]
        ))

        # Build complete metadata
        metadata = {
            **config,
            'lecture_id': lecture_num,
            'lecture_number': lecture_num,
            'file_name': file_name,
            'doc_type': 'lecture',
            'keywords': all_keywords,
        }

        return metadata

    def enrich_textbook(self, file_name: str) -> Dict[str, Any]:
        """Build metadata for textbook chunks"""
        if 'PWS_INNOVATION_BOOK' in file_name:
            return {
                'title': 'PWS Innovation Book',
                'file_name': file_name,
                'doc_type': 'textbook',
                'difficulty': 'intermediate',
                'author': 'Lawrence Aronhime',
                'problem_types': ['all'],
                'frameworks_mentioned': [
                    'problem_theory',
                    'pws_methodology',
                    'innovation_frameworks'
                ],
                'has_examples': True,
                'has_definitions': True,
                'keywords': [
                    'innovation', 'problems worth solving',
                    'methodology', 'frameworks', 'textbook'
                ]
            }

        if 'Extended Research' in file_name:
            return {
                'title': 'Extended Research Foundation',
                'file_name': file_name,
                'doc_type': 'textbook',
                'difficulty': 'advanced',
                'problem_types': ['all'],
                'frameworks_mentioned': [
                    'creative_destruction',
                    'innovators_dilemma',
                    'diffusion_theory',
                    'behavioral_economics'
                ],
                'has_examples': True,
                'has_definitions': True,
                'keywords': [
                    'research', 'theory', 'frameworks',
                    'foundations', 'academic', 'literature'
                ]
            }

        return self._get_default_metadata(file_name, 'textbook')

    def enrich_framework(self, framework_name: str) -> Dict[str, Any]:
        """Build metadata for framework documents"""
        frameworks = {
            'creative_destruction': {
                'title': 'Creative Destruction',
                'author': 'Joseph Schumpeter',
                'year': 1942,
                'problem_types': ['un-defined', 'ill-defined'],
                'difficulty': 'intermediate',
                'keywords': [
                    'schumpeter', 'capitalism', 'economic change',
                    'innovation', 'disruption', 'entrepreneurship'
                ]
            },
            'innovators_dilemma': {
                'title': "The Innovator's Dilemma",
                'author': 'Clayton Christensen',
                'year': 1997,
                'problem_types': ['ill-defined'],
                'difficulty': 'intermediate',
                'keywords': [
                    'christensen', 'disruptive innovation',
                    'sustaining innovation', 'business', 'incumbents'
                ]
            },
            'three_box_solution': {
                'title': 'Three Box Solution',
                'author': 'Vijay Govindarajan',
                'year': 2016,
                'problem_types': ['all'],
                'difficulty': 'advanced',
                'keywords': [
                    'govindarajan', 'portfolio', 'box1', 'box2',
                    'box3', 'innovation', 'execution'
                ]
            },
            'jobs_to_be_done': {
                'title': 'Jobs-to-be-Done',
                'author': 'Clayton Christensen',
                'year': 2016,
                'problem_types': ['ill-defined', 'well-defined'],
                'difficulty': 'intermediate',
                'keywords': [
                    'jtbd', 'customer', 'needs', 'hiring',
                    'jobs', 'milkshake', 'progress'
                ]
            }
        }

        return frameworks.get(framework_name, self._get_default_metadata(framework_name, 'framework'))

    def _extract_keywords(self, content: str, top_n: int = 15) -> List[str]:
        """
        Extract keywords from content

        Simple frequency-based extraction
        (Could be enhanced with NLP/TF-IDF)
        """
        # Common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
            'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was',
            'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do',
            'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }

        # Tokenize and clean
        words = re.findall(r'\b[a-z]{4,}\b', content.lower())

        # Filter stop words
        filtered = [w for w in words if w not in stop_words]

        # Count frequency
        frequency = {}
        for word in filtered:
            frequency[word] = frequency.get(word, 0) + 1

        # Sort by frequency
        sorted_words = sorted(frequency.items(), key=lambda x: x[1], reverse=True)

        # Return top N
        return [word for word, _ in sorted_words[:top_n]]

    def _get_default_metadata(
        self,
        file_name: str,
        doc_type: str = 'reference'
    ) -> Dict[str, Any]:
        """Get default metadata for unknown documents"""
        return {
            'title': file_name,
            'file_name': file_name,
            'doc_type': doc_type,
            'difficulty': 'intermediate',
            'problem_types': [],
            'frameworks_mentioned': [],
            'tools_introduced': [],
            'keywords': []
        }
