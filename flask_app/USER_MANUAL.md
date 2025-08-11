# AutoFlow Pro - User Manual

Welcome to AutoFlow Pro, your local web automation tool. This guide explains the main features and how to use them.

Getting Started
- Open http://127.0.0.1:5050 in your browser after starting the app.
- Use the tabs at the top to navigate: Requests, Actions, Scenarios, Environments, Snippets.

Requests
- The Request Manager lists sample requests.
- Click Send to execute a request against the active environment (Development by default).
- Responses are displayed as JSON or text. Pre and post scripts can modify environment variables.

Actions (Selenium)
- Click "Run Selenium Demo" to open a Chrome window and verify a page title.
- Useful for login flows (e.g., Siebel) and other browser automations.

Scenarios
- Run the sample "JSONPlaceholder Flow" to execute multiple steps in sequence.
- Each step may be a request or an action. Results are shown in a summary alert.

Environments
- View key/value pairs used in variable substitution (e.g., {{base_url}}).
- Secrets are masked in the UI. Update values directly in the database or extend the UI.

Snippets
- Preloaded with common JavaScript and Python snippets.
- Copy snippets to reuse when authoring requests and actions.

Trello (Optional)
- If you set TRELLO_API_KEY and TRELLO_TOKEN, the app reads your boards.
- Without keys, it gracefully falls back to JSONPlaceholder sample data.

Tips
- Use {{variable_name}} in URLs or bodies to reuse environment values.
- Pre-request scripts can set variables before a request runs.
- Post-request scripts can extract data from responses into environment variables.
