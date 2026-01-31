# Recommended Prompts for Future Sessions

This document contains optimized prompts for common tasks with the Engram Trading Bot.

---

## 🧪 Testing Prompts

### Comprehensive Testing
```
Run comprehensive tests on the Engram Trading Bot including:
- Integration tests for Engram-FreqTrade connectivity
- Telegram bot functionality tests (all commands)
- LMStudio AI connectivity and fallback tests
- Performance benchmarks (throughput, latency, memory)
- Stress tests (concurrent operations, memory leaks)
- Edge case and error recovery tests
- Security validation tests

Generate detailed test reports with pass/fail rates, performance metrics, and consolidate all results into a final summary.
```

### Quick Smoke Tests
```
Run quick smoke tests on the Engram Trading Bot to verify:
- Bot starts successfully
- Telegram connectivity works
- LMStudio or fallback AI responds
- Basic commands work (/start, /status, /help)
- Configuration loads correctly

Provide a pass/fail summary.
```

### Performance Testing
```
Run performance tests on the Engram Trading Bot:
- Measure operations per second
- Test concurrent message handling (10+ simultaneous)
- Check memory usage and detect leaks
- Benchmark response times
- Test under sustained load (30+ seconds)

Report metrics and identify bottlenecks.
```

### Security Testing
```
Run security tests on the Engram Trading Bot:
- Test authentication and authorization
- Verify no credentials are logged or exposed
- Test input validation and sanitization
- Check for SQL injection vulnerabilities
- Verify secure API communication
- Test rate limiting and abuse prevention

Generate security audit report.
```

---

## 🚀 Deployment Prompts

### Production Deployment Preparation
```
Prepare the Engram Trading Bot for production deployment:
- Verify all configurations are production-ready
- Test all critical paths (100% pass required)
- Generate comprehensive deployment documentation
- Create quick start guide
- Validate security settings
- Check environment variable configuration
- Test fallback mechanisms
- Generate deployment checklist

Provide production readiness certification.
```

### Docker Deployment
```
Create Docker deployment for the Engram Trading Bot:
- Write Dockerfile with all dependencies
- Create docker-compose.yml for multi-container setup
- Add environment variable configuration
- Include health checks
- Add volume mounts for persistence
- Create deployment documentation
- Test Docker build and run

Provide Docker deployment guide.
```

### Cloud Deployment (AWS/GCP/Azure)
```
Create cloud deployment guide for the Engram Trading Bot on [AWS/GCP/Azure]:
- Recommend instance types and sizes
- Create deployment scripts
- Configure auto-scaling
- Set up monitoring and logging
- Configure security groups and firewalls
- Add backup and disaster recovery
- Create cost estimation

Provide complete cloud deployment guide.
```

---

## 🔧 Configuration Prompts

### LMStudio Endpoint Update
```
Update LMStudio endpoint configuration to [NEW_ENDPOINT]:
- Update all configuration files (JSON, Python, shell scripts)
- Update documentation references
- Test connectivity to new endpoint
- Verify fallback mechanisms still work
- Run integration tests
- Update environment variable examples

Provide update summary with files changed.
```

### Environment Variable Migration
```
Migrate all hardcoded credentials to environment variables:
- Identify all hardcoded tokens, API keys, passwords
- Replace with environment variable lookups
- Update configuration loading logic
- Add .env.example file
- Update documentation
- Test with environment variables
- Verify no credentials in code

Provide migration guide and security improvements.
```

### Telegram Bot Configuration
```
Configure Telegram bot for the Engram Trading Bot:
- Set up bot token and chat ID
- Configure notification settings
- Test message sending and receiving
- Set up command handlers
- Configure rate limiting
- Test error handling
- Verify real chat_id (no mock values)

Provide configuration guide and test results.
```

---

## 📚 Documentation Prompts

### Comprehensive Documentation
```
Create comprehensive documentation for the Engram Trading Bot:
- README.md with overview and quick start
- Deployment guides (quick start, detailed, platform-specific)
- Configuration guides (all settings explained)
- API documentation (all endpoints and methods)
- Testing guides (how to run tests)
- Troubleshooting guides (common issues and solutions)
- Architecture documentation (system design)
- Contributing guidelines

Organize in docs/ folder with clear structure.
```

### API Documentation
```
Generate API documentation for the Engram Trading Bot:
- Document all REST endpoints
- Document all Telegram commands
- Document all configuration options
- Include request/response examples
- Add error codes and messages
- Include authentication details
- Add rate limiting information

Use OpenAPI/Swagger format if possible.
```

### Troubleshooting Guide
```
Create troubleshooting guide for the Engram Trading Bot:
- Common issues and solutions
- Error messages and their meanings
- Debugging steps
- Log file locations and interpretation
- Network connectivity issues
- LMStudio timeout issues
- Telegram bot issues
- Configuration problems

Include diagnostic commands and expected outputs.
```

---

## 🔍 Analysis Prompts

### Code Review
```
Perform comprehensive code review of the Engram Trading Bot:
- Check code quality and style
- Identify potential bugs
- Review error handling
- Check security vulnerabilities
- Review performance optimizations
- Check documentation completeness
- Suggest improvements

Provide detailed review report with recommendations.
```

### Performance Analysis
```
Analyze performance of the Engram Trading Bot:
- Profile CPU usage
- Analyze memory consumption
- Identify bottlenecks
- Review database queries
- Check API call efficiency
- Analyze response times
- Suggest optimizations

Provide performance analysis report with recommendations.
```

