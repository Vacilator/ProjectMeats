#!/bin/bash
# ProjectMeats Deployment Testing and Validation Script
# Implements the Testing and Validation Agent from the delegation plan
# Provides comprehensive end-to-end testing for deployment validation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/opt/projectmeats"
SERVICE_NAME="projectmeats"
TEST_LOG="/tmp/projectmeats_deployment_test_$(date +%Y%m%d_%H%M%S).log"
TEST_DOMAIN="localhost"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Logging functions
log_header() { echo -e "\n${PURPLE}🧪 $1${NC}" | tee -a "$TEST_LOG"; }
log_info() { echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$TEST_LOG"; }
log_success() { echo -e "${GREEN}[PASS]${NC} $1" | tee -a "$TEST_LOG"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$TEST_LOG"; }
log_error() { echo -e "${RED}[FAIL]${NC} $1" | tee -a "$TEST_LOG"; }
log_test() { echo -e "${WHITE}[TEST]${NC} $1" | tee -a "$TEST_LOG"; }

# Test result tracking
pass_test() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    log_success "$1"
}

fail_test() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    log_error "$1"
}

# Initialize test suite
init_tests() {
    echo "ProjectMeats Deployment Test Suite" > "$TEST_LOG"
    echo "Generated: $(date)" >> "$TEST_LOG"
    echo "=================================" >> "$TEST_LOG"
    echo "" >> "$TEST_LOG"
    
    log_header "ProjectMeats Deployment Validation Suite"
    log_info "Test log: $TEST_LOG"
    log_info "Testing domain: $TEST_DOMAIN"
    echo -e "${WHITE}========================================${NC}"
}

# Test 1: Service Status Tests
test_service_status() {
    log_header "Service Status Tests"
    
    log_test "Testing if ProjectMeats service is active..."
    if systemctl is-active --quiet projectmeats; then
        pass_test "ProjectMeats service is active"
    else
        fail_test "ProjectMeats service is not active"
    fi
    
    log_test "Testing if ProjectMeats service is enabled..."
    if systemctl is-enabled --quiet projectmeats; then
        pass_test "ProjectMeats service is enabled for auto-start"
    else
        fail_test "ProjectMeats service is not enabled for auto-start"
    fi
    
    log_test "Testing if PostgreSQL service is active..."
    if systemctl is-active --quiet postgresql; then
        pass_test "PostgreSQL service is active"
    else
        fail_test "PostgreSQL service is not active"
    fi
    
    log_test "Testing if Nginx service is available..."
    if systemctl is-active --quiet nginx; then
        pass_test "Nginx service is active"
    else
        log_warning "Nginx service is not active (optional for backend-only testing)"
        TESTS_TOTAL=$((TESTS_TOTAL + 1))
    fi
}

# Test 2: Process and Port Tests  
test_processes_and_ports() {
    log_header "Process and Port Tests"
    
    log_test "Testing if Gunicorn process is running..."
    if pgrep -f "gunicorn.*projectmeats" >/dev/null; then
        process_count=$(pgrep -f "gunicorn.*projectmeats" | wc -l)
        pass_test "Gunicorn process is running ($process_count processes)"
    else
        fail_test "Gunicorn process not found"
    fi
    
    log_test "Testing if port 8000 is listening..."
    if netstat -tlnp 2>/dev/null | grep -q ":8000.*LISTEN"; then
        pass_test "Port 8000 is listening"
    else
        fail_test "Port 8000 is not listening"
    fi
    
    log_test "Testing PostgreSQL port 5432..."
    if netstat -tlnp 2>/dev/null | grep -q ":5432.*LISTEN"; then
        pass_test "PostgreSQL port 5432 is listening"
    else
        fail_test "PostgreSQL port 5432 is not listening"
    fi
}

# Test 3: HTTP Response Tests
test_http_responses() {
    log_header "HTTP Response Tests"
    
    # Test basic HTTP connectivity
    log_test "Testing HTTP connectivity to Django backend..."
    if timeout 10s curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ | grep -q "200\|302\|404"; then
        response_code=$(timeout 10s curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/)
        pass_test "Django backend responds with HTTP $response_code"
    else
        fail_test "Django backend not responding to HTTP requests"
    fi
    
    # Test API endpoints
    log_test "Testing API root endpoint..."
    if timeout 10s curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/ | grep -q "200\|301\|404"; then
        api_response=$(timeout 10s curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/)
        pass_test "API root endpoint responds with HTTP $api_response"
    else
        fail_test "API root endpoint not responding"
    fi
    
    # Test admin interface
    log_test "Testing Django admin interface..."
    if timeout 10s curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/admin/ | grep -q "200\|302"; then
        admin_response=$(timeout 10s curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/admin/)
        pass_test "Django admin responds with HTTP $admin_response"
    else
        fail_test "Django admin not responding"
    fi
    
    # Test API documentation
    log_test "Testing API documentation endpoint..."
    if timeout 10s curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/schema/swagger-ui/ | grep -q "200"; then
        pass_test "API documentation is accessible"
    else
        log_warning "API documentation not accessible (may be expected in production)"
        TESTS_TOTAL=$((TESTS_TOTAL + 1))
    fi
}

