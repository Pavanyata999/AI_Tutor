# AI Tutor Orchestrator

An intelligent middleware orchestrator that autonomously connects conversational AI tutors to multiple educational tools by extracting required parameters from chat context and managing complex tool interactions without manual configuration.

## 🎯 Overview

The AI Tutor Orchestrator acts as the "brain" that sits between a student's conversation with an AI tutor and the actual educational tools (quiz generators, note makers, concept explainers, etc.). It intelligently:

- Understands conversational context and determines educational tool needs
- Extracts parameters from natural conversation using LangChain and LangGraph
- Validates and formats requests for proper tool execution
- Handles diverse tool schemas across multiple educational functionalities
- Maintains conversation state and student personalization context

## 🏗️ Architecture

The system follows a hybrid agent architecture with these core components:

- **Context Analysis Engine**: Parses conversation and identifies educational intent
- **Parameter Extraction System**: Maps conversational elements to tool parameters
- **Tool Orchestration Layer**: Manages API calls using LangGraph workflows
- **State Management**: Maintains conversation context and student profiles
- **Schema Validation**: Ensures data integrity and security

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- PostgreSQL (optional, defaults to SQLite)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-tutor-orchestrator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your OpenAI API key and other configurations
```

4. Start the orchestrator service:
```bash
python main.py
```

5. Start the mock educational tools (in separate terminals):
```bash
python mock_tools/note_maker.py
python mock_tools/flashcard_generator.py
python mock_tools/concept_explainer.py
```

### API Endpoints

- `POST /orchestrate` - Main orchestration endpoint
- `POST /analyze-context` - Analyze conversation context
- `POST /extract-parameters` - Extract parameters from context
- `GET /tools` - List available educational tools
- `GET /health` - Health check endpoint

## 📚 Usage Examples

### Basic Orchestration

```python
import httpx

# Example conversation context
context = {
    "user_info": {
        "user_id": "student123",
        "name": "Alice",
        "grade_level": "10",
        "learning_style_summary": "Visual learner",
        "emotional_state_summary": "Focused and motivated",
        "mastery_level_summary": "Level 6 - Good understanding"
    },
    "chat_history": [
        {"role": "user", "content": "I need help with calculus derivatives"},
        {"role": "assistant", "content": "I'd be happy to help!"}
    ],
    "current_message": "Can you create flashcards for derivatives?",
    "teaching_style": "visual",
    "emotional_state": "focused",
    "mastery_level": 6
}

# Make orchestration request
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/orchestrate",
        json=context
    )
    result = response.json()
    print(result)
```

### Example Response

```json
{
    "success": true,
    "tool_response": {
        "success": true,
        "data": {
            "flashcards": [
                {
                    "front": "What is a derivative?",
                    "back": "A derivative represents the rate of change...",
                    "difficulty": "medium",
                    "examples": ["Example: f(x) = x² has derivative f'(x) = 2x"]
                }
            ]
        }
    },
    "educational_intent": {
        "intent_type": "flashcard_generation",
        "confidence": 0.9,
        "suggested_tool": "flashcard_generator"
    }
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_context_analyzer.py -v
pytest tests/test_tool_orchestrator.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## 📖 Documentation

- [File Structure](filestruct.txt) - Complete project structure
- [System Explanation](explanation.txt) - Detailed architecture explanation
- [Technology Stack](techstack.txt) - Complete technology stack
- [API Documentation](docs/api_documentation.md) - API endpoint documentation

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Application Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Educational Tools URLs
NOTE_MAKER_URL=http://localhost:8001
FLASHCARD_GENERATOR_URL=http://localhost:8002
CONCEPT_EXPLAINER_URL=http://localhost:8003

# Database Configuration
DATABASE_URL=sqlite:///./ai_tutor.db
```

### Tool Configuration

Each educational tool can be configured with custom endpoints and schemas. The system supports:

- **Note Maker**: Generates structured notes with multiple styles
- **Flashcard Generator**: Creates study flashcards with difficulty levels
- **Concept Explainer**: Provides explanations with adaptive depth

## 🎨 Personalization Features

The system incorporates comprehensive personalization:

### Teaching Styles
- **Direct**: Clear, concise, step-by-step instruction
- **Socratic**: Question-based guided discovery learning
- **Visual**: Descriptive imagery and analogical explanations
- **Flipped Classroom**: Application-focused with assumed prior knowledge

### Emotional States
- **Focused/Motivated**: High engagement, ready for challenges
- **Anxious**: Needs reassurance and simplified approach
- **Confused**: Requires clarification and step-by-step breakdown
- **Tired**: Minimal cognitive load, gentle interaction

### Mastery Levels (1-10 Scale)
- **Levels 1-3**: Foundation building with maximum scaffolding
- **Levels 4-6**: Developing competence with guided practice
- **Levels 7-9**: Advanced application and nuanced understanding
- **Level 10**: Full mastery enabling innovation and teaching others

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Scale services
docker-compose up -d --scale orchestrator=3
```

### Kubernetes Deployment

```bash
# Deploy to Kubernetes
kubectl apply -f kubernetes/

# Check deployment status
kubectl get pods
kubectl get services
```

## 📊 Monitoring

The system includes comprehensive monitoring:

- **Health Checks**: `/health` endpoint for service status
- **Metrics**: Performance metrics and statistics
- **Logging**: Structured logging with different levels
- **Error Tracking**: Comprehensive error handling and reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT models
- LangChain team for the excellent framework
- FastAPI team for the modern web framework
- All contributors and testers

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the test examples

---

**Built with ❤️ for intelligent education**
# AI_Tutor
