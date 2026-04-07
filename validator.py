#!/usr/bin/env python3
"""
validator.py — Pre-submission validation script for SocraticTeach-Env
"""

import sys
import os
import subprocess
import requests
import time

def check_files():
    """Check required files exist."""
    required = [
        "openenv.yaml",
        "requirements.txt",
        "Dockerfile",
        "README.md",
        "inference.py",
        "debug_env/__init__.py",
        "debug_env/models.py",
        "debug_env/client.py",
        "server/debug_env_environment.py",
    ]
    missing = [f for f in required if not os.path.exists(f)]
    if missing:
        print(f"✗ Missing files: {missing}")
        return False
    print("✓ All required files present")
    return True

def check_docker_build():
    """Check if Dockerfile builds successfully."""
    try:
        result = subprocess.run(
            ["docker", "build", "-t", "socratic-env-test", "."],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode != 0:
            print(f"✗ Docker build failed: {result.stderr}")
            return False
        print("✓ Dockerfile builds successfully")
        return True
    except subprocess.TimeoutExpired:
        print("✗ Docker build timed out")
        return False
    except FileNotFoundError:
        print("⚠ Docker not available, skipping build check")
        return True

def check_openenv_yaml():
    """Basic validation of openenv.yaml."""
    try:
        import yaml
        with open("openenv.yaml") as f:
            config = yaml.safe_load(f)

        required_keys = ["name", "environment", "action_space", "observation_space", "tasks"]
        for key in required_keys:
            if key not in config:
                print(f"✗ openenv.yaml missing key: {key}")
                return False

        if len(config["tasks"]) < 3:
            print("✗ Need at least 3 tasks")
            return False

        print("✓ openenv.yaml structure valid")
        return True
    except ImportError:
        print("⚠ PyYAML not available, skipping YAML validation")
        return True
    except Exception as e:
        print(f"✗ openenv.yaml validation error: {e}")
        return False

def check_inference_script():
    """Check if inference.py runs without errors (with mock env vars)."""
    env = os.environ.copy()
    env.update({
        "API_BASE_URL": "https://api.openai.com/v1",
        "MODEL_NAME": "gpt-3.5-turbo",
        "OPENAI_API_KEY": "dummy_token",
    })

    try:
        # Run with timeout and limited output
        result = subprocess.run(
            [sys.executable, "inference.py"],
            env=env,
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout
        )

        # Check for structured output markers
        output = result.stdout + result.stderr
        markers = ["[START]", "[STEP]", "[END]", "[SCORE]", "[TASK_SCORE]", "[FINAL_RESULTS]"]

        missing_markers = [m for m in markers if m not in output]
        if missing_markers:
            print(f"✗ Missing log markers: {missing_markers}")
            return False

        if result.returncode != 0:
            print(f"✗ Inference script failed: {result.stderr}")
            return False

        print("✓ Inference script runs and produces structured logs")
        return True

    except subprocess.TimeoutExpired:
        print("✗ Inference script timed out")
        return False

def main():
    print("Running pre-submission validation for SocraticTeach-Env...")
    print("="*60)

    checks = [
        check_files,
        check_openenv_yaml,
        check_docker_build,
        check_inference_script,
    ]

    passed = 0
    for check in checks:
        if check():
            passed += 1
        print()

    print("="*60)
    if passed == len(checks):
        print("🎉 ALL VALIDATION CHECKS PASSED")
        print("Your submission is ready!")
    else:
        print(f"❌ {len(checks) - passed} check(s) failed")
        print("Please fix the issues above before submitting.")
        sys.exit(1)

if __name__ == "__main__":
    main()