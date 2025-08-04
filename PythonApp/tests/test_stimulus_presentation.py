import json
import os
import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QFileDialog
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from gui.stimulus_controller import StimulusController, TimingLogger
from gui.stimulus_panel import StimulusControlPanel


class StimulusTestWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Stimulus Presentation Test')
        self.setGeometry(100, 100, 800, 600)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.stimulus_controller = StimulusController(self)
        self.stimulus_panel = StimulusControlPanel(self)
        layout.addWidget(QLabel('Stimulus Presentation Test'))
        layout.addWidget(self.stimulus_panel)
        layout.addWidget(self.stimulus_controller)
        self.create_test_buttons(layout)
        self.connect_test_signals()
        self.test_results = []
        print('[DEBUG_LOG] StimulusTestWindow initialized')

    def create_test_buttons(self, layout):
        self.load_test_video_btn = QPushButton('Load Test Video')
        self.load_test_video_btn.clicked.connect(self.load_test_video)
        layout.addWidget(self.load_test_video_btn)
        self.run_tests_btn = QPushButton('Run All Tests')
        self.run_tests_btn.clicked.connect(self.run_all_tests)
        layout.addWidget(self.run_tests_btn)
        self.results_label = QLabel('Test Results: Not started')
        layout.addWidget(self.results_label)

    def connect_test_signals(self):
        self.stimulus_panel.file_loaded.connect(self.stimulus_controller.
            load_video)
        self.stimulus_panel.play_requested.connect(self.stimulus_controller
            .test_play)
        self.stimulus_panel.pause_requested.connect(self.
            stimulus_controller.test_pause)
        self.stimulus_panel.start_recording_play_requested.connect(self.
            test_synchronized_start)
        self.stimulus_panel.mark_event_requested.connect(self.
            stimulus_controller.mark_event)
        self.stimulus_controller.status_changed.connect(self.on_status_changed)
        self.stimulus_controller.experiment_started.connect(self.
            on_experiment_started)
        self.stimulus_controller.experiment_ended.connect(self.
            on_experiment_ended)
        self.stimulus_controller.error_occurred.connect(self.on_error_occurred)

    def load_test_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self,
            'Select Test Video', '',
            'Video Files (*.mp4 *.avi *.mov *.mkv *.wmv);;All Files (*)')
        if file_path:
            self.stimulus_panel.load_file(file_path)
            print(f'[DEBUG_LOG] Test video loaded: {file_path}')

    def test_synchronized_start(self):
        print('[DEBUG_LOG] Testing synchronized start...')
        screen_index = self.stimulus_panel.get_selected_screen()
        print('[DEBUG_LOG] Simulating device recording start...')
        if self.stimulus_controller.start_stimulus_playback(screen_index):
            self.stimulus_panel.set_experiment_active(True)
            print('[DEBUG_LOG] Synchronized start test successful')
            self.test_results.append('✓ Synchronized start test passed')
        else:
            print('[DEBUG_LOG] Synchronized start test failed')
            self.test_results.append('✗ Synchronized start test failed')

    def run_all_tests(self):
        print('[DEBUG_LOG] Starting comprehensive test suite...')
        self.test_results.clear()
        self.test_component_initialization()
        self.test_signal_connections()
        self.test_timing_logger()
        self.test_screen_detection()
        if self.stimulus_controller.current_video_file:
            self.test_keyboard_shortcuts()
        self.display_test_results()

    def test_component_initialization(self):
        try:
            assert self.stimulus_controller is not None
            assert self.stimulus_controller.media_player is not None
            assert self.stimulus_controller.video_widget is not None
            assert self.stimulus_controller.timing_logger is not None
            assert self.stimulus_panel is not None
            assert hasattr(self.stimulus_panel, 'start_recording_play_btn')
            assert hasattr(self.stimulus_panel, 'mark_event_btn')
            self.test_results.append('✓ Component initialization test passed')
            print('[DEBUG_LOG] Component initialization test passed')
        except Exception as e:
            self.test_results.append(
                f'✗ Component initialization test failed: {e}')
            print(f'[DEBUG_LOG] Component initialization test failed: {e}')

    def test_signal_connections(self):
        try:
            assert hasattr(self.stimulus_panel, 'file_loaded')
            assert hasattr(self.stimulus_panel,
                'start_recording_play_requested')
            assert hasattr(self.stimulus_panel, 'mark_event_requested')
            assert hasattr(self.stimulus_controller, 'status_changed')
            assert hasattr(self.stimulus_controller, 'experiment_started')
            assert hasattr(self.stimulus_controller, 'experiment_ended')
            self.test_results.append('✓ Signal connections test passed')
            print('[DEBUG_LOG] Signal connections test passed')
        except Exception as e:
            self.test_results.append(f'✗ Signal connections test failed: {e}')
            print(f'[DEBUG_LOG] Signal connections test failed: {e}')

    def test_timing_logger(self):
        try:
            test_logger = TimingLogger('test_logs')
            log_file = test_logger.start_experiment_log('test_video.mp4')
            assert os.path.exists(log_file)
            test_logger.log_stimulus_start(30000)
            test_logger.log_event_marker(15000, 'Test marker')
            test_logger.log_stimulus_end(30000, 'completed')
            with open(log_file, 'r') as f:
                log_data = json.load(f)
            assert 'experiment_info' in log_data
            assert 'events' in log_data
            assert len(log_data['events']) == 3
            os.remove(log_file)
            self.test_results.append('✓ Timing logger test passed')
            print('[DEBUG_LOG] Timing logger test passed')
        except Exception as e:
            self.test_results.append(f'✗ Timing logger test failed: {e}')
            print(f'[DEBUG_LOG] Timing logger test failed: {e}')

    def test_screen_detection(self):
        try:
            screens = QApplication.screens()
            screen_count = len(screens)
            self.stimulus_panel.populate_screen_combo()
            combo_count = self.stimulus_panel.screen_combo.count()
            assert combo_count == screen_count
            self.test_results.append(
                f'✓ Screen detection test passed ({screen_count} screens)')
            print(
                f'[DEBUG_LOG] Screen detection test passed: {screen_count} screens detected'
                )
        except Exception as e:
            self.test_results.append(f'✗ Screen detection test failed: {e}')
            print(f'[DEBUG_LOG] Screen detection test failed: {e}')

    def test_keyboard_shortcuts(self):
        try:
            assert hasattr(self.stimulus_controller, 'space_shortcut')
            assert hasattr(self.stimulus_controller, 'escape_shortcut')
            assert hasattr(self.stimulus_controller.video_widget,
                'space_pressed')
            assert hasattr(self.stimulus_controller.video_widget,
                'escape_pressed')
            self.test_results.append('✓ Keyboard shortcuts test passed')
            print('[DEBUG_LOG] Keyboard shortcuts test passed')
        except Exception as e:
            self.test_results.append(f'✗ Keyboard shortcuts test failed: {e}')
            print(f'[DEBUG_LOG] Keyboard shortcuts test failed: {e}')

    def display_test_results(self):
        passed = len([r for r in self.test_results if r.startswith('✓')])
        total = len(self.test_results)
        result_text = f'Test Results: {passed}/{total} passed\n' + '\n'.join(
            self.test_results)
        self.results_label.setText(result_text)
        print(
            f'[DEBUG_LOG] Test suite completed: {passed}/{total} tests passed')
        for result in self.test_results:
            print(f'[DEBUG_LOG] {result}')

    def on_status_changed(self, status):
        print(f'[DEBUG_LOG] Status changed: {status}')

    def on_experiment_started(self):
        print('[DEBUG_LOG] Experiment started signal received')

    def on_experiment_ended(self):
        print('[DEBUG_LOG] Experiment ended signal received')
        self.stimulus_panel.set_experiment_active(False)

    def on_error_occurred(self, error):
        print(f'[DEBUG_LOG] Error occurred: {error}')