# Test 4: Database Tests
test_database() {
    log_header "Database Tests"
    
    log_test "Testing PostgreSQL connection..."
    if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
        pass_test "PostgreSQL is ready and accepting connections"
    else
        fail_test "PostgreSQL is not ready"
    fi
    
    log_test "Testing Django database connection..."
    if [[ -f "$PROJECT_DIR/backend/manage.py" ]]; then
        cd "$PROJECT_DIR/backend"
        if [[ -f "../venv/bin/python" ]]; then
            source ../venv/bin/activate
            export $(cat /etc/projectmeats/projectmeats.env 2>/dev/null | grep -v '^#' | xargs) 2>/dev/null || true
            
            if timeout 15s python manage.py check --database default >/dev/null 2>&1; then
                pass_test "Django database connection is working"
            else
                fail_test "Django database connection failed"
            fi
            
            # Test migrations
            log_test "Testing database migrations status..."
            if timeout 15s python manage.py showmigrations --verbosity=0 | grep -q "\[X\]"; then
                pass_test "Database migrations are applied"
            else
                fail_test "Database migrations may not be applied"
            fi
        else
            fail_test "Python virtual environment not found"
        fi
    else
        fail_test "Django manage.py not found"
    fi
}

# Test 5: File System Tests
test_filesystem() {
    log_header "File System Tests"
    
    # Test project directory structure
    log_test "Testing project directory structure..."
    required_dirs=("$PROJECT_DIR/backend" "$PROJECT_DIR/venv" "/var/log/projectmeats" "/var/run/projectmeats")
    missing_dirs=()
    
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            missing_dirs+=("$dir")
        fi
    done
    
    if [[ ${#missing_dirs[@]} -eq 0 ]]; then
        pass_test "All required directories exist"
    else
        fail_test "Missing directories: ${missing_dirs[*]}"
    fi
    
    # Test file permissions
    log_test "Testing file permissions..."
    permission_issues=()
    
    # Check log directory ownership
    if [[ -d "/var/log/projectmeats" ]]; then
        log_owner=$(stat -c %U /var/log/projectmeats)
        if [[ "$log_owner" == "www-data" ]]; then
            pass_test "Log directory has correct ownership"
        else
            fail_test "Log directory ownership incorrect (owner: $log_owner, expected: www-data)"
        fi
    fi
    
    # Test static files
    log_test "Testing static files collection..."
    if [[ -d "$PROJECT_DIR/backend/staticfiles" ]]; then
        if find "$PROJECT_DIR/backend/staticfiles" -name "*.css" -o -name "*.js" | head -1 | grep -q "."; then
            pass_test "Static files are collected"
        else
            log_warning "Static files directory exists but may be empty"
            TESTS_TOTAL=$((TESTS_TOTAL + 1))
        fi
    else
        fail_test "Static files directory does not exist"
    fi
}

# Test 6: Configuration Tests
test_configuration() {
    log_header "Configuration Tests"
    
    # Test systemd service file
    log_test "Testing systemd service configuration..."
    service_file="/etc/systemd/system/$SERVICE_NAME.service"
    if [[ -f "$service_file" ]]; then
        pass_test "Systemd service file exists"
        
        # Check for key configuration elements
        if grep -q "WorkingDirectory" "$service_file"; then
            pass_test "Service file has WorkingDirectory configured"
        else
            fail_test "Service file missing WorkingDirectory"
        fi
        
        if grep -q "DJANGO_SETTINGS_MODULE" "$service_file"; then
            pass_test "Service file has Django settings configured"
        else
            fail_test "Service file missing Django settings"
        fi
    else
        fail_test "Systemd service file not found"
    fi
    
    # Test environment configuration
    log_test "Testing environment configuration..."
    if [[ -f "/etc/projectmeats/projectmeats.env" ]]; then
        pass_test "Environment configuration file exists"
        
        # Check for critical environment variables
        critical_vars=("SECRET_KEY" "DATABASE_URL" "ALLOWED_HOSTS")
        missing_vars=()
        
        for var in "${critical_vars[@]}"; do
            if ! grep -q "^$var=" /etc/projectmeats/projectmeats.env; then
                missing_vars+=("$var")
            fi
        done
        
        if [[ ${#missing_vars[@]} -eq 0 ]]; then
            pass_test "All critical environment variables are configured"
        else
            fail_test "Missing environment variables: ${missing_vars[*]}"
        fi
    else
        fail_test "Environment configuration file not found"
    fi
}

# Test 7: Security Tests
test_security() {
    log_header "Security Tests"
    
    # Test service isolation
    log_test "Testing service user isolation..."
    if [[ -f "/etc/systemd/system/$SERVICE_NAME.service" ]]; then
        if grep -q "User=www-data" /etc/systemd/system/$SERVICE_NAME.service; then
            pass_test "Service runs with non-root user (www-data)"
        else
            fail_test "Service may be running as root (security risk)"
        fi
        
        if grep -q "ProtectSystem=strict" /etc/systemd/system/$SERVICE_NAME.service; then
            pass_test "Service has system protection enabled"
        else
            log_warning "Service system protection not configured"
            TESTS_TOTAL=$((TESTS_TOTAL + 1))
        fi
    fi
    
    # Test file permissions
    log_test "Testing sensitive file permissions..."
    if [[ -f "/etc/projectmeats/projectmeats.env" ]]; then
        env_perms=$(stat -c %a /etc/projectmeats/projectmeats.env)
        if [[ "$env_perms" == "640" ]] || [[ "$env_perms" == "600" ]]; then
            pass_test "Environment file has secure permissions ($env_perms)"
        else
            fail_test "Environment file has insecure permissions ($env_perms)"
        fi
    fi
}

# Test 8: Performance Tests
test_performance() {
    log_header "Performance Tests"
    
    # Test response time
    log_test "Testing HTTP response time..."
    if command -v curl >/dev/null; then
        response_time=$(timeout 15s curl -o /dev/null -s -w "%{time_total}" http://127.0.0.1:8000/ 2>/dev/null || echo "999")
        if (( $(echo "$response_time < 5.0" | bc -l 2>/dev/null || echo "0") )); then
            pass_test "HTTP response time is acceptable (${response_time}s)"
        else
            log_warning "HTTP response time is slow (${response_time}s)"
            TESTS_TOTAL=$((TESTS_TOTAL + 1))
        fi
    else
        log_warning "curl not available for response time testing"
        TESTS_TOTAL=$((TESTS_TOTAL + 1))
    fi
    
    # Test memory usage
    log_test "Testing memory usage..."
    if command -v ps >/dev/null; then
        gunicorn_memory=$(ps aux | grep gunicorn | grep -v grep | awk '{sum += $6} END {print sum/1024}' 2>/dev/null || echo "0")
        if (( $(echo "$gunicorn_memory < 500" | bc -l 2>/dev/null || echo "1") )); then
            pass_test "Gunicorn memory usage is reasonable (${gunicorn_memory}MB)"
        else
            log_warning "Gunicorn memory usage is high (${gunicorn_memory}MB)"
            TESTS_TOTAL=$((TESTS_TOTAL + 1))
        fi
    fi
}

# Test 9: Log File Tests
test_logs() {
    log_header "Log File Tests"
    
    log_test "Testing error log file..."
    if [[ -f "/var/log/projectmeats/error.log" ]]; then
        pass_test "Error log file exists"
        
        # Check for recent critical errors
        if tail -50 /var/log/projectmeats/error.log | grep -qi "critical\|emergency"; then
            fail_test "Critical errors found in recent logs"
        else
            pass_test "No critical errors in recent logs"
        fi
    else
        fail_test "Error log file not found"
    fi
    
    log_test "Testing access log file..."
    if [[ -f "/var/log/projectmeats/access.log" ]]; then
        pass_test "Access log file exists"
    else
        log_warning "Access log file not found (may be expected on new deployment)"
        TESTS_TOTAL=$((TESTS_TOTAL + 1))
    fi
    
    # Test systemd journal
    log_test "Testing systemd journal entries..."
    if journalctl -u projectmeats --since "1 hour ago" --no-pager | grep -q "."; then
        pass_test "Systemd journal contains service entries"
    else
        log_warning "No recent systemd journal entries for service"
        TESTS_TOTAL=$((TESTS_TOTAL + 1))
    fi
}

# Test 10: Integration Tests
test_integration() {
    log_header "Integration Tests"
    
    # Test full request cycle
    log_test "Testing full HTTP request cycle..."
    if timeout 20s curl -s -X GET http://127.0.0.1:8000/admin/ | grep -qi "django\|admin"; then
        pass_test "Full HTTP request cycle works (Django admin accessible)"
    else
        fail_test "Full HTTP request cycle failed"
    fi
    
    # Test API endpoint if available
    log_test "Testing API endpoint functionality..."
    if timeout 20s curl -s -X GET http://127.0.0.1:8000/api/v1/ | grep -qi "api\|version"; then
        pass_test "API endpoint is functional"
    else
        log_warning "API endpoint test inconclusive (may require authentication)"
        TESTS_TOTAL=$((TESTS_TOTAL + 1))
    fi
}

# Generate test report
generate_report() {
    log_header "Test Results Summary"
    
    echo "" | tee -a "$TEST_LOG"
    echo "========================================" | tee -a "$TEST_LOG"
    echo "PROJECTMEATS DEPLOYMENT TEST RESULTS" | tee -a "$TEST_LOG"
    echo "========================================" | tee -a "$TEST_LOG"
    echo "Total Tests: $TESTS_TOTAL" | tee -a "$TEST_LOG"
    echo "Passed: $TESTS_PASSED" | tee -a "$TEST_LOG"
    echo "Failed: $TESTS_FAILED" | tee -a "$TEST_LOG"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}Status: ALL TESTS PASSED ✅${NC}" | tee -a "$TEST_LOG"
        success_rate="100%"
    else
        success_rate=$(echo "scale=1; $TESTS_PASSED * 100 / $TESTS_TOTAL" | bc -l 2>/dev/null || echo "N/A")
        echo -e "${YELLOW}Status: $TESTS_FAILED TESTS FAILED ⚠️${NC}" | tee -a "$TEST_LOG"
    fi
    
    echo "Success Rate: ${success_rate}" | tee -a "$TEST_LOG"
    echo "Timestamp: $(date)" | tee -a "$TEST_LOG"
    echo "========================================" | tee -a "$TEST_LOG"
    echo "" | tee -a "$TEST_LOG"
    
    # Recommendations
    if [[ $TESTS_FAILED -gt 0 ]]; then
        echo "RECOMMENDATIONS:" | tee -a "$TEST_LOG"
        echo "================" | tee -a "$TEST_LOG"
        echo "1. Review failed tests above" | tee -a "$TEST_LOG"
        echo "2. Run diagnostic script: sudo ./diagnose_deployment.sh" | tee -a "$TEST_LOG"
        echo "3. Fix issues and re-run this test suite" | tee -a "$TEST_LOG"
        echo "4. Check logs: sudo journalctl -u projectmeats -f" | tee -a "$TEST_LOG"
        echo "" | tee -a "$TEST_LOG"
    else
        echo "✅ DEPLOYMENT IS HEALTHY!" | tee -a "$TEST_LOG"
        echo "=========================" | tee -a "$TEST_LOG"
        echo "Your ProjectMeats deployment is working correctly." | tee -a "$TEST_LOG"
        echo "" | tee -a "$TEST_LOG"
    fi
    
    log_info "Test report saved to: $TEST_LOG"
    
    # Copy to project directory if possible
    if [[ -d "$PROJECT_DIR" ]]; then
        cp "$TEST_LOG" "$PROJECT_DIR/deployment_test_report.log"
        log_info "Test report also saved to: $PROJECT_DIR/deployment_test_report.log"
    fi
    
    return $TESTS_FAILED
}

# Main execution function
main() {
    # Check if running as root (required for some tests)
    if [[ $EUID -ne 0 ]]; then
        echo -e "${YELLOW}Warning: Running as non-root user. Some tests may be limited.${NC}"
        sleep 2
    fi
    
    init_tests
    
    # Run all test suites
    test_service_status
    test_processes_and_ports
    test_http_responses
    test_database
    test_filesystem
    test_configuration
    test_security
    test_performance
    test_logs
    test_integration
    
    # Generate final report
    generate_report
    exit_code=$?
    
    echo
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}🎉 All tests passed! Deployment is healthy.${NC}"
    else
        echo -e "${RED}⚠️ Some tests failed. Review the report above.${NC}"
    fi
    
    exit $exit_code
}

# Execute main function
main "$@"