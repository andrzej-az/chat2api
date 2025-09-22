# CHAT2API

🤖 A simple ChatGPT to API proxy

🌟 Use free, unlimited `GPT-3.5` without an account.

💥 Supports using accounts with AccessToken, with support for `O3-mini/high`, `O1/mini/Pro`, `GPT-4/4o/mini`, and `GPTs`.

🔍 The response format is identical to the official API, making it compatible with almost all clients.

👮 When used with the user management frontend [Chat-Share](https://github.com/h88782481/Chat-Share), you must configure environment variables in advance (set ENABLE_GATEWAY to True and AUTO_SEED to False).


## Community Group

[https://t.me/chat2api](https://t.me/chat2api)

Please read the repository documentation, especially the FAQ section, before asking questions.

When asking a question, please provide:

1. A screenshot of the startup logs (with sensitive information redacted, including environment variables and version number).
2. The error log information (with sensitive information redacted).
3. The status code and response body of the API request.

## Features

### The latest version number is stored in `version.txt`

### Reverse-Engineered API Features
> - [x] Streaming and non-streaming responses
> - [x] Login-free GPT-3.5 conversations
> - [x] GPT-3.5 model conversations (if the model name passed does not include gpt-4, it defaults to gpt-3.5, i.e., text-davinci-002-render-sha)
> - [x] GPT-4 series model conversations (pass a model name containing: gpt-4, gpt-4o, gpt-4o-mini, gpt-4-mobile to use the corresponding model; requires an AccessToken)
> - [x] O1 series model conversations (pass a model name containing o1-preview, o1-mini to use the corresponding model; requires an AccessToken)
> - [x] GPT-4 model for drawing, coding, and browsing
> - [x] Support for GPTs (pass model name: gpt-4-gizmo-g-*)
> - [x] Support for Team Plus accounts (requires passing the team account id)
> - [x] Upload images and files (in the API's corresponding format, supports URL and base64)
> - [x] Can be used as a gateway for distributed multi-machine deployment
> - [x] Multi-account polling, supporting both `AccessToken` and `RefreshToken`
> - [x] Automatic retries on request failure, automatically polls the next token
> - [x] Token management, with support for uploading and clearing
> - [x] Scheduled refresh of `AccessToken` using `RefreshToken` / A non-forced refresh of all tokens will occur on every startup, and a forced refresh will occur every 4 days at 3 AM.
> - [x] Support for file downloads (requires history to be enabled)
> - [x] Support for inference process output for models like `O3-mini/high`, `O1/mini/Pro`

### Official Website Mirror Features
> - [x] Supports the native official website mirror
> - [x] Randomly selects from a backend account pool, `Seed` sets a random account
> - [x] Log in directly by entering a `RefreshToken` or `AccessToken`
> - [x] Supports `O3-mini/high`, `O1/mini/Pro`, `GPT-4/4o/mini`
> - [x] Disables sensitive information endpoints and some setting endpoints
> - [x] `/login` page, automatically redirects to the login page after logout
> - [x] `/?token=xxx` for direct login, where xxx can be a `RefreshToken`, `AccessToken`, or `SeedToken` (random seed)
> - [x] Supports session isolation for different SeedTokens
> - [x] Supports the `GPTs` store
> - [x] Supports official-exclusive features like `DeepResearch`, `Canvas`, etc.
> - [x] Supports switching between different languages


> TODO
> - [ ] Nothing for now, feel free to open an `issue`

## Reverse-Engineered API

An API with a format completely identical to `OpenAI`, supporting `AccessToken` or `RefreshToken`. It can be used with GPT-4, GPT-4o, GPT-4o-Mini, GPTs, O1-Pro, O1, O1-Mini, O3-Mini, O3-Mini-High:

```bash
curl --location 'http://127.0.0.1:5005/v1/chat/completions' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{Token}}' \
--data '{
     "model": "gpt-3.5-turbo",
     "messages": [{"role": "user", "content": "Say this is a test!"}],
     "stream": true
   }'
```

Pass your account's `AccessToken` or `RefreshToken` as `{{ Token }}`.
You can also use the value of your `Authorization` environment variable, which will randomly select a backend account.

If you have a team account, you can pass `ChatGPT-Account-ID` to use the Team workspace:

- Method 1:
Pass the `ChatGPT-Account-ID` value in the `headers`.

- Method 2:
`Authorization: Bearer <AccessToken or RefreshToken>,<ChatGPT-Account-ID>`

If you have set the `AUTHORIZATION` environment variable, you can pass its value as `{{ Token }}` to enable multi-token polling.

> - `AccessToken` retrieval: After logging into the official ChatGPT website, open [https://chatgpt.com/api/auth/session](https://chatgpt.com/api/auth/session) to get the `accessToken` value.
> - `RefreshToken` retrieval: This method is not provided here.
> - Login-free gpt-3.5 does not require a token.

## Tokens Management

1. Configure the `AUTHORIZATION` environment variable as your `Auth Code`, then run the program.

2. Visit `/tokens` or `/{api_prefix}/tokens` to view the number of existing tokens, upload new tokens, or clear all tokens.

3. When making a request, pass the `Auth Code` configured in `AUTHORIZATION` to use the polled tokens for conversation.

![tokens.png](docs/tokens.png)

## Official Website Mirror

1. Set the `ENABLE_GATEWAY` environment variable to `true`, then run the program. Note that once enabled, others can access your gateway directly via the domain.

2. Upload `RefreshToken` or `AccessToken` on the Tokens Management page.

3. Visit `/login` to go to the login page.

![login.png](docs/login.png)

4. Enter the native official website mirror to start using it.

![chatgpt.png](docs/chatgpt.png)

## Environment Variables

Each environment variable has a default value. If you don't understand the meaning of an environment variable, do not set it, and especially do not pass an empty value. Strings do not need quotes.

| Category | Variable Name | Example Value | Default Value | Description |
|---|---|---|---|---|
| Security | API_PREFIX | `your_prefix` | `None` | API prefix password. If not set, it can be easily accessed. If set, requests must be made to `/your_prefix/v1/chat/completions`. |
| | AUTHORIZATION | `your_first_authorization`,<br/>`your_second_authorization` | `[]` | Your self-defined authorization codes for multi-account token polling, separated by commas. |
| | AUTH_KEY | `your_auth_key` | `None` | Set this if your private gateway requires an `auth_key` header for requests. |
| Request Related | CHATGPT_BASE_URL | `https://chatgpt.com` | `https://chatgpt.com` | ChatGPT gateway address. Setting this will change the requested website. Multiple gateways can be separated by commas. |
| | PROXY_URL | `http://ip:port`,<br/>`http://username:password@ip:port` | `[]` | Global proxy URL. Enable this if you encounter 403 errors. Multiple proxies can be separated by commas. |
| | EXPORT_PROXY_URL | `http://ip:port` or<br/>`http://username:password@ip:port` | `None` | Egress proxy URL, to prevent leaking the source IP when requesting images and files. |
| Functionality | HISTORY_DISABLED | `true` | `true` | Whether to disable saving chat history and return a conversation_id. |
| | POW_DIFFICULTY | `00003a` | `00003a` | The proof-of-work difficulty to solve. Do not change if you don't understand it. |
| | RETRY_TIMES | `3` | `3` | Number of retries on error. Using `AUTHORIZATION` will automatically poll the next random/sequential account. |
| | CONVERSATION_ONLY | `false` | `false` | Whether to use the conversation endpoint directly. Enable this only if your gateway supports automatic `POW` solving. |
| | ENABLE_LIMIT | `true` | `true` | If enabled, it will not attempt to bypass official rate limits, helping to prevent account bans. |
| | UPLOAD_BY_URL | `false` | `false` | If enabled, conversations in the format `URL + space + text` will automatically parse the URL content and upload it. Multiple URLs are separated by spaces. |
| | SCHEDULED_REFRESH | `false` | `false` | Whether to schedule `AccessToken` refreshes. If enabled, a non-forced refresh of all tokens will occur on startup, and a forced refresh will occur every 4 days at 3 AM. |
| | RANDOM_TOKEN | `true` | `true` | Whether to randomly select a backend `Token`. If enabled, it will use a random backend account; if disabled, it will be sequential polling. |
| Gateway | ENABLE_GATEWAY | `false` | `false` | Whether to enable gateway mode. If enabled, the mirror site can be used, but it will be unprotected. |
| | AUTO_SEED | `false` | `true` | Whether to enable random account mode. Enabled by default. Entering a `seed` will randomly match a backend `Token`. If disabled, you need to manually integrate with an API for `Token` management. |

## Deployment

### Direct Deployment

```bash
git clone https://github.com/andrzej-az/chat2api
cd chat2api
pip install -r requirements.txt
python app.py
```

### Docker Deployment

You need to have Docker and Docker Compose installed.

```bash
docker run -d \
  --name chat2api \
  -p 5005:5005 \
  andrzejaz/chat2api:latest
```

### (Recommended, for PLUS accounts) Docker Compose Deployment

Create a new directory, for example `chat2api`, and enter it:

```bash
mkdir chat2api
cd chat2api
```

Download the `docker-compose-warp.yml` file from the repository into this directory:

```bash
wget https://raw.githubusercontent.com/andrzej-az/chat2api/main/docker-compose-warp.yml
```

Modify the environment variables in the `docker-compose-warp.yml` file, save it, and then run:

```bash
docker-compose up -d
```


## Frequently Asked Questions (FAQ)

> - Error Codes:
>   - `401`: The current IP does not support login-free access. Please try changing your IP address, setting a proxy in the `PROXY_URL` environment variable, or your authentication has failed.
>   - `403`: Please check the logs for specific error information.
>   - `429`: The request limit for the current IP has been exceeded within an hour. Please try again later or change your IP.
>   - `500`: Internal server error; the request failed.
>   - `502`: Bad gateway error or network is unavailable. Please try changing your network environment.

> - Known Issues:
>   - Many IPs from Japan do not support login-free access. It is recommended to use a US IP for login-free GPT-3.5.
>   - 99% of accounts support free `GPT-4o`, but it is enabled based on IP region. Currently, Japan and Singapore IPs are known to have a higher probability of being enabled.

> - What is the `AUTHORIZATION` environment variable?
>   - It is a self-defined authentication for chat2api. It must be set to use the saved token polling feature. Pass it as the `APIKEY` in your requests.
> - How to get an AccessToken?
>   - After logging into the official ChatGPT website, open [https://chatgpt.com/api/auth/session](https://chatgpt.com/api/auth/session) to get the `accessToken` value.


## License

MIT License
