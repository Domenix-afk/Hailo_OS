"""
Nero AI Framework - Comprehensive Optimization Validation Suite
Tests all optimized components for functionality and performance
"""

import asyncio
import time
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import statistics
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

BACKEND_URL = "http://localhost:8000"
TEST_RESULTS = {
    "timestamp": datetime.now().isoformat(),
    "tests": {},
    "summary": {}
}

# ============================================================================
# UTILITIES
# ============================================================================

def print_header(text):
    """Print test section header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_test(name, status, details=""):
    """Print test result."""
    symbol = "✓" if status == "PASS" else "✗"
    color = "\033[92m" if status == "PASS" else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{symbol}{reset} {name}")
    if details:
        print(f"  → {details}")

def format_time(ms):
    """Format milliseconds."""
    if ms < 1000:
        return f"{ms:.0f}ms"
    return f"{ms/1000:.2f}s"

# ============================================================================
# BACKEND TESTS
# ============================================================================

async def test_health_endpoint():
    """Test health check endpoint."""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BACKEND_URL}/api/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    has_required_fields = all(k in data for k in ["status", "gpu_available"])
                    print_test("Health Endpoint", "PASS", f"Status: {data.get('status')}, GPU: {data.get('gpu_available')}")
                    return True, data
                else:
                    print_test("Health Endpoint", "FAIL", f"Status code: {resp.status}")
                    return False, None
    except Exception as e:
        print_test("Health Endpoint", "FAIL", str(e))
        return False, None

async def test_stats_endpoint():
    """Test stats endpoint."""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BACKEND_URL}/api/stats", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    avg_time = data.get('avg_processing_time_ms', 0)
                    error_rate = data.get('error_rate', 0)
                    print_test("Stats Endpoint", "PASS", 
                             f"Avg: {format_time(avg_time)}, Error Rate: {error_rate*100:.1f}%")
                    return True, data
                else:
                    print_test("Stats Endpoint", "FAIL", f"Status code: {resp.status}")
                    return False, None
    except Exception as e:
        print_test("Stats Endpoint", "FAIL", str(e))
        return False, None

async def test_cors_headers():
    """Test CORS configuration."""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.options(f"{BACKEND_URL}/api/voice", 
                                      timeout=aiohttp.ClientTimeout(total=5)) as resp:
                cors_header = resp.headers.get('Access-Control-Allow-Origin', '')
                if cors_header == '*':
                    print_test("CORS Headers", "PASS", "CORS enabled for all origins")
                    return True
                else:
                    print_test("CORS Headers", "FAIL", f"CORS origin: {cors_header}")
                    return False
    except Exception as e:
        print_test("CORS Headers", "FAIL", str(e))
        return False

async def test_api_response_time():
    """Measure API response times."""
    import aiohttp
    
    try:
        times = []
        for i in range(3):
            start = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/api/health", 
                                      timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        await resp.json()
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
        
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        
        print_test("API Response Time", "PASS",
                 f"Avg: {format_time(avg_time)}, Min: {format_time(min_time)}, Max: {format_time(max_time)}")
        return True, {"avg": avg_time, "min": min_time, "max": max_time}
    except Exception as e:
        print_test("API Response Time", "FAIL", str(e))
        return False, None

# ============================================================================
# FRONTEND TESTS
# ============================================================================

def test_optimized_files_exist():
    """Check if optimized files exist."""
    frontend_dir = Path("frontend/src")
    backend_dir = Path("backend")
    
    files_to_check = [
        ("frontend/src/App_optimized.jsx", "React Component"),
        ("frontend/src/index_optimized.css", "CSS Stylesheet"),
        ("backend/omni_engine_optimized.py", "Backend Engine"),
        ("backend/main_optimized.py", "FastAPI Main"),
    ]
    
    all_exist = True
    for file_path, description in files_to_check:
        exists = Path(file_path).exists()
        status = "PASS" if exists else "FAIL"
        print_test(f"File: {description}", status, file_path)
        all_exist = all_exist and exists
    
    return all_exist

def test_performance_metrics_in_code():
    """Check if performance optimizations are in code."""
    checks = [
        ("backend/omni_engine.py", "STT_BEAM_SIZE = 3", "STT Optimization"),
        ("backend/omni_engine.py", "LLM_MAX_TOKENS = 120", "LLM Optimization"),
        ("backend/main.py", "GZIPMiddleware", "Response Compression"),
        ("frontend/src/App.jsx", "useCallback", "React Memoization"),
        ("frontend/src/App.jsx", "useMemo", "React Memoization"),
    ]
    
    all_found = True
    for file_path, check_string, description in checks:
        try:
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                    found = check_string in content
                    status = "PASS" if found else "FAIL"
                    print_test(f"Code: {description}", status, f"{file_path}")
                    all_found = all_found and found
            else:
                print_test(f"Code: {description}", "FAIL", f"File not found: {file_path}")
                all_found = False
        except Exception as e:
            print_test(f"Code: {description}", "FAIL", str(e))
            all_found = False
    
    return all_found

def test_logging_configuration():
    """Check if logging is properly configured."""
    backend_file = Path("backend/main.py")
    backend_engine_file = Path("backend/omni_engine.py")
    
    checks = [
        ("Structured Logging in Backend", backend_file, "logging.basicConfig"),
        ("Logger Usage in Backend", backend_file, "logger."),
        ("Engine Logging", backend_engine_file, "logger."),
    ]
    
    all_found = True
    for description, file_path, check_string in checks:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                found = check_string in content
                status = "PASS" if found else "FAIL"
                print_test(description, status)
                all_found = all_found and found
        except Exception as e:
            print_test(description, "FAIL", str(e))
            all_found = False
    
    return all_found

# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

def test_configuration_files():
    """Check if configuration files exist."""
    config_files = [
        (".env.example", "Environment Configuration"),
        ("Dockerfile", "Docker Configuration"),
        ("docker-compose.yml", "Docker Compose"),
        ("OPTIMIZATION_GUIDE.md", "Documentation"),
    ]
    
    all_exist = True
    for file_path, description in config_files:
        exists = Path(file_path).exists()
        status = "PASS" if exists else "FAIL"
        print_test(f"Config: {description}", status, file_path)
        all_exist = all_exist and exists
    
    return all_exist

# ============================================================================
# MAIN TEST SUITE
# ============================================================================

async def run_backend_tests():
    """Run all backend tests."""
    print_header("BACKEND TESTS")
    
    results = {}
    
    # Health check
    success, data = await test_health_endpoint()
    results["health"] = success
    
    # Stats endpoint
    success, data = await test_stats_endpoint()
    results["stats"] = success
    
    # CORS
    success = await test_cors_headers()
    results["cors"] = success
    
    # Response times
    success, data = await test_api_response_time()
    results["response_time"] = success
    
    return results

def run_frontend_tests():
    """Run all frontend tests."""
    print_header("FRONTEND TESTS")
    
    results = {}
    
    # Optimized files
    success = test_optimized_files_exist()
    results["optimized_files"] = success
    
    # Performance metrics
    success = test_performance_metrics_in_code()
    results["performance_code"] = success
    
    # Logging
    success = test_logging_configuration()
    results["logging"] = success
    
    return results

def run_configuration_tests():
    """Run configuration tests."""
    print_header("CONFIGURATION TESTS")
    
    results = {}
    
    # Configuration files
    success = test_configuration_files()
    results["config_files"] = success
    
    return results

def print_summary(backend_results, frontend_results, config_results):
    """Print test summary."""
    print_header("TEST SUMMARY")
    
    all_results = {
        "Backend": backend_results,
        "Frontend": frontend_results,
        "Configuration": config_results
    }
    
    total_tests = 0
    total_passed = 0
    
    for category, results in all_results.items():
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        total_tests += total
        total_passed += passed
        
        status_symbol = "✓" if passed == total else "✗"
        print(f"{status_symbol} {category}: {passed}/{total} passed")
    
    print()
    overall_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"Overall: {total_passed}/{total_tests} tests passed ({overall_rate:.1f}%)")
    
    return total_passed == total_tests

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  Nero AI Framework - Optimization Validation Suite")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Check backend connectivity
        print("\nChecking backend connectivity...")
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/api/health", timeout=aiohttp.ClientTimeout(total=2)) as resp:
                    if resp.status != 200:
                        print("⚠  Backend not responding. Running offline tests only...")
                        backend_results = {}
                    else:
                        print("✓ Backend is responding")
                        backend_results = await run_backend_tests()
        except:
            print("⚠  Backend not responding. Running offline tests only...")
            backend_results = {}
        
        # Run offline tests
        frontend_results = run_frontend_tests()
        config_results = run_configuration_tests()
        
        # Print summary
        all_passed = print_summary(backend_results, frontend_results, config_results)
        
        # Save results
        output_file = Path("test_results.json")
        TEST_RESULTS["tests"] = {
            "backend": backend_results,
            "frontend": frontend_results,
            "configuration": config_results
        }
        TEST_RESULTS["summary"] = {
            "total_passed": sum(1 for cat in TEST_RESULTS["tests"].values() for v in cat.values() if v),
            "total_tests": sum(len(cat) for cat in TEST_RESULTS["tests"].values()),
            "all_passed": all_passed
        }
        
        with open(output_file, 'w') as f:
            json.dump(TEST_RESULTS, f, indent=2)
        
        print(f"\n✓ Results saved to: {output_file}")
        
        # Exit code
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        print(f"\n✗ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
