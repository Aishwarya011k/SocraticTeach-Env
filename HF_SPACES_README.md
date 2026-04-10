---
title: SocraticTeach-Env
emoji: 🎓
colorFrom: blue
colorTo: purple
sdk: docker
sdk_version: 1.0
pinned: false
license: mit
---

# SocraticTeach-Env: Interactive Teaching RL Environment

An OpenEnv-compliant reinforcement learning environment where AI agents learn to teach students using the Socratic method.

## 🎓 What is This?

SocraticTeach-Env is a sophisticated RL environment that simulates an interactive teaching scenario. An AI agent (teacher) learns to effectively instruct a student by asking guiding questions, providing hints, and facilitating discovery—rather than directly stating answers.

This implements the **Socratic method**, a proven pedagogical approach where the teacher guides students to arrive at their own conclusions through inquiry.

## ✨ Key Features

- **9 Programming Topics** across 3 difficulty levels (Easy, Medium, Hard)
- **45+ Quiz Questions** (5 MCQ per topic) for comprehensive assessment
- **Student Misconception Tracking** - identifies and measures false beliefs
- **Confusion Score Dynamics** - real-time understanding tracking
- **Multi-Component Reward Formula** - balances improvement, efficiency, and resolution
- **Rule-Based Student Simulator** - no LLM required for baseline
- **Full OpenEnv Compliance** - production-ready RL environment

## 🚀 Quick Start

### Using the Interface

1. Click the **"🔄 Reset Environment"** button to start a new episode
2. Enter a guiding question in the **"Teacher Message"** textbox
3. Click **"📤 Send Message & Step"** to see the student's response
4. Watch the confusion score and reward signals update
5. Continue for up to 10 turns until episode completes

### Example Topics

**Easy:**
- Loops in Python  
- Lists in Python
- Functions in Python

**Medium:**
- Recursion in Python
- Sorting Algorithms
- Binary Search

**Hard:**
- Trees in Computer Science
- Time Complexity
- Dynamic Programming

## 💡 Teaching Tips

✅ **Effective Teaching (→ +0.05 reward):**
- "Why do you think that?"
- "What would happen if...?"
- "Can you explain how...?"
- "Consider what happens when..."

❌ **Ineffective Teaching (→ -0.10 reward):**
- "The answer is..."
- "It means..."
- "You're wrong, actually..."
- Direct statements without questions

## 📊 Understanding Rewards

| Score | Meaning |
|-------|---------|
| **-0.5 to 0.0** | Poor teaching (direct answers, no learning) |
| **0.0 to 0.5** | Decent teaching (some improvement) |
| **0.5 to 1.0** | Excellent teaching (misconception resolved, efficient) |

The reward combines:
- Quiz score improvement (45% weight)
- Misconception resolution (15% bonus)
- Teaching quality (10-25%)
- Efficiency penalty (-5% based on turns)

## 🎮 How Episodes Work

1. **Reset** → Random topic assigned, student given misconception
2. **Pre-Quiz** → Student scores 1-2/5 (has wrong belief)
3. **Teaching (Turns 1-9)** → You ask questions, student responds
4. **Completion (Turn 10)** → Post-quiz runs, final reward calculated
5. **Results** → See misconception resolved status and learning gains

### Episode Flow Example

```
Episode starts: "Loops in Python" (Easy)
Misconception: "while loops always run forever"
Student Pre-Quiz: 1/5 correct
Confusion: 0.8 (very confused)

You ask: "Why do you think while loops always run forever?"
Student: "I don't know, I just assumed..."
Confusion: 0.7 (slightly less confused)
Reward: +0.05 ✅

[Continue for up to 10 turns...]

Episode ends:
Post-Quiz: 3/5 correct (improved!)
Misconception Resolved: Yes ✅
Final Reward: 0.65 (excellent!)
```

## 📚 Topics & Misconceptions

### Easy Level
- **Loops in Python**: "while loops always run forever"
- **Lists in Python**: "lists can only store numbers"
- **Functions in Python**: "functions run automatically when defined"

### Medium Level
- **Recursion in Python**: "recursion always causes infinite loops"
- **Sorting Algorithms**: "bubble sort is always the fastest"
- **Binary Search**: "binary search works on unsorted lists"

### Hard Level
- **Trees in CS**: "binary trees must always be balanced"
- **Time Complexity**: "O(n²) is always slower than O(n log n)"
- **Dynamic Programming**: "DP is just recursion with loops"

## 🔧 Technical Details

- **Framework**: OpenEnv (openenv-core)
- **Language**: Python 3.8+
- **Interface**: Gradio
- **Backend**: Rule-based student simulator
- **Deployment**: Docker container
- **Port**: 7860

## 📖 Full Documentation

For complete documentation, visit the GitHub repository or check the files:
- `README.md` - Full feature documentation
- `DEPLOYMENT.md` - Deployment guide
- `openenv.yaml` - OpenEnv specification
- `validation_script.py` - Environment validation

## 🎓 Use Cases

1. **Educational AI Research** - Study effective teaching strategies
2. **Tutor Development** - Train AI tutoring agents
3. **Teaching Method Evaluation** - Compare Socratic vs. direct instruction
4. **Curriculum Design** - Test progressive difficulty trajectories
5. **Interactive Learning** - Create adaptive educational experiences

## ⚙️ System Requirements

- **CPU**: 2 vCPU minimum
- **RAM**: 8GB minimum
- **Storage**: ~500MB for dependencies
- **Episode Runtime**: < 2 minutes per full episode

## 🔗 Links

- **GitHub**: [Repository](https://github.com/username/socraticteach-env)
- **OpenEnv**: [Documentation](https://github.com/openenv/openenv)
- **Paper**: Research on Socratic teaching methods

## ✅ Validation

This environment has been validated to:
- ✅ Pass OpenEnv compliance checks
- ✅ Handle 45+ quiz questions across 9 topics
- ✅ Support complete 10-turn episodes
- ✅ Calculate rewards accurately
- ✅ Track misconception resolution
- ✅ Provide structured logging

## 💬 Feedback

Try different teaching approaches and observe:
- How confusion scores decrease with good questions
- How misconceptions resolve with Socratic method
- How rewards reflect teaching quality
- How efficiency affects final scores

**Start teaching! 🚀**
