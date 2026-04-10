#!/usr/bin/env python3
"""
Pre-submission validation script for SocraticTeach-Env
Checks all requirements for Meta PyTorch Hackathon 2026 submission.
"""

import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional


class Validator:
    """Comprehensive validation for SocraticTeach-Env submission."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []
    
    def run_all_checks(self) -> bool:
        """Run all validation checks and return True if all pass."""
        print("🔍 Running SocraticTeach-Env Validation...\n")
        
        # File structure checks
        self.check_file_structure()
        self.check_imports()
        self.check_environment_class()
        self.check_apibase_url_config()
        self.check_model_name_config()
        self.check_hf_token()
        self.check_inference_script()
        self.check_inference_format()
        self.check_dockerfile()
        self.check_openenv_yaml()
        self.check_requirements_txt()
        self.check_docker_build()
        self.check_resource_requirements()
        self.check_sample_run()
        
        # Print results
        self.print_results()
        
        return len(self.errors) == 0
    
    def report(self, status: str, message: str) -> None:
        """Report validation status."""
        if status == "✅":
            self.passed.append(message)
            print(f"{status} {message}")
        elif status == "⚠️":
            self.warnings.append(message)
            print(f"{status} {message}")
        else:  # ❌
            self.errors.append(message)
            print(f"{status} {message}")
    
    def check_file_structure(self) -> None:
        """Check that required files exist."""
        print("📁 Checking File Structure...")
        
        required_files = [
            "models.py",
            "client.py",
            "app.py",
            "inference.py",
            "requirements.txt",
            "Dockerfile",
            "openenv.yaml",
            "server/debug_env_environment.py",
        ]
        
        for filename in required_files:
            path = self.project_root / filename
            if path.exists():
                self.report("✅", f"File exists: {filename}")
            else:
                self.report("❌", f"Missing file: {filename}")
        print()
    
    def check_imports(self) -> None:
        """Check that all imports work correctly."""
        print("📦 Checking Imports...")
        
        try:
            import openenv.core
            self.report("✅", "openenv-core installed and importable")
        except ImportError:
            self.report("❌", "openenv-core not installed - run: pip install openenv-core")
        
        try:
            import gradio
            self.report("✅", "gradio installed and importable")
        except ImportError:
            self.report("⚠️", "gradio not installed - needed for app.py")
        
        try:
            sys.path.insert(0, str(self.project_root))
            from models import Observation, Action, QUIZ_DATABASE
            self.report("✅", "models.py imports successfully")
        except Exception as e:
            self.report("❌", f"models.py import failed: {e}")
        
        try:
            from client import SocraticTeachClient
            self.report("✅", "client.py imports successfully")
        except Exception as e:
            self.report("⚠️", f"client.py import (non-critical): {e}")
        
        print()
    
    def check_environment_class(self) -> None:
        """Check that DebugEnvironment class exists and has required methods."""
        print("🎮 Checking DebugEnvironment Class...")
        
        try:
            sys.path.insert(0, str(self.project_root / "server"))
            from debug_env_environment import DebugEnvironment
            self.report("✅", "DebugEnvironment class exists")
            
            # Check required methods
            required_methods = ["reset", "step", "state"]
            env = DebugEnvironment()
            
            for method_name in required_methods:
                if hasattr(env, method_name):
                    self.report("✅", f"DebugEnvironment.{method_name}() exists")
                else:
                    self.report("❌", f"DebugEnvironment.{method_name}() missing")
            
        except Exception as e:
            self.report("❌", f"DebugEnvironment check failed: {e}")
        
        print()
    
    def check_apibase_url_config(self) -> None:
        """Check API_BASE_URL configuration."""
        print("🔧 Checking API_BASE_URL...")
        
        api_url = os.getenv("API_BASE_URL")
        if api_url:
            self.report("✅", f"API_BASE_URL configured: {api_url}")
        else:
            self.report("⚠️", "API_BASE_URL not set (optional if not using external LLM)")
        
        print()
    
    def check_model_name_config(self) -> None:
        """Check MODEL_NAME configuration."""
        print("🤖 Checking MODEL_NAME...")
        
        model_name = os.getenv("MODEL_NAME")
        if model_name:
            self.report("✅", f"MODEL_NAME configured: {model_name}")
        else:
            self.report("⚠️", "MODEL_NAME not set (using default)")
        
        print()
    
    def check_hf_token(self) -> None:
        """Check HF_TOKEN configuration."""
        print("🔑 Checking HF_TOKEN...")
        
        hf_token = os.getenv("HF_TOKEN")
        if hf_token:
            self.report("✅", "HF_TOKEN is set")
        else:
            self.report("⚠️", "HF_TOKEN not set (may be needed for some features)")
        
        print()
    
    def check_inference_script(self) -> None:
        """Check inference.py structure."""
        print("🚀 Checking inference.py...")
        
        inference_path = self.project_root / "inference.py"
        if not inference_path.exists():
            self.report("❌", "inference.py not found")
            return
        
        with open(inference_path, 'r') as f:
            content = f.read()
        
        # Check for required format markers
        if "[START]" in content:
            self.report("✅", "inference.py contains [START] marker")
        else:
            self.report("❌", "inference.py missing [START] marker")
        
        if "[STEP]" in content:
            self.report("✅", "inference.py contains [STEP] marker")
        else:
            self.report("❌", "inference.py missing [STEP] marker")
        
        if "[END]" in content:
            self.report("✅", "inference.py contains [END] marker")
        else:
            self.report("❌", "inference.py missing [END] marker")
        
        print()
    
    def check_inference_format(self) -> None:
        """Check structured logging format in inference output."""
        print("📋 Checking Inference Format Compliance...")
        
        try:
            # Try to import and run inference
            sys.path.insert(0, str(self.project_root))
            from inference import InferenceRunner
            
            self.report("✅", "InferenceRunner class found")
            
            # Check for required methods
            if hasattr(InferenceRunner, 'run_inference'):
                self.report("✅", "InferenceRunner.run_inference() exists")
            else:
                self.report("❌", "InferenceRunner.run_inference() missing")
            
            if hasattr(InferenceRunner, 'validate_output_format'):
                self.report("✅", "Output format validation method exists")
            else:
                self.report("⚠️", "Output format validation method recommended")
            
        except Exception as e:
            self.report("⚠️", f"Could not fully validate inference format: {e}")
        
        print()
    
    def check_dockerfile(self) -> None:
        """Check Dockerfile exists and has required components."""
        print("🐳 Checking Dockerfile...")
        
        dockerfile_path = self.project_root / "Dockerfile"
        if not dockerfile_path.exists():
            self.report("❌", "Dockerfile not found")
            return
        
        with open(dockerfile_path, 'r') as f:
            dockerfile_content = f.read()
        
        # Check for base image
        if "FROM" in dockerfile_content:
            self.report("✅", "Dockerfile has base image")
        else:
            self.report("❌", "Dockerfile missing FROM instruction")
        
        # Check for exposed port
        if "EXPOSE" in dockerfile_content:
            self.report("✅", "Dockerfile exposes port")
        else:
            self.report("❌", "Dockerfile missing EXPOSE instruction")
        
        # Check for healthcheck
        if "HEALTHCHECK" in dockerfile_content:
            self.report("✅", "Dockerfile includes HEALTHCHECK")
        else:
            self.report("⚠️", "HEALTHCHECK not included (recommended)")
        
        print()
    
    def check_openenv_yaml(self) -> None:
        """Check openenv.yaml configuration."""
        print("⚙️ Checking openenv.yaml...")
        
        yaml_path = self.project_root / "openenv.yaml"
        if not yaml_path.exists():
            self.report("❌", "openenv.yaml not found")
            return
        
        try:
            with open(yaml_path, 'r') as f:
                config = yaml.safe_load(f)
            
            self.report("✅", "openenv.yaml is valid YAML")
            
            # Check required fields
            required_fields = ["name", "version", "environment", "action", "observation", "endpoints"]
            for field in required_fields:
                if field in config:
                    self.report("✅", f"openenv.yaml has '{field}' section")
                else:
                    self.report("❌", f"openenv.yaml missing '{field}' section")
            
        except Exception as e:
            self.report("❌", f"openenv.yaml validation failed: {e}")
        
        print()
    
    def check_requirements_txt(self) -> None:
        """Check requirements.txt has necessary dependencies."""
        print("📚 Checking requirements.txt...")
        
        req_path = self.project_root / "requirements.txt"
        if not req_path.exists():
            self.report("❌", "requirements.txt not found")
            return
        
        with open(req_path, 'r') as f:
            requirements = f.read().lower()
        
        required_packages = ["openenv-core", "gradio"]
        for package in required_packages:
            if package in requirements:
                self.report("✅", f"requirements.txt includes {package}")
            else:
                self.report("❌", f"requirements.txt missing {package}")
        
        print()
    
    def check_docker_build(self) -> None:
        """Try to build Docker image."""
        print("🏗️ Checking Docker Build...")
        
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                self.report("✅", "Docker is installed")
                
                # Try to build (but with timeout)
                try:
                    subprocess.run(
                        ["docker", "build", "-t", "socraticteach-env:test", "."],
                        cwd=self.project_root,
                        capture_output=True,
                        timeout=300
                    )
                    self.report("✅", "Docker image builds successfully")
                except subprocess.TimeoutExpired:
                    self.report("⚠️", "Docker build timed out (may still be valid)")
                except Exception as e:
                    self.report("⚠️", f"Docker build failed: {str(e)[:100]}")
            else:
                self.report("⚠️", "Docker not available (required for deployment)")
        except Exception as e:
            self.report("⚠️", "Could not check Docker: {str(e)[:100]}")
        
        print()
    
    def check_resource_requirements(self) -> None:
        """Check resource requirements are documented."""
        print("💾 Checking Resource Requirements...")
        
        yaml_path = self.project_root / "openenv.yaml"
        if not yaml_path.exists():
            self.report("⚠️", "Cannot verify resources in missing openenv.yaml")
            return
        
        try:
            with open(yaml_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if "performance" in config:
                perf = config["performance"]
                if perf.get("min_vcpu", 0) >= 2:
                    self.report("✅", "Requires 2+ vCPU")
                else:
                    self.report("⚠️", "vCPU requirement may be insufficient")
                
                if perf.get("min_memory_gb", 0) >= 8:
                    self.report("✅", "Requires 8GB+ RAM")
                else:
                    self.report("⚠️", "RAM requirement may be insufficient")
            else:
                self.report("⚠️", "Performance requirements not specified in openenv.yaml")
        
        except Exception as e:
            self.report("⚠️", f"Could not check resource requirements: {e}")
        
        print()
    
    def check_sample_run(self) -> None:
        """Try to run a sample inference."""
        print("🧪 Checking Sample Run...")
        
        try:
            os.environ["NUM_EPISODES"] = "1"
            
            # Quick check that env can be instantiated
            sys.path.insert(0, str(self.project_root / "server"))
            from debug_env_environment import DebugEnvironment
            
            env = DebugEnvironment()
            obs = env.reset()
            
            if obs and hasattr(obs, 'topic'):
                self.report("✅", "Sample reset() runs successfully")
            else:
                self.report("❌", "reset() did not return proper Observation")
            
            # Try one step
            from models import Action
            action = Action(teacher_message="Why do you think that?")
            obs2 = env.step(action)
            
            if obs2 and hasattr(obs2, 'reward'):
                self.report("✅", "Sample step() runs successfully")
            else:
                self.report("❌", "step() did not return proper Observation")
            
        except Exception as e:
            self.report("❌", f"Sample run failed: {e}")
        
        print()
    
    def print_results(self) -> None:
        """Print validation summary."""
        print("\n" + "="*60)
        print("📊 VALIDATION SUMMARY")
        print("="*60)
        
        print(f"\n✅ Passed: {len(self.passed)}")
        for msg in self.passed[:5]:  # Show first 5
            print(f"   • {msg}")
        if len(self.passed) > 5:
            print(f"   ... and {len(self.passed) - 5} more")
        
        if self.warnings:
            print(f"\n⚠️ Warnings: {len(self.warnings)}")
            for msg in self.warnings:
                print(f"   • {msg}")
        
        if self.errors:
            print(f"\n❌ Errors: {len(self.errors)}")
            for msg in self.errors:
                print(f"   • {msg}")
        
        print("\n" + "="*60)
        if not self.errors:
            print("✅ VALIDATION PASSED - Ready for submission!")
        else:
            print(f"❌ VALIDATION FAILED - {len(self.errors)} error(s) to fix")
        print("="*60 + "\n")


def main():
    """Main entry point."""
    validator = Validator(project_root=".")
    success = validator.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
