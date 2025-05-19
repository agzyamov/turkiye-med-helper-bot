# Deploying Türkiye Med Helper Bot on Render.com

This guide will help you deploy your Telegram bot on Render.com's free tier with webhooks to prevent the service from sleeping when inactive.

## Setup Steps

### 1. Create a Web Service on Render

1. Sign in to your [Render.com](https://render.com) account
2. Click "New" and select "Web Service"
3. Connect your GitHub repository or upload your code
4. Give your service a name (e.g., "turkiye-med-helper-bot")

### 2. Configure the Service

Fill in the following settings:

- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python eczane_bot.py`
- **Plan**: Free

### 3. Set Environment Variables

In the "Environment" section, add the following environment variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `BOT_TOKEN` | `your-bot-token` | Your Telegram bot token from @BotFather |
| `COLLECT_API_KEY` | `your-api-key` | Your CollectAPI key |
| `RENDER` | `true` | Enables webhook mode |

Render automatically sets `RENDER_EXTERNAL_URL` and `PORT` variables, which our code uses.

### 4. Deploy Your Service

1. Click "Create Web Service"
2. Wait for the initial deployment to complete (this may take a few minutes)

### 5. Test Your Bot

Once deployed, test your bot by:
1. Sending `/start` to your bot in Telegram
2. Trying the `/healthcheck` command
3. Using `/eczaneler` to find pharmacies

## How Webhooks Prevent Sleep

On Render's free tier, services go to sleep after 15 minutes of inactivity. However, with webhook mode:

1. When a user sends a message to your bot, Telegram sends an HTTP request to your Render app
2. This request automatically wakes up your app if it's sleeping
3. Your app processes the message and responds
4. After 15 minutes without messages, your app goes back to sleep
5. When the next message arrives, the cycle repeats

This approach is much more efficient than polling, where your app would continuously check for messages and never go to sleep.

## Troubleshooting

If your bot isn't responding:

1. Check the logs in your Render dashboard for any errors
2. Verify that all environment variables are set correctly
3. Make sure your bot token is valid
4. Check if the webhook is set up correctly by visiting:
   `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo`

## Maintaining the Bot

- Monitor your bot's performance through the Render dashboard
- Check the logs periodically for any errors or issues
- Remember that on the free tier, your bot will take a few seconds to wake up when receiving the first message after a period of inactivity
