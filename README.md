# Video Surveillance Analysis Tool

A Python-based video surveillance analysis tool that uses Google's ADK (Agent Development Kit) to analyze video content for security threats and suspicious activities.


## Prerequisites

- Python 3.8 or higher
- Google API key for Gemini AI
- Video files to analyze

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/srinivasg0/threat-detection.git
   cd threatagent
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up your Google API key after creating .env file**
   ```
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY= Your_API_KEY
   ```

## Usage

### Basic Usage

1. **Add video files**
   
   Place your video files in the `videos/` directory. The tool supports common video formats (MP4, AVI, MOV, etc.).

2. **Run the analysis**

   python run.py


### Testing

The project includes several test scripts to verify functionality:

- **Test video extraction**: `python test_video_extraction.py`
- **Test video summarization**: `python test_video_summarization.py`
- **Test simple run**: `python test_simple_run.py`

### Configuration

You can modify the analysis parameters in `src/settings.py`:

- Frame extraction rate
- Analysis thresholds
- Output format settings

## Project Structure

```
threatagent/
├── src/                    # Source code
│   ├── agents/            # AI agent implementations
│   ├── tools/             # Utility tools and helpers
│   ├── results/           # Output directory for results
│   ├── run_batch.py       # Main batch processing logic
│   ├── settings.py        # Configuration settings
│   └── __init__.py
├── videos/                # Input video files directory
├── requirements.txt       # Python dependencies
├── run.py                 # Main entry point
├── setup.py              # Package setup script
└── README.md             # This file
```






