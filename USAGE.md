# Usage Guide for Past Project

## Face Recognition System

The face recognition system is located in the `face_recognition/` directory and can be used standalone or as part of the larger project.

### Standalone Usage

```bash
cd face_recognition
pip install -r requirements.txt
python main.py
```

### As a Python Package

You can also import and use the face recognition components in your own Python code:

```python
# Add face_recognition to your Python path or install it
import sys
sys.path.append('path/to/past')

from face_recognition import config, face_engine, face_database

# Initialize components
db = face_database.FaceDatabase()
engine = face_engine.FaceEngine(db)

# Use in your code
# ... your implementation here
```

### Quick Commands

```bash
# Run face recognition system
cd face_recognition && python main.py

# Add a person to database
cd face_recognition && python add_person.py "John Doe" photo.jpg

# Test setup
cd face_recognition && python test_setup.py
```

### For More Information

See `face_recognition/README.md` for complete documentation.
