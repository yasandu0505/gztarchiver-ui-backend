# Getting Started

## Prerequisites

- Python 3.8+
- Git
- pip


### Installation & Setup

**Fork & Clone the Repository**

   ```bash
   git clone https://github.com/your-username/gztarchiver-ui-backend.git
   cd gztarchiver-ui-backend
   ```

### Development Setup

1. **Create Virtual Environment**
```bash
   # Create virtual environment
   python -m venv .venv

   # Activate virtual environment
   # On Windows:
   .venv\Scripts\activate

   # On macOS/Linux:
   source .venv/bin/activate
   ```
2. **Install Dependencies**

    ```bash
   pip install -r requirements.txt
   ```
   
3. **Environment Configuration**

   Create a `.env` file in the root directory and follow the [env example](./.env.example):

   ```env
   GLOBAL_METADATA_URL=YOUR-GLOBAL-METADATA-URL
   QUERY_API=YOUR-QUERY-API
   CACHE_TTL=YOUR-CACHE-TTL
   REQUEST_TIMEOUT=YOUR-REQUEST-TIMEOUT

   # this part use to configure the CORS settings
   # replace with your frontend URLs
   # for local development, you can use http://localhost:5173 if using Vite
   # for production, replace with your deployed frontend URLs
   # e.g., https://your-frontend.vercel.app or https://your-frontend   
   LOCAL_CORS="YOUR-LOCAL-URL"
   DEPLOYED_CORS="YOUR-DEPLOYED-URL"

   ```
4. **Run the Application**

   ```bash
   # Development server
   uvicorn main:app --reload
   ```

   The API will be available at: `http://localhost:8000` and
   Docs/Contract will be available at: `http://localhost:8000/docs`
