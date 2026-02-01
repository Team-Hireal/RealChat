"""
RealChat Module Testing Suite

Tests all newly created modules:
- Agent Manager
- Privacy Controller
- Message Analyzer
- Moments Browser
- Relationship Analyzer
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test results
test_results = {
    'passed': [],
    'failed': [],
    'total': 0
}

def test_result(test_name, passed, error=None):
    """Record test result"""
    test_results['total'] += 1
    if passed:
        test_results['passed'].append(test_name)
        print(f"✓ {test_name}")
    else:
        test_results['failed'].append({'test': test_name, 'error': str(error)})
        print(f"✗ {test_name}: {error}")

print("=" * 60)
print("RealChat Module Testing Suite")
print("=" * 60)

# Test 1: Agent Manager
print("\n[1] Testing Agent Manager...")
try:
    from modules.agent_manager import AgentManager, AgentType, AgentState, agent_manager

    # Test singleton
    manager1 = AgentManager()
    manager2 = AgentManager()
    assert manager1 is manager2, "Singleton pattern failed"
    test_result("Agent Manager: Singleton pattern", True)

    # Test agent activation
    agent_manager.activate_agent(AgentType.MESSAGE_ANALYZER)
    assert agent_manager.get_active_agent() == AgentType.MESSAGE_ANALYZER
    test_result("Agent Manager: Activate agent", True)

    # Test mutual exclusion
    try:
        agent_manager.activate_agent(AgentType.MOMENTS_BROWSER, force=False)
        test_result("Agent Manager: Mutual exclusion", False, "Should have raised error")
    except Exception:
        test_result("Agent Manager: Mutual exclusion", True)

    # Test deactivation
    agent_manager.deactivate_agent(AgentType.MESSAGE_ANALYZER)
    assert agent_manager.get_active_agent() is None
    test_result("Agent Manager: Deactivate agent", True)

except Exception as e:
    test_result("Agent Manager: Module import/basic tests", False, e)

# Test 2: Privacy Controller
print("\n[2] Testing Privacy Controller...")
try:
    from modules.privacy_controller import PrivacyController, PrivacyFeature, AuthorizationLevel, privacy_controller

    # Test authorization request
    privacy_controller.request_authorization(
        PrivacyFeature.READ_MESSAGES,
        AuthorizationLevel.AUTHORIZED
    )
    test_result("Privacy Controller: Request authorization", True)

    # Test authorization check
    is_authorized = privacy_controller.check_authorization(PrivacyFeature.READ_MESSAGES)
    assert is_authorized == True
    test_result("Privacy Controller: Check authorization", True)

    # Test contact-specific authorization
    privacy_controller.request_authorization(
        PrivacyFeature.BROWSE_MOMENTS,
        AuthorizationLevel.AUTHORIZED_WITH_CONTACTS,
        contacts=['test_contact_1', 'test_contact_2']
    )
    assert privacy_controller.check_authorization(PrivacyFeature.BROWSE_MOMENTS, 'test_contact_1')
    assert not privacy_controller.check_authorization(PrivacyFeature.BROWSE_MOMENTS, 'test_contact_3')
    test_result("Privacy Controller: Contact-specific authorization", True)

    # Test revocation
    privacy_controller.revoke_authorization(PrivacyFeature.READ_MESSAGES)
    assert not privacy_controller.check_authorization(PrivacyFeature.READ_MESSAGES)
    test_result("Privacy Controller: Revoke authorization", True)

except Exception as e:
    test_result("Privacy Controller: Module tests", False, e)

# Test 3: Storage System Updates
print("\n[3] Testing Storage System Updates...")
try:
    from core.storage import UnifiedStorage

    storage = UnifiedStorage()

    # Test agent state storage
    storage.save_agent_state('test_agent', {'status': 'active', 'timestamp': datetime.now().isoformat()})
    loaded_state = storage.load_agent_state('test_agent')
    assert loaded_state['status'] == 'active'
    test_result("Storage: Agent state save/load", True)

    # Test message importance storage
    storage.save_message_importance('contact_1', 'msg_1', 8.5, {'category': 'high'})
    importance = storage.load_message_importance('contact_1', 'msg_1')
    assert importance['score'] == 8.5
    test_result("Storage: Message importance save/load", True)

    # Test pinned messages
    storage.save_pinned_message('contact_1', 'msg_1', {'content': 'Test message'})
    pinned = storage.load_pinned_messages()
    assert len(pinned) > 0
    test_result("Storage: Pinned messages save/load", True)

    # Test relationship analysis storage
    storage.save_relationship_analysis('contact_1', {
        'category': 'professional',
        'confidence': 0.85,
        'reasoning': 'Test analysis'
    })
    analysis = storage.load_relationship_analysis('contact_1')
    assert analysis['category'] == 'professional'
    test_result("Storage: Relationship analysis save/load", True)

except Exception as e:
    test_result("Storage System: Updates", False, e)

# Test 4: Message Analyzer
print("\n[4] Testing Message Analyzer...")
try:
    from modules.message_analyzer import MessageAnalyzer, message_analyzer

    # Re-authorize for testing
    privacy_controller.request_authorization(
        PrivacyFeature.READ_MESSAGES,
        AuthorizationLevel.AUTHORIZED
    )
    privacy_controller.request_authorization(
        PrivacyFeature.PIN_MESSAGES,
        AuthorizationLevel.AUTHORIZED
    )

    # Test message scoring
    test_message = {
        'content': 'URGENT: Please call me ASAP regarding the important meeting today at 3pm',
        'unread': True
    }
    test_contact = {
        'id': 'contact_1',
        'category': 'professional'
    }

    analysis = message_analyzer.analyze_importance(test_message, test_contact)
    assert analysis['authorized'] == True
    assert analysis['score'] > 7.0  # Should be high priority
    test_result("Message Analyzer: Importance scoring", True)

    # Test should_pin logic
    assert analysis['should_pin'] == True
    test_result("Message Analyzer: Pin recommendation", True)

    # Test batch analysis
    messages = [
        {'id': 'msg_1', 'content': 'Hi', 'contact_id': 'contact_1'},
        {'id': 'msg_2', 'content': 'URGENT: Need help!', 'contact_id': 'contact_1'}
    ]
    contacts = {'contact_1': test_contact}
    batch_results = message_analyzer.analyze_batch(messages, contacts)
    assert len(batch_results) == 2
    assert batch_results[0]['score'] > batch_results[1]['score']  # Sorted by score
    test_result("Message Analyzer: Batch analysis", True)

except Exception as e:
    test_result("Message Analyzer: Module tests", False, e)

# Test 5: Moments Browser
print("\n[5] Testing Moments Browser...")
try:
    from modules.moments_browser import MomentsBrowser, moments_browser

    # Test moment content analysis
    test_moment = {
        'content': 'Great meeting with the team today! Working on an exciting new project.',
        'images': ['img1.jpg'],
        'likes': 10,
        'comments': 3
    }

    analysis = moments_browser.analyze_moment_content(test_moment)
    assert 'content_type' in analysis
    assert 'topics' in analysis
    assert 'work' in analysis['topics']  # Should detect work-related content
    test_result("Moments Browser: Content analysis", True)

    # Test contact categorization from moments
    test_moments = [
        {'content': 'Office meeting today', 'images': []},
        {'content': 'Working on project deadline', 'images': []},
        {'content': 'Business conference', 'images': []}
    ]

    categorization = moments_browser.categorize_contact_from_moments('contact_1', test_moments)
    assert categorization['category'] == 'professional'
    test_result("Moments Browser: Contact categorization", True)

except Exception as e:
    test_result("Moments Browser: Module tests", False, e)

# Test 6: Relationship Analyzer
print("\n[6] Testing Relationship Analyzer...")
try:
    from modules.relationship_analyzer import RelationshipAnalyzer, relationship_analyzer

    # Test interaction stats calculation
    test_chat_history = [
        {'timestamp': '2026-01-25T10:00:00', 'content': 'Hello'},
        {'timestamp': '2026-01-26T11:00:00', 'content': 'How are you?'},
        {'timestamp': '2026-01-27T12:00:00', 'content': 'Great!'}
    ]

    stats = relationship_analyzer._calculate_interaction_stats(test_chat_history)
    assert stats['total_messages'] == 3
    assert stats['frequency'] > 0
    test_result("Relationship Analyzer: Interaction stats", True)

    # Test prompt building
    contact_data = {
        'name': 'Test Contact',
        'chat_history': test_chat_history,
        'moments': [],
        'interaction_stats': stats,
        'contact_info': {}
    }

    prompt = relationship_analyzer._build_classification_prompt(contact_data)
    assert 'Test Contact' in prompt
    assert 'professional' in prompt
    test_result("Relationship Analyzer: Prompt building", True)

except Exception as e:
    test_result("Relationship Analyzer: Module tests", False, e)

# Print summary
print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)
print(f"Total tests: {test_results['total']}")
print(f"Passed: {len(test_results['passed'])} ✓")
print(f"Failed: {len(test_results['failed'])} ✗")

if test_results['failed']:
    print("\nFailed tests:")
    for failure in test_results['failed']:
        print(f"  - {failure['test']}: {failure['error']}")

print("\n" + "=" * 60)

# Save results to file
results_file = 'test_results.json'
with open(results_file, 'w') as f:
    json.dump(test_results, f, indent=2)

print(f"\nTest results saved to: {results_file}")

# Exit with appropriate code
sys.exit(0 if len(test_results['failed']) == 0 else 1)
