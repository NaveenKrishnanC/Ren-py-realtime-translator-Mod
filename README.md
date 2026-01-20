# Ren-py-realtime-translator-Mod
Detailed Guide: Ren'Py Realtime Translate Mod v0.44.a

This comprehensive guide covers the latest version of the Ren'Py Realtime Translate mod, which allows you to translate visual novels in real-time as you play. The mod supports multiple translation services and features an intelligent caching system for optimal performance.

Version History & Changes

What's New in v0.44.a:

New Features:
Added Free LLM Service option - no API key required for basic translations
Added Auto Service Mode - automatically rotates between Google, Bing, and Free LLM
Enhanced Variable Substitution - better handling of in-game variables like [player_name]
Improved Font System - automatic font group management with fallbacks
Added Opera Aria Support (experimental) - another free translation option
Enhanced Cache Management - more efficient saving and loading
Improved Self-Voicing Translation - TTS text now gets translated
Enhanced Error Handling - better retry logic and fallback mechanisms

Changes from v0.28.d:
Improved thread management and asynchronous processing
Better text redrawing and display management
Enhanced glossary system with automatic reordering
Improved pre-scanning functionality for faster initial translations
Better integration with Ren'Py's text rendering pipeline
IMPORTANT: All configuration now happens in realtimetrans.rpy, not transconfig.rpy

Part 1: Installation & Setup

Step 1: Download Required Files
You will need these files: three .rpy files and one font file.

realtimetrans.rpy - The main engine AND configuration of the mod (contains all settings)
transconfig.rpy - The configuration screen interface only (setting with game, optional)
useragentlist.rpy - A list of web browser identifiers to help avoid API blocks
GoNotoCurrent-Regular.ttf - A versatile font supporting many languages (download from GitHub)

Step 2: Install Files in Your Game
Locate your Ren'Py game directory (the folder containing the game subfolder)
Copy all three .rpy files and the font file into the game folder
Your game folder should now contain these new files alongside your existing scripts

Step 3: Initial Test
Launch your Ren'Py game
Start game, look for a new <<< button in the top-right corner (translation toggle)
Try clicking the <<< button - it should change color (blue = enabled, red = disabled)

Part 2: Configuration

IMPORTANT CHANGE IN v0.44.a:
All configuration settings are now stored in realtimetrans.rpy, NOT transconfig.rpy!

Configuration is the most crucial step. You can configure basic settings in-game through Preferences → Translation Settings, but advanced settings must be edited directly in realtimetrans.rpy.

Basic Settings (Configurable In-Game)

Enable Translation: False → Set to True to activate the mod
Target Language: de → Use ISO 639-1 codes (de=German, es=Spanish, fr=French, etc.)
Translation Service: google → Options: google, bing, LLM, freellm, auto
Time Interval: 1.5 → Seconds between translation requests (lower = faster but more API calls)
Redraw Time: 0.1 → Seconds between screen redraws (affects performance)
Enable RTL: False → Enable for Arabic, Hebrew, Urdu, Persian, etc.
Enable PROXY: False → Enable if you need proxy support

Configuring for Google Translate (Recommended for Beginners)
Select "Google" as your Translation Service
Set your Target Language code
Toggle "Enable Translation" to ON
No additional configuration needed - works out of the box
Best balance of speed, reliability, and quality

Configuring for Free LLM (New in v0.44.a)
Select "freellm" as your Translation Service
Set your Target Language code
Toggle "Enable Translation" to ON
No API key required - completely free
Good quality for most translations
May be slower than Google Translate

Configuring for Auto Mode (New in v0.44.a)
Select "auto" as your Translation Service
The mod will automatically rotate between Google, Bing, and Free LLM
Helps avoid rate limits and service restrictions
Provides backup options if one service fails

Advanced Configuration in realtimetrans.rpy

CRITICAL: You must edit realtimetrans.rpy for advanced settings!


Getting an API Key for LLM Mode
Go to OpenRouter (recommended) or another LLM provider
Create an account and verify your email
Navigate to the API Keys section
Generate a new API key
Copy the key and paste it into the api_keys list in realtimetrans.rpy
Set model name from your llm provider python example , model_name in realtimetrans.rpy
Set endpoint url from your llm provider python example , base_url in realtimetrans.rpy
Save the file and restart your game

Configuration Examples

Example 1: Quick Google Translate Setup
Code:
translation_service = "google"
target_language = "de"  # German
enable_translation = True
# That's it! Google Translate works out of the box
Example 2: Premium LLM Setup
Code:
translation_service = "LLM"
api_keys = ["sk-or-v1-your-key-here", "sk-or-v1-backup-key"]
model_name = "anthropic/claude-3-5-sonnet-20241022:free"
base_url = "https://openrouter.ai/api/v1/chat/completions"
temperature = 0.05
max_tokens = 8000
appended_lines = 15
enable_translation = True

Part 3: How to Use the Mod

Starting Translation
After configuring realtimetrans.rpy, launch your game
Go to Preferences → Translation Settings
Toggle "Enable Translation" to ON (or set it to True in the realtimetrans file)
Start playing your visual novel normally
The mod will begin translating text automatically

Real-time Translation Process
As you progress through dialogue, the mod will:
Detect new, untranslated text in dialogue boxes
Check if the text is already cached
Send uncached text to your selected translation service
Receive the translation and replace text on-screen
Save the translation in translation_cache.json for future use
Handle variables like [player_name] automatically when they become available

