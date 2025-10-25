"""
Person information API module.
Handles fetching person details via API (currently using dummy responses).
"""
import time
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import config


@dataclass
class EmploymentEntry:
    """Employment history entry."""
    role: str
    company: str
    years: str


@dataclass
class PersonInfo:
    """Person information data class."""
    person_id: str
    name: str
    email: str
    phone: str
    employment_history: List[EmploymentEntry] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'person_id': self.person_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'employment_history': [
                {'role': e.role, 'company': e.company, 'years': e.years}
                for e in self.employment_history
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PersonInfo':
        """Create PersonInfo from dictionary."""
        employment = [
            EmploymentEntry(**e) for e in data.get('employment_history', [])
        ]
        return cls(
            person_id=data['person_id'],
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            employment_history=employment
        )


class PersonInfoAPI:
    """API client for fetching person information."""
    
    # Dummy data for generating responses
    FIRST_NAMES = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer",
        "Michael", "Linda", "William", "Elizabeth", "David", "Barbara",
        "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah"
    ]
    
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
        "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
        "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson"
    ]
    
    JOB_ROLES = [
        "Senior Engineer", "Software Developer", "Data Scientist",
        "Product Manager", "Engineering Manager", "Tech Lead",
        "DevOps Engineer", "Security Analyst", "UX Designer",
        "Solutions Architect", "Backend Developer", "Frontend Developer"
    ]
    
    COMPANIES = [
        "Tech Corp", "Innovation Labs", "Digital Solutions",
        "Cloud Systems", "Data Dynamics", "Smart Analytics",
        "Future Tech", "Quantum Computing Inc", "AI Ventures",
        "Startup XYZ", "Global Software", "Enterprise Solutions"
    ]
    
    def __init__(self):
        """Initialize the API client."""
        self._cache: Dict[str, PersonInfo] = {}
        # Seed random for consistent dummy data per person_id
        self._person_seeds: Dict[str, int] = {}
    
    def get_person_info(
        self,
        person_id: str,
        image_path: Optional[str] = None
    ) -> Optional[PersonInfo]:
        """
        Get person information (currently returns dummy data).
        
        Args:
            person_id: Unique person identifier
            image_path: Path to person's image (for future real API)
        
        Returns:
            PersonInfo object or None if failed
        """
        # Check cache first
        if person_id in self._cache:
            return self._cache[person_id]
        
        # Simulate API delay
        if config.API_CALL_DELAY > 0:
            time.sleep(config.API_CALL_DELAY)
        
        # Generate dummy response
        info = self._generate_dummy_info(person_id)
        
        # Cache the response
        self._cache[person_id] = info
        
        return info
    
    def _generate_dummy_info(self, person_id: str) -> PersonInfo:
        """
        Generate dummy person information.
        
        Args:
            person_id: Person identifier for consistent generation
        
        Returns:
            PersonInfo with dummy data
        """
        # Get or create seed for this person
        if person_id not in self._person_seeds:
            # Use hash of person_id for consistent randomization
            self._person_seeds[person_id] = hash(person_id) % 10000
        
        seed = self._person_seeds[person_id]
        rng = random.Random(seed)
        
        # Generate name
        first_name = rng.choice(self.FIRST_NAMES)
        last_name = rng.choice(self.LAST_NAMES)
        name = f"{first_name} {last_name}"
        
        # Generate email
        email = f"{first_name.lower()}.{last_name.lower()}@company.com"
        
        # Generate phone
        area_code = rng.randint(200, 999)
        prefix = rng.randint(200, 999)
        line = rng.randint(1000, 9999)
        phone = f"+1 ({area_code}) {prefix}-{line}"
        
        # Generate employment history (1-3 entries)
        num_jobs = rng.randint(1, 3)
        employment = []
        
        current_year = 2025
        years_back = 0
        
        for i in range(num_jobs):
            role = rng.choice(self.JOB_ROLES)
            company = rng.choice(self.COMPANIES)
            
            if i == 0:
                # Current job
                start_year = current_year - rng.randint(1, 5)
                years = f"{start_year}-Present"
            else:
                # Previous jobs
                duration = rng.randint(1, 4)
                end_year = current_year - years_back - 1
                start_year = end_year - duration
                years = f"{start_year}-{end_year}"
                years_back += duration + 1
            
            employment.append(EmploymentEntry(
                role=role,
                company=company,
                years=years
            ))
        
        return PersonInfo(
            person_id=person_id,
            name=name,
            email=email,
            phone=phone,
            employment_history=employment
        )
    
    def clear_cache(self) -> None:
        """Clear the cached responses."""
        self._cache.clear()
    
    def get_cached_info(self, person_id: str) -> Optional[PersonInfo]:
        """
        Get cached person info without making API call.
        
        Args:
            person_id: Person identifier
        
        Returns:
            Cached PersonInfo or None
        """
        return self._cache.get(person_id)


# Global API instance
_api_instance = None


def get_api_instance() -> PersonInfoAPI:
    """Get global PersonInfoAPI instance."""
    global _api_instance
    if _api_instance is None:
        _api_instance = PersonInfoAPI()
    return _api_instance

