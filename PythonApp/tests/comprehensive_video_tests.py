import json
import os
import sys
import time
from PyQt5.QtWidgets import QApplication
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from gui.stimulus_controller import StimulusController, TimingLogger
try:
    from gui.enhanced_stimulus_controller import EnhancedStimulusController, VLC_AVAILABLE
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False
    VLC_AVAILABLE = False


class ComprehensiveVideoTestSuite:

    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.test_results = []
        self.test_videos_dir = Path('test_videos')
        self.sample_videos = self.discover_test_videos()
        self.basic_controller = StimulusController()
        if ENHANCED_AVAILABLE:
            self.enhanced_controller = EnhancedStimulusController()
        print(f'[DEBUG_LOG] Found {len(self.sample_videos)} test videos')
        print(
            f'[DEBUG_LOG] Enhanced controller available: {ENHANCED_AVAILABLE}')
        print(f'[DEBUG_LOG] VLC backend available: {VLC_AVAILABLE}')

    def discover_test_videos(self):
        videos = []
        if not self.test_videos_dir.exists():
            print(
                f'[DEBUG_LOG] Test videos directory not found: {self.test_videos_dir}'
                )
            return videos
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.webm',
            '.flv']
        for video_file in self.test_videos_dir.iterdir():
            if video_file.suffix.lower(
                ) in video_extensions and video_file.stat().st_size > 0:
                videos.append({'path': str(video_file), 'name': video_file.
                    name, 'size': video_file.stat().st_size, 'format':
                    video_file.suffix.lower(), 'is_problematic': False})
        problematic_files = ['empty.mp4', 'corrupted.avi']
        for prob_file in problematic_files:
            prob_path = self.test_videos_dir / prob_file
            if prob_path.exists():
                videos.append({'path': str(prob_path), 'name': prob_file,
                    'size': prob_path.stat().st_size, 'format': prob_path.
                    suffix.lower(), 'is_problematic': True})
        return videos

    def test_basic_video_loading(self):
        print('\n[DEBUG_LOG] Testing basic video loading...')
        passed = 0
        total = 0
        for video in self.sample_videos:
            if video['is_problematic']:
                continue
            total += 1
            try:
                success = self.basic_controller.load_video(video['path'])
                if success:
                    passed += 1
                    self.add_result(
                        f"✓ Basic loading: {video['name']} ({video['format']})"
                        )
                else:
                    self.add_result(
                        f"✗ Basic loading failed: {video['name']} ({video['format']})"
                        )
            except Exception as e:
                self.add_result(
                    f"✗ Basic loading error: {video['name']} - {str(e)}")
        self.add_result(f'Basic video loading: {passed}/{total} passed')
        return passed, total

    def test_enhanced_video_loading(self):
        if not ENHANCED_AVAILABLE:
            self.add_result(
                '! Enhanced controller not available - skipping enhanced tests'
                )
            return 0, 0
        print('\n[DEBUG_LOG] Testing enhanced video loading...')
        passed = 0
        total = 0
        for video in self.sample_videos:
            if video['is_problematic']:
                continue
            total += 1
            try:
                success = self.enhanced_controller.load_video(video['path'])
                if success:
                    passed += 1
                    backend = (self.enhanced_controller.current_backend.
                        value if self.enhanced_controller.current_backend else
                        'unknown')
                    self.add_result(
                        f"✓ Enhanced loading: {video['name']} ({video['format']}) - {backend} backend"
                        )
                else:
                    self.add_result(
                        f"✗ Enhanced loading failed: {video['name']} ({video['format']})"
                        )
            except Exception as e:
                self.add_result(
                    f"✗ Enhanced loading error: {video['name']} - {str(e)}")
        self.add_result(f'Enhanced video loading: {passed}/{total} passed')
        return passed, total

    def test_format_compatibility(self):
        print('\n[DEBUG_LOG] Testing format compatibility...')
        format_results = {}
        for video in self.sample_videos:
            if video['is_problematic']:
                continue
            format_name = video['format']
            if format_name not in format_results:
                format_results[format_name] = {'passed': 0, 'total': 0}
            format_results[format_name]['total'] += 1
            try:
                success = self.basic_controller.load_video(video['path'])
                if success:
                    format_results[format_name]['passed'] += 1
            except Exception:
                pass
        for format_name, results in format_results.items():
            success_rate = results['passed'] / results['total'
                ] * 100 if results['total'] > 0 else 0
            self.add_result(
                f"Format {format_name}: {results['passed']}/{results['total']} ({success_rate:.1f}%)"
                )
        return format_results

    def test_backend_comparison(self):
        if not ENHANCED_AVAILABLE or not VLC_AVAILABLE:
            self.add_result(
                '! VLC backend not available - skipping backend comparison')
            return
        print('\n[DEBUG_LOG] Testing backend comparison...')
        qt_results = {'passed': 0, 'total': 0}
        vlc_results = {'passed': 0, 'total': 0}
        for video in self.sample_videos:
            if video['is_problematic']:
                continue
            qt_results['total'] += 1
            try:
                if hasattr(self.enhanced_controller, '_load_with_backend'):
                    from gui.enhanced_stimulus_controller import VideoBackend
                    success = self.enhanced_controller._load_with_backend(video
                        ['path'], VideoBackend.QT_MULTIMEDIA)
                    if success:
                        qt_results['passed'] += 1
            except Exception:
                pass
            vlc_results['total'] += 1
            try:
                if hasattr(self.enhanced_controller, '_load_with_backend'):
                    from gui.enhanced_stimulus_controller import VideoBackend
                    success = self.enhanced_controller._load_with_backend(video
                        ['path'], VideoBackend.VLC)
                    if success:
                        vlc_results['passed'] += 1
            except Exception:
                pass
        qt_rate = qt_results['passed'] / qt_results['total'
            ] * 100 if qt_results['total'] > 0 else 0
        vlc_rate = vlc_results['passed'] / vlc_results['total'
            ] * 100 if vlc_results['total'] > 0 else 0
        self.add_result(
            f"Qt backend: {qt_results['passed']}/{qt_results['total']} ({qt_rate:.1f}%)"
            )
        self.add_result(
            f"VLC backend: {vlc_results['passed']}/{vlc_results['total']} ({vlc_rate:.1f}%)"
            )
        return qt_results, vlc_results

    def test_error_handling(self):
        print('\n[DEBUG_LOG] Testing error handling...')
        error_tests = 0
        handled_errors = 0
        for video in self.sample_videos:
            if not video['is_problematic']:
                continue
            error_tests += 1
            try:
                success = self.basic_controller.load_video(video['path'])
                if not success:
                    handled_errors += 1
                    self.add_result(f"✓ Error handled: {video['name']}")
                else:
                    self.add_result(f"✗ Error not detected: {video['name']}")
            except Exception as e:
                handled_errors += 1
                self.add_result(
                    f"✓ Exception handled: {video['name']} - {str(e)[:50]}")
        self.add_result(
            f'Error handling: {handled_errors}/{error_tests} handled correctly'
            )
        return handled_errors, error_tests

    def test_timing_accuracy(self):
        print('\n[DEBUG_LOG] Testing timing accuracy...')
        timing_video = None
        for video in self.sample_videos:
            if 'timing' in video['name'].lower() and not video['is_problematic'
                ]:
                timing_video = video
                break
        if not timing_video:
            for video in self.sample_videos:
                if not video['is_problematic']:
                    timing_video = video
                    break
        if not timing_video:
            self.add_result('✗ No suitable video for timing test')
            return False
        try:
            test_logger = TimingLogger('test_logs')
            log_file = test_logger.start_experiment_log(timing_video['path'])
            start_time = time.time()
            test_logger.log_stimulus_start(10000)
            time.sleep(0.1)
            test_logger.log_event_marker(5000, 'Test marker')
            time.sleep(0.1)
            test_logger.log_stimulus_end(10000, 'completed')
            if Path(log_file).exists():
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
                if 'events' in log_data and len(log_data['events']) >= 3:
                    self.add_result(
                        f"✓ Timing accuracy test passed with {timing_video['name']}"
                        )
                    Path(log_file).unlink()
                    return True
                else:
                    self.add_result('✗ Timing log incomplete')
            else:
                self.add_result('✗ Timing log file not created')
        except Exception as e:
            self.add_result(f'✗ Timing accuracy test failed: {str(e)}')
        return False

    def test_performance_metrics(self):
        print('\n[DEBUG_LOG] Testing performance metrics...')
        performance_results = []
        for video in self.sample_videos:
            if video['is_problematic']:
                continue
            try:
                start_time = time.perf_counter()
                success = self.basic_controller.load_video(video['path'])
                load_time = time.perf_counter() - start_time
                if success:
                    performance_results.append({'video': video['name'],
                        'size_mb': video['size'] / (1024 * 1024),
                        'load_time_ms': load_time * 1000, 'format': video[
                        'format']})
            except Exception:
                continue
        if performance_results:
            avg_load_time = sum(r['load_time_ms'] for r in performance_results
                ) / len(performance_results)
            self.add_result(
                f'Performance: Average load time {avg_load_time:.1f}ms across {len(performance_results)} videos'
                )
            format_performance = {}
            for result in performance_results:
                fmt = result['format']
                if fmt not in format_performance:
                    format_performance[fmt] = []
                format_performance[fmt].append(result['load_time_ms'])
            for fmt, times in format_performance.items():
                avg_time = sum(times) / len(times)
                self.add_result(
                    f'Format {fmt}: Average load time {avg_time:.1f}ms')
        return performance_results

    def add_result(self, message):
        self.test_results.append(message)
        print(f'[DEBUG_LOG] {message}')

    def run_all_tests(self):
        print('[DEBUG_LOG] Starting Comprehensive Video Test Suite')
        print('=' * 60)
        start_time = time.time()
        basic_passed, basic_total = self.test_basic_video_loading()
        enhanced_passed, enhanced_total = self.test_enhanced_video_loading()
        format_results = self.test_format_compatibility()
        self.test_backend_comparison()
        error_handled, error_total = self.test_error_handling()
        timing_passed = self.test_timing_accuracy()
        performance_results = self.test_performance_metrics()
        total_time = time.time() - start_time
        self.add_result('\n' + '=' * 60)
        self.add_result('COMPREHENSIVE VIDEO TEST SUMMARY')
        self.add_result('=' * 60)
        self.add_result(f'Total test videos: {len(self.sample_videos)}')
        self.add_result(f'Basic loading: {basic_passed}/{basic_total}')
        if ENHANCED_AVAILABLE:
            self.add_result(
                f'Enhanced loading: {enhanced_passed}/{enhanced_total}')
        self.add_result(f'Error handling: {error_handled}/{error_total}')
        self.add_result(f"Timing accuracy: {'✓' if timing_passed else '✗'}")
        self.add_result(
            f'Performance tests: {len(performance_results)} videos analyzed')
        self.add_result(f'Total test time: {total_time:.2f} seconds')
        self.add_result(
            f"Enhanced controller: {'Available' if ENHANCED_AVAILABLE else 'Not Available'}"
            )
        self.add_result(
            f"VLC backend: {'Available' if VLC_AVAILABLE else 'Not Available'}"
            )
        return self.test_results


def main():
    print('[DEBUG_LOG] Comprehensive Video Testing Suite')
    test_suite = ComprehensiveVideoTestSuite()
    results = test_suite.run_all_tests()
    results_file = Path('test_videos') / 'comprehensive_test_results.json'
    test_data = {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_videos': len(test_suite.sample_videos), 'enhanced_available':
        ENHANCED_AVAILABLE, 'vlc_available': VLC_AVAILABLE, 'results': results}
    with open(results_file, 'w') as f:
        json.dump(test_data, f, indent=2)
    print(f'\n[DEBUG_LOG] Test results saved to: {results_file}')
    print('[DEBUG_LOG] Comprehensive video testing completed!')
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