### Security Audit
```
Perform security audit of the Engram Trading Bot:
- Review authentication and authorization
- Check for credential exposure
- Review input validation
- Check for injection vulnerabilities
- Review API security
- Check dependency vulnerabilities
- Review logging practices

Provide security audit report with risk ratings.
```

---

## 🛠️ Enhancement Prompts

### Add New Feature
```
Add [FEATURE_NAME] to the Engram Trading Bot:
- Design the feature architecture
- Implement the feature
- Add comprehensive tests
- Update documentation
- Test integration with existing features
- Verify no regressions
- Update configuration if needed

Provide implementation summary and test results.
```

### Improve Error Handling
```
Enhance error handling in the Engram Trading Bot:
- Add try-catch blocks where missing
- Implement retry logic with exponential backoff
- Add graceful degradation
- Improve error messages
- Add error logging
- Implement fallback mechanisms
- Test all error scenarios

Provide error handling improvements summary.
```

### Add AI Fallback
```
Implement AI fallback mechanism for the Engram Trading Bot:
- Create fallback chain (Primary AI → Secondary AI → Rule-Based)
- Implement fast timeout detection
- Add automatic failover
- Implement health checks
- Add fallback status logging
- Test all fallback scenarios
- Update documentation

Provide fallback implementation guide and test results.
```

---

## 🐛 Debugging Prompts

### Debug Specific Issue
```
Debug [ISSUE_DESCRIPTION] in the Engram Trading Bot:
- Reproduce the issue
- Analyze logs and error messages
- Identify root cause
- Implement fix
- Test the fix
- Verify no regressions
- Update documentation if needed

Provide debugging report with root cause and solution.
```

### Debug LMStudio Timeout
```
Debug LMStudio timeout issues in the Engram Trading Bot:
- Test LMStudio connectivity
- Check network configuration
- Analyze timeout settings
- Test with different timeout values
- Implement retry logic
- Add fallback mechanism
- Test all scenarios

Provide timeout debugging report and solution.
```

### Debug Memory Leak
```
Debug memory leak in the Engram Trading Bot:
- Profile memory usage over time
- Identify memory leak sources
- Analyze object retention
- Implement fixes
- Test with long-running operations
- Verify leak is fixed
- Add memory monitoring

Provide memory leak analysis and fix report.
```

---

## 📊 Reporting Prompts

### Generate Test Report
```
Generate comprehensive test report for the Engram Trading Bot:
- Summarize all test suites
- Calculate overall pass rate
- Highlight critical path results
- Show performance metrics
- List all failures with details
- Provide recommendations
- Include test coverage statistics

Format as professional report with charts if possible.
```

### Generate Deployment Report
```
Generate deployment readiness report for the Engram Trading Bot:
- Verify all tests pass
- Check configuration completeness
- Verify security settings
- Check documentation completeness
- List deployment requirements
- Provide deployment checklist
- Include risk assessment

Provide production readiness certification.
```

### Generate Performance Report
```
Generate performance report for the Engram Trading Bot:
- Measure throughput (ops/sec)
- Measure latency (response times)
- Measure resource usage (CPU, memory)
- Test under load
- Compare with benchmarks
- Identify bottlenecks
- Provide optimization recommendations

Include performance charts and metrics.
```

---

## 🔄 Maintenance Prompts

### Update Dependencies
```
Update dependencies for the Engram Trading Bot:
- Check for outdated packages
- Update to latest stable versions
- Test compatibility
- Run all tests
- Update documentation
- Check for breaking changes
- Update requirements.txt/package.json

Provide dependency update report.
```

### Refactor Code
```
Refactor [MODULE_NAME] in the Engram Trading Bot:
- Improve code structure
- Remove code duplication
- Improve naming
- Add type hints
- Improve documentation
- Maintain functionality
- Run all tests

Provide refactoring summary with improvements.
```

### Optimize Performance
```
Optimize performance of the Engram Trading Bot:
- Profile current performance
- Identify bottlenecks
- Implement optimizations
- Benchmark improvements
- Verify no regressions
- Update documentation
- Run all tests

Provide performance optimization report with before/after metrics.
```

---

## 🎯 Quick Reference

### Most Common Prompts

1. **Quick Test**: "Run quick smoke tests on the Engram Trading Bot"
2. **Full Test**: "Run comprehensive tests on the Engram Trading Bot"
3. **Deploy**: "Prepare the Engram Trading Bot for production deployment"
4. **Update Endpoint**: "Update LMStudio endpoint to [NEW_URL]"
5. **Debug Issue**: "Debug [ISSUE] in the Engram Trading Bot"

### Template Format

```
[ACTION] [TARGET] for the Engram Trading Bot:
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

Provide [DELIVERABLE].
```

---

## 💡 Tips for Effective Prompts

1. **Be Specific**: Clearly state what you want
2. **Include Context**: Mention the Engram Trading Bot
3. **List Requirements**: Break down what needs to be done
4. **Request Deliverables**: Specify what output you want
5. **Set Quality Standards**: Mention pass rates, coverage, etc.
6. **Include Testing**: Always ask for testing
7. **Request Documentation**: Ask for docs to be updated

---

**Last Updated**: January 31, 2026
**Version**: 1.0
**Status**: Production Ready
