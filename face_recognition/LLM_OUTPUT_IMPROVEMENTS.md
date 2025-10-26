# LLM Output and Display Improvements

## Changes Made

### 1. LLM Prompt Updates (`person_info.py`)

**Removed:**
- Emoji instructions
- Bullet point formatting
- Verbose output (5-6 bullets)

**Added:**
- Extraction of actual social media URLs from Supabase data
- More concise output instructions (3-4 short lines, max 150 chars)
- Plain text sentences instead of bullet points
- Explicit instruction: "NO EMOJIS. NO BULLET POINTS."

**New Prompt:**
```python
Create a VERY BRIEF summary (max 3-4 short lines) with key information about this person.
Focus on: profession/role, location if available, 1-2 notable facts.
NO EMOJIS. NO BULLET POINTS. Just concise sentences.
Keep total output under 150 characters.
Include actual social media URLs if provided above.
```

**Social Media URL Extraction:**
```python
# Extract social media links from Supabase data
social_links = []
if isinstance(social_media, dict):
    for platform, data in social_media.items():
        if isinstance(data, dict) and 'url' in data:
            social_links.append(f"{platform}: {data['url']}")
        elif isinstance(data, str) and data.startswith('http'):
            social_links.append(f"{platform}: {data}")
```

### 2. Info Box Dimensions (`config.py`)

**Made Narrower:**
- Added `INFO_BOX_MAX_WIDTH = 350` pixels (was unlimited)
- Reduced padding from 8px to 6px on all sides
- Reduced line spacing from 3px to 2px
- Slightly increased title font for better readability (0.45 → 0.5)
- Reduced small font for links (0.3 → 0.28)

**Before:**
- Padding: 8px all around
- Line spacing: 3px
- No max width

**After:**
- Padding: 6px all around
- Line spacing: 2px
- Max width: 350px

### 3. Display Formatting (`info_display.py`)

**Removed Emojis:**
- "🔍 Scraping..." → "Scraping..."
- "❌ Error" → "Error"

**Added Word Wrapping:**
- Lines longer than 45 characters are automatically wrapped
- URLs are kept on single lines (not wrapped)
- URLs displayed in smaller font (INFO_FONT_SCALE_SMALL)

**Smart Font Sizing:**
- Name: Bold, larger font (TITLE)
- Description: Normal font (NORMAL)
- Social links/URLs: Smaller font (SMALL)

**Width Constraint:**
```python
# Apply maximum width constraint
if box_width > config.INFO_BOX_MAX_WIDTH:
    box_width = config.INFO_BOX_MAX_WIDTH
```

## Example Output

### Before:
```
🎯 John Doe
━━━━━━━━━━━━━━━━━━━━

• 💼 Software Engineer at Tech Corp
• 📍 San Francisco, CA
• 🎓 Stanford University alumnus
• 💻 Specializes in AI/ML
• 🌐 Active on Twitter
• 📧 john@example.com
```

### After:
```
John Doe
━━━━━━━━━━━━━━━

Software Engineer at Tech Corp,
San Francisco. Specializes in AI/ML.
Stanford University alumnus.
Twitter: https://twitter.com/johndoe
```

## Benefits

1. **More Professional**: No emojis, cleaner appearance
2. **More Compact**: Narrower box, less screen space
3. **More Useful**: Actual clickable social media URLs (when copied)
4. **Better Readability**: Proper word wrapping, consistent spacing
5. **More Concise**: 150 character limit keeps info brief and scannable

## Configuration

All display settings can be adjusted in `config.py`:
- `INFO_BOX_MAX_WIDTH` - Maximum box width
- `INFO_FONT_SCALE_TITLE` - Name font size
- `INFO_FONT_SCALE_NORMAL` - Description font size
- `INFO_FONT_SCALE_SMALL` - Links font size
- `INFO_LINE_SPACING` - Space between lines
- `INFO_BOX_PADDING_*` - Padding around content

