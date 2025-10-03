#!/usr/bin/env python3
"""
Simple test script for the unified audio generator - audio generation only.
"""

import sys
import os
import tempfile

# Add the aiv_lib path
sys.path.insert(0, '/Users/admin_user/Documents/workplace/repo/aiv_lib')

# Mock the configuration system to avoid GCP secrets
class MockConfig:
    def __init__(self):
        self.config = {
            "output_folder": "/tmp",
            "use_local_audio_generation": "TRUE",
            "ELEVEN_LABS_API_KEY": None,  # No API key for testing
        }
    
    def get_config_value(self, key):
        return self.config.get(key)

# Replace the config manager
import aiv_lib.util_ConfigManager
mock_config = MockConfig()
aiv_lib.util_ConfigManager.get_config_value = mock_config.get_config_value

# Also mock it in the audio modules
import aiv_lib.audio_generator.audio_generator_local
import aiv_lib.audio_generator.audio_generator_external
import aiv_lib.audio_generator.unified_audio_generator

aiv_lib.audio_generator.audio_generator_external.get_config_value = mock_config.get_config_value
aiv_lib.audio_generator.unified_audio_generator.get_config_value = mock_config.get_config_value

# Now import and test
from aiv_lib.ArtifactQuality import ArtifactQuality
from aiv_lib.audio_generator.unified_audio_generator import (
    generateAudio, 
    generateFemaleAudio,
    generateMaleAudio,
    listAvailableVoices
)

def main():
    print("=== SIMPLE AUDIO GENERATOR TEST ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Test files will be created in: {temp_dir}")
        
        # Test 1: Mock quality
        print("\n1. Testing MOCK quality:")
        try:
            mock_file = os.path.join(temp_dir, "test_mock.wav")
            result = generateAudio(
                mock_file, 
                "Hello, this is a test of mock audio generation.", 
                voice="Alice", 
                quality=ArtifactQuality.MOCK
            )
            print(f"✓ Mock generation successful: {os.path.exists(mock_file)}")
            if os.path.exists(mock_file):
                print(f"  File size: {os.path.getsize(mock_file)} bytes")
        except Exception as e:
            print(f"✗ Mock generation failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 2: LQ quality
        print("\n2. Testing LQ quality:")
        try:
            lq_file = os.path.join(temp_dir, "test_lq.wav")
            result = generateAudio(
                lq_file, 
                "This is a low quality test using edge-tts or mock generation.", 
                voice="Brian", 
                quality=ArtifactQuality.LQ
            )
            print(f"✓ LQ generation successful: {os.path.exists(lq_file)}")
            if os.path.exists(lq_file):
                print(f"  File size: {os.path.getsize(lq_file)} bytes")
        except Exception as e:
            print(f"✗ LQ generation failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 3: Convenience functions
        print("\n3. Testing convenience functions:")
        try:
            female_file = os.path.join(temp_dir, "test_female.wav")
            generateFemaleAudio(female_file, "Female voice test.", ArtifactQuality.MOCK)
            print(f"✓ Female voice generation: {os.path.exists(female_file)}")
            
            male_file = os.path.join(temp_dir, "test_male.wav")
            generateMaleAudio(male_file, "Male voice test.", ArtifactQuality.MOCK)
            print(f"✓ Male voice generation: {os.path.exists(male_file)}")
        except Exception as e:
            print(f"✗ Convenience functions failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 4: List available voices
        print("\n4. Available voices:")
        try:
            listAvailableVoices()
            print("✓ Voice listing successful")
        except Exception as e:
            print(f"✗ Voice listing failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n=== SIMPLE TEST COMPLETED ===")

if __name__ == "__main__":
    main() 