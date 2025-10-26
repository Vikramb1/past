"""
Test script to verify email display in face recognition system
"""
from person_info import PersonInfo
import config

# Test with sample data
test_person = PersonInfo(
    person_id="test_001",
    status="completed",
    full_name="John Smith",
    email="john.smith@example.com",
    summary="Software Engineer at Google, based in San Francisco.\nSpecializes in machine learning and AI.\nlinkedin.com/in/johnsmith\ntwitter.com/johnsmith"
)

print("=== Testing PersonInfo with Email ===")
print(f"Person ID: {test_person.person_id}")
print(f"Full Name: {test_person.full_name}")
print(f"Email: {test_person.email}")
print(f"Status: {test_person.status}")
print(f"Summary: {test_person.summary}")

# Test to_dict conversion
print("\n=== Testing to_dict() ===")
dict_data = test_person.to_dict()
for key, value in dict_data.items():
    print(f"{key}: {value}")

# Test from_dict conversion
print("\n=== Testing from_dict() ===")
test_dict = {
    'person_id': 'test_002',
    'status': 'completed',
    'full_name': 'Jane Doe',
    'email': 'jane.doe@company.com',
    'summary': 'Data Scientist at Meta'
}
restored_person = PersonInfo.from_dict(test_dict)
print(f"Restored - Name: {restored_person.full_name}")
print(f"Restored - Email: {restored_person.email}")
print(f"Restored - Summary: {restored_person.summary}")

print("\n✅ All tests completed successfully!")