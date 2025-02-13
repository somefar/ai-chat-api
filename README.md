# AI Chat API

This is a FastAPI-based backend service that integrates multiple AI chat models (ChatGPT, Claude, and DeepSeek) into a single API endpoint.

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
4. Run the server locally:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### POST /api/chat
Send a message to any of the supported AI models.

Request body:
```json
{
    "message": "Your message here",
    "model": "gpt|claude|deepseek",
    "conversation_id": "optional_conversation_id"
}
```

### GET /api/health
Health check endpoint to verify the API is running.

## Deployment to Cloudflare

1. Install Wrangler (Cloudflare CLI):
   ```bash
   npm install -g wrangler
   ```

2. Login to Cloudflare:
   ```bash
   wrangler login
   ```

3. Configure Environment Variables in Cloudflare Dashboard:
   - Go to Workers & Pages > Your Worker > Settings > Variables
   - Add the following variables:
     - OPENAI_API_KEY
     - ANTHROPIC_API_KEY
     - DEEPSEEK_API_KEY

4. Update wrangler.toml:
   - Get your zone_id from Cloudflare Dashboard > Your Domain > Overview
   - Add it to the zone_id field in wrangler.toml

5. Deploy:
   ```bash
   wrangler deploy
   ```

6. Configure DNS in Cloudflare:
   - Add an A record pointing to your Worker
   - Enable SSL/TLS to Full (strict)

## Domain Setup

1. Point your domain (somefar.com) to your server
2. Configure SSL certificates for HTTPS
3. Update CORS settings in main.py if needed

## Security Notes

- Never commit your .env file
- Keep your API keys secure
- Use HTTPS in production
- Consider implementing rate limiting and authentication
- Cloudflare provides additional security features like:
  - DDoS protection
  - Web Application Firewall (WAF)
  - Rate limiting
  - Bot protection 