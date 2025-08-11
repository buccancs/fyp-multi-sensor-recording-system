#!/bin/bash

# GitHub Actions Integration Status Checker
# Verifies that GitHub Actions is properly configured and accessible

set -e

echo "🔍 GitHub Actions Integration Status Check"
echo "=========================================="

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOWS_DIR="$REPO_ROOT/.github/workflows"

# Check if workflows directory exists
if [ ! -d "$WORKFLOWS_DIR" ]; then
    echo "❌ GitHub workflows directory not found at: $WORKFLOWS_DIR"
    exit 1
fi

echo "✅ GitHub workflows directory found"

# Check for virtual test environment workflow
VTE_WORKFLOW="$WORKFLOWS_DIR/virtual-test-environment.yml"
if [ ! -f "$VTE_WORKFLOW" ]; then
    echo "❌ Virtual test environment workflow not found"
    exit 1
fi

echo "✅ Virtual test environment workflow found"

# Validate workflow syntax (basic check)
if command -v yamllint >/dev/null 2>&1; then
    echo "🔍 Validating workflow YAML syntax..."
    if yamllint "$VTE_WORKFLOW"; then
        echo "✅ Workflow YAML syntax is valid"
    else
        echo "⚠️  Workflow YAML has syntax issues (but may still work)"
    fi
else
    echo "⚠️  yamllint not available, skipping syntax validation"
fi

# Check workflow content
echo "🔍 Checking workflow configuration..."

# Check for required triggers
if grep -q "workflow_dispatch:" "$VTE_WORKFLOW"; then
    echo "✅ Manual workflow dispatch enabled"
else
    echo "❌ Manual workflow dispatch not configured"
fi

if grep -q "pull_request:" "$VTE_WORKFLOW"; then
    echo "✅ Pull request triggers configured"
else
    echo "❌ Pull request triggers not configured"
fi

if grep -q "push:" "$VTE_WORKFLOW"; then
    echo "✅ Push triggers configured"
else
    echo "❌ Push triggers not configured"
fi

# Check for test scenarios
SCENARIOS=("quick" "ci" "stress" "sync")
FOUND_SCENARIOS=0

for scenario in "${SCENARIOS[@]}"; do
    if grep -q "$scenario" "$VTE_WORKFLOW"; then
        echo "✅ Test scenario '$scenario' found in workflow"
        ((FOUND_SCENARIOS++))
    else
        echo "⚠️  Test scenario '$scenario' not found in workflow"
    fi
done

if [ $FOUND_SCENARIOS -ge 2 ]; then
    echo "✅ Sufficient test scenarios configured ($FOUND_SCENARIOS/4)"
else
    echo "❌ Insufficient test scenarios configured ($FOUND_SCENARIOS/4)"
fi

# Check for other important workflows
OTHER_WORKFLOWS=("ci-cd.yml" "integration-testing.yml" "performance-monitoring.yml")
FOUND_OTHER=0

for workflow in "${OTHER_WORKFLOWS[@]}"; do
    if [ -f "$WORKFLOWS_DIR/$workflow" ]; then
        echo "✅ Additional workflow found: $workflow"
        ((FOUND_OTHER++))
    else
        echo "ℹ️  Optional workflow not found: $workflow"
    fi
done

# Check virtual test environment files
VTE_DIR="$REPO_ROOT/tests/integration/virtual_environment"
if [ ! -d "$VTE_DIR" ]; then
    echo "❌ Virtual test environment directory not found"
    exit 1
fi

echo "✅ Virtual test environment directory found"

REQUIRED_FILES=(
    "run_virtual_test.sh"
    "setup_dev_environment.sh"
    "test_runner.py"
    "virtual_device_client.py"
)

MISSING_FILES=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$VTE_DIR/$file" ]; then
        echo "✅ Required file found: $file"
    else
        echo "❌ Required file missing: $file"
        ((MISSING_FILES++))
    fi
done

if [ $MISSING_FILES -eq 0 ]; then
    echo "✅ All required virtual test files present"
else
    echo "❌ Missing $MISSING_FILES required virtual test files"
fi

# Check integration guide and documentation
DOCS=("VIRTUAL_TEST_INTEGRATION_GUIDE.md" "TEST_RUNNER_README.md" "run_local_test.sh")
MISSING_DOCS=0

for doc in "${DOCS[@]}"; do
    if [ -f "$REPO_ROOT/$doc" ]; then
        echo "✅ Documentation found: $doc"
    else
        echo "❌ Documentation missing: $doc"
        ((MISSING_DOCS++))
    fi
done

if [ $MISSING_DOCS -eq 0 ]; then
    echo "✅ All integration documentation present"
else
    echo "❌ Missing $MISSING_DOCS integration documentation files"
fi

# Summary
echo ""
echo "📊 Integration Status Summary"
echo "=============================="

TOTAL_CHECKS=7
PASSED_CHECKS=0

# Basic checks
[ -d "$WORKFLOWS_DIR" ] && ((PASSED_CHECKS++))
[ -f "$VTE_WORKFLOW" ] && ((PASSED_CHECKS++))
[ $FOUND_SCENARIOS -ge 2 ] && ((PASSED_CHECKS++))
[ $MISSING_FILES -eq 0 ] && ((PASSED_CHECKS++))
[ $MISSING_DOCS -eq 0 ] && ((PASSED_CHECKS++))
[ -d "$VTE_DIR" ] && ((PASSED_CHECKS++))

# Workflow triggers check
TRIGGER_CHECKS=0
grep -q "workflow_dispatch:" "$VTE_WORKFLOW" && ((TRIGGER_CHECKS++))
grep -q "pull_request:" "$VTE_WORKFLOW" && ((TRIGGER_CHECKS++))
grep -q "push:" "$VTE_WORKFLOW" && ((TRIGGER_CHECKS++))

if [ $TRIGGER_CHECKS -eq 3 ]; then
    ((PASSED_CHECKS++))
fi

echo "Passed: $PASSED_CHECKS/$TOTAL_CHECKS checks"

if [ $PASSED_CHECKS -eq $TOTAL_CHECKS ]; then
    echo ""
    echo "🎉 GitHub Actions Integration: ✅ FULLY INTEGRATED"
    echo "   - Workflows properly configured"
    echo "   - Virtual test environment complete"
    echo "   - Documentation comprehensive"
    echo "   - Manual and automatic triggers enabled"
    echo ""
    echo "🚀 Ready for:"
    echo "   - Automatic PR testing"
    echo "   - Manual workflow dispatch"
    echo "   - Local development and testing"
    echo "   - CI/CD automation"
    exit 0
elif [ $PASSED_CHECKS -ge 5 ]; then
    echo ""
    echo "⚠️  GitHub Actions Integration: 🟡 MOSTLY INTEGRATED"
    echo "   - Core functionality working"
    echo "   - Some optional features missing"
    echo "   - Manual testing recommended"
    exit 0
else
    echo ""
    echo "❌ GitHub Actions Integration: 🔴 INCOMPLETE"
    echo "   - Critical components missing"
    echo "   - Integration may not work properly"
    echo "   - Setup and configuration needed"
    exit 1
fi