def create_test_video():
    try:
        import cv2
        import numpy as np
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('test_video.mp4', fourcc, 30.0, (640, 480))
        for i in range(300):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            color = int(255 * (i / 300))
            frame[:, :] = [color, 100, 255 - color]
            cv2.putText(frame, f'Frame {i}', (50, 50), cv2.
                FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            out.write(frame)
        out.release()
        print('[DEBUG_LOG] Test video created: test_video.mp4')
        return 'test_video.mp4'
    except ImportError:
        print('[DEBUG_LOG] OpenCV not available, cannot create test video')
        return None
    except Exception as e:
        print(f'[DEBUG_LOG] Error creating test video: {e}')
        return None


def main():
    print('[DEBUG_LOG] Starting Stimulus Presentation Test Suite')
    app = QApplication(sys.argv)
    test_window = StimulusTestWindow()
    test_window.show()
    test_video = create_test_video()
    if test_video:
        QTimer.singleShot(1000, lambda : test_window.stimulus_panel.
            load_file(test_video))
    print('[DEBUG_LOG] Test window created. Use the interface to run tests.')
    print('[DEBUG_LOG] Available tests:')
    print('[DEBUG_LOG] 1. Load Test Video - Load a video file for testing')
    print('[DEBUG_LOG] 2. Run All Tests - Run comprehensive test suite')
    print('[DEBUG_LOG] 3. Manual Testing - Use stimulus panel controls')
    print(
        '[DEBUG_LOG] 4. Keyboard Shortcuts - Space (play/pause), Esc (exit fullscreen)'
        )
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
