#!/usr/bin/env python3
"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Demo script for Responsible AI Steganography Detection
"""

import sys
import os
import json
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.services.steganography_service import SteganographyDetectionService


def print_result(title: str, result: Dict[str, Any]):
    """Pretty print detection results"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")
    
    print(f"📊 Suspicious: {'🚨 YES' if result['is_suspicious'] else '✅ NO'}")
    print(f"🎯 Confidence: {result['confidence_score']:.1f}%")
    
    if result['detected_techniques']:
        print(f"🔧 Techniques: {', '.join(result['detected_techniques'])}")
        
        # Show detailed results for detected techniques
        for technique in result['detected_techniques']:
            details = result['details'][technique]
            print(f"\n   📋 {technique.upper()}:")
            print(f"      Confidence: {details['confidence']}%")
            
            if technique == 'zero_width' and details.get('found_characters'):
                print(f"      Found {len(details['found_characters'])} zero-width characters")
                if details.get('binary_pattern'):
                    print(f"      Binary pattern: {details['binary_pattern']}")
            
            elif technique == 'whitespace' and details.get('anomalies'):
                print(f"      Anomalies: {', '.join(details['anomalies'])}")
            
            elif technique == 'unicode' and details.get('exploits'):
                print(f"      Found {len(details['exploits'])} Unicode exploits")
    
    if result['recommendations']:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"   {i}. {rec}")


def main():
    """Run steganography detection demo"""
    print("🛡️  Responsible AI Steganography Detection Demo")
    print("=" * 60)
    
    # Initialize service
    service = SteganographyDetectionService()
    
    # Test cases
    test_cases = [
        {
            'title': 'Clean Text (No Steganography)',
            'text': 'This is a normal text without any hidden content. It should pass all security checks.'
        },
        {
            'title': 'Zero-Width Character Attack',
            'text': 'This text contains\u200Bhidden\u200Bmessage\u200Busing zero-width spaces.'
        },
        {
            'title': 'Multiple Zero-Width Characters',
            'text': 'Complex\u200Bencoding\u200Cwith\u200Dmultiple\u2060types\uFEFFof invisible chars.'
        },
        {
            'title': 'Whitespace Manipulation',
            'text': '''Line with trailing spaces    
Another line with different trailing   
Third line with more trailing      
Fourth line with spaces  '''
        },
        {
            'title': 'Systematic Capitalization Pattern',
            'text': 'The Quick Brown Fox Jumps Over The Lazy Dog Every Morning Surely'
        },
        {
            'title': 'Unicode Homograph Attack',
            'text': 'This text has both latin a and cyrillic а characters mixed together.'
        },
        {
            'title': 'Frequency Anomaly',
            'text': 'aaaabbbbccccddddeeeeffffgggghhhhiiiijjjjkkkkllllmmmmnnnnoooopppp' * 3
        },
        {
            'title': 'Complex Multi-Technique Attack',
            'text': f'''This is а complex test with multiple techniques.\u200B
It has trailing spaces   
And\u200Czero-width\u200Dcharacters\u2060mixed\uFEFFin.
The Alternating Capitalization Might Also Be Suspicious.
Mixed latin аnd cyrillic сharacters.'''
        }
    ]
    
    # Run tests
    for test_case in test_cases:
        try:
            result = service.detect_steganography(test_case['text'])
            print_result(test_case['title'], result)
        except Exception as e:
            print(f"\n❌ Error testing '{test_case['title']}': {str(e)}")
    
    # Performance test
    print(f"\n{'='*60}")
    print("🚀 Performance Test")
    print(f"{'='*60}")
    
    import time
    
    # Test with larger text
    large_text = "This is a performance test sentence. " * 1000  # ~37,000 characters
    
    start_time = time.time()
    result = service.detect_steganography(large_text)
    end_time = time.time()
    
    print(f"📊 Processed {len(large_text):,} characters in {(end_time - start_time)*1000:.2f}ms")
    print(f"🎯 Result: {'Suspicious' if result['is_suspicious'] else 'Clean'}")
    print(f"📈 Confidence: {result['confidence_score']:.1f}%")
    
    # Summary statistics
    print(f"\n{'='*60}")
    print("📈 Demo Summary")
    print(f"{'='*60}")
    
    suspicious_count = sum(1 for case in test_cases if service.detect_steganography(case['text'])['is_suspicious'])
    
    print(f"✅ Tests completed: {len(test_cases)}")
    print(f"🚨 Suspicious texts detected: {suspicious_count}")
    print(f"🛡️  Clean texts: {len(test_cases) - suspicious_count}")
    print(f"🎯 Detection rate: {(suspicious_count / len(test_cases)) * 100:.1f}%")
    
    print(f"\n🔧 Available Detection Techniques:")
    techniques_info = {
        'zero_width': 'Zero-Width Character Detection',
        'whitespace': 'Whitespace Pattern Analysis', 
        'linguistic': 'Linguistic Steganography',
        'frequency': 'Character Frequency Analysis',
        'unicode': 'Unicode Exploitation Detection'
    }
    
    for technique, description in techniques_info.items():
        print(f"   • {technique}: {description}")
    
    print(f"\n💡 For more detailed analysis, check the API documentation!")
    print(f"🌐 API URL: http://localhost:5001/rai/v1/steganography/docs")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        sys.exit(1)
