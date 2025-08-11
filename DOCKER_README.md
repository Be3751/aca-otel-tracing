# Local Development Setup

## Quick Start

1. **Copy environment variables:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env with your Azure credentials:**
   - Add your Application Insights connection string
   - Add your Azure Storage account details (for receipt service)

3. **Choose your development mode:**

   ### Development Mode (Recommended for coding)
   ```bash
   # Uses bind mounts for live code reloading - no rebuild needed
   docker compose -f docker-compose.dev.yml up --build
   ```
   
   ### Production Mode
   ```bash
   # Traditional build - requires rebuild on code changes
   docker compose up --build
   ```

4. **View logs to see traceparent headers:**
   ```bash
   # In separate terminal windows
   docker compose logs -f checkout
   docker compose logs -f order-processor  
   docker compose logs -f receipt
   ```

## Development Workflow

### With Development Mode (docker-compose.dev.yml):
- ✅ Code changes instantly reflected (no rebuild)
- ✅ Flask auto-reload enabled
- ✅ Debug mode enabled
- ✅ Bind mounts for live updates
- 🔄 Just edit files and save - changes appear immediately

### With Production Mode:
- 🔄 Requires `docker compose build` after code changes
- 📦 Better for final testing before deployment

## Service Details

- **checkout**: Runs continuously, sends orders every 60 seconds to order-processor
- **order-processor**: Flask API on port 8001, forwards to receipt service
- **receipt**: Flask API on port 8002, saves orders to Azure Blob Storage

## Expected Output

You should see traceparent headers printed in the logs:
- checkout: `Outgoing traceparent (checkout -> order-processor): 00-xxxxx-xxxxx-01`
- order-processor: `Incoming traceparent` and `Outgoing traceparent`  
- receipt: `Incoming traceparent (order-processor -> receipt): 00-xxxxx-xxxxx-01`

## Stopping Services

```bash
docker compose down
```

## Troubleshooting

- If services fail to start, check your .env file has valid Azure credentials
- For receipt service errors, ensure the Azure Storage container exists
- Check service logs with `docker compose logs <service_name>`
