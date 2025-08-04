import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
logging.basicConfig(level=logging.INFO, format=
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s', datefmt=
    '%Y-%m-%d %H:%M:%S', handlers=[logging.FileHandler(
    'all_full_suites_test.log'), logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)


class AllFullTestSuitesOrchestrator:

    def __init__(self):
        self.test_suites = [{'name':
            'Recording Functionality Full Test Suite', 'script':
            'test_recording_full_suite.py', 'focus':
            'recording_functionality', 'description':
            'Tests all recording-related features and workflows'}, {'name':
            'Device Management Full Test Suite', 'script':
            'test_device_management_full_suite.py', 'focus':
            'device_management', 'description':
            'Tests device discovery, connection, and management'}, {'name':
            'Calibration Full Test Suite', 'script':
            'test_calibration_full_suite.py', 'focus': 'calibration',
            'description': 'Tests camera calibration and data processing'},
            {'name': 'File Management Full Test Suite', 'script':
            'test_file_management_full_suite.py', 'focus':
            'file_management', 'description':
            'Tests data export, import, and file operations'}, {'name':
            'Network Connectivity Full Test Suite', 'script':
            'test_network_connectivity_full_suite.py', 'focus':
            'network_connectivity', 'description':
            'Tests network protocols and communication'}]
        self.results = {}
        self.start_time = None
        self.end_time = None

    async def run_all_test_suites(self, parallel: bool=False) ->Dict[str, Any]:
        self.start_time = datetime.now()
        logger.info('=' * 80)
        logger.info(
            'RUNNING ALL FULL TEST SUITES - Multi-Sensor Recording System')
        logger.info('=' * 80)
        logger.info(
            f"Execution mode: {'Parallel' if parallel else 'Sequential'}")
        logger.info(f'Total test suites: {len(self.test_suites)}')
        logger.info('')
        overall_results = {'orchestrator': 'All Full Test Suites',
            'start_time': self.start_time.isoformat(), 'execution_mode': 
            'parallel' if parallel else 'sequential', 'test_suite_results':
            {}, 'summary': {}, 'overall_success': True}
        try:
            if parallel:
                tasks = []
                for suite_info in self.test_suites:
                    task = self._run_test_suite(suite_info)
                    tasks.append(task)
                suite_results = await asyncio.gather(*tasks,
                    return_exceptions=True)
                for i, result in enumerate(suite_results):
                    suite_info = self.test_suites[i]
                    if isinstance(result, Exception):
                        overall_results['test_suite_results'][suite_info[
                            'focus']] = {'suite_name': suite_info['name'],
                            'success': False, 'error': str(result)}
                        overall_results['overall_success'] = False
                    else:
                        overall_results['test_suite_results'][suite_info[
                            'focus']] = result
                        if not result.get('success', False):
                            overall_results['overall_success'] = False
            else:
                for suite_info in self.test_suites:
                    logger.info(f"Running {suite_info['name']}...")
                    result = await self._run_test_suite(suite_info)
                    overall_results['test_suite_results'][suite_info['focus']
                        ] = result
                    if not result.get('success', False):
                        overall_results['overall_success'] = False
                    await asyncio.sleep(2)
            self._generate_comprehensive_summary(overall_results)
        except Exception as e:
            logger.error(f'Test suite orchestration failed: {e}')
            overall_results['overall_success'] = False
            overall_results['orchestration_error'] = str(e)
        finally:
            self.end_time = datetime.now()
            overall_results['end_time'] = self.end_time.isoformat()
            overall_results['total_duration'] = (self.end_time - self.
                start_time).total_seconds()
            await self._save_comprehensive_results(overall_results)
            logger.info('=' * 80)
            logger.info('ALL FULL TEST SUITES COMPLETED')
            logger.info('=' * 80)
        return overall_results

    async def _run_test_suite(self, suite_info: Dict[str, str]) ->Dict[str, Any
        ]:
        result = {'suite_name': suite_info['name'], 'focus': suite_info[
            'focus'], 'script': suite_info['script'], 'success': False,
            'start_time': datetime.now().isoformat(), 'duration': 0,
            'exit_code': None}
        start_time = time.time()
        try:
            logger.info(f"Starting {suite_info['name']}...")
            process = await asyncio.create_subprocess_exec(sys.executable,
                suite_info['script'], cwd=Path(__file__).parent, stdout=
                asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()
            result['exit_code'] = process.returncode
            result['duration'] = time.time() - start_time
            result['end_time'] = datetime.now().isoformat()
            if process.returncode == 0:
                result['success'] = True
                logger.info(f"✅ {suite_info['name']} completed successfully")
            else:
                result['success'] = False
                result['stderr'] = stderr.decode() if stderr else ''
                logger.error(
                    f"❌ {suite_info['name']} failed with exit code {process.returncode}"
                    )
            if stdout:
                result['stdout'] = stdout.decode()
        except Exception as e:
            result['duration'] = time.time() - start_time
            result['end_time'] = datetime.now().isoformat()
            result['error'] = str(e)
            logger.error(f"❌ {suite_info['name']} failed with exception: {e}")
        return result

    def _generate_comprehensive_summary(self, results: Dict[str, Any]):
        summary = {'total_suites': len(self.test_suites),
            'successful_suites': 0, 'failed_suites': 0, 'total_duration':
            results.get('total_duration', 0), 'suite_breakdown': {}}
        for focus, suite_result in results.get('test_suite_results', {}).items(
            ):
            if suite_result.get('success', False):
                summary['successful_suites'] += 1
            else:
                summary['failed_suites'] += 1
            summary['suite_breakdown'][focus] = {'name': suite_result.get(
                'suite_name', 'Unknown'), 'success': suite_result.get(
                'success', False), 'duration': suite_result.get('duration',
                0), 'exit_code': suite_result.get('exit_code', None)}
        if summary['total_suites'] > 0:
            summary['success_rate'] = summary['successful_suites'] / summary[
                'total_suites'] * 100
        else:
            summary['success_rate'] = 0
        results['summary'] = summary
        logger.info('=' * 60)
        logger.info('COMPREHENSIVE TEST SUMMARY')
        logger.info('=' * 60)
        logger.info(f"Total Test Suites: {summary['total_suites']}")
        logger.info(f"Successful Suites: {summary['successful_suites']}")
        logger.info(f"Failed Suites: {summary['failed_suites']}")
        logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"Total Duration: {summary['total_duration']:.1f} seconds")
        logger.info('')
        for focus, breakdown in summary['suite_breakdown'].items():
            status = '✅ PASSED' if breakdown['success'] else '❌ FAILED'
            duration = breakdown['duration']
            logger.info(f"{status} - {breakdown['name']} ({duration:.1f}s)")
        logger.info('=' * 60)

    async def _save_comprehensive_results(self, results: Dict[str, Any]):
        try:
            results_dir = Path('test_results')
            results_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            results_file = (results_dir /
                f'all_full_suites_results_{timestamp}.json')
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f'Comprehensive test results saved to: {results_file}')
            summary_file = (results_dir /
                f'all_full_suites_summary_{timestamp}.md')
            await self._generate_comprehensive_markdown_report(summary_file,
                results)
        except Exception as e:
            logger.error(f'Failed to save comprehensive results: {e}')

    async def _generate_comprehensive_markdown_report(self, file_path: Path,
        results: Dict[str, Any]):
        try:
            with open(file_path, 'w') as f:
                f.write(
                    '# Comprehensive Test Report - All Full Test Suites\n\n')
                f.write(f'**Generated:** {datetime.now().isoformat()}\n')
                f.write(
                    f"**Total Duration:** {results.get('total_duration', 0):.2f} seconds\n"
                    )
                f.write(
                    f"**Execution Mode:** {results.get('execution_mode', 'unknown').title()}\n"
                    )
                f.write(
                    f"""**Overall Result:** {'✅ PASSED' if results.get('overall_success') else '❌ FAILED'}

"""
                    )
                summary = results.get('summary', {})
                f.write('## Executive Summary\n\n')
                f.write(
                    f"- **Total Test Suites:** {summary.get('total_suites', 0)}\n"
                    )
                f.write(
                    f"- **Successful Suites:** {summary.get('successful_suites', 0)}\n"
                    )
                f.write(
                    f"- **Failed Suites:** {summary.get('failed_suites', 0)}\n"
                    )
                f.write(
                    f"- **Success Rate:** {summary.get('success_rate', 0):.1f}%\n\n"
                    )
                f.write('## Test Suite Results\n\n')
                for focus, suite_result in results.get('test_suite_results', {}
                    ).items():
                    status = '✅ PASSED' if suite_result.get('success'
                        ) else '❌ FAILED'
                    suite_name = suite_result.get('suite_name', 'Unknown Suite'
                        )
                    duration = suite_result.get('duration', 0)
                    exit_code = suite_result.get('exit_code', 'N/A')
                    f.write(f'### {suite_name}\n\n')
                    f.write(f'**Status:** {status}\n')
                    f.write(
                        f"**Focus Area:** {focus.replace('_', ' ').title()}\n")
                    f.write(f'**Duration:** {duration:.2f} seconds\n')
                    f.write(f'**Exit Code:** {exit_code}\n')
                    if 'error' in suite_result:
                        f.write(f"**Error:** {suite_result['error']}\n")
                    f.write('\n')
                f.write('## Recommendations\n\n')
                if results.get('overall_success'):
                    f.write(
                        """✅ All test suites passed successfully. The multi-sensor recording system is functioning correctly across all functional areas.

"""
                        )
                else:
                    f.write(
                        """⚠️ Some test suites failed. Review the failed areas and address issues before deployment:

"""
                        )
                    for focus, suite_result in results.get('test_suite_results'
                        , {}).items():
                        if not suite_result.get('success'):
                            f.write(
                                f"- **{focus.replace('_', ' ').title()}**: Requires attention\n"
                                )
                    f.write('\n')
                f.write('## Test Coverage\n\n')
                f.write('This comprehensive test covers:\n')
                f.write(
                    '- 🎥 **Recording Functionality**: All recording workflows and controls\n'
                    )
                f.write(
                    '- 📱 **Device Management**: Device discovery, connection, and management\n'
                    )
                f.write(
                    '- 📐 **Calibration**: Camera calibration and data processing\n'
                    )
                f.write(
                    '- 📁 **File Management**: Data export, import, and file operations\n'
                    )
                f.write(
                    """- 🌐 **Network Connectivity**: Communication protocols and network resilience
"""
                    )
            logger.info(f'Comprehensive markdown report saved to: {file_path}')
        except Exception as e:
            logger.error(
                f'Failed to generate comprehensive markdown report: {e}')


async def main():
    print('=' * 80)
    print('ALL FULL TEST SUITES ORCHESTRATOR - Multi-Sensor Recording System')
    print('=' * 80)
    print()
    print('Available execution modes:')
    print('1. Sequential (default) - Run test suites one after another')
    print('2. Parallel - Run all test suites simultaneously')
    print()
    parallel_mode = False
    orchestrator = AllFullTestSuitesOrchestrator()
    results = await orchestrator.run_all_test_suites(parallel=parallel_mode)
    print('=' * 80)
    print('FINAL RESULTS - ALL TEST SUITES')
    print('=' * 80)
    print(
        f"Overall Success: {'✅ PASSED' if results.get('overall_success') else '❌ FAILED'}"
        )
    if 'summary' in results:
        summary = results['summary']
        print(f"Total Test Suites: {summary.get('total_suites', 0)}")
        print(f"Successful: {summary.get('successful_suites', 0)}")
        print(f"Failed: {summary.get('failed_suites', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0):.1f}%")
        print(f"Total Duration: {summary.get('total_duration', 0):.1f} seconds"
            )
    print('=' * 80)
    return results


if __name__ == '__main__':
    results = asyncio.run(main())
    sys.exit(0 if results.get('overall_success', False) else 1)