The Cache System (Enhanced in v0.44.a)
First encounter: You might notice a slight delay (0.5-3 seconds) as text is translated
Second encounter: Same text loads instantly from local cache
Performance benefit: Subsequent playthroughs are significantly faster
Cache location: translation_cache.json
Cache management: Automatically saved every 30 seconds and on game exit if possible
Cache sharing: You can copy this file between different game installations

Variable Substitution (New in v0.44.a)
The mod now intelligently handles in-game variables:

Example: If the game has text like "Hello, [player_name]!" where player_name = "Alice"
The mod waits until the variable value is available
Processes the text as "Hello, Alice!"
Translates it appropriately
Handles both the original text and any similar patterns automatically

Toggle Display
Click the <<< button in the top-right corner
Blue button = translations are visible (mod is active)
Red button = original text is visible (mod is paused)
Use this to quickly compare translations with originals
Toggling forces a full screen redraw for immediate updates

Part 4: Troubleshooting & Advanced Tips

Common Issues

Text isn't translating at all
Check enable_translation = True in realtimetrans.rpy
Verify the <<< button is BLUE (not red)
Ensure you've set the correct target language code
For LLM mode: Verify your API key in realtimetrans.rpy is valid
Check your internet connection is working
Look for error messages in the log
Try restarting the game after configuration changes

Translations appear slow or game is laggy
Decrease time_interval (try 1.0 or 0.5 seconds) in realtimetrans.rpy
Use Google Translate instead of LLM (much faster)
Increase redraw_time to reduce screen updates
Check your internet connection speed and latency
Disable font size adjustment if not needed

Translation quality is poor ( with LLM)
Try a different model
Increase appended_lines for better context (try 15-20)
Decrease temperature for more literal translations (try 0.01)
Edit the TRANSLATION_PROMPT in realtimetrans.rpy for game-specific terminology
Use Google Translate or add a glossary for technical terms
Increase max_tokens if complex sentences are being cut off

Missing characters appear as squares or boxes
Replace trans_font with a font supporting your target language
Ensure font file is in the game folder
Try fonts from Google Noto Fonts that support your language
Check that your language code is correct
Enable persistent.enable_rtl = True if using Arabic, Hebrew, or other RTL languages

Pro Tips

Pre-scanning for Fastest Experience (New in v0.44.a)
The mod automatically scans ALL game text
This creates a comprehensive cache from the start
Let this process complete (may take minutes depending on game size)
Result: Minimal delays during actual gameplay

Advanced Cache Management
Share caches: Transfer between different games or computers
Manual editing: Open in text editor to fix individual translations
Reset cache: Delete the file to force re-translation of everything

API Key Management
Use multiple keys: .api_keys = ["key1", "key2", "key3"]
The mod automatically rotates through available keys
Helps avoid rate limits on free tiers
Keys are tried in order if one fails
Monitor your API usage on the provider's dashboard

Performance Tuning Guide

For Slow Computers OR Phone:
Edit these values in realtimetrans.rpy:
Code:
time_interval = 2.0  # Less frequent requests
redraw_time = 0.2  # Less frequent redraws
translation_service = "google"  # Fastest service
font_size_adjustment_enabled = False  # Disable font scaling
glossary_enabled = False  # Disable glossary
appended_lines = 5  # Less context

Part 5: Android Installation Guide

Installation Steps
On your Android device, use a file manager with root access (recommended) or access via USB debugging
Navigate to: Android/data/YOUR_GAME_APP/files/
Create a new folder named: game
Copy all mod files (.rpy files and font) to: Android/data/YOUR_GAME_APP/files/game/
Launch the game and verify the <<< button appears
Access translation settings through Preferences menu

Note: Some file managers may require special permissions to access the Android/data folder.

Part 6: Technical Details & Advanced Features

Translation Services Comparison

Google Translate: Fast, reliable, free, good quality. Best for most users.
Bing Translate: Alternative to Google, similar quality, free.
Free LLM: Best quality, completely free, slower.
LLM: Best quality, customizable, requires subscription. Best for quality-focused users.
Opera Aria: Experimental, limited availability, unstable.
Auto Mode: Rotates between services, reliable, helps avoid rate limits.

File Structure & Organization
Code:
game/
├── realtimetrans.rpy           # Main engine AND configuration (edit this file!)
├── transconfig.rpy             # Configuration screen UI only (no config storage now,optional)
├── useragentlist.rpy           # Browser identifiers for API requests
├── GoNotoCurrent-Regular.ttf   # Multi-language font support
├── glossary.json               # Custom terminology (optional, create yourself)
Glossary System (Enhanced in v0.44.a)
Create a glossary.json file in your game folder:
JSON:
{
    "character_name": "Character Name",
    "special_term": "Special Term",
    "game_specific_word": "Translation",
    "mc_name": "Main Character"
}
Then enable it in realtimetrans.rpy:
Code:
glossary_enabled = True
Understanding Persistent Variables
All configuration is stored in persistent variables that maintain their values between game sessions:
Values set in realtimetrans.rpy are defaults
Changes made through the in-game UI override these values
Persistent data is saved automatically and survives game restarts
To reset: delete persistent file or set values to None

By following this comprehensive guide, you should be able to successfully install, configure, and optimize the RealTime Translate mod v0.44.a now.
