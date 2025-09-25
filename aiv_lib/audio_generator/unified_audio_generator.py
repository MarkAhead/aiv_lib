import os
from aiv_lib.ArtifactQuality import ArtifactQuality

# Import the specific generators
from aiv_lib.audio_generator.audio_generator_external import generateAudioByPrompt as external_generateAudioByPrompt
from aiv_lib.audio_generator.audio_generator_external import generateSoundEffectsByPrompt as external_generateSoundEffectsByPrompt
# Local generator (Edge-TTS or mock tone)
from aiv_lib.audio_generator.audio_generator_low import generateAudioByPrompt as low_generateAudioByPrompt
from aiv_lib.audio_generator.audio_generator_low import generateSoundEffectsByPrompt as low_generateSoundEffectsByPrompt

def generateAudio(output_file, text, voice="Alice", quality=ArtifactQuality.LQ):
    """
    Generate audio using AI with specified quality level.
    
    Args:
        output_file: Path where the generated audio will be saved
        text: Text to convert to speech
        voice: Voice to use for generation (default: "Alice")
        quality: Audio quality level - ArtifactQuality.LQ, ArtifactQuality.HQ, or ArtifactQuality.MOCK (default: LQ)
    """
    quality = ArtifactQuality.get_quality_level(quality)
    
    print(f"Generating audio with {quality.value} quality using voice '{voice}'")
    
    # Choose the appropriate generator based on quality
    if quality == ArtifactQuality.HQ:
        # High quality uses ElevenLabs
        print("Using ElevenLabs generator (HQ)")
        return external_generateAudioByPrompt(output_file, text, voice, quality)
    else:
        voice = "Christopher"
        # LQ and MOCK go through the low-quality generator (edge-tts / mock)
        print(f"Using low-quality generator for {quality.value} audio")
        return low_generateAudioByPrompt(output_file, text, voice, quality)

def generateSoundEffects(output_file, effect_description, quality=ArtifactQuality.LQ):
    """
    Generate sound effects using AI with specified quality level.
    
    Args:
        output_file: Path where the generated audio file should be saved
        effect_description: Text description of the sound effect (e.g., "door creaking", "rain falling")
        quality: Audio quality level - ArtifactQuality.LQ, ArtifactQuality.HQ, or ArtifactQuality.MOCK (default: LQ)
    """
    quality = ArtifactQuality.get_quality_level(quality)
    
    print(f"Generating sound effect '{effect_description}' with {quality.value} quality")
    
    # Choose the appropriate generator based on quality
    if quality == ArtifactQuality.HQ:
        print("Using ElevenLabs generator for HQ sound effects")
        return external_generateSoundEffectsByPrompt(output_file, effect_description, quality)
    else:
        print(f"Using low-quality generator for {quality.value} sound effects")
        return low_generateSoundEffectsByPrompt(output_file, effect_description, quality)

def listAvailableVoices():
    """List all available voices from both generators."""
    print("=== UNIFIED AUDIO GENERATOR VOICES ===")
    print("\nStandard Voice Aliases:")
    voice_descriptions = {
        "Alice": "Clear and engaging female voice",
        "Brian": "Middle-aged male voice", 
        "Aria": "Professional female voice",
        "Daniel": "Clear male voice",
        "Markus": "Mature male voice",
        "Sally": "Friendly female voice",
        "Bill": "Casual male voice",
        "Callum": "Deep, gravelly male voice",
        "VF": "Dr. Von Fusion character voice",
        "Daksh": "Hindi/Indian accent voice",
    }
    
    for voice, description in voice_descriptions.items():
        print(f"  - {voice}: {description}")
    
    print(f"\nQuality Levels:")
    print("  - LQ: Edge-TTS / mock (audio_generator_low)")
    print("  - HQ: ElevenLabs (premium quality)")
    
    # List voices from low-quality generator
    try:
        print("\n=== LOW-QUALITY GENERATOR (Edge-TTS) ===")
        from aiv_lib.audio_generator.audio_generator_low import listAvailableVoices as listLowVoices
        listLowVoices()
    except Exception as e:
        print(f"Could not list low-quality voices: {e}")

if __name__ == "__main__":
    from aiv_lib.util_ConfigManager import create_output_folder
    # Get output folder for testing
    audio_test_folder = create_output_folder("audio_test")
    
    test_text = "Hello, this is a test of the unified audio generator."
    
    print("=== UNIFIED AUDIO GENERATOR TEST ===")
    
    # # Test different quality levels
    # print("\n1. Testing MOCK quality:")
    # generateAudio(
    #     os.path.join(audio_test_folder, "test_mock.wav"),
    #     test_text,
    #     voice="Christopher",
    #     quality=ArtifactQuality.MOCK
    # )
    
    # print("\n2. Testing LQ quality:")
    # generateAudio(
    #     os.path.join(audio_test_folder, "test_lq.wav"),
    #     test_text,
    #     voice="Brian", 
    #     quality=ArtifactQuality.LQ
    # )
    
    generateSoundEffects(
        os.path.join(audio_test_folder, "test_sound_effect.wav"),
        "Birds chirping in a forest",
        quality=ArtifactQuality.LQ
    )
    
    # # Only test HQ if we have API key configured
    # eleven_labs_key = get_config_value("ELEVEN_LABS_API_KEY")
    # if eleven_labs_key:

    #     print("\n3. Testing HQ quality:")
    #     generateAudio(
    #         os.path.join(audio_test_folder, "test_hq.mp3"),
    #         test_text,
    #         voice="Alice",
    #         quality=ArtifactQuality.HQ
    #     )
    # else:
    #     print("\n3. Skipping HQ test (no ElevenLabs API key configured)")
    
    # # Test sound effects
    # print("\n4. Testing sound effects:")
    # generateSoundEffects(
    #     os.path.join(audio_test_folder, "test_sound_effect.wav"),
    #     "Birds chirping in a forest",
    #     quality=ArtifactQuality.LQ
    # )
    

    
    # # List available voices
    # print("\n7. Available voices:")
    # listAvailableVoices()
    
    print(f"\nAll test files saved to: {audio_test_folder}")
    print(f"Test completed!")
