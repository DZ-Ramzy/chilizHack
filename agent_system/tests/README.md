# Sports Quest AI - Test Suite

This directory contains all test files for the Sports Quest AI Backend system.

## Test Files

### Integration Tests
- **`test_complete_integration.py`** - Complete system integration test with SportDevs API
- **`test_agents_system.py`** - AI agent system functionality tests 
- **`test_full_integration.py`** - Full integration test (legacy)

### API Tests
- **`test_working_api.py`** - SportDevs API connectivity test
- **`test_sportdevs.py`** - SportDevs specific functionality test

### Database Tests
- **`test_teams_db.py`** - Database team operations test

### Utility Tests
- **`test_auth_methods.py`** - Authentication methods test
- **`test_matches_structure.py`** - Match data structure validation

## Running Tests

### Run All Integration Tests
```bash
# From project root
python tests/test_complete_integration.py
python tests/test_agents_system.py
```

### Run Specific Test Categories
```bash
# SportDevs API tests
python tests/test_working_api.py
python tests/test_sportdevs.py

# Database tests  
python tests/test_teams_db.py

# Full integration
python tests/test_full_integration.py
```

## Test Results Summary

### Latest Test Results
- **Complete Integration**: 6/7 tests passed (85.7% success)
- **Agent System**: 7/7 tests passed (100% success)
- **SportDevs API**: 100% operational
- **Database Integration**: 5/5 teams synced successfully

### Key Metrics
- SportDevs API connectivity: ✅ 100% functional
- Team synchronization: ✅ 5/5 teams synced  
- Quest generation: ✅ Individual/Clash/Collective quests
- Multilingual support: ✅ FR/EN/ES languages
- Database operations: ✅ All CRUD operations working

## Test Environment

### Requirements
- Python 3.11+
- Valid SPORTDEVS_API_KEY in .env
- SQLite database (auto-created)
- All dependencies from requirements.txt

### Setup
```bash
# Ensure you're in project root
cd /path/to/agent_system

# Run tests
python tests/test_name.py
```

## Notes

- Tests automatically initialize fresh database
- SportDevs API key required for API tests
- All import paths adjusted for tests/ subdirectory
- Tests include comprehensive logging and detailed output