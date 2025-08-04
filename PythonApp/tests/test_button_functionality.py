import re
import os


def check_file_content(file_path, expected_patterns):
    if not os.path.exists(file_path):
        return False, f'File not found: {file_path}'
    with open(file_path, 'r') as f:
        content = f.read()
    missing_patterns = []
    for pattern_name, pattern in expected_patterns.items():
        if not re.search(pattern, content, re.MULTILINE | re.DOTALL):
            missing_patterns.append(pattern_name)
    if missing_patterns:
        return False, f'Missing patterns: {missing_patterns}'
    return True, 'All patterns found'


def test_main_ui_state_fixes():
    file_path = (
        'AndroidApp/src/main/java/com/multisensor/recording/ui/MainUiState.kt')
    expected_patterns = {'manual_controls_default_true':
        'showManualControls.*=.*true.*//.*Enable manual controls by default',
        'can_start_recording_simplified':
        'showManualControls.*//.*Allow recording if manual controls are enabled'
        , 'lenient_button_logic':
        'isInitialized.*&&.*!isRecording.*&&.*!isLoadingRecording.*&&.*showManualControls'
        }
    success, message = check_file_content(file_path, expected_patterns)
    assert success, message


def test_main_view_model_fixes():
    file_path = (
        'AndroidApp/src/main/java/com/multisensor/recording/ui/MainViewModel.kt'
        )
    expected_patterns = {'fallback_initialization_method':
        'fun initializeSystemWithFallback\\(\\)',
        'camera_fail_still_initialize':
        'isInitialized = true.*//.*Still allow other functionality',
        'manual_controls_on_init': 'showManualControls.*=.*true',
        'error_still_enable_ui':
        'isInitialized = true.*//.*Enable basic UI even on error'}
    success, message = check_file_content(file_path, expected_patterns)
    assert success, message


def test_main_activity_fixes():
    file_path = (
        'AndroidApp/src/main/java/com/multisensor/recording/MainActivity.kt')
    expected_patterns = {'fallback_on_permission_denied':
        'viewModel\\.initializeSystemWithFallback\\(\\)',
        'timeout_fallback':
        'Handler.*postDelayed.*initializeSystemWithFallback',
        'permission_retry_logic':
        'Permission flow may have stalled.*fallback initialization'}
    success, message = check_file_content(file_path, expected_patterns)
    assert success, message


def run_all_tests():
    print('🧪 Testing Button Functionality Fixes')
    print('=' * 50)
    tests = [('MainUiState Button Logic', test_main_ui_state_fixes), (
        'MainViewModel Fallback', test_main_view_model_fixes), (
        'MainActivity Permission Handling', test_main_activity_fixes)]
    passed = 0
    total = len(tests)
    for test_name, test_func in tests:
        print(f'\n🔍 Testing: {test_name}')
        try:
            success, message = test_func()
            if success:
                print(f'✅ PASS: {message}')
                passed += 1
            else:
                print(f'❌ FAIL: {message}')
        except Exception as e:
            print(f'❌ ERROR: {e}')
    print(f'\n📊 Results: {passed}/{total} tests passed')
    if passed == total:
        print('🎉 All tests passed! Button functionality should be fixed.')
        return True
    else:
        print(
            '⚠️  Some tests failed. Button functionality may still have issues.'
            )
        return False


if __name__ == '__main__':
    if os.path.exists('AndroidApp'):
        success = run_all_tests()
        exit(0 if success else 1)
    else:
        print('❌ Error: Run this script from the repository root directory')
        exit(1)